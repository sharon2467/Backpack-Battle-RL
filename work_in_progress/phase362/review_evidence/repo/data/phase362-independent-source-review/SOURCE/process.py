"""Explicit oracle process driver. No process starts at import or compilation."""
from pathlib import Path
import os
import shutil
import signal
import selectors
import subprocess
import sys
import time
from phase362_oracle_storage import directory, pin, write_new

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


def execute_process(source_root, task, run, project, check_only=False):
    source_root, task, run, project = map(directory, (source_root,task,run,project))
    output = run/'output'
    mode = 'parse' if check_only else 'native'
    stdout_path, stderr_path = output/(mode+'-stdout.log'), output/(mode+'-stderr.log')
    if stdout_path.exists() or stderr_path.exists(): raise ValueError('unique process attempt')
    cmd = command(source_root,task,project,output,check_only)
    started = time.monotonic(); limit = 30 if check_only else 300
    abort = None; timed_out = False; phase = 'startup'; phase_deadline = started+120
    observed = set(); tails = {'stdout':'','stderr':''}; written=0
    with stdout_path.open('xb') as out, stderr_path.open('xb') as err:
        proc = subprocess.Popen(cmd,cwd=run,env=environment(task,run),stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=0,start_new_session=True,close_fds=True)
        selector=selectors.DefaultSelector()
        for pipe,name,dest in ((proc.stdout,'stdout',out),(proc.stderr,'stderr',err)):
            os.set_blocking(pipe.fileno(),False); selector.register(pipe,selectors.EVENT_READ,(name,dest))
        try:
            while proc.poll() is None or selector.get_map():
                now = time.monotonic()
                for key,unused in selector.select(timeout=0.05):
                    data=os.read(key.fd,65536)
                    if not data: selector.unregister(key.fileobj); continue
                    name,dest=key.data
                    if written+len(data)>32*MIB:
                        with (output/(mode+'-first-log-overflow.bin')).open('xb') as overflow: overflow.write(data)
                        abort='stdout/stderr controlled writer32MiB'; break
                    dest.write(data); dest.flush(); written+=len(data)
                    tails[name]=(tails[name]+data.decode(errors='replace'))[-131072:]
                if abort: break
                try: usage(run)
                except ValueError as exc: abort = str(exc); break
                if stdout_path.stat().st_size + stderr_path.stat().st_size > 32*MIB:
                    abort='stdout/stderr threshold32MiB'; break
                log = tails['stdout']
                for marker,name,seconds in [('NATIVE_PLAYER_SETUP_BEGIN','setup',30),('NATIVE_PHASE combat_wait','battle',120),
                    ('NATIVE_PHASE finalizing','finalization',10),('NATIVE_CAPTURE_WRITTEN','exit',5)]:
                    if marker in log and phase != name and name not in observed:
                        observed.add(name); phase=name; phase_deadline=now+seconds
                errors=tails['stderr']
                if 'SCRIPT ERROR:' in errors: abort='native_script_error'; break
                if now-started >= limit or (not check_only and now >= phase_deadline):
                    timed_out=True; abort='wall_timeout:'+phase; break
                try: proc.wait(timeout=0.05)
                except subprocess.TimeoutExpired: pass
        finally:
            selector.close()
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try: proc.wait(timeout=5)
                except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL); proc.wait()
            try: os.killpg(proc.pid,signal.SIGTERM)
            except ProcessLookupError: pass
    errors=stderr_path.read_text(errors='replace'); stdout=stdout_path.read_text(errors='replace')
    if check_only and any(marker in stdout for marker in ('NATIVE_PHASE','NATIVE_PLAYER_SETUP','NATIVE_CAPTURE_')):
        abort='check-only unexpectedly executed collector'
    result=dict(exit_code=proc.returncode,timed_out=timed_out,abort_reason=abort,duration_seconds=time.monotonic()-started,
        process_clean_exit=proc.returncode==0 and not abort and 'ERROR:' not in errors,
        command=cmd,actual_oracle_processes=0 if check_only else 1,parse_only=check_only,
        limits=dict(wall=limit,attempt_bytes=1536*MIB,log_bytes=32*MIB,free_floor=4*1024**3),
        enforcement='POLLING_NOT_KERNEL_AGGREGATE_QUOTA',policy='bounded-writers-and-monitored-process/1')
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


