"""Output-only365 closure. No SUT imports, child processes or scientific reruns."""
from pathlib import Path
import hashlib
import json
import stat

R=Path(__file__).resolve().parents[1]
D=R/'data/phase365-independent-source-review'

def pin(path):
    raw=path.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def desc(path):return dict(path=str(path.relative_to(R)),**pin(path))
def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def read(path):return json.loads(path.read_text())
def verify_owner(path):
    value=read(path)
    for row in value['files']:assert desc(R/row['path'])==row
    return value

def main():
    source_owner=verify_owner(D/'source-owner.json')
    author=R/'data/phase365-control-recovery-source'
    author_owner=verify_owner(author/'source-owner.json')
    out=D/'first-001';report=read(out/'report.json');language=read(D/'language-project/regression-report.json')
    execution=read(out/'language/execution.json');monitor=execution['monitor']
    assert report['status']=='PASS' and report['failure'] is None and len(report['cases'])==40
    assert report['remaining_NOT_EXECUTED']==[] and len(language['cases'])==14 and not language['failures']
    for seal in (out/'output-seal.json',out/'language/joint-seal.json'):
        for row in read(seal)['files']:assert desc(R/row['path'])==row
    assert not (D/'first-stderr.log').read_bytes() and not (out/'language/output/language-stderr.log').read_bytes()
    mapping=read(R/'data/phase365-source-recovery-plan/restore-map.json')
    assert (len(mapping['file_differences']),len(mapping['directory_differences']),len(mapping['staged_files']))==(78,7,2)
    explicit={
      13:'Dynamic wrong-schema only; fixed case_id is covered by exact old recursive helper SOURCE, not a second mutated language row.',
      20:'Dynamic abort+timeout+exit0 preserves process failure. Source-change veto and separate clean flag are SOURCE reviewed, no real project-changing host execution.',
      23:'Dynamic missing neutral payload, not actual61273B sink removed; exact actual sink target/payload descriptor is frozen in SOURCE map.',
      24:'Dynamic missing neutral payload, not actual marker removed; actual28B marker target/payload descriptor frozen in SOURCE map.',
      26:'Dynamic wrong payload SHA; preserved ZIP CRC/SHA checked on valid real tiny ZIP by verify_evidence. BadCRC not separately injected.',
      27:'Dynamic traversal payload descriptor and duplicate manifest path rejection; no exhaustive path security claim.',
      28:'Dynamic hardlinked payload and symlink member refusal. Mutable target uses same exact regular_target gate before any writes; actual pool never touched.',
      29:'Dynamic changed file mode refusal; full inventory mtime equality and atomic_image recheck are SOURCE verified. No separate mtime-only invocation.',
      32:'Genuine neutral78file/7dir/2data manifests/payloads and real engineering restore80files; twice full bytes/mode/mtime readback, failed state unchanged. Later case35 deliberately corrupts this tiny aftertree; case32 sealed readback records its earlier actual state.',
      33:'Real partial restore: second payload changed AFTER successful preflight; first file written then refusal, journal+partial inventories retained and failed state unchanged. No retry.',
      34:'Direct stage commit API rejects missing independent report despite caller approval bool; public exactROOT source/review gate is SOURCE reviewed, not synthetically authorized.',
      36:'SOURCE no copytree/reconstruct plus actual80engineering writes; metadata restoration loops all target dirs as required by parent mtime changes.',
      37:'SOURCE whole-byte collector inverse and75source path conservation, pre-execution preparation proof; no new GDparse/fullGame execution.',
      38:'SOURCE normalized whole-module host AST inverse and frozen363 process/storage identities; no old36336controls rerun.',
      39:'SOURCE recover order and commit independent ownership/binding before state_write, rollback on check_ready exception; dynamic missingROOTconfig rejects.',
      40:'Scope obligation recorded; actual failedpool restore, independent full physical readback, ROOT READY commit and attempt02 all NOT_EXECUTED here.'
    }
    coverage=[]
    for row in report['cases']:
        number=row['id']
        family='REAL_EMPTY_PROJECT_GD' if number<=14 else 'SYNTHETIC_CONTROL_METADATA' if number<=21 else 'SYNTHETIC_TINY_FS_AND_SOURCE' if number<=35 else 'SOURCE_AND_SCOPE'
        coverage.append(dict(id=number,label=row['label'],status='ACCEPTED_BOUNDED',family=family,
            evidence=desc(out/('case-%02d.json'%number)),qualification=explicit.get(number,'Dynamic exact frozen helper outcome under presealed unit input; not actual native evidence.')))
    save(D/'coverage.json',dict(schema='phase365-independent-coverage/1',planned=40,actual_recorded=40,limit=48,
        full_actual12_positive=False,full_projection_positive=False,cases=coverage))
    review=dict(schema='phase365-independent-final-review/1',
        status='INDEPENDENT365_CONTROL_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING',
        source_freeze=desc(author/'combined-source-freeze.json'),native=0,models=0,
        scope='Bounded SOURCE delta + real empty-project Godot comparator regression + synthetic host-control metadata and neutral finite filesystem recovery stages. NOT actual Game/pool recovery/native/King admission.',
        verdict='No new SOURCE blocker within reviewed365 delta. Actual restore/readback/READY remain separate ROOT-controlled gates.',
        counts=dict(report['counts'],recorded_obligations=40,presealed_limit=48,Godot_engine_programs=1,
            generic_monitor_calls=1,oracle_wrapper_calls=0,exact_old_helper_direct_calls=2,callee_plain_Node_instances=1,
            synthetic_host_calls=7,synthetic_recovery_top_level_calls=19,engineering_restore_calls=2,
            synthetic_complete_restore_file_writes=80,synthetic_fault_restore_file_writes_before_rejection=1,
            actual_native_input_builds=0,projection_calls=0,automatic_retries=0),
        first_execution=dict(exit_code=0,stdout=desc(D/'first-stdout.log'),stderr=desc(D/'first-stderr.log'),
            report=desc(out/'report.json'),failure=None),
        language=dict(exit_code=monitor['exit_code'],process_clean_exit=monitor['process_clean_exit'],
            wall_seconds=monitor['duration_seconds'],cases=14,accept=2,reject=12,
            report=desc(D/'language-project/regression-report.json'),jointseal=desc(out/'language/joint-seal.json'),
            strict_BOOL_actual_types=True,no_mutation=True,original_helper_unmodified=True,
            original_helper_BOOL_still_false=True,autoloads=language['autoloads'],Game_node_present=False,
            stderr_bytes=0,cleanup_live_remaining=monitor['cleanup']['live_remaining'],
            zombies_not_claimed_reaped=monitor['cleanup']['zombies_not_claimed_reaped'],
            max_observed_scan_gap_seconds=monitor['polling']['max_observed_scan_gap_seconds'],
            polling_not_kernel_aggregate_quota=True),
        audit=dict(Python_command='-I -B -S',SOURCE_loading='Exact frozen source snapshots via compile+exec;6 imports including neutral fixture generator.',
            Python_open_audit_hook=False,closed_file_sandbox_claim=False,
            child_boundary='Explicit empty project, independent XDG/userdata paths, no Game/autoload source; exact trusted engine/offline/Xvfb bootstrap. Not a kernel filesystem sandbox.'),
        source_conservation=read(D/'source-review.json'),
        actual_map=dict(file_differences=78,directory_differences=7,staged_files=2,
            map=desc(R/'data/phase365-source-recovery-plan/restore-map.json'),
            staged_payload_source='Exact previous bundle/inputs descriptors required; no new fixtures substituted.'),
        coverage=desc(D/'coverage.json'),output_jointseal=desc(out/'output-seal.json'),
        remaining=dict(actual_pool_restore='NOT_EXECUTED',independent_actual_fulltree_readback='NOT_EXECUTED',
            ROOT_READY_commit='NOT_EXECUTED',new_original_attempt='NOT_AUTHORIZED_BY_THIS_REVIEW',
            GDparse_and_real_connection_order='PREVIOUS_OR_FUTURE_ACTUAL_GATE_NOT_RETESTED',
            full_actual12_positive=False,full_projection_positive=False,King_production_admitted=False,
            runtime356_gate='CLOSED',reader361='PENDING'),
        old363_successes_reused=True,old364_failure_and_language_probe_untouched=True,
        no_more_writes=True)
    save(D/'review.json',review)
    selected=[p for p in D.rglob('*') if p.is_file() and not p.is_symlink()]
    selected.extend(R/row['path'] for row in author_owner['files'])
    selected.extend([R/'tests/phase365_prepare_independent_controls.py',R/'tests/phase365_independent_controls.py',
        R/'tests/phase365_independent_tiny_evidence.py',R/'tests/phase365_finalize_independent_review.py',
        R/'docs/phase365_independent_control_recovery_validation_spec.md'])
    selected=sorted(set(selected))
    for p in selected:assert stat.S_ISREG(p.lstat().st_mode) and p.lstat().st_nlink==1
    owner=dict(schema='phase365-independent-final-owner/1',files=[desc(p) for p in selected],
        external_runtime_paths='provenance only, not owner leaves',no_more_writes=True)
    save(D/'owned-files.json',owner);verify_owner(D/'owned-files.json')
    print(json.dumps(dict(review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),leaves=len(selected),
        bytes=sum(row['size'] for row in owner['files']),status=review['status'])))

if __name__=='__main__':main()
