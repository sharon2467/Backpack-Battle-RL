"""398 two-function SOURCE repair: text/compile/AST/inverse only, no SUT import/map run."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import re
import stat
import traceback

R=Path(__file__).resolve().parents[1]
D=R/'data/phase398-attempt05-recovery-source'
SD=R/'data/phase398-independent-readback-source'
HD=R/'data/phase398-source-handoff'
OLD=R/'data/phase395-attempt05-recovery-source'
OLD_SD=R/'data/phase395-independent-readback-source'
SPEC=R/'docs/phase398_source_leaf_before_read_and_reader_owner_bootstrap_spec.md'
REVIEW='INDEPENDENT399_ATTEMPT05_COMPLETE_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING'
READBACK='INDEPENDENT398_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'


def pin(p):
    i=p.lstat()
    assert stat.S_ISREG(i.st_mode) and i.st_nlink==1 and not any(q.is_symlink() for q in (p,*p.parents))
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())


def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))

def read(p):return json.loads(p.read_text())

def save(p,value):
    with p.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False);stream.write('\n')

def write(p,text):
    with p.open('x') as stream:stream.write(text)

def functions(text):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}

def span(text,name):
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
    return ''.join(text.splitlines(True)[node.lineno-1:node.end_lineno])


class Delta:
    def __init__(self,p):self.path=p;self.before=p.read_text();self.text=self.before;self.edits=[]
    def edit(self,a,b,kind='protocol',count=1):
        assert self.text.count(a)==count,(self.path,a[:100],self.text.count(a),count)
        positions=[m.start() for m in re.finditer(re.escape(a),self.text)]
        self.edits.append(dict(before=a,after=b,kind=kind,positions=[pos+i*(len(b)-len(a)) for i,pos in enumerate(positions)]))
        self.text=self.text.replace(a,b)
    def finish(self,p,semantic,changed):
        inverse=self.text
        for e in reversed(self.edits):
            for pos in reversed(e['positions']):
                assert inverse[pos:pos+len(e['after'])]==e['after']
                inverse=inverse[:pos]+e['before']+inverse[pos+len(e['after']):]
        assert inverse==self.before
        normalized=self.text
        # Distinct protocol substitutions are injective for these fixed sources.
        for e in reversed(self.edits):
            if e['kind']=='protocol':normalized=normalized.replace(e['after'],e['before'])
        before,after,norm=map(functions,(self.before,self.text,normalized))
        assert before.keys()==after.keys()==norm.keys()
        actual={k for k in before if before[k]!=after[k]};actual_semantic={k for k in before if before[k]!=norm[k]}
        assert actual==set(changed),(p,actual,changed)
        assert actual_semantic==set(semantic),(p,actual_semantic,semantic)
        compile(self.text,str(p),'exec');write(p,self.text)
        save(D/(p.stem+'-inverse.json'),dict(before=desc(self.path),after=desc(p),edits=self.edits,byte_inverse='EXACT_COMPLETE_BYTES',
            changed_functions=sorted(actual),semantic_changed_functions=sorted(actual_semantic),protocol_only_functions=sorted(actual-actual_semantic),
            conserved_functions=sorted(set(before)-actual),semantically_conserved_functions=sorted(set(before)-actual_semantic)))
        write(D/(p.stem+'-source.patch'),''.join(difflib.unified_diff(self.before.splitlines(True),self.text.splitlines(True),fromfile=str(self.path.relative_to(R)),tofile=str(p.relative_to(R)))))


LEAF='''def recovery_source_leaf(root, row):
    require(type(row) is dict and set(row) == {'path','size','sha256'}, 'closed exact SOURCE descriptor')
    require(type(row['path']) is str and bool(row['path']) and '\\\\' not in row['path'] and '\\0' not in row['path'] and
            all(part not in ('', '.', '..') for part in row['path'].split('/')), 'canonical SOURCE path field')
    require(type(row['size']) is int and row['size'] >= 0 and type(row['sha256']) is str and len(row['sha256']) == 64 and
            all(char in '0123456789abcdef' for char in row['sha256']), 'strict SOURCE size/SHA fields')
    path = member(root, row['path'])
    regular_target(path)
    return descriptor(root, row)'''

GATE_PROTOCOL=[('phase395-root-pool-recovery/1','phase398-root-pool-recovery/1'),
               ('phase395-complete-install-recovery-SOURCE/1','phase398-complete-install-recovery-SOURCE/1'),
               ('separate exact395 recovery action','separate exact398 recovery action'),
               ('separate395 recovery freeze','separate398 recovery freeze'),
               ('independent396 recovery SOURCE review required','independent399 recovery SOURCE review required'),
               ('actual owned396 recovery SOURCE closure','actual owned399 recovery SOURCE closure')]


def main():
    D.mkdir(exist_ok=False);SD.mkdir(exist_ok=False)
    baseline={}
    for name in ['data/phase395-source-handoff/owned-files.json','data/phase396-independent-static-first-001/owned-files.json']:
        p=R/name;baseline[name]=desc(p)
        for row in read(p)['files']:
            assert desc(R/row['path'])==row;baseline[row['path']]=row
    finding=R/'data/phase396-independent-static-first-001/static-findings.json'
    assert pin(finding)==dict(size=5431,sha256='af1313061f1ad8a69216033251913677feffa33cf089c56efcf1330f803ebd51')
    assert [x['id']for x in read(finding)['findings']]==['F01','F02']
    mapping=OLD/'map/restore-map.json';pins=OLD/'map/source-input-pins.json'
    assert pin(mapping)==dict(size=68985,sha256='b9fae3743994c3f5a3b3e590a4b849b914cf0422343fd42738e4d639b6b13dc1')
    assert pin(pins)==dict(size=102475,sha256='b1eae13cfcc3094a38c965cedc8785226a92c54ed9b87e86e6487509b1081510')
    assert len(read(pins)['files'])==524
    save(D/'old-source-before.json',dict(files=list(baseline.values()),original_capture_or_archive_reads=0))

    gate=Delta(R/'tests/phase395_recovery_gate_source.py')
    gate.edit(span(gate.text,'recovery_source_leaf'),LEAF,kind='semantic')
    for a,b in GATE_PROTOCOL:gate.edit(a,b)
    gate.finish(R/'tests/phase398_recovery_gate_source.py',['recovery_source_leaf'],['recovery_source_leaf','source_gate'])

    rec=Delta(R/'tests/phase395_pool_recovery.py')
    rec.edit(span(rec.text,'recovery_source_leaf'),LEAF,kind='semantic')
    for a,b in GATE_PROTOCOL:rec.edit(a,b)
    rec.edit("SOURCE = 'data/phase395-attempt05-recovery-source'","SOURCE = 'data/phase398-attempt05-recovery-source'")
    rec.edit('INDEPENDENT396_ATTEMPT05_COMPLETE_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING',REVIEW)
    rec.edit('INDEPENDENT395_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',READBACK)
    rec.finish(R/'tests/phase398_pool_recovery.py',['recovery_source_leaf'],['recovery_source_leaf','source_gate'])
    assert span(rec.text,'recovery_source_leaf')==span(gate.text,'recovery_source_leaf')
    assert span(rec.text,'source_gate')==span(gate.text,'source_gate')

    reader=Delta(R/'tests/phase395_independent_restored_readback.py')
    before="    require(pin(SD/'source-owner.json')==dict(size=args.source_owner_size,sha256=args.source_owner_sha256),'actual frozen readback Source owner pin')\n    owner=read(SD/'source-owner.json')"
    after="    owner_descriptor=dict(path=str((SD/'source-owner.json').relative_to(R)),size=args.source_owner_size,sha256=args.source_owner_sha256)\n    owner_path=verify_descriptor(R,owner_descriptor)\n    owner=read(owner_path)"
    reader.edit(before,after,kind='semantic')
    for a,b in [('physical395 complete-install','physical398 complete-install'),
        ('data/phase395-independent-actual-readback-first-001','data/phase398-independent-actual-readback-first-001'),
        ('data/phase395-independent-readback-source','data/phase398-independent-readback-source'),
        ('INDEPENDENT395_ATTEMPT05_RESTORED_POOL_EXACT_TARGET_READBACK_PASS',READBACK),
        ('phase395-root-pool-recovery/1','phase398-root-pool-recovery/1'),
        ('ROOT exact395 restore-only source','ROOT exact398 restore-only source'),
        ('exact395 API readback status','exact398 API readback status'),
        ('actual395 recovery SOURCE accepted closure','actual398 recovery SOURCE accepted closure'),
        ('phase395-independent-physical-readback/1','phase398-independent-physical-readback/1'),
        ('BLOCKED_INDEPENDENT395_RESTORED_POOL_READBACK','BLOCKED_INDEPENDENT398_RESTORED_POOL_READBACK'),
        ('phase395-independent-readback-owner/1','phase398-independent-readback-owner/1'),
        ('docs/phase395_complete_restore_source_implementation_addendum.md',str(SPEC.relative_to(R))),
        ('tests/phase395_independent_restored_readback.py','tests/phase398_independent_restored_readback.py')]:
        reader.edit(a,b,count=reader.text.count(a))
    reader.finish(R/'tests/phase398_independent_restored_readback.py',['prepare_contract'],['prepare_contract','main'])
    for name in ['readonly-process-inspector.py','CAPSULE385.json']:
        write(SD/name,(OLD_SD/name).read_text());assert pin(SD/name)==pin(OLD_SD/name)

    # Static call-order checks only; neither function is imported or invoked.
    leaf=next(n for n in ast.parse(rec.text).body if isinstance(n,ast.FunctionDef) and n.name=='recovery_source_leaf')
    top=[]
    for node in leaf.body:
        value=node.value if isinstance(node,(ast.Assign,ast.Expr,ast.Return)) else None
        if isinstance(value,ast.Call) and isinstance(value.func,ast.Name):top.append(value.func.id)
    assert top==['require','require','require','member','regular_target','descriptor']
    prepare=span(reader.text,'prepare_contract')
    assert prepare.index('owner_path=verify_descriptor(R,owner_descriptor)')<prepare.index('owner=read(owner_path)')<prepare.index("for row in owner['files']:verify_descriptor(R,row)")
    assert "pin(SD/'source-owner.json')" not in prepare and "read(SD/'source-owner.json')" not in prepare
    old_inverse=read(OLD/'phase395_pool_recovery-inverse.json')
    for name in old_inverse['conserved_functions']:assert functions(rec.text)[name]==functions(rec.before)[name]
    old_inverse_reader=read(OLD/'phase395_independent_restored_readback-inverse.json')
    for name in old_inverse_reader['conserved_functions']:assert functions(reader.text)[name]==functions(reader.before)[name]
    save(D/'static-order-and-conservation.json',dict(F01_top_level_call_order=top,F01_template_equals_generated=True,F02_verified_owner_path_before_decode=True,
        recovery395_conserved_methods=old_inverse['conserved_functions'],reader395_conserved_methods=old_inverse_reader['conserved_functions'],
        method_calls=0,module_imports=0,proof_scope='SOURCE AST/text/complete byte inverse; dynamic399 pending'))

    old_freeze=read(OLD/'combined-source-freeze.json');freeze=copy.deepcopy(old_freeze)
    files={row['path']:row for row in old_freeze['files']}
    for row in baseline.values():files[row['path']]=row
    new_sources=[Path(__file__),SPEC,R/'tests/phase398_recovery_gate_source.py',R/'tests/phase398_pool_recovery.py',R/'tests/phase398_independent_restored_readback.py',SD/'readonly-process-inspector.py',SD/'CAPSULE385.json']
    for p in new_sources:files[str(p.relative_to(R))]=desc(p)
    # Retain old map/source helper as actual reuse, not a new398 map generation.
    imports=[]
    for row in old_freeze['import_closure']:
        imports.append(desc(R/'tests/phase398_pool_recovery.py') if row['path']=='tests/phase395_pool_recovery.py' else row)
    inventory=[]
    for p in [R/row['path']for row in imports]+new_sources:
        if p.suffix!='.py':continue
        compile(p.read_text(),str(p),'exec');modules=[]
        for node in ast.walk(ast.parse(p.read_text())):
            if isinstance(node,ast.Import):modules.extend(n.name for n in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:modules.append(node.module)
        local=sorted({m for m in modules if (R/'tests'/(m+'.py')).is_file()})
        assert all('tests/'+m+'.py' in files for m in local)
        inventory.append(dict(path=str(p.relative_to(R)),local_imports=local))
    save(D/'import-closure.json',dict(files=imports,inventory=inventory,pre_import_requirement='Root verifies actual ordinary source payloads before interpreter;398 consumer independently gates before content reads'))
    files[str((D/'import-closure.json').relative_to(R))]=desc(D/'import-closure.json')
    freeze.update(schema='phase398-complete-install-recovery-SOURCE/1',files=list(files.values()),import_closure=imports,
        recovery_module=desc(R/'tests/phase398_pool_recovery.py'),source_design=desc(SPEC),repair_origin=desc(OLD/'combined-source-freeze.json'),
        repair_findings=desc(finding),repair_review=desc(R/'data/phase396-independent-static-first-001/review.json'),
        reused_map=True,map_generator_origin=freeze.pop('map_generator'),actual_operations_allowed=0)
    assert freeze['restore_map']==desc(mapping) and freeze['input_pins']==desc(pins)
    assert freeze['complete_install']==old_freeze['complete_install'] and freeze['terminal_component_context']==old_freeze['terminal_component_context']
    for row in freeze['files']:assert desc(R/row['path'])==row
    save(D/'combined-source-freeze.json',freeze)

    operations={k:0 for k in read(OLD/'api-contract.json')['operational_calls']}
    api=dict(schema='phase398-recovery-api-contract/1',root_schema='phase398-root-pool-recovery/1',source_review_status=REVIEW,readback_status=READBACK,
        SOURCE=str(D.relative_to(R)),MAP=str(mapping.relative_to(R)),INPUT_PINS=str(pins.relative_to(R)),map_schema='phase395-attempt05-complete-restore-source-map/1',
        functions=dict(recovery_source_leaf='(root,row:{path,size,sha256}) -> physical gate before exact descriptor hash; unchanged member/regular_target/descriptor',
            source_gate='(source_root,config_descriptor,action) -> root,config;398 authority and actual399 review required',
            recover='(source_root,config_descriptor,pool,baseline,failed_run,previous_run,action,output=None); restore and commit_ready separately released',
            reader='CLI unchanged; --source-owner-size/sha256 form fixed398 SD-relative descriptor, verified before bootstrap read'),
        source_freeze=desc(D/'combined-source-freeze.json'),map=desc(mapping),input_pins=desc(pins),terminal_context=freeze['terminal_component_context'],
        reader_source_contract=str((SD/'source-contract.json').relative_to(R)),reader_source_owner=str((SD/'source-owner.json').relative_to(R)),
        source_review=None,actual_restore_authorization=None,restore_receipt=None,independent_physical_report=None,READY_authorization=None,
        operational_calls=operations,operation_scope='398 only;395 two successful saved generations and all prior errors remain immutable provenance',map_generation_entrypoint_added=False)
    save(D/'api-contract.json',api)
    save(D/'protocol-reuse-inventory.json',dict(active=dict(root_schema=api['root_schema'],SOURCE=api['SOURCE'],review=REVIEW,readback=READBACK,recovery=desc(R/'tests/phase398_pool_recovery.py'),reader=desc(R/'tests/phase398_independent_restored_readback.py')),
        retained=dict(map=desc(mapping),input_pins=desc(pins),schema=api['map_schema'],saved_helper=desc(R/'tests/phase395_saved_complete_evidence.py'),component_context=freeze['terminal_component_context'],
                      installed_source_freeze=freeze['complete_install']['installed_source_freeze']),
        inherited_protocol_literals='395 map/provenance and391/392/Root395 context intentionally unchanged; no historical source status serves as399 acceptance'))
    for row in baseline.values():assert desc(R/row['path'])==row
    save(D/'old-source-readback.json',dict(status='ALL395_AND396_OWNED_SOURCE_LEAVES_IDENTICAL',files=list(baseline.values()),original_run_or_capture_reads=0))
    save(D/'summary.json',dict(status='SOURCE_FROZEN_INDEPENDENT399_PENDING',freeze=desc(D/'combined-source-freeze.json'),api=desc(D/'api-contract.json'),
        semantic_functions=['recovery_source_leaf','prepare_contract'],source_compile=True,byte_inverse=True,AST_conservation=True,operational_calls=operations))
    own=dict(files)
    for p in sorted(D.rglob('*')):
        if p.is_file():own[str(p.relative_to(R))]=desc(p)
    save(D/'source-owner.json',dict(schema='phase398-recovery-source-owner/1',files=list(own.values()),scope='SOURCE two IO gate repairs only; dynamic399/recovery/reader not executed'))

    contract=copy.deepcopy(read(OLD_SD/'source-contract.json'))
    contract.update(schema='phase398-independent-readback-source-contract/1',SOURCE_review_status=REVIEW,readback_status=READBACK,
        source_freeze=desc(D/'combined-source-freeze.json'),recovery_source_owner=desc(D/'source-owner.json'),source_API=desc(D/'api-contract.json'),
        process_inspector_source=desc(SD/'readonly-process-inspector.py'),process_inspector_origin=desc(OLD_SD/'readonly-process-inspector.py'),
        failed_capsule_manifest=desc(SD/'CAPSULE385.json'))
    assert contract['restore_map']==desc(mapping) and contract['input_pins']==desc(pins)
    old_contract=read(OLD_SD/'source-contract.json')
    allowed={'schema','SOURCE_review_status','readback_status','source_freeze','recovery_source_owner','source_API','process_inspector_source','process_inspector_origin','failed_capsule_manifest'}
    assert all(contract[k]==old_contract[k] for k in contract if k not in allowed)
    save(SD/'source-contract.json',contract)
    save(SD/'summary.json',dict(status='SOURCE_COMPILED_NOT_IMPORTED_DYNAMIC399_PENDING',reader=desc(R/'tests/phase398_independent_restored_readback.py'),contract=desc(SD/'source-contract.json'),F02='strict existing verifier owns bootstrap physical gate',reader_imports=0,reader_calls=0))
    reader_own=dict(own);reader_own[str((D/'source-owner.json').relative_to(R))]=desc(D/'source-owner.json')
    for p in sorted(SD.iterdir()):
        if p.is_file():reader_own[str(p.relative_to(R))]=desc(p)
    save(SD/'source-owner.json',dict(schema='phase398-readback-source-owner/1',files=list(reader_own.values()),scope='398 readonly-reader SOURCE; actual bootstrap rejection not executed by author'))
    HD.mkdir(exist_ok=False)
    save(HD/'summary.json',dict(status='398_SOURCE_HANDOFF_INDEPENDENT399_PENDING',recovery_owner=desc(D/'source-owner.json'),reader_owner=desc(SD/'source-owner.json'),freeze=desc(D/'combined-source-freeze.json'),api=desc(D/'api-contract.json'),
        reused_map=desc(mapping),reused_input_pins=desc(pins),all_operational_calls=operations,no_more_writes=True))
    complete=dict(reader_own)
    complete[str((SD/'source-owner.json').relative_to(R))]=desc(SD/'source-owner.json');complete[str((HD/'summary.json').relative_to(R))]=desc(HD/'summary.json')
    save(HD/'owned-files.json',dict(schema='phase398-handoff-owner/1',files=list(complete.values()),scope='SOURCE only; no map regeneration or operational execution'))
    for row in complete.values():assert desc(R/row['path'])==row
    for row in baseline.values():assert desc(R/row['path'])==row
    print(json.dumps(dict(handoff_owner=desc(HD/'owned-files.json'),recovery_owner=desc(D/'source-owner.json'),reader_owner=desc(SD/'source-owner.json'),freeze=desc(D/'combined-source-freeze.json'),api=desc(D/'api-contract.json'),leaves=len(complete),bytes=sum(row['size']for row in complete.values()))))


if __name__=='__main__':
    try:main()
    except BaseException:
        failure=next(D/('source-preparation-failure-%03d'%n)for n in range(1,100)if not (D/('source-preparation-failure-%03d'%n)).exists())
        failure.mkdir(parents=True)
        for p in R.glob('tests/phase398_*.py'):write(failure/p.name,p.read_text())
        write(failure/'traceback.txt',traceback.format_exc());raise
