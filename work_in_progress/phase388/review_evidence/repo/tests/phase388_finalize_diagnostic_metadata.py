"""Output-only finalizer: reads previously sealed controls, never original capture."""
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SD=R/'data/phase388-independent-metadata-source'
D=R/'data/phase388-independent-final'
OLD=R/'data/phase388-independent-cleanup-control'
def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def read(p):return json.loads(p.read_text())
def verify(row):
    p=R/row['path'];assert p.is_relative_to(R) and not p.is_symlink() and pin(p)=={k:row[k] for k in ('size','sha256')};return p
def main():
    for row in read(SD/'source-owner.json')['files']:verify(row)
    c=read(verify(read(SD/'contract.json')['extraction']));p=read(verify(read(SD/'contract.json')['correlation']))
    assert c['control']==p['cleanup']=={'physics_frame':2724,'idle_frame':341,'is_in_physics_frame':True}
    assert p['matching_frame_signal']=={'line':2564,'kind':'physics','physics_frame':2724,'idle_frame':341}
    assert p['second_future_physics']=={'line':2567,'kind':'physics','physics_frame':2726,'idle_frame':342}
    assert p['first_eligible_actual_idle']=={'line':2574,'kind':'idle','physics_frame':2732,'idle_frame':342}
    assert p['actual_future_physics_count']==p['F_minus_C']==8 and p['actual_idle_at_exact_two']==[]
    D.mkdir(exist_ok=False)
    finding=dict(status='DIAGNOSTIC388_FIRST_ELIGIBLE_IDLE_REJECTED_BY_EXACT_TWO_PHYSICS',
        diagnostic_source_partition='Three control fields narrowly authorized from otherwise OPAQUE EXPECTED_ONLY postcleanup file; NOT lawful model input or accepted12 source.',
        extraction=desc(OLD/'cleanup-clock-control.json'),correlation=desc(OLD/'clock-correlation.json'),
        direct_control=dict(cleanup=c['control'],frame_signal=p['matching_frame_signal'],ineligible_idle=p['recorded_idles_after_cleanup_before_cut'],second_future_physics=p['second_future_physics'],first_eligible_actual_idle=p['first_eligible_actual_idle'],actual_future_physics_count=8,actual_idle_at_exact_C_plus_2=False),
        SOURCE_derived='Cleanup is marked after the physics_frame signal in physics2724; idle2724 follows with0futurephysics and is ineligible. The next eightphysics precede the next actual idle2732. That is the first idle meeting>=C+2; exact equality to2726 is false. Current producer rejects this real first eligible idle before endpoint/final/private collector dispatch. This is a scheduling-contract mismatch, not evidence that an earlier eligible idle callback was missed.',
        coupled_contracts=['sink exact2 check/emit guard/endpoint label','collector exact2 guard','schema terminal exact2 tail count'],
        future_requirements=['Explicit Root SOURCE choice/version: first actual idle after>=2 strictly future physics signals, or a separately enforced scheduler domain.','Preserve actual ordered pass/cleanup/cut relation and actual tail count; do not label8as2 or only relax one layer.','Keep same-stack/preinternal/once/ack/getter readonly guards; Source producer/collector/schema/endpoint must agree.','Keep cleanup/terminal diagnostics outside model initial/runtime/stop inputs and never use this extraction to repair old inputs or validation.'],
        not_proved=['Why actualscheduler produced8-step batches (logging overhead hypothesis remains unproved)','Full12/schema/RNG/history/model equivalence','All schedules/productionKing/native acceptance or permission to retry'],
        sibling_business_values_decoded=False,original_capture_modified=False,old386_unknownC_history_unchanged=True,
        execution_counts=dict(original_extractions=1,original_correlations=1,original_process_exit=1,original_error='PosixPath finding serialization metadata',output_only_finalizer=1,new_opaque_reads=0,new_clock_correlations=0,SUT_calls=0,models=0,Godot=0,new_native=0,inputbuilds=0,projection=0,actualpool_reads=0,pool_writes=0,restore=0,READY=0,business_expected_semantics_reads=0),
        preserved_firstfailure=desc(OLD/'first-metadata-failure/owned-files.json'),historical386=desc(R/'data/phase386-independent-first-idle-triage/finding.json'),no_more_writes=True)
    (D/'finding.json').write_text(json.dumps(finding,indent=2)+'\n')
    paths=[p for p in OLD.rglob('*') if p.is_file()]+[p for p in SD.rglob('*') if p.is_file()]+[D/'finding.json',R/'tests/phase388_cleanup_clock_control_extract.py',R/'tests/phase388_finalize_diagnostic_metadata.py',R/'docs/phase388_cleanup_clock_control_extraction_spec.md',R/'docs/phase388_diagnostic_metadata_finalize_spec.md',R/'data/phase388-independent-source/source-owner.json',R/'data/phase386-independent-first-idle-triage/finding.json',R/'data/phase386-independent-first-idle-triage/source-evidence.json',R/'data/phase386-independent-first-idle-triage/clock-control-projection.json',R/'data/phase375-food-hook-source/after-source/native_random_observer_sink_v7.gd']
    owner=dict(files=[desc(p) for p in sorted(set(paths))],original_opaque_file_provenance_only=True,no_more_writes=True)
    (D/'owned-files.json').write_text(json.dumps(owner,indent=2)+'\n')
    for row in owner['files']:verify(row)
    print(json.dumps(dict(status=finding['status'],finding=desc(D/'finding.json'),owner=desc(D/'owned-files.json'),leaves=len(owner['files']),bytes=sum(r['size'] for r in owner['files']))))
if __name__=='__main__':main()
