"""Explicit oracle process driver. No process starts at import or compilation."""
from pathlib import Path
import os
import shutil
import signal
import selectors
import subprocess
import sys
import time
import math
from phase363_oracle_storage import directory, pin, write_new

MIB = 1024**2
USER_PREFIX = 'data/godot/app_userdata/Backpack Battles/'
USER_NAMES = {USER_PREFIX + name for name in ('logs/godot.log','full/backpack.cfg','full/backpack.save',
    'full/backup/backup_1.save','full/continue.save','full/history.db')}


def user_kind(name):
    if name in USER_NAMES: return 'unique-native-user-evidence'
    if name.startswith(USER_PREFIX + 'native-capture/'): return 'raw-native-capture'
    if name.startswith('cache/'): return 'isolated-runtime-cache-retained'
    if name.startswith('tmp/xvfb-run.') and name.endswith('/Xauthority'): return 'ephemeral-Xauthority-retained'
    if name.startswith(USER_PREFIX): return 'native-application-data-retained'
    if name.startswith(('config/','run/','tmp/')): return 'isolated-runtime-file-retained'
    raise ValueError('outside declared native user roots: ' + name)


def usage(root):
    total = 0; files = 0
    for path in root.rglob('*'):
        if path.is_symlink(): raise ValueError('new run symlink')
        if path.is_file():
            try: total += path.stat().st_size
            except FileNotFoundError: continue # runtime temp removed between scans
            files += 1
            if path.is_relative_to(root / 'user'): user_kind(path.relative_to(root / 'user').as_posix())
    if total > 1536*MIB: raise ValueError('attempt write threshold1536MiB')
    if shutil.disk_usage(root).free < 4*1024**3: raise ValueError('4GiB free floor')
    return dict(bytes=total, files=files)


def environment(task, run):
    return dict(PATH=str(task / 'debian/usr/bin') + ':/usr/bin:/bin', LANG='C.UTF-8', USER='agent', LOGNAME='agent',
        XDG_DATA_HOME=str(run/'user/data'), XDG_CONFIG_HOME=str(run/'user/config'), XDG_CACHE_HOME=str(run/'user/cache'),
        XDG_RUNTIME_DIR=str(run/'user/run'), TMPDIR=str(run/'user/tmp'), LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe',
        LD_LIBRARY_PATH=str(task/'debian/usr/lib/x86_64-linux-gnu'))


def command(source_root, task, project, output, check_only):
    args = [sys.executable, str(source_root/'tests/godotsteam_offline_exec.py'),
        str(task/'debian/usr/bin/xvfb-run'), '-a', '-s', '-screen 0 1280x720x24 -nolisten tcp', '-e', str(output/'xvfb.log'),
        str(task/'engine/godotsteam.362.editor.x86_64'), '--path', str(project), '--audio-driver', 'Dummy', '--time-scale', '1.0']
    return args + (['--check-only','--script','res://native_combat_capture.gd'] if check_only
                   else ['--script','res://native_combat_capture.gd','res://Core/Main.tscn'])


def _seconds(value,positive=True):
    if type(value) not in (int,float) or not math.isfinite(value) or (value<=0 if positive else value<0):
        raise ValueError('finite monitor timing parameter')
    return float(value)


def _group_members(pgid):
    """Inspect only the spawned session/group; zombies are reported, not live."""
    result=[]
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit(): continue
        try:
            fields=(entry/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[2])==pgid and int(fields[3])==pgid:
                result.append(dict(pid=int(entry.name),state=fields[0],live=fields[0] not in ('Z','X')))
        except (FileNotFoundError,ProcessLookupError,PermissionError): continue
    return sorted(result,key=lambda row:row['pid'])


def _signal_group(pgid,kind):
    try: os.killpg(pgid,kind); return True
    except ProcessLookupError: return False


def cleanup_process_group(proc,term_grace_seconds=5.0,kill_grace_seconds=0.5):
    """TERM→grace→KILL remaining own group, even if leader already exited."""
    term_grace=_seconds(term_grace_seconds,False);kill_grace=_seconds(kill_grace_seconds,False)
    pgid=proc.pid
    if pgid<=1 or pgid==os.getpgrp() or pgid==os.getsid(0): raise ValueError('refuse caller process group')
    started=time.monotonic();before=_group_members(pgid)
    term_sent=_signal_group(pgid,signal.SIGTERM)
    deadline=started+term_grace
    while any(row['live'] for row in _group_members(pgid)) and time.monotonic()<deadline:
        proc.poll() # nonblocking reap of our leader, unrelated to descendant test
        time.sleep(min(0.01,max(0.0,deadline-time.monotonic())))
    remaining=_group_members(pgid)
    kill_sent=False
    if any(row['live'] for row in remaining):
        kill_sent=_signal_group(pgid,signal.SIGKILL)
        deadline=time.monotonic()+kill_grace
        while any(row['live'] for row in _group_members(pgid)) and time.monotonic()<deadline:
            proc.poll();time.sleep(min(0.01,max(0.0,deadline-time.monotonic())))
    proc.poll()
    after=_group_members(pgid)
    return dict(pgid=pgid,leader_returncode=proc.returncode,term_sent=term_sent,kill_sent=kill_sent,
        term_grace_seconds=term_grace,kill_grace_seconds=kill_grace,before=before,after=after,
        live_remaining=[row for row in after if row['live']],zombies_not_claimed_reaped=[row['pid'] for row in after if not row['live']],
        duration_seconds=time.monotonic()-started)


def monitor_command(command_args,cwd,env,output_dir,prefix,wall_seconds,*,scan_callback=None,
                    poll_seconds=0.05,term_grace_seconds=0.2,kill_grace_seconds=0.5,
                    log_limit_bytes=32*MIB,phase_markers=(),initial_phase_seconds=None,abort_markers=()):
    """Real generic child monitor; never a capture, oracle wrapper or FakeNative.

    One selector wait per iteration. The interval additionally includes actual
    IO/scan overhead, exposed by timestamps/max gap; no timed proc.wait here.
    """
    if type(command_args) is not list or not command_args or any(type(arg) is not str for arg in command_args):
        raise ValueError('explicit argv list')
    if type(prefix) is not str or not prefix or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in prefix):
        raise ValueError('simple unique monitor output prefix')
    if type(log_limit_bytes) is not int or log_limit_bytes<1: raise ValueError('positive log cap INT')
    wall=_seconds(wall_seconds);poll=_seconds(poll_seconds)
    _seconds(term_grace_seconds,False);_seconds(kill_grace_seconds,False)
    if scan_callback is not None and not callable(scan_callback): raise ValueError('monitor scan callback')
    cwd,output=directory(cwd),directory(output_dir)
    stdout_path,stderr_path=output/(prefix+'-stdout.log'),output/(prefix+'-stderr.log')
    if stdout_path.exists() or stderr_path.exists(): raise ValueError('unique process attempt')
    started=time.monotonic();wall_deadline=started+wall
    phase='startup';phase_deadline=None if initial_phase_seconds is None else started+_seconds(initial_phase_seconds)
    observed=set();tails={'stdout':'','stderr':''};written=0;abort=None;timed_out=False
    scan_times=[];scan_count=0;last_scan=None;max_scan_gap=0.0;cleanup=None
    with stdout_path.open('xb') as out,stderr_path.open('xb') as err:
        proc=subprocess.Popen(command_args,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,bufsize=0,start_new_session=True,close_fds=True)
        selector=selectors.DefaultSelector()
        for pipe,name,dest in ((proc.stdout,'stdout',out),(proc.stderr,'stderr',err)):
            os.set_blocking(pipe.fileno(),False);selector.register(pipe,selectors.EVENT_READ,(name,dest))
        try:
            while proc.poll() is None or selector.get_map():
                timeout=min(poll,max(0.0,wall_deadline-time.monotonic()))
                if phase_deadline is not None: timeout=min(timeout,max(0.0,phase_deadline-time.monotonic()))
                for key,unused in selector.select(timeout=timeout):
                    try: data=os.read(key.fd,65536)
                    except BlockingIOError: continue
                    if not data: selector.unregister(key.fileobj);continue
                    name,dest=key.data
                    if written+len(data)>log_limit_bytes:
                        with (output/(prefix+'-first-log-overflow.bin')).open('xb') as overflow:overflow.write(data)
                        abort='controlled_log_cap';break
                    dest.write(data);dest.flush();written+=len(data)
                    tails[name]=(tails[name]+data.decode(errors='replace'))[-131072:]
                if abort:break
                now=time.monotonic();scan_count+=1
                if last_scan is not None:max_scan_gap=max(max_scan_gap,now-last_scan)
                last_scan=now
                if len(scan_times)<8192:scan_times.append(now-started)
                if scan_callback is not None:
                    try:scan_callback()
                    except (ValueError,OSError) as exc:abort='scan_rejected:'+str(exc);break
                for marker,name,seconds in phase_markers:
                    if marker in tails['stdout'] and name not in observed:
                        observed.add(name);phase=name;phase_deadline=time.monotonic()+_seconds(seconds)
                if any(marker in tails['stderr'] for marker in abort_markers):abort='configured_stderr_marker';break
                now=time.monotonic()
                if now>=wall_deadline or phase_deadline is not None and now>=phase_deadline:
                    timed_out=True;abort='wall_timeout:'+phase;break
                # No second wait/sleep: next iteration has the sole selector wait.
        finally:
            active_duration=time.monotonic()-started
            selector.close()
            cleanup=cleanup_process_group(proc,term_grace_seconds,kill_grace_seconds)
            proc.stdout.close();proc.stderr.close()
    if cleanup['live_remaining']:abort=abort or 'own_process_group_cleanup_incomplete'
    result=dict(scope='GENERIC_SUBPROCESS_MONITOR_ONLY_NOT_ORACLE_OR_CAPTURE',generic_subprocesses=1,actual_oracle_processes=0,
        command=list(command_args),exit_code=proc.returncode,timed_out=timed_out,abort_reason=abort,
        process_clean_exit=proc.returncode==0 and not abort,duration_seconds=time.monotonic()-started,
        active_duration_seconds=active_duration,cleanup=cleanup,
        polling=dict(single_selector_wait_seconds=poll,extra_timed_wait=False,scan_count=scan_count,
                     scan_times_seconds=scan_times,samples_truncated=scan_count>len(scan_times),max_observed_scan_gap_seconds=max_scan_gap,
                     model='ONE_SELECTOR_WAIT_PLUS_IO_SCAN_OVERHEAD'),
        limits=dict(wall=wall,log_bytes=log_limit_bytes),
        enforcement='POLLING_NOT_KERNEL_AGGREGATE_QUOTA',policy='bounded-writers-and-monitored-process/1')
    write_new(output/(prefix+'-monitor-result.json'),result)
    return result


def execute_process(source_root,task,run,project,check_only=False):
    """Only this wrapper constructs the real, fixed oracle command/counts."""
    if type(check_only) is not bool:raise ValueError('check_only BOOL')
    source_root,task,run,project=map(directory,(source_root,task,run,project))
    output=run/'output';mode='parse' if check_only else 'native'
    cmd=command(source_root,task,project,output,check_only)
    result=monitor_command(cmd,run,environment(task,run),output,mode,30 if check_only else 300,
        scan_callback=lambda:usage(run),poll_seconds=0.05,term_grace_seconds=5.0,kill_grace_seconds=0.5,
        initial_phase_seconds=None if check_only else 120,
        phase_markers=() if check_only else (('NATIVE_PLAYER_SETUP_BEGIN','setup',30),('NATIVE_PHASE combat_wait','battle',120),
            ('NATIVE_PHASE finalizing','finalization',10),('NATIVE_CAPTURE_WRITTEN','exit',5)),
        abort_markers=('SCRIPT ERROR:',))
    stderr=(output/(mode+'-stderr.log')).read_text(errors='replace')
    stdout=(output/(mode+'-stdout.log')).read_text(errors='replace')
    if check_only and any(marker in stdout for marker in ('NATIVE_PHASE','NATIVE_PLAYER_SETUP','NATIVE_CAPTURE_')):
        result['abort_reason']='check-only unexpectedly executed collector'
    result=dict(result,scope='FIXED_REAL_ORACLE_WRAPPER' if not check_only else 'FIXED_REAL_GODOT_CHECK_ONLY_WRAPPER',
        actual_oracle_processes=0 if check_only else 1,parse_only=check_only,
        process_clean_exit=result['process_clean_exit'] and result['abort_reason'] is None and 'ERROR:' not in stderr)
    result['limits'].update(attempt_bytes=1536*MIB,free_floor=4*1024**3)
    write_new(output/(mode+'-process-result.json'),result)
    return result


def rename_capture(run):
    run=directory(run)
    sources=list((run/'user/data').rglob('native-capture'))
    if len(sources)!=1: raise ValueError('exactly one native raw capture')
    source=directory(sources[0]); target=run/'output/capture'
    if target.exists() or source.stat().st_dev!=target.parent.stat().st_dev: raise ValueError('new same-FS capture target')
    files={str(p.relative_to(source)):pin(p) for p in source.rglob('*') if p.is_file()}
    if len(files)>64 or sum(row['size'] for row in files.values())>512*MIB: raise ValueError('capture64files/512MiB')
    if any(p.is_symlink() for p in source.rglob('*')): raise ValueError('capture symlink')
    os.rename(source,target)
    if {str(p.relative_to(target)):pin(p) for p in target.rglob('*') if p.is_file()} != files: raise ValueError('capture rename bytes')
    write_new(run/'output/capture-relocation.json',dict(original=str(source),current=str(target),files=files,physical_copy=False))
    return target


