"""SOURCE-only finite design review identity checks; no SUT/audit execution."""
import ast
import hashlib
import json
from pathlib import Path
import re
import stat

ROOT=Path('/workspace/python-original-engine/repo')
OUT=ROOT/'data/phase405-independent-design-review'
DESIGN='data/phase405-initial-source-feasibility-design/'
READS={}

def load(row):
    p=Path(row['path']);p=p if p.is_absolute() else ROOT/p
    for x in [p,*p.parents]:assert not x.is_symlink(),str(x)
    a=p.lstat();assert stat.S_ISREG(a.st_mode) and a.st_nlink==1
    raw=p.read_bytes();b=p.lstat()
    for f in ('st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns'):assert getattr(a,f)==getattr(b,f)
    value=dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    assert value=={k:row[k] for k in ('size','sha256')},str(p)
    READS[str(p)]=value
    return raw

def pin(p):
    s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
    raw=p.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def ref(n):return dict(path=n,**pin(ROOT/n))
def save(n,v):(OUT/n).open('x').write(json.dumps(v,indent=2,sort_keys=True)+'\n')

def main():
    assert not OUT.exists();OUT.mkdir()
    ownerrow=dict(path=DESIGN+'owned-files.json',size=1181,sha256='323b672eb761f85dbce98d243a2e48e36912f3e7a76a49c93857e49c4cb6dc1f')
    owner=json.loads(load(ownerrow));docs={x['path']:load(x) for x in owner['files']}
    allow=json.loads(docs[DESIGN+'finite-source-allowset.json']);sources={x['path']:load(x) for x in allow['files']}
    assert len(sources)==allow['file_count']==41 and sum(map(len,sources.values()))==allow['bytes']==1495334
    api=json.loads(docs[DESIGN+'source-api-pins.json']);schema=load(api['schema_module']).decode();tree=ast.parse(schema);lines=schema.splitlines(keepends=True)
    byline={n.lineno:n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
    apiverified=[]
    for row in api['python_functions']:
        n=byline[row['line']];assert n.name==row['name'] and n.end_lineno==row['end_line']
        assert '('+ast.unparse(n.args)+')'==row['signature']
        raw=''.join(lines[n.lineno-1:n.end_lineno]).encode()
        assert len(raw)==row['size'] and hashlib.sha256(raw).hexdigest()==row['sha256']
        apiverified.append(row)
    gdverified=[]
    for group in api['producer_functions']:
        text=load(group['module']).decode();matches=list(re.finditer(r'^func ([A-Za-z_][A-Za-z0-9_]*)\([^\n]*',text,re.M))
        for row in group['functions']:
            pairs=[(i,m) for i,m in enumerate(matches) if m.group(1)==row['name']];assert len(pairs)==1
            i,m=pairs[0];raw=text[m.start():matches[i+1].start() if i+1<len(matches) else len(text)].encode()
            assert text[:m.start()].count('\n')+1==row['line'] and m.group(0)==row['declaration']
            assert len(raw)==row['size'] and hashlib.sha256(raw).hexdigest()==row['sha256']
            gdverified.append(dict(module=group['module'],**row))
    assert len(apiverified)==13 and len(gdverified)==12
    patch=json.loads(sources['data/phase391-terminal-source/native-patch-source.json'])
    for row in allow['executed_source_relations']:
        expected=patch['paths'][row['resource']]
        assert {k:row['original'][k] for k in ('size','sha256')}==expected['before']
        assert row['executed391_after']==dict(path=expected['after_path'],**expected['after'])
        assert load(row['original'])==sources[row['original']['path']]
        assert load(row['executed391_after'])==sources[row['executed391_after']['path']]
    assert len(allow['executed_source_relations'])==11
    contract=json.loads(sources['data/phase349-king-fresh-source/source-defaults-and-topology-contract.json'])
    for row in allow['scene_contract_relations']:
        assert row in contract['original_sources'].values();load(row)
    assert len(allow['scene_contract_relations'])==2
    fields=json.loads(docs[DESIGN+'field-obligation-manifest.json'])
    five=fields['Timer_selected_five_private_chain'];thirty=fields['Timer_other_thirty_private_chain'];allroles=fields['Timer_public_roles']
    assert len(five)==len(set(five))==5 and len(thirty)==len(set(thirty))==30 and not set(five)&set(thirty)
    assert len(allroles)==len(set(allroles))==35 and set(allroles)==set(five)|set(thirty)
    root402=json.loads(load(api['root402_acceptance']))
    assert root402['status']=='ROOT_ACCEPTS_FIXED06_BOUNDED_TERMINAL_SOURCE_PROCESS_CONTROLS'
    assert api['initial_audit_SUT_budget']==0 and api['optional_separate_structural_job_max_top_calls']==1
    for path,value in list(READS.items()):load(dict(path=path,**value))
    save('source-identity-verification.json',dict(status='PASS',design_owner=ownerrow,design_leaves=5,design_bytes=sum(map(len,docs.values())),
        source_leaf_count=41,source_bytes=1495334,python_API_count=13,GD_function_count=12,original_after_associations=11,scene_associations=2,
        timer_roles=dict(selected5=five,other30=thirty,all35=allroles),verified_python_APIs=apiverified,verified_GD_functions=gdverified,
        consumed_pins=[dict(path=p,**v) for p,v in sorted(READS.items())],post_pins_unchanged=True,SUT_imports=0,SUT_calls=0,run_reads=0,capture_reads=0))
    interfaces=[
        dict(id='I01',result='PASS_DESIGN',subject='Actual12/Root402 identity and I/O isolation',
            evidence='405 sections2.1/3.1 require a new real Root audit release after SOURCE/independent review; only exact12 run leaves. Receipts are authority metadata, not permission to follow their run paths.',
            implementation_condition='Pre-content canonical regular+nlink1 gate including ancestor links; fixed SOURCE allowset; all permissions strictINT0 including SUT. Record approved source references separately from input paths.'),
        dict(id='I02',result='PASS_DESIGN',subject='DIRECT_OBSERVATION / SOURCE_DERIVED / MISSING',
            evidence='Direct presence still requires typed domain/owner/phase validation; nonfresh direct value is REJECTED, never replaced by derived defaults. SOURCE_DERIVED requires six explicit proof obligations; missing proof blocks.',
            implementation_condition='Keep expected constraint and actual value separate. A boolean verified tag or partial excerpt cannot complete a chain. No micro-simulator/eval or Python constructor defaults.'),
        dict(id='I03',result='PASS_DESIGN_CHAIN_NOT_YET_PROVEN',subject='Game.PLAYER reuse/fresh allocation/no-writer chain',
            evidence='Original Game.gd:2251–2265 has if not PLAYER allocation and else PLAYER.INVENTORY.reset. New item lineage does not prove new Character. Collector.start_controlled_combat:439 and ensure_source_window:819 impose controls but their existence alone does not prove actual branch execution.',
            implementation_condition='Require actual lawful identity/phase plus fixed collector allocation/prepare/no-writer SOURCE evidence for each side and each phase. If unavailable, MISSING; do not read runtime/postcleanup/diagnostic controls to fill it.'),
        dict(id='I04',result='PASS_DESIGN',subject='35 Timer roles split5+30',
            evidence='Manifest has35 unique roles, disjoint5 selected facts and30 others; exact set equality verified. Five no-start labels do not establish remaining30 or native private state.',
            implementation_condition='Per-role stable owner/birth/configuration/no-start proof; public0/stopped is public only. Record active31 versus4 aux without dropping aux. Missing engine/scene/writer SOURCE yields MISSING or a separately approved finite supplement.'),
        dict(id='I05',result='PASS_DESIGN_NOT_FULL_SCHEMA',subject='Raw type/alias/slot/phase evidence',
            evidence='405 requires strict duplicate-key/NaN/UTF8/typed decimal/REALbits/physical-order controls, fixed P20/O19 slot gap and39 identities, earlyNULL role integrity, prepare/checkpoint adjacency and source-resource ownership.',
            implementation_condition='Implement only the closed shapes actually consumed by this audit. Incomplete alias/owner/slot/phase evidence must leave affected proof incomplete or reject domain; parsing JSON cannot confer fullschema or binding acceptance. Enforce counters/caps from pinned SOURCE, not observed sizes.'),
        dict(id='I06',result='PASS_DESIGN',subject='Fail-closed result without model/native fallback',
            evidence='Output FEASIBLE_PENDING_FULL_STRUCTURAL_VALIDATION only if every required row is supported with complete proof; MISSING/domain/integrity failures remain separate. Optional391 public validator is a different later release/job, at most1 call.',
            implementation_condition='No bundle/runtime/Tape/projection/candidate code or automatic fallback. First actual job failure preserved; missing-source report is a valid endpoint, not a reason to retry or edit capture.')]
    report=dict(schema='independent405-short-design-review/1',status='INDEPENDENT405_DESIGN_ACCEPTED_FOR_SMALL_STDLIB_AUDIT_SOURCE_IMPLEMENTATION_ROOT_PENDING',
        design_owner=ownerrow,design_spec=next(x for x in owner['files'] if x['path'].startswith('docs/')),
        independent_spec=ref('docs/phase405_independent_short_design_review_spec.md'),source_verification=ref('data/phase405-independent-design-review/source-identity-verification.json'),
        interfaces=interfaces,decision='Root may authorize implementation of a new small stdlib-only audit SOURCE. Implementer must not read actual12. Independent SOURCE review and distinct real Root release precede the independent executor single actual run.',
        logical_future_source_obligations=8,new_test_family_added=False,
        implementation_scope='405 audit functions1–7 only. Optional structural job8 is not automatic and need not be implemented for the first0-SUT audit.',
        field_proof_current_status='NOT_ESTABLISHED_BEFORE_AUTHORIZED_AUDIT',writer_closure_proven=False,
        minor_editorial_notes=['Real API inventory filename is source-api-pins.json; the prose actual-api-inventory.json label is not an additional artifact or permission.',
            'Use the sealed11-file allowset as authoritative; the narrative shortened GD enumeration omits ItemDescriptor.gd although it is actually included and checked.'],
        retained_limits=['403 candidate/reader/comparator implementation not authorized here.','356/361 remain CLOSED; no source changed.',
            'No genuine input/schema acceptance, private native Timer values, independent same-seed claim or King production admission.',
            'Prior native cleanfalse/zombie constraints remain outside this input feasibility result.',
            'The finite41 SOURCE list is verified, not claimed to close every writer/resource dependency.'],
        operations={k:0 for k in ('SUT_imports','SUT_calls','schema_calls','capture_reads','run_reads','expected_reads','inputbuild','projection','bundle','models','native','Godot','Timer','FrameDriver','RNG','livepool','proc','restore','READY')},
        native=0,models=0,inputbuild=0,no_more_writes_after_owner=True)
    save('review.json',report)
    paths=[ROOT/'docs/phase405_independent_short_design_review_spec.md',ROOT/'tests/phase405_independent_short_design_review.py',*sorted(OUT.iterdir())]
    owned={str(p.relative_to(ROOT)):pin(p) for p in paths}
    save('owned-files.json',dict(schema='independent405-review-owner/1',files=owned,leaf_count=len(owned),total_bytes=sum(v['size'] for v in owned.values()),all_regular_single_link=True,native=0,models=0,inputbuild=0))
    for n,v in owned.items():assert pin(ROOT/n)==v
    print(json.dumps(dict(review=ref('data/phase405-independent-design-review/review.json'),owner=ref('data/phase405-independent-design-review/owned-files.json'),leaves=len(owned),bytes=sum(v['size'] for v in owned.values())),sort_keys=True))

if __name__=='__main__':main()
