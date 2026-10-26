"""Permitted controls/clock counters only; opaque capture payloads never decoded."""
import collections
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SD=R/'data/phase386-independent-source'
D=R/'data/phase386-independent-first-idle-triage'
RUN=Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261025-attempt05')
CAP=RUN/'output/capture'
def pin(p):
    h=hashlib.sha256();size=0
    with p.open('rb') as f:
        for block in iter(lambda:f.read(65536),b''):h.update(block);size+=len(block)
    return dict(size=size,sha256=h.hexdigest())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def read(p):return json.loads(p.read_text())
def save(n,x):
    p=D/n;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
    return p
def mirror(p,n):
    q=D/n;q.parent.mkdir(parents=True,exist_ok=True)
    with q.open('xb') as f:f.write(p.read_bytes())
    return q
def require(x,m):
    if not x:raise ValueError(m)
def counter(v):require(type(v)is int and 0<=v<(1<<63),'strict clock control INT');return v
def gd_method(path,name):
    text=path.read_text();lines=text.splitlines();i=next(i for i,l in enumerate(lines) if l.startswith('func '+name+'('));j=next((j for j in range(i+1,len(lines)) if lines[j].startswith('func ')),len(lines));return dict(path=path.relative_to(R).as_posix(),line_start=i+1,line_end=j,text='\n'.join(lines[i:j])+'\n')
def slice_source(path,lo,hi):
    return dict(path=path.relative_to(R).as_posix(),line_start=lo,line_end=hi,text='\n'.join(path.read_text().splitlines()[lo-1:hi])+'\n')
def main():
    D.mkdir(exist_ok=False)
    for row in read(SD/'source-owner.json')['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'independent Source drift')
    controls={}
    for name in ['source-partition.json','process_result.json','parse-process-result.json','native-process-result.json']:
        p=mirror(RUN/'output'/name,'controls/'+name);controls[name]=read(p)
    failure=read(mirror(CAP/'observer7_failure.json','controls/observer7_failure.json'))
    require(failure['code']=='SOURCE_MISSED_FIRST_IDLE_CUT' and failure['site']=='clock_idle_signal' and failure['sequence']==74346,'actual first failure')
    require(failure['capture_complete'] is False,'incomplete actual failure')
    identities={p.name:pin(p) for p in sorted(CAP.iterdir()) if p.is_file()}
    partition=controls['source-partition.json']
    for key in ['lawful_inputs_present','expected_observations_opaque','control_failures_opaque']:
        for name,row in partition.get(key,{}).items():require(identities[name]=={k:row[k] for k in ('size','sha256')},'partition actual hash '+name)
    require(len(partition['lawful_inputs_present'])==12 and partition['lawful_inputs_missing']==[] and partition['capture_complete'] is False,'presence not validity')
    save('capture-opaque-identities.json',identities)
    cp=read(CAP/'king-clock-checkpoint.json')
    # Extract only declared control/framing fields; delta/time/resource data not used.
    checkpoint={k:cp[k] for k in ['schema','lineage']}
    checkpoint['checkpoint']={k:cp['checkpoint'][k] for k in ['phase','physics_frame','idle_frame','util_frame_counter']}
    p=counter(checkpoint['checkpoint']['physics_frame']);i=counter(checkpoint['checkpoint']['idle_frame'])+1
    rows=[];idle_gaps=[];previous_idle_p=p;previous_idle_line=0
    with (CAP/'king-clock-passes.jsonl').open('rb') as stream:
        for line_number,line in enumerate(stream,1):
            require(line.endswith(b'\n') and line.strip(),'clock JSONL framing')
            raw=json.loads(line);row={'line':line_number,**{k:raw[k] for k in ['kind','physics_frame','idle_frame']}}
            require(row['kind'] in ('physics','idle'),'clock kind')
            counter(row['physics_frame']);counter(row['idle_frame'])
            if row['kind']=='physics':p+=1
            require(row['physics_frame']==p and row['idle_frame']==i,'actual control counter continuity')
            rows.append(row)
            if row['kind']=='idle':
                idle_gaps.append(dict(idle_line=line_number,idle_frame=i,physics_frame=p,physics_since_previous_idle_or_checkpoint=p-previous_idle_p,previous_idle_line=previous_idle_line))
                previous_idle_p=p;previous_idle_line=line_number;i+=1
    require(rows and rows[-1]['kind']=='idle','last recorded clock callback idle')
    kinds=collections.Counter(row['kind'] for row in rows);hist=collections.Counter(row['physics_since_previous_idle_or_checkpoint'] for row in idle_gaps)
    summary=dict(checkpoint=checkpoint,rows=len(rows),kind_counts=dict(kinds),first=rows[0],last=rows[-1],tail_rows=rows[-24:],last_idle_intervals=idle_gaps[-12:],physics_per_idle_histogram={str(k):v for k,v in sorted(hist.items())},control_counter_continuity=True,full_delta_clock_schema_validated=False,clock_sequence_field='None in producer pass row; line is physical file ordinal, distinct from observer sequence74346')
    save('clock-control-projection.json',dict(summary=summary,rows=rows,idle_intervals=idle_gaps))
    sink=R/'data/phase375-food-hook-source/after-source/native_random_observer_sink_v7.gd';collector=R/'data/phase370-oracle-source/collector.gd';game=R/'data/phase359-king-producer-source/after-source/Core/Game.gd';schema=R/'tests/phase375_king_observer_schema.py';host=R/'tests/phase380_oracle_host.py';godotmain=R/'data/phase027-implementation-design/full-source/upstream/main/main.cpp';tree=R/'data/phase251-logic-reset-timer-source-plan/Godot3.6.2/scene/main/scene_tree.cpp'
    excerpts=[gd_method(sink,n) for n in ['begin_king_clock','clock_physics_signal','clock_idle_signal','clock_pass','close_king_clock','source_mark_cleanup','source_cut_reject','emit_source_idle_cut_once']]
    excerpts += [gd_method(collector,n) for n in ['on_combat_end','on_idle_source_cut','finish_source_cut']]
    excerpts += [gd_method(game,n) for n in ['endCombat','combatEndDeferred']]
    excerpts += [slice_source(godotmain,2353,2414),slice_source(tree,577,605),slice_source(tree,623,643)]
    # Exact function slice avoids printing/interpreting embedded schema tables.
    text=schema.read_text();lines=text.splitlines();lo=next(n for n,l in enumerate(lines) if l.startswith('def validate_terminal_evidence('));hi=next((n for n in range(lo+1,len(lines)) if lines[n].startswith('schema =')),len(lines));excerpts.append(slice_source(schema,lo+1,hi))
    save('source-evidence.json',dict(sources=[desc(x) for x in [sink,collector,game,schema,host,godotmain,tree]],excerpts=excerpts))
    proc={}
    for name in ['parse-process-result.json','native-process-result.json']:
        x=controls[name];proc[name]={k:x[k] for k in ['exit_code','duration_seconds','process_clean_exit','abort_reason','timed_out','cleanup']}
    F=rows[-1]['physics_frame'];P=idle_gaps[-2]['physics_frame'] if len(idle_gaps)>1 else None
    finding=dict(status='BLOCKED386_FIRST_IDLE_EXACT_TWO_PHYSICS_PREDICATE_CONTROL_TRIAGE',direct=dict(observer_failure=failure,processes=proc,capture_files=len(identities),capture_bytes=sum(x['size'] for x in identities.values()),lawful_present=12,lawful_validated=False,capture_complete=False,primary=partition['primary_failure'],secondary=partition['secondary_errors'],project_changed=controls['process_result.json']['source_changes_after_run'],clock_summary=summary),
      SOURCE_derived=dict(predicate='clock_pass(idle) writes current frame first; with cleanup C nonnull and F>=C+2, source rejects unless F==C+2, before close/endpoint/final/UIclose/private dispatch/collector snapshot or validation.',failure_implies='On this SOURCE path integer F-C>=3, not necessarily a missed callback. Exact C is not included in the allowed failure/pass/checkpoint controls.',clock_failure_candidate_frame=F,previous_recorded_idle_physics=P,cleanup_C_proven=False,cleanup_C_bound_from_failure=dict(maximum=F-3,minimum_if_prior_idle_observed_without_close=P-1 if P is not None else None),
        production_route='Game.endCombat schedules combatEndDeferred. Its observer leave calls source_mark_cleanup; SceneTree flushes deferred queue within physics iteration as well as idle; Godot Main performs zero-or-more physics iterations (normal max8) then an idle callback. Multiple physics callbacks between idle callbacks are legitimate engine scheduling.',
        hypothesis='If C+2 falls inside a legitimate multi-physics burst, the first actual idle can have F>C+2 and the exact equality rejects it even when no actual idle callback was missed. Clock continuity and final burst show schedule facts; exact cleanup-phase alignment remains unknown under current opaque-file restriction.',
        performance_causality='Logging/slow frame cost as the trigger of batching is NOT established: delta bits, wall-time per frame, runtime/postcleanup/UI/diagnostic state not decoded.',
        coupled_contract='Collector oncut and schema validate_terminal_evidence also require exact two future physics; changing only the sink comparison would leave downstream rejection or an inconsistent endpoint claim. No repair applied.'),
      forbidden_files_decoded=False,metadata_semantics_used=False,opaque_unchanged_scope=['observer7-runtime.jsonl','observer7-registration.jsonl','observer7-allocations.jsonl','king-post-cleanup-source.json','king-ui-authority.jsonl','source-window-diagnostic.jsonl','other non-authorized payloads'],
      missing_for_exact_cause=['Direct cleanup_clock physics/idle/in_physics is in explicitly OPAQUE postcleanup file; not read.','No allowed control directly exports cleanup C at failure. Cannot assert the precise C/F difference or that this was the first eligible actual idle from a complete cleanup association.','No proof of why scheduler produced the observed batches or whether all business/native outcomes match Python; no model/expected comparison allowed.'],
      minimal_next_boundary='Root may narrowly authorize existing cleanup frame control extraction or a new control-only failure field, then jointly define first-eligible-idle versus exact-two-physics contract across producer/collector/schema before any retry. Do not relax equality, inject stop inputs, alter layout/seeds or patch actual capture here.',
      actual_counts=dict(readonly_analyzer=1,clock_projection_runs=1,full_schema_calls=0,SUT_imports=0,SUT_calls=0,inputbuilds=0,models=0,Godot=0,new_native=0,actualpool_inventory=0,pool_writes=0,restore=0,READY=0,expected_semantics_reads=0),no_more_writes=True)
    save('finding.json',finding)
    own=[x for x in D.rglob('*') if x.is_file()]+[SD/'source-owner.json',R/'tests/phase386_independent_clock_control_triage.py',R/'docs/phase386_first_idle_cut_control_triage_spec.md',sink,collector,game,schema,host,godotmain,tree]
    owner=dict(files=[desc(p) for p in sorted(set(own))],external_capture_provenance_only=True,no_more_writes=True)
    save('owned-files.json',owner)
    for row in owner['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'actual owner readback')
    print(json.dumps(dict(status=finding['status'],finding=desc(D/'finding.json'),owner=desc(D/'owned-files.json'),leaves=len(owner['files']),bytes=sum(r['size'] for r in owner['files']),clock_rows=len(rows),kind_counts=dict(kinds),last_idle=idle_gaps[-1],cleanup_frame='NOT_DECODED_OPAQUE')))
if __name__=='__main__':main()
