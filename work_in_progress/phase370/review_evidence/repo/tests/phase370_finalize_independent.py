"""Output-only370 independent closure. Never rerun language/helper successes."""
from pathlib import Path
import hashlib,json

R=Path(__file__).resolve().parents[1];D=R/'data/phase370-independent-execution'
def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def verify_owner(p):
 v=read(p)
 for row in v['files']:assert desc(R/row['path'])==row
 return v

def main():
 for name in ('source-owner.json','helper-source-owner.json','language-first-001/owned-files.json','helpers-first-001/owned-files.json'):verify_owner(D/name)
 lang=read(D/'language-project/language-report.json');execution=read(D/'language-first-001/execution-receipt.json')
 interpretation=read(D/'language-first-001/interpretation.json');helpers=read(D/'helpers-first-001/report.json')
 assert interpretation['status']=='PASS' and helpers['status']=='PASS' and not helpers['failure']
 assert lang['completed'] and lang['failure'] is None and len(lang['cases'])==15 and len(helpers['cases'])==13
 assert len(lang['resource_loads'])==2 and all(row['can_instance'] for row in lang['resource_loads'])
 assert all(row['pass'] for row in lang['cases']) and lang['autoloads']==[] and lang['Game_present'] is False
 assert (D/'language-first-001/output/language-stderr.log').stat().st_size==0
 original=read(R/'data/phase368-independent-source-preparation/contract.json')
 q={
 1:'New370 full-byte inverses independently checked; old successful mechanical75/15scope facts reused by exact old identities, not rerun.',
 2:'SOURCE signal remains observation-control only; no EventBus/site-matrix/accepted12input change. Full resources loaded, no business lifecycle.',
 3:'SOURCE old SceneTree listener statements conserved. Unit has real mainSceneTree/private signal; not actual Game connection-order proof.',
 4:'SOURCE original sampling functions unchanged; production fullsnapshot/getStats not invoked in unit.',
 5:'GOOD actual sole receiver/EngineIDs/stamps, flags0/emptybinds and synchronous EMITTING->ack->FINALIZING->FINALIZED trace.',
 6:'EXTRA actual receiver rejects before dispatch. Changed/wrong method/identity/duplicate rows additionally SOURCE exact predicates; not separate dynamic cases.',
 7:'DEFERRED and BINDS actual reject; SOURCE flags !=INT0/known native row fields cover remaining nonzero flags. No fake connection-list API.',
 8:'MISSING actual reject. Absent observer/signal and incomplete nullable row fields SOURCE only.',
 9:'Actual unit connect Error captured; production attach/source_control_snapshot resource loaded and SOURCE reviewed, no Game fixture birth.',
 10:'ALREADY_FAILED preserves original unit primary. Collector missing/UI/config/metadata predicates SOURCE reviewed only.',
 11:'Begin/bind SOURCE false branches and original helper preserved; actual Game begin/bind not invoked.',
 12:'Placement reached markers SOURCE-only, algorithm conserved; no actual placement/geometry claim.',
 13:'Original clock_pass and nonterminal clock branches SOURCE-conserved, not a simulated Game clock.',
 14:'New explicit ui_check_controls false/failed early return SOURCE proof. Unit UI flags are disclosed manual control prestate, not native observations.',
 15:'Clock failure->reject->return ordering SOURCE proof; no Timer/Game stepping.',
 16:'emit helper checks actual Engine stamps against synthetic completion-control prestate. Actual cleanup+2 future physics and first-native-idle remain future original evidence.',
 17:'Endpoint/final-source failures prevent emit by SOURCE control flow. Native writer/snapshot calls not faked in language units.',
 18:'UI-close failure no-emit SOURCE flow; no UI production lifecycle invoked.',
 19:'Exact emission helper actual nested-stack trace plus SOURCE clock/write/UI order; full business sampling and serialization not executed.',
 20:'Actual script NIL/observedtrue/native Error unavailable measured; BLOCKED/NO_ACK actual reject. Old INT/OK requirement superseded, never normalized to0.',
 21:'Actual live receiver ID/Engine stamps and BAD_ACK_TYPE measured. Remaining mismatch/stale branches SOURCE predicates, no invented native IDs.',
 22:'REENTRY and DUPLICATE actual reject with one dispatch; production collector once guard before stable_snapshot SOURCE proof.',
 23:'DUPLICATE dispatch remains count1; direct CLOSED_FALSE rejects. Later clock_idle_signal alreadyclosed entry SOURCE-only (does not imply quiet return or native tail test).',
 24:'FINISH_INT/FINISH_FALSE actual reject; unit receiver finish result only. Production finish-source errors are SOURCE flow; full actual capture not claimed.',
 25:'Actual control writer captures real private/tree connection tables on unit paths. Complete rows/type/indices-before-reject and unknown/cap handling SOURCE reviewed; no synthetic replacement connection API.',
 26:'DIAG_CAP record cap actual. Other byte/depth/row/unknown limits and nullable availability SOURCE only, not exhaustive fuzz/security proof.',
 27:'DIAG_CAP actual secondary with first failure preserved; ALREADY_FAILED original remains. Filesystem open/write failure branches SOURCE only, no fault-IO reruns.',
 28:'All15 unit observer/UI/clock counters unchanged; SOURCE no RNG/business/record calls in added control methods. Godot internal randomness not instrumented.',
 29:'New schema positive/old map/BOOLrestore/old ROOT negatives; actual saved attempt02 receipt/state pins verified. No actual ROOT authorization positive faked.',
 30:'Independent saved-only derivation78/7/2,80payload byte identities/metadata relationships and CRC. No map regeneration or live inventory.',
 31:'New-schema bad targetmtime, hardlink payload, real badCRC rejected. Unknown actualpool paths/restore preimage safety inherited by exact unchanged SOURCE and prior365 tests, not rerun.',
 32:'SOURCE separate ROOTmap/action/review/owner/readback/READY gates; no realpool operation or fake independent acceptance. Actual restore/fulltree/READY/attempt03 still separate.'}
 coverage=[dict(id=row['id'],label=row['label'],status='ACCEPTED_BOUNDED_SOURCE_AND_SPECIFIED_UNITS',evidence_kind_and_limit=q[row['id']]) for row in original['controls']]
 coverage.append(dict(id=33,label='Two-stage frozen DTO and finish return',status='ACCEPTED_SOURCE_CONTROL_SCOPE_BUSINESS_NATIVE_PATH_OPEN',
  evidence_kind_and_limit='Production finish has no sampling/getter calls and complete scripts parsed. Actual sink helper calls unit-only finish returning BOOL/INT/false; unit does not serialize production DTO or run production finish. Production frozen primitive DTO/serialization actual positive remains future native capture, not a fake Game test.'))
 save(D/'coverage.json',dict(schema='phase370-independent-bounded-coverage/1',obligations=33,cases=coverage,
  actual_language_cases=15,actual_helper_cases=13,complete_resources_loaded=2,
  rule='33 obligations combine specific SOURCE proof, exact conserved prior evidence and stated actual units; they are not33 new dynamic Game cases.'))
 monitor=execution['monitor'];hcounts=helpers['counts']
 prior=[R/'data/phase368-independent-source-review/review.json',R/'data/phase369-independent-execution/review.json']
 review=dict(schema='phase370-independent-source-final/1',status='INDEPENDENT370_SCRIPT_SIGNAL_RETURN_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING',
  source_freeze=desc(R/'data/phase370-oracle-source/combined-source-freeze.json'),native=0,models=0,
  scope='Bounded oracle SOURCE repair + actual complete-resource parse/load and language-control units + synthetic host/schema-preflight and saved-map validation. Not original Game, actual12, fullprojection, model or King admission.',
  source_review=desc(D/'static-review.json'),coverage=desc(D/'coverage.json'),
  language=dict(processes=1,engine_version='3.6.2',fullresource_attempts=2,resource_instances=0,lifecycle_calls=0,
   cases=15,failures=0,unit_Node_instances=lang['unit_node_instances'],unit_main_SceneTree=1,
   explicitly_instrumented_emit_ack_calls=lang['exact_method_calls'],
   additional_control_snapshot_calls=dict(count=30,basis='SOURCE-derived2percase x15; not a complete nested API profiler'),
   callback_entries=sum(row['callbacks'] for row in lang['cases']),unit_finish_calls=sum(row['finishes'] for row in lang['cases']),
   first_exit=monitor['exit_code'],process_clean_exit_field=monitor['process_clean_exit'],duration_seconds=monitor['duration_seconds'],
   stderr=desc(D/'language-first-001/output/language-stderr.log'),
   cleanup=dict(term_sent=monitor['cleanup']['term_sent'],live_remaining=monitor['cleanup']['live_remaining'],zombies_not_claimed_reaped=monitor['cleanup']['zombies_not_claimed_reaped'],
    limitation='Leader exit0/process_clean_exit field is not a claim that the entire PGID has zero residual kernel objects. One zombie explicitly retained as not reaped.'),
   max_observed_scan_gap_seconds=monitor['polling']['max_observed_scan_gap_seconds'],policy=monitor['enforcement'],
   original_Game=0,autoloads=[],full_business_DTO_positive=False,unit_finish_production_serialization=False,
   raw_jointseal=desc(D/'language-first-001/raw-joint-seal.json'),output_owner=desc(D/'language-first-001/owned-files.json')),
  helper=dict(cases=13,failures=0,counts=hcounts,report=desc(D/'helpers-first-001/report.json'),owner=desc(D/'helpers-first-001/owned-files.json'),
   synthetic_FS_evidence_bundles=1,synthetic_new_schema_maps=1,synthetic_restore_calls=0,actual_native_input_builds=0,
   original_combined_stdout='Execution tool observed exit0 and single PASS JSON; no separate helper stdout/stderr files were created.'),
  actual_totals=dict(Godot_language_processes=1,actual_Game=0,new_native_battles=0,Python_CombatEngine=0,models=0,projection=0,
   SOURCE_definition_imports=9,actual_pool_reads=0,actual_pool_mutations=0,restore=0,READY=0,saved_descriptor_verifications=hcounts['saved_map_reads'],
   language_reruns=0,helper_reruns=0,old363_365_test_reruns=0),
  audit=dict(open_audit_hook=False,closed_file_kernel_sandbox_claim=False,
   boundary='Pinned SOURCE definitions without __main__; own empty project/XDG/unit outputs and explicitly allowlisted saved evidence paths. No livepool root was passed to semantic helpers. No claims of exhaustive third-party/network attempt testing.'),
  first_failures_preserved=[desc(p) for p in prior],old_mechanical_evidence_reused=desc(R/'data/phase369-independent-execution/static-review.json'),
  permissions_after_review=dict(realpool_restore='ROOT_SEPARATE_RELEASE',independent_actual_fulltree='AFTER_RESTORE_ROOT_RELEASE',READY='ROOT_SEPARATE_COMMIT',attempt03='ROOT_SEPARATE_FRESH_PLAN_PARSE_ORIGINAL_RELEASE'),
  runtime356='CLOSED',reader361='PENDING',full_actual12_positive=False,fullprojection_positive=False,King_production_admitted=False,
  no_more_writes=True)
 save(D/'review.json',review)
 author=verify_owner(R/'data/phase370-oracle-source/source-owner.json')
 files=[p for p in D.rglob('*') if p.is_file()]
 files += [R/row['path'] for row in author['files']]
 files += [R/'tests/phase370_prepare_independent.py',R/'tests/phase370_language_probe.gd',R/'tests/phase370_run_independent_language.py',R/'tests/phase370_independent_helpers.py',R/'tests/phase370_finalize_independent.py',R/'docs/phase370_independent_execution_spec.md']
 save(D/'owned-files.json',dict(schema='phase370-independent-final-owner/1',files=[desc(p) for p in sorted(set(files))],repo_only=True,no_more_writes=True))
 owner=verify_owner(D/'owned-files.json')
 print(json.dumps(dict(review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),leaves=len(owner['files']),bytes=sum(row['size'] for row in owner['files']),status=review['status'])))

if __name__=='__main__':main()
