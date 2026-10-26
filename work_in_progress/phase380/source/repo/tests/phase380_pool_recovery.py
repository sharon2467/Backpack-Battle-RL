"""Exact existing-pool recovery SOURCE. Restore never commits READY or launches a process."""
from pathlib import Path
import argparse
import contextlib
import fcntl
import json
import os
import stat
from phase380_oracle_storage import (directory, member, pin, read, write_new, sync,
    regular_target, atomic_image, state_write, check_ready, map_recorded, c)
from phase380_oracle_host import descriptor, verify_owner, REVIEW_STATUS, SOURCE

from phase380_partial_map import analyze_saved_partial,KNOWN_MISSING

MAP = 'data/phase380-attempt04-partial-recovery-source/restore-map.json'
INPUT_PINS = 'data/phase380-attempt04-partial-recovery-source/source-input-pins.json'
READBACK_STATUS = 'INDEPENDENT380_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'


def require(value, message):
    if not value: raise ValueError(message)


def evidence_path(roots, row):
    require(type(row) is dict and set(row)=={'root','path','size','sha256'}, 'exact rooted descriptor')
    require(row['root'] in roots, 'unknown evidence root')
    path=descriptor(roots[row['root']],{k:row[k] for k in ('path','size','sha256')})
    regular_target(path)
    return path


def source_gate(source_root, config_descriptor, action):
    root=directory(source_root); config=read(descriptor(root,config_descriptor))
    require(config.get('schema')=='phase380-root-pool-recovery/1' and config.get('action')==action,
            'separate exact root recovery action')
    require(config.get('root_'+action+'_authorized') is True, 'explicit root action required')
    require(all(type(config.get(k)) is int and config[k]==0 for k in
        ('native_allowed','models_allowed','projection_allowed')), 'strictINT0 non-recovery permissions')
    freeze_path=descriptor(root,config['source_freeze'])
    require(config['source_freeze']['path']==SOURCE+'/combined-source-freeze.json','exact365 SOURCE freeze')
    freeze=read(freeze_path)
    for row in freeze['files']: descriptor(root,row)
    leaves=verify_owner(root,config['source_owner'])
    require(leaves.get(str(Path(__file__).absolute().relative_to(root)))==pin(Path(__file__)) and
        leaves.get(config['source_freeze']['path'])==pin(freeze_path),'owned executing recovery and freeze')
    reviews=config.get('reviews')
    require(type(reviews) is list and bool(reviews),'actual independent SOURCE review required')
    for review in reviews:
        receipt=descriptor(root,review['receipt']); owned=verify_owner(root,review['owner']); value=read(receipt)
        require(owned.get(review['receipt']['path'])==pin(receipt) and value.get('status')==REVIEW_STATUS and
            value.get('source_freeze')==config['source_freeze'],'owned actual reviewed365 closure')
        require(all(type(value.get(k)) is int and value[k]==0 for k in ('native','models')),'review zero native/models')
    require(config.get('restore_map')==next(row for row in freeze['files'] if row['path']==MAP), 'exact map binding')
    require(config.get('input_pins')==next(row for row in freeze['files'] if row['path']==INPUT_PINS), 'exact input evidence binding')
    return root,config


def check_roots(source_root, pool, baseline, failed_run, previous_run, config):
    roots={k:directory(v) for k,v in dict(source_root=source_root,pool=pool,baseline=baseline,
        failed_run=failed_run,previous_run=previous_run).items()}
    require(config.get('roots')=={k:str(v) for k,v in roots.items()},'exact actual roots, not historical aliases')
    values=list(roots.values())
    require(all(a!=b and not a.is_relative_to(b) and not b.is_relative_to(a)
        for i,a in enumerate(values) for b in values[i+1:]),'disjoint recovery roots')
    require(set(p.name for p in roots['pool'].iterdir())=={'.lock','state.json','project','data'},'exact failed pool layout')
    return roots


@contextlib.contextmanager
def locked_pool(roots):
    pool=roots['pool']; path=member(pool,'.lock'); regular_target(path)
    with path.open('r+b') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for key in ('pool','failed_run','previous_run'): c.process_check(roots[key])
        yield


def check_failed_state(roots, expected):
    path=member(roots['pool'],'state.json'); regular_target(path)
    require(pin(path)==expected,'failed state original bytes changed')
    value=read(path)
    require(value.get('status')=='failed','state remains failed until independent readback')
    return value


def verify_evidence(roots,mapping,input_pins):
    for row in input_pins['files']: evidence_path(roots,row)
    analyzed=analyze_saved_partial(roots['source_root'],roots['failed_run'],roots['previous_run'])
    core=analyzed['core']
    require(set(mapping)==set(core)|{'roots','roots_are'} and all(mapping[k]==v for k,v in core.items()),'exact saved partial map, no synthetic journal or unknown fields')
    require(input_pins==analyzed['input_pins'],'complete exact saved evidence pins')
    require(mapping['known_absent_creates']==sorted(KNOWN_MISSING),'only two proven absent-target creates')
    aliases=mapping['roots'];relocation={aliases[k]:str(roots[k]) for k in roots if k in aliases and aliases[k]!=str(roots[k])}
    failed,failed_data,target,target_data=[analyzed[k] for k in ('failed','failed_data','target','target_data')]
    require(c.inventory(roots['baseline'])==analyzed['base'],'actual baseline full bytes/mode/mtime drift')
    bundle=roots['previous_run']/'output/compaction';proof=read(bundle/'pool-roundtrip.json')
    require(proof.get('status')=='PASS' and map_recorded(proof['run'],relocation)==roots['previous_run'] and map_recorded(proof['pool'],relocation)==roots['pool'] and
        proof['bundle_sha256']==c.digest(bundle/'bundle-manifest.json') and proof['provenance_sha256']==c.digest(roots['previous_run']/'output/pool-provenance.json'),'old READY proof/run/root identities')
    require(c.retained(roots['previous_run'])==read(bundle/'retained-evidence.json') and c.inventory(roots['previous_run']/'output/driver')==read(bundle/'driver-files.json'),'old retained/driver evidence')
    payloads=[]
    for row in mapping['file_differences']:
        payload=evidence_path(roots,row['payload']);payloads.append(('project',row['path'],payload,row['target']))
    before_data=c.index(failed_data)
    for row in mapping['staged_files']:
        payload=evidence_path(roots,row['payload'])
        if before_data[row['target']['path']]!=row['target']:payloads.append(('data',row['target']['path'],payload,row['target']))
    saved=roots['failed_run']/'output/failed-pool-preservation';state=pin(saved/'failed-pool-state.json')
    require(map_recorded(read(saved/'failed-pool-state.json')['run'],relocation)==roots['failed_run'],'exact failed state/run binding')
    return dict(failed=failed,failed_data=failed_data,target=target,target_data=target_data,failed_state=state,payloads=payloads,bundle=bundle,
        relocations=relocation,known_absent_creates=sorted(KNOWN_MISSING))


def directory_metadata(root, target):
    rows=[row for row in c.index(target).values() if row['kind']=='directory']
    for row in sorted(rows,key=lambda x:len(Path(x['path']).parts) if x['path']!='.' else 0,reverse=True):
        path=root if row['path']=='.' else member(root,row['path'])
        directory(path); os.chmod(path,row['mode']); os.utime(path,ns=(row['mtime_ns'],row['mtime_ns'])); sync(path)


def actual_targets(roots, evidence):
    project=c.inventory(roots['pool']/'project'); data=c.inventory(roots['pool']/'data')
    require(project==evidence['target'] and data==evidence['target_data'],'complete restored target mismatch')
    return dict(project=project,staged=data)


def restore_exact(roots, evidence, output, binding):
    """Mutation entry after evidence validation; never changes pool state."""
    output=Path(output).absolute(); directory(output.parent)
    require(not output.exists() and not output.is_symlink(),'new recovery output only')
    require(all(not output.is_relative_to(roots[k]) for k in ('pool','baseline','failed_run','previous_run')),'recovery report outside preserved roots')
    require(set(c.index(evidence['target']))-set(c.index(evidence['failed']))==KNOWN_MISSING and not set(c.index(evidence['failed']))-set(c.index(evidence['target'])) and evidence.get('known_absent_creates')==sorted(KNOWN_MISSING),'exact2 partial-map creations only')
    check_failed_state(roots,evidence['failed_state'])
    require(c.inventory(roots['pool']/'project')==evidence['failed'] and
        c.inventory(roots['pool']/'data')==evidence['failed_data'],'actual current tree must equal preserved failed tree')
    todo=[]
    for tree,name,payload,target in evidence['payloads']:
        path=member(roots['pool']/tree,name)
        known=tree=='project' and name in KNOWN_MISSING
        info=regular_target(path,absent=known)
        if known:
            require(info is None,'only proven absent targets may be created')
        else:
            require(info is not None,'existing target required')
        todo.append((path,payload,target,None if info is None else dict(identity=pin(path),mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns)))
    need=sum(row['size'] for _,_,row,_ in todo)+16*1024**2
    import shutil
    require(shutil.disk_usage(roots['pool']).free>=need,'recovery small-payload headroom')
    output.mkdir(mode=0o700); journal=[]; write_new(output/'intent.json',dict(binding,pool_state='failed',writes=len(todo)))
    try:
        for path,payload,target,before in todo:
            raw=payload.read_bytes(); require(pin(payload)=={k:target[k] for k in ('size','sha256')},'payload changed before write')
            atomic_image(path,raw,before)
            os.chmod(path,target['mode']); os.utime(path,ns=(target['mtime_ns'],target['mtime_ns']))
            with path.open('rb') as stream: os.fsync(stream.fileno())
            sync(path.parent)
            journal.append(dict(path=str(path),before=before,target=target,actual=pin(path)))
            write_new(output/('write-%03d.json'%len(journal)),journal[-1])
        directory_metadata(roots['pool']/'project',evidence['target']); directory_metadata(roots['pool']/'data',evidence['target_data'])
        first=actual_targets(roots,evidence); second=actual_targets(roots,evidence); require(first==second,'double full readback')
        check_failed_state(roots,evidence['failed_state'])
        for name,value in first.items(): write_new(output/(name+'-actual.json'),value)
        result=dict(binding,status='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING',
            failed_state=evidence['failed_state'],writes=len(journal),author_engineering_readback_only=True,
            independent_readback=False,READY_committed=False,native=0,models=0,Game_copies=0)
        write_new(output/'restore-receipt.json',result); sync(output)
        return result
    except BaseException as exc:
        failure=dict(status='RESTORE_FAILED_STATE_FAILED_PARTIAL_PRESERVED',error=repr(exc),completed_writes=journal)
        for name in ('project','data'):
            try: write_new(output/(name+'-partial.json'),c.inventory(roots['pool']/name))
            except BaseException as capture: failure[name+'_capture_error']=repr(capture)
        write_new(output/'restore-first-failure.json',failure); sync(output)
        raise


def commit_ready(root,config,roots,evidence,binding):
    receipt=descriptor(root,config['restore_receipt']); restored=read(receipt)
    require(restored.get('status')=='RESTORED_EXACT_TARGET_STATE_REMAINS_FAILED_INDEPENDENT_READBACK_PENDING' and
        all(restored.get(k)==v for k,v in binding.items()) and restored.get('failed_state')==evidence['failed_state'],
        'actual matching engineering restore receipt, not independent acceptance')
    review=descriptor(root,config['independent_readback']['receipt'])
    owned=verify_owner(root,config['independent_readback']['owner']); report=read(review)
    require(owned.get(config['independent_readback']['receipt']['path'])==pin(review),'owned real independent readback')
    require(report.get('status')==READBACK_STATUS and report.get('restore_receipt')==config['restore_receipt'] and
        all(report.get(k)==v for k,v in binding.items()) and report.get('failed_state')==evidence['failed_state'],
        'independent report exact target/root/source/map/restore receipt binding')
    for key,name in (('project_readback','target'),('staged_readback','target_data')):
        leaf=descriptor(root,report[key]); require(owned.get(report[key]['path'])==pin(leaf) and read(leaf)==evidence[name],
            'actual owned independent full-tree readback leaves')
    check_failed_state(roots,evidence['failed_state']); actual_targets(roots,evidence); actual_targets(roots,evidence)
    state_write(roots['pool'],dict(status='ready',run=str(roots['previous_run']),bundle_inventory=c.inventory(evidence['bundle'])))
    try: check_ready(roots['pool'],roots['baseline'],evidence['relocations'])
    except BaseException:
        # Failed postcommit verification cannot leave an unverified READY flag.
        state_write(roots['pool'],read(roots['failed_run']/'output/failed-pool-preservation/failed-pool-state.json'))
        raise
    return dict(status='READY_COMMITTED_AFTER_OWNED_INDEPENDENT_EXACT_READBACK',roots=binding['roots'],native=0,models=0)


def recover(source_root,config_descriptor,pool,baseline,failed_run,previous_run,action,output=None):
    root,config=source_gate(source_root,config_descriptor,action)
    roots=check_roots(root,pool,baseline,failed_run,previous_run,config)
    mapping=read(descriptor(root,config['restore_map'])); pins=read(descriptor(root,config['input_pins']))
    binding=dict(roots={k:str(v) for k,v in roots.items()},restore_map=config['restore_map'],
        source_freeze=config['source_freeze'],project_target=mapping['project_target'],staged_target=mapping['staged_target'])
    with locked_pool(roots):
        evidence=verify_evidence(roots,mapping,pins)
        if action=='restore':
            require(output is not None,'new external recovery report directory')
            return restore_exact(roots,evidence,output,binding)
        require(output is None,'commit uses existing owned reports, no restore output')
        return commit_ready(root,config,roots,evidence,binding)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source-root','pool','baseline','failed-run','previous-run'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--config',required=True); parser.add_argument('--config-size',type=int,required=True)
    parser.add_argument('--config-sha256',required=True); parser.add_argument('--action',choices=('restore','commit_ready'),required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); config=dict(path=args.config,size=args.config_size,sha256=args.config_sha256)
    print(json.dumps(recover(args.source_root,config,args.pool,args.baseline,args.failed_run,args.previous_run,args.action,args.output),indent=2))


if __name__=='__main__': main()
