"""Selective cleanup_clock diagnostic decoder; no sibling business values decoded."""
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SD=R/'data/phase388-independent-source'
D=R/'data/phase388-independent-cleanup-control'
RAW=Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261025-attempt05/output/capture/king-post-cleanup-source.json')
EXPECTED=dict(size=24942,sha256='7d30041b5205da977675ac19e0e1f655c1a906f5c7ae17b2b0b0060c0f629b9a')
PROJECTION=R/'data/phase386-independent-first-idle-triage/clock-control-projection.json'
PROJECTION_PIN=dict(size=339833,sha256='bdf8b6d189debc766bb35ef0ff2b09bd8b87a8b904300a4604925143dfb36bd3')
def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def save(n,x):
    p=D/n
    with p.open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False);f.write('\n')
    return p
def require(x,m):
    if not x:raise ValueError(m)
def ws(text,i):
    while i<len(text) and text[i].isspace():i+=1
    return i
def skip_string(text,i):
    require(text[i]=='"','lexical string start');i+=1
    while i<len(text):
        if text[i]=='\\':i+=2
        elif text[i]=='"':return i+1
        else:i+=1
    raise ValueError('unterminated lexical string')
def skip_value(text,i):
    i=ws(text,i)
    if text[i]=='"':return skip_string(text,i)
    if text[i] in '[{':
        stack=[text[i]];i+=1
        while i<len(text) and stack:
            ch=text[i]
            if ch=='"':i=skip_string(text,i);continue
            if ch in '[{':stack.append(ch)
            elif ch in ']}':require(stack.pop()==('[' if ch==']' else '{'),'lexical container balance')
            i+=1
        require(not stack,'unterminated lexical container');return i
    while i<len(text) and text[i] not in ',}':i+=1
    return i
def select_control(text):
    """Only root key strings and the target3-field value are JSON decoded."""
    i=ws(text,0);require(text[i]=='{','root JSON object');i+=1;selected=[];decoder=json.JSONDecoder()
    while True:
        i=ws(text,i)
        if text[i]=='}':i+=1;break
        require(text[i]=='"','root key syntax');end=skip_string(text,i);key=json.loads(text[i:end]);i=ws(text,end);require(text[i]==':','root colon');start=ws(text,i+1);end=skip_value(text,start)
        if key=='cleanup_clock':selected.append(json.loads(text[start:end]))
        i=ws(text,end)
        if text[i]==',':i+=1;continue
        require(text[i]=='}','root delimiter');i+=1;break
    require(not text[i:].strip() and len(selected)==1,'one exact root cleanup control, no trailing input')
    value=selected[0];require(type(value)is dict,'control dictionary')
    require(set(value)=={'physics_frame','idle_frame','is_in_physics_frame'},'Unexpected cleanup_clock key set; no expansion authorized: '+str(sorted(value)))
    require(type(value['physics_frame'])is int and value['physics_frame']>=0 and type(value['idle_frame'])is int and value['idle_frame']>=0 and type(value['is_in_physics_frame'])is bool,'strict control INT/BOOL')
    return value
def main():
    D.mkdir(exist_ok=False)
    source_owner=json.loads((SD/'source-owner.json').read_text())
    for row in source_owner['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'independent SOURCE drift')
    require(pin(RAW)==EXPECTED,'exact existing postcleanup identity')
    control=select_control(RAW.read_text())
    require(pin(RAW)==EXPECTED,'postcleanup changed during diagnostic extraction')
    require(pin(PROJECTION)==PROJECTION_PIN,'reuse exact386 projection')
    source=json.loads(PROJECTION.read_text());rows=source['rows'];require(len(rows)==2574,'existing row count')
    C=control['physics_frame'];I=control['idle_frame'];kind='physics' if control['is_in_physics_frame'] else 'idle'
    anchors=[row for row in rows if row['kind']==kind and row['physics_frame']==C and row['idle_frame']==I]
    require(len(anchors)==1,'unique cleanup frame-signal association required, otherwise evidence gap')
    anchor=anchors[0];tail=[row for row in rows if row['line']>anchor['line']]
    eligible=[row for row in tail if row['kind']=='idle' and row['physics_frame']>=C+2]
    require(eligible,'actual eligible recorded idle needed');first=eligible[0]
    future_physics=[row for row in tail if row['kind']=='physics' and row['line']<first['line']]
    second=future_physics[1] if len(future_physics)>=2 else None
    require(first==rows[-1] and first['physics_frame']==2732 and first['idle_frame']==342,'failure idle association')
    require(second is not None and second['physics_frame']==C+2,'second future physics signal')
    idles_before=[row for row in tail if row['kind']=='idle' and row['line']<first['line']]
    exact_idle=[row for row in tail if row['kind']=='idle' and row['physics_frame']==C+2]
    require(len(future_physics)==first['physics_frame']-C and len(future_physics)>2 and not exact_idle,'exact2 overrun witness')
    extracted=save('cleanup-clock-control.json',dict(original_file_provenance=str(RAW),original_file_identity=EXPECTED,extracted_key='cleanup_clock',control=control,authority='DIAGNOSTIC CONTROL FROM OTHERWISE OPAQUE EXPECTED_ONLY POSTCLEANUP; NOT LAWFUL MODEL INPUT',sibling_business_values_decoded=False))
    correlation=save('clock-correlation.json',dict(source_projection=desc(PROJECTION),cleanup=control,matching_frame_signal=anchor,cleanup_marker_order='SOURCE-derived: mark occurs at end of deferred Game cleanup, after the frame signal callback represented by this row',eligible_threshold_physics=C+2,second_future_physics=second,first_eligible_actual_idle=first,recorded_idles_after_cleanup_before_cut=idles_before,actual_idle_at_exact_two=exact_idle,future_physics_signals_to_cut=future_physics,actual_future_physics_count=len(future_physics),F_minus_C=first['physics_frame']-C,clock_continuity_revalidated=False,all2574rows_reused_unchanged=True))
    sink=R/'data/phase375-food-hook-source/after-source/native_random_observer_sink_v7.gd';text=sink.read_text()
    require('value["cleanup_clock"] = source_cleanup' in text and '"is_in_physics_frame": Engine.is_in_physics_frame()' in text,'actual direct control origin')
    finding=dict(status='DIAGNOSTIC388_FIRST_ELIGIBLE_IDLE_REJECTED_BY_EXACT_TWO_PHYSICS',extracted_control=extracted,correlation=correlation,
        direct_control_facts=dict(cleanup=control,matching_recorded_signal=anchor,actual_clock_last_idle=first,future_physics_count=len(future_physics),actual_idle_at_exact_C_plus_2_exists=False,first_eligible_idle_by_recorded_order=first),
        SOURCE_derived_cause='Producer records current idle then tests current physics>=cleanup+2 and rejects unless equal. Actual first idle satisfying the threshold is the recorded failing last idle; there is no idle signal at cleanup+2. This rejects a legitimate batched schedule, not evidence that an earlier eligible idle callback was missed. Cleanup mark ordering relative to the matching frame signal uses the already pinned Game/SceneTree SOURCE route, not business-state decoding.',
        bounded_conclusion='Control witness closes386 exact-C gap for this actual capture. It does not validate other12 carrier contracts, state/history/RNG equivalence or all possible schedules.',
        exact2_coupling=['sink clock_idle_signal equality and endpoint two_future_physics_signals=2','sink emit_source_idle_cut_once and collector on_idle_source_cut equality','schema validate_terminal_evidence requires exactly2 physics in cleanup tail; changing sink only is insufficient'],
        future_contract_requirements=['Root must explicitly choose and version first actual idle after at least2 strictly future physics signals versus a separately enforced scheduler policy.','Record/reconstruct actual cleanup/cut association and actual future-physics count from ordered clock controls; do not label a larger tail as exactly2.','Update producer/collector/endpoint/schema SOURCE together, keep same-stack/preinternal/once/ack/finish guards and readonly snapshot semantics.','Diagnostic cleanup/terminal proof from expected-only file cannot become model initial state, stop command or a missing input repair.','No blanket relaxation, new seed/layout, accepted validation.json or repaired original capture follows from this finding.'],
        not_established=['Performance/logging overhead as the cause of8-physics batches','Full native/model/input completeness or valid12 projection','Any all-schedule closure or automatic permission for new capture/model'],
        historical386=desc(R/'data/phase386-independent-first-idle-triage/finding.json'),historical386_C_was_not_read=True,
        actual_counts=dict(diagnostic_extractions=1,control_correlations=1,new_clock_or_schema_validations=0,SUT_imports=0,SUT_calls=0,Godot=0,new_native=0,models=0,inputbuilds=0,projection=0,pool_inventory=0,pool_writes=0,restore=0,READY=0,business_expected_semantics_reads=0),no_more_writes=True)
    save('finding.json',finding)
    paths=[p for p in D.iterdir() if p.is_file()]+[SD/'source-owner.json',R/'tests/phase388_cleanup_clock_control_extract.py',R/'docs/phase388_cleanup_clock_control_extraction_spec.md',PROJECTION,R/'data/phase386-independent-first-idle-triage/finding.json',R/'data/phase386-independent-first-idle-triage/source-evidence.json',sink]
    owner=dict(files=[desc(p) for p in sorted(set(paths))],original_opaque_postcleanup_external_provenance_only=True,no_more_writes=True)
    save('owned-files.json',owner)
    for row in owner['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'actual owner readback')
    print(json.dumps(dict(status=finding['status'],cleanup=control,first_eligible_idle=first,future_physics=len(future_physics),finding=desc(D/'finding.json'),owner=desc(D/'owned-files.json'),leaves=len(owner['files']),bytes=sum(r['size'] for r in owner['files']))))
if __name__=='__main__':main()
