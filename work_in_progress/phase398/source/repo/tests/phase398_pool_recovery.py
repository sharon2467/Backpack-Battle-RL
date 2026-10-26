"""Exact existing-pool recovery SOURCE. Restore never commits READY or launches a process."""
from pathlib import Path
import argparse
import contextlib
import fcntl
import json
import os
import stat
from phase363_oracle_storage import (directory, member, pin, read, write_new, sync,
    regular_target, atomic_image, state_write, check_ready, map_recorded, c)
from phase375_oracle_host import descriptor, verify_owner
from phase395_saved_complete_evidence import validate_complete_saved

SOURCE = 'data/phase398-attempt05-recovery-source'
REVIEW_STATUS = 'INDEPENDENT399_ATTEMPT05_COMPLETE_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING'

MAP = 'data/phase395-attempt05-recovery-source/map/restore-map.json'
INPUT_PINS = 'data/phase395-attempt05-recovery-source/map/source-input-pins.json'
READBACK_STATUS = 'INDEPENDENT398_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'


def require(value, message):
    if not value: raise ValueError(message)


def evidence_path(roots, row):
    require(type(row) is dict and set(row)=={'root','path','size','sha256'}, 'exact rooted descriptor')
    require(row['root'] in roots, 'unknown evidence root')
    path=descriptor(roots[row['root']],{k:row[k] for k in ('path','size','sha256')})
    regular_target(path)
    return path


def source_gate(source_root, config_descriptor, action):
    root = directory(source_root)
    config = read(recovery_source_leaf(root, config_descriptor))
    require(config.get('schema') == 'phase398-root-pool-recovery/1' and config.get('action') == action and action in ('restore','commit_ready'), 'separate exact398 recovery action')
    require(config.get('root_'+action+'_authorized') is True, 'explicit Root action required')
    require(all(type(config.get(k)) is int and config[k] == 0 for k in ('native_allowed','models_allowed','projection_allowed')), 'strictINT0 non-recovery permissions')
    freeze_path = recovery_source_leaf(root, config['source_freeze'])
    require(config['source_freeze']['path'] == SOURCE+'/combined-source-freeze.json', 'separate398 recovery freeze')
    freeze = read(freeze_path)
    require(freeze.get('schema') == 'phase398-complete-install-recovery-SOURCE/1', 'closed complete-install SOURCE family')
    declared = {}
    for row in freeze['files']:
        require(row['path'] not in declared, 'unique recovery freeze leaves')
        recovery_source_leaf(root, row); declared[row['path']] = row
    leaves = recovery_source_owner(root, config['source_owner'])
    require(leaves.get(str(Path(__file__).absolute().relative_to(root))) == pin(Path(__file__)) and leaves.get(config['source_freeze']['path']) == pin(freeze_path), 'owner covers executing recovery and its freeze')
    for row in freeze['import_closure']:
        require(declared.get(row['path']) == row and leaves.get(row['path']) == {k:row[k] for k in ('size','sha256')}, 'all actual import sources owned/frozen')
    reviews = config.get('reviews')
    require(type(reviews) is list and bool(reviews), 'independent399 recovery SOURCE review required')
    for review in reviews:
        path = recovery_source_leaf(root, review['receipt']); owned = recovery_source_owner(root, review['owner']); value = read(path)
        require(owned.get(review['receipt']['path']) == pin(path) and value.get('status') == REVIEW_STATUS and value.get('source_freeze') == config['source_freeze'], 'actual owned399 recovery SOURCE closure')
        require(all(type(value.get(k)) is int and value[k] == 0 for k in ('native','models')), 'recovery SOURCE review grants no native/model')
    for key,name in (('restore_map',MAP),('input_pins',INPUT_PINS)):
        require(config.get(key) == declared.get(name) and config[key]['path'] == name, 'exact actual map/input binding')
    context = freeze['terminal_component_context']
    require(config.get('terminal_component_context') == context and declared.get(context['path']) == context, 'Root/freeze actual component context descriptor')
    validate_terminal_component_context(root, context)
    if action == 'commit_ready':
        recovery_source_leaf(root, config['restore_receipt'])
        recovery_source_leaf(root, config['independent_readback']['receipt'])
        recovery_source_owner(root, config['independent_readback']['owner'])
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


def verify_evidence(roots, mapping, input_pins):
    """Validate saved failed/previous trees and every payload before mutable operations."""
    for row in input_pins['files']: evidence_path(roots,row)
    completed=validate_complete_saved(roots)
    require(input_pins.get('schema')=='phase395-attempt05-saved-control-pins/1' and input_pins['files']==completed['files'] and mapping.get('complete_install')==completed['summary'],'complete saved evidence ledger/association/counts')
    receipt=read(evidence_path(roots,mapping['failed_preservation']))
    require(mapping.get('schema')=='phase395-attempt05-complete-restore-source-map/1' and receipt.get('schema')=='attempt05-installed-failed-pool-preservation/1' and receipt.get('status')=='PRESERVED_NOT_RESTORED' and type(receipt.get('restore')) is int and receipt['restore']==0,
        'real preservation receipt required')
    # Receipt historical roots must resolve explicitly to these actual roots.
    aliases=mapping['roots']; relocation={aliases[k]:str(roots[k]) for k in roots if k in aliases and aliases[k]!=str(roots[k])}
    saved=roots['failed_run']/'output/failed-pool-preservation'
    failed=read(evidence_path(roots,mapping['failed_project_inventory']))
    failed_data=read(member(saved,'failed-staged-files.json'))
    failed_base=read(member(saved,'baseline-files.json'))
    target=read(evidence_path(roots,mapping['project_target']))
    target_data=read(evidence_path(roots,mapping['staged_target']))
    for tree in (failed,failed_data,failed_base,target,target_data): c.index(tree)
    require(c.inventory(roots['baseline'])==failed_base,'baseline actual bytes/mode/mtime drift')
    bundle=roots['previous_run']/'output/compaction'
    base,old_project,_=c.load_bundle(bundle)
    require(base==failed_base and old_project==target and read(bundle/'staged-inputs.json')==target_data,'previous bundle exact targets')
    proof=read(bundle/'pool-roundtrip.json')
    require(proof.get('status')=='PASS' and map_recorded(proof['run'],relocation)==roots['previous_run'] and
        map_recorded(proof['pool'],relocation)==roots['pool'] and proof['bundle_sha256']==c.digest(bundle/'bundle-manifest.json') and
        proof['provenance_sha256']==c.digest(roots['previous_run']/'output/pool-provenance.json'),'actual prior READY proof')
    require(c.retained(roots['previous_run'])==read(bundle/'retained-evidence.json') and
        c.inventory(roots['previous_run']/'output/driver')==read(bundle/'driver-files.json'),'prior retained/driver evidence')
    plan=read(member(saved,'overlay-manifest.json'))
    require(c.overlay_plan(failed_base,failed)==plan,'failed overlay manifest')
    c.validate_archive(member(saved,'failed-project-overlay.zip'),failed,plan)
    require(receipt['overlay_sha256']==c.digest(saved/'failed-project-overlay.zip') and
        receipt['overlay_bytes']==(saved/'failed-project-overlay.zip').stat().st_size,'preserved failed overlay identity')
    before,after=c.index(failed),c.index(target)
    require(before.keys()==after.keys(),'unknown/missing project paths, preserve then BLOCK')
    changed_files={p for p in before if before[p]!=after[p] and before[p]['kind']=='file'}
    changed_dirs={p for p in before if before[p]!=after[p] and before[p]['kind']=='directory'}
    require(len(mapping['file_differences'])==len(changed_files) and len(mapping['directory_differences'])==len(changed_dirs) and
        changed_files=={row['path'] for row in mapping['file_differences']} and
        changed_dirs=={row['path'] for row in mapping['directory_differences']},'complete manifest-derived file/directory differences')
    require(len(mapping['staged_files'])==sum(row['kind']=='file' for row in c.index(target_data).values()),'exact target staged files')
    payloads=[]
    for row in mapping['file_differences']:
        require(row['before_preserved']==before[row['path']] and row['target']==after[row['path']],'mapped preimage/target drift')
        payload=evidence_path(roots,row['payload'])
        require(pin(payload)=={k:row['target'][k] for k in ('size','sha256')},'project payload target bytes')
        payloads.append(('project',row['path'],payload,row['target']))
    for row in mapping['directory_differences']:
        require(row['before']==before[row['path']] and row['target']==after[row['path']],'directory map drift')
    fdata,tdata=c.index(failed_data),c.index(target_data)
    require(fdata.keys()==tdata.keys() and {row['target']['path'] for row in mapping['staged_files']}==
        {p for p,v in tdata.items() if v['kind']=='file'},'exact staged path sets')
    for row in mapping['staged_files']:
        target_row=row['target']; require(target_row==tdata[target_row['path']],'staged target drift')
        payload=evidence_path(roots,row['payload'])
        require(pin(payload)=={k:target_row[k] for k in ('size','sha256')},'staged payload bytes')
        payloads.append(('data',target_row['path'],payload,target_row))
    state=pin(member(saved,'failed-pool-state.json'))
    require(map_recorded(read(saved/'failed-pool-state.json')['run'],relocation)==roots['failed_run'],
        'saved failed state must belong to this failed attempt')
    return dict(failed=failed,failed_data=failed_data,target=target,target_data=target_data,
        failed_state=state,payloads=payloads,bundle=bundle,relocations=relocation)


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
    check_failed_state(roots,evidence['failed_state'])
    require(c.inventory(roots['pool']/'project')==evidence['failed'] and
        c.inventory(roots['pool']/'data')==evidence['failed_data'],'actual current tree must equal preserved failed tree')
    todo=[]
    for tree,name,payload,target in evidence['payloads']:
        path=member(roots['pool']/tree,name); info=regular_target(path)
        todo.append((path,payload,target,dict(identity=pin(path),mode=stat.S_IMODE(info.st_mode),mtime_ns=info.st_mtime_ns)))
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


"""New recovery gate only; complete-install mutator stays the frozen375 algorithm."""


def recovery_source_leaf(root, row):
    require(type(row) is dict and set(row) == {'path','size','sha256'}, 'closed exact SOURCE descriptor')
    require(type(row['path']) is str and bool(row['path']) and '\\' not in row['path'] and '\0' not in row['path'] and
            all(part not in ('', '.', '..') for part in row['path'].split('/')), 'canonical SOURCE path field')
    require(type(row['size']) is int and row['size'] >= 0 and type(row['sha256']) is str and len(row['sha256']) == 64 and
            all(char in '0123456789abcdef' for char in row['sha256']), 'strict SOURCE size/SHA fields')
    path = member(root, row['path'])
    regular_target(path)
    return descriptor(root, row)

def recovery_source_owner(root, row):
    path = recovery_source_leaf(root, row)
    value = read(path)
    rows = value['files']
    require(type(rows) is list and bool(rows), 'nonempty actual owner')
    result = {}
    for leaf in rows:
        require(leaf['path'] not in result, 'unique owned source leaves')
        result[leaf['path']] = pin(recovery_source_leaf(root, leaf))
    return result


def validate_terminal_component_context(root, context_descriptor):
    context = read(recovery_source_leaf(root, context_descriptor))
    require(context.get('schema') == 'root391-bounded-component-context/1' and
            context.get('status') == 'ROOT_391_BOUNDED_COMPONENT_ACCEPTED_LANGUAGE_AND_NATIVE_PENDING', 'real bounded component Root context')
    for key in ('READY_allowed','inputbuilds_allowed','models','native','restore_allowed'):
        require(type(context.get(key)) is int and context[key] == 0, 'component context grants no operations')
    sf = recovery_source_leaf(root, context['source_freeze'])
    so = recovery_source_owner(root, context['source_owner'])
    require(so.get(context['source_freeze']['path']) == pin(sf), 'owned actual391 freeze')
    freeze = read(sf)
    require(freeze['active_source_tuple'] == context['source_tuple'], 'actual391 terminal tuple context')
    recovery_source_leaf(root, context['source_tuple'])
    review_path = recovery_source_leaf(root, context['independent_review'])
    owned = recovery_source_owner(root, context['independent_owner'])
    review = read(review_path)
    require(owned.get(context['independent_review']['path']) == pin(review_path) and
            review.get('status') == 'INDEPENDENT392_FIRST_ELIGIBLE_IDLE_SOURCE_ACCEPTED_ROOT_PENDING' and
            review.get('source_freeze') == context['source_freeze'], 'owned real392 reviewed391 component')
    require(all(type(review.get(key)) is int and review[key] == 0 for key in ('native','models')), 'bounded component zero native/model')
    return context



def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source-root','pool','baseline','failed-run','previous-run'): parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--config',required=True); parser.add_argument('--config-size',type=int,required=True)
    parser.add_argument('--config-sha256',required=True); parser.add_argument('--action',choices=('restore','commit_ready'),required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args(); config=dict(path=args.config,size=args.config_size,sha256=args.config_sha256)
    print(json.dumps(recover(args.source_root,config,args.pool,args.baseline,args.failed_run,args.previous_run,args.action,args.output),indent=2))


if __name__=='__main__': main()
