"""Output-only continuation after completed SOURCE/AST checks; no SUT or rerun."""
import hashlib
import json
from pathlib import Path
import stat

ROOT=Path('/workspace/python-original-engine/repo')
OUT=ROOT/'data/phase403-independent-design-review'
ATIME=[]

def pin(path):
    before=path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink==1
    raw=path.read_bytes();after=path.lstat()
    for field in ('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'):
        assert getattr(before,field)==getattr(after,field),(str(path),field)
    assert len(raw)==before.st_size
    ATIME.append(dict(path=str(path.relative_to(ROOT)),before_ns=before.st_atime_ns,after_ns=after.st_atime_ns,
                      changed=before.st_atime_ns!=after.st_atime_ns))
    return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())

def ref(name):return dict(path=name,**pin(ROOT/name))
def save(name,value):(OUT/name).open('x').write(json.dumps(value,sort_keys=True,indent=2)+'\n')

def main():
    assert not (OUT/'review.json').exists() and not (OUT/'owned-files.json').exists()
    verification=json.loads((OUT/'source-identity-verification.json').read_bytes())
    sourcepins={r['path']:r for r in verification['consumed_source_pins']}
    report=dict(schema='independent403-design-review/1',
        status='INDEPENDENT403_DESIGN_DIRECTION_ACCEPTED_PREIMPLEMENTATION_INPUT_AUDIT_REQUIRED',
        design_owner=verification['design_owner'],design_spec=sourcepins['docs/phase403_genuine_input_and_independent_model_design_spec.md'],
        independent_spec=ref('docs/phase403_independent_design_review_spec.md'),findings=ref('docs/phase403_independent_design_review_findings.md'),
        source_verification=ref('data/phase403-independent-design-review/source-identity-verification.json'),
        review_scope='SOURCE-only design feasibility; not implementation acceptance or gate opening',
        verified=dict(design_leaves=5,design_bytes=81616,source_leaves=68,source_bytes=2346208,actual_AST_functions=90,actual_AST_modules=10,
                      source349_to351_identical=15,source349_to356_identical=13,source_postpins_passed_before_first_sealer_error=True,
                      SOURCE_AST_cycles_repeated_during_sealer_continuation=False),
        finite_findings=[
            dict(id='D01',result='PASS_DESIGN',subject='Three356 admission paths and361 reader remain closed; joint identity needed at input/runtime/result/comparator boundaries.'),
            dict(id='D02',result='PASS_WITH_EXPLICIT_HASH_LAYER_RULE',subject='Code binds immutable391 identity; external engineering freeze/review/release binds candidate bytes without self-hash cycle.'),
            dict(id='D03',result='PASS_DESIGN',subject='Preserve349 Timer/FrameDriver; replace351 alternating/C+2 checker assumptions.'),
            dict(id='D04',result='PASS_DESIGN',subject='5/17-key compatibility with strict INPUT/EXPECTED separation, raw clock and constructor-only initial runtime.'),
            dict(id='D05',result='PASS_DESIGN',subject='Tape is conditional direct primitive replay, not independent same-seed closure.'),
            dict(id='D06',result='PASS_DESIGN_PENDING_SITE_MAP',subject='Preserve callback order/tail; seal required business-site/model-observation map before checker implementation.'),
            dict(id='D07',result='PASS_DESIGN',subject='Consume four extra outer groups; never fabricate native private Timer values.'),
            dict(id='D08',result='PASS_CONDITIONAL_SCOPE',subject='Budget exception only if implemented for new profile; activation death unsupported.'),
            dict(id='D09',result='NOT_ESTABLISHED_ACTUAL_INPUT_PENDING',subject='Classify every required initial field DIRECT_OBSERVATION / SOURCE_DERIVED / MISSING.'),
            dict(id='D10',result='SUFFICIENT_LOGICAL_COVERAGE_NOT_API_CAP',subject='Retain20 finite obligations; exact call caps and legitimate full-gate positive authority must be sealed later.'),
            dict(id='D11',result='PREIMPLEMENTATION_AUDIT_RECOMMENDED',subject='Separate lawful12 presence/SOURCE-chain feasibility audit; no bundle/model/old-reader bypass.')],
        initial_field_structural_evidence=dict(
            buffProtectStacks='Direct lawful checkpoint carrier via sink.source_resources1388 and checkpoint704. Actual presence/type/owner/value not read.',
            invulnerable_invulnerabilityItem_invulBubbleVisible='Not directly in checkpoint/source_resources path. Character typed sites are runtime; aggregate snapshot is EXPECTED. Complete SOURCE derivation remains possible but unestablished.',
            crown_light='Potential prepare/setState/onStateChanged derivation; needs complete fresh allocation and no-intervening-writer proof, not partial excerpts/defaults alone.',
            private_Timer='Five selected fresh facts do not automatically cover all modeled Timers. Native private values remain unobserved.',
            actual_input_result='NOT_ESTABLISHED_WITHOUT_SEPARATE_AUTHORIZED_LAWFUL12_AUDIT'),
        future_audit=dict(independent_scope_valid=True,
            authority='Distinct real Root input-audit release binding401/402/executed-source and exactly12 descriptors. Current402 control-only release is insufficient.',
            output='Coverage/provenance report only; no fixture/runtime/draw bundle or Engine DTO.',
            minimum_existing_schema_assisted_APIs=[
                dict(module='tests/phase391_king_observer_schema.py',function='validate_sources_with_binding',signature='(raw11, binding_bytes, source_contract)',line=2362,maximum_top_level_calls=1),
                dict(module='tests/phase391_king_observer_schema.py',function='decode_sources',signature='(raw_by_name)',line=1704,maximum_top_level_calls=1)],
            optional_smaller_scope='Stdlib-only bounded presence inventory0 SUT calls; cannot claim full schema/source-chain acceptance.',
            classifications=['DIRECT_OBSERVATION','SOURCE_DERIVED','MISSING'],
            source_derived_requirement='Complete fresh allocation/configuration/prepare/no-intervening-writer chain to actual activation, with actual lawful identity/phase and pinned original SOURCE.',
            source_extension='Explicitly pin necessary full original SOURCE absent from40368 leaves; no arbitrary metadata-following or live pool reads.',
            prohibited='No old361 reader/projection/seal functions,356 admission/Engine, terminal helper rerun, AST-copied validator or altered module constants.',
            first_failure='Preserve and stop; missing route becomes BLOCKED_INITIAL_SOURCE. New capture needs distinct producer/schema/tuple/native authority.',not_executed=True),
        obligation_refinements={
            '1_2':'No fabricated Root/review positives; absent real authority remains SOURCE-only or genuine earlier-negative scope.',
            '7_9':'Per-field direct/source-derived/missing; complete modeled Timer membership and no-writer chain.',
            '12_15':'Only new interface regression; no old acceptance replay. Expected C mutations never rerun model.',
            '16':'NOT_APPLICABLE unless new-profile ending-budget exception implemented.',
            '18_19':'Four outer groups plus explicit required site mapping. Unsupported business sites block completeness.',
            '20':'Separate engineering authority launcher/input/model/comparator domains; capture forbidden to model.'},
        errors_preserved=[ref('data/phase403-independent-design-review/inventory-display-first-error.json'),ref('data/phase403-independent-design-review/sealer-first-error.json')],
        sealer_continuation='Root explicitly authorized excluding only atime from stat stability; dev/ino/mode/nlink/size/mtime_ns/ctime_ns and SHA/ordinary-file gates retained. No68/90 check rerun.',
        operations={k:0 for k in ('SUT_imports','SUT_calls','schema_calls','capture_reads','run_reads','expected_reads','Engine','FrameDriver','Timer','RNG','models','inputbuild','projection','native','Godot','proc','livepool','restore','READY')},
        native=0,models=0,inputbuild=0,implementation_release=False,old356_361_gates='UNCHANGED_CLOSED',King_production_admitted=False,
        no_more_writes_after_owner=True)
    save('review.json',report)
    save('sealer-atime-reference-observations.json',dict(scope='Own review references only; original first-failure stat values were not logged, so its cause is not retroactively asserted.',observations=ATIME.copy()))
    paths=[ROOT/'docs/phase403_independent_design_review_spec.md',ROOT/'docs/phase403_independent_design_review_findings.md',
        ROOT/'tests/phase403_independent_static_design_identity.py',ROOT/'tests/phase403_seal_independent_design_review.py',*sorted(OUT.iterdir())]
    files={str(p.relative_to(ROOT)):pin(p) for p in paths}
    owner=dict(schema='independent403-design-review-owner/1',files=files,leaf_count=len(files),total_bytes=sum(v['size'] for v in files.values()),
               all_regular_single_link=True,native=0,models=0,inputbuild=0)
    save('owned-files.json',owner)
    for name,row in files.items():assert pin(ROOT/name)==row
    print(json.dumps(dict(review=ref('data/phase403-independent-design-review/review.json'),owner=ref('data/phase403-independent-design-review/owned-files.json'),
                         leaves=len(files),bytes=owner['total_bytes']),sort_keys=True))

if __name__=='__main__':main()
