"""Generate exactly two fixed-success recovery Source copies; no payload import."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import traceback

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/phase625-fixed002-success-recovery-source'
TARGETS={'writer':ROOT/'tests/phase625_restore_predecessor.py','reader':ROOT/'tests/phase625_independent_predecessor_readback.py'}
OLD={'writer':ROOT/'tests/phase590_restore_predecessor.py','reader':ROOT/'tests/phase590_independent_predecessor_readback.py'}


def pin(path):
    path=Path(path);raw=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def read(path):return json.loads(Path(path).read_bytes())


def save(path,value):
    with Path(path).open('x') as stream:stream.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def functions(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}


class Delta:
    def __init__(self,text):self.text=text;self.changes=[]
    def replace(self,before,after,label):
        assert before!=after and self.text.count(before)==1,('strict unique span',label)
        at=self.text.index(before);self.text=self.text[:at]+after+self.text[at+len(before):]
        self.changes.append(dict(offset=at,before=before,after=after,label=label))
    def assign(self,name,value,expression=False):
        nodes=[n for n in ast.parse(self.text).body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
        assert len(nodes)==1 and nodes[0].col_offset==0
        n=nodes[0];lines=self.text.splitlines(keepends=True);start=sum(map(len,lines[:n.lineno-1]));end=sum(map(len,lines[:n.end_lineno]))
        assert start>0 and self.text[start-1]=='\n' and self.text[end-1]=='\n'
        assert n.end_col_offset==len(lines[n.end_lineno-1].removesuffix('\n').encode())
        self.replace(self.text[start-1:end],'\n'+name+' = '+(value if expression else repr(value))+'\n','AST complete physical-line assignment:'+name)
    def inverse(self):
        text=self.text
        for row in reversed(self.changes):
            at=row['offset'];assert text[at:at+len(row['after'])]==row['after']
            text=text[:at]+row['before']+text[at+len(row['after']):]
        return text


def main():
    assert not OUT.exists();OUT.mkdir();(OUT/'inverse').mkdir()
    generated=[]
    try:
        for p in TARGETS.values():assert not p.exists(),'immutable output module'
        freeze=pin(ROOT/'data/phase621-hooks110-rebinding-source/host/combined-source-freeze.json')
        assert freeze['sha256']=='2df37012b8f3313ce010104a0fe835a87f066556c965753fede8c3874a1e748a'
        host=read(ROOT/freeze['path']);assert host['run_name']=='original030-mixed-modifiers-A-single-002'
        assert host['project_install_count']==79 and host['project_install_source_bytes']==817696
        storage=pin(ROOT/'tests/phase621_oracle_storage.py');assert storage==host['storage']
        originals={k:p.read_text() for k,p in OLD.items()};deltas={k:Delta(v) for k,v in originals.items()}
        w=deltas['writer']
        w.assign('RUN',"NATIVE / 'runs/original030-mixed-modifiers-A-single-002'",expression=True)
        w.assign('FREEZE',freeze)
        node=next(n for n in ast.parse(w.text).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCES' for t in n.targets))
        sources=ast.literal_eval(node.value);sources['storage']=storage;w.assign('SOURCES',sources)
        w.replace("sum(row['size'] for row in expected_after.values())==817389","sum(row['size'] for row in expected_after.values())==817696",'exact79 corpus binding only')
        for before,after in [("'phase590-fixed-predecessor-restore-request/1'","'phase625-fixed002-predecessor-restore-request/1'"),
                             ("'phase590-restore-'","'phase625-restore-'"),
                             ("'phase590-fixed-predecessor-restore-result/1'","'phase625-fixed002-predecessor-restore-result/1'"),
                             ("'phase590-restore-output-owner/1'","'phase625-restore-output-owner/1'")]:
            w.replace(before,after,'declarative namespace:'+before)
        TARGETS['writer'].write_text(w.text);generated.append(TARGETS['writer'])
        r=deltas['reader'];r.assign('RUN','original030-mixed-modifiers-A-single-002');r.assign('FREEZE',freeze)
        r.replace("sum(x['size'] for x in expected_after.values()) == 817389","sum(x['size'] for x in expected_after.values()) == 817696",'exact79 corpus binding only')
        for before,after in [("'phase590-fixed-predecessor-readback-request/1'","'phase625-fixed002-predecessor-readback-request/1'"),
                             ("'phase590-readback-'","'phase625-readback-'"),
                             ("'phase590-independent-readback-result/1'","'phase625-independent-fixed002-readback-result/1'"),
                             ("'phase590-readback-output-owner/1'","'phase625-readback-output-owner/1'")]:
            r.replace(before,after,'declarative namespace:'+before)
        TARGETS['reader'].write_text(r.text);generated.append(TARGETS['reader'])
        compiled=[];census=[]
        for role,d in deltas.items():
            assert d.inverse()==originals[role],'complete Source inverse'
            old,new=functions(originals[role]),functions(d.text);assert set(old)==set(new)
            changed=[n for n in old if old[n]!=new[n]]
            assert set(changed)==({'validate_request','prepare','main'} if role=='writer' else {'readback','main'}),(role,changed)
            compile(TARGETS[role].read_bytes(),str(TARGETS[role]),'exec');compiled.append(pin(TARGETS[role]))
            save(OUT/'inverse'/(role+'.json'),dict(schema='phase625-complete-source-inverse/1',before=pin(OLD[role]),after=pin(TARGETS[role]),replacements=d.changes,exact=True))
            (OUT/'inverse'/(role+'.patch')).write_text(''.join(difflib.unified_diff(originals[role].splitlines(True),d.text.splitlines(True),fromfile=str(OLD[role].relative_to(ROOT)),tofile=str(TARGETS[role].relative_to(ROOT)))))
            normalized={n:new[n] for n in new}
            if role=='writer':
                normalized['prepare']=normalized['prepare'].replace('817696','817389')
                normalized['validate_request']=normalized['validate_request'].replace('phase625-fixed002-predecessor-restore-request/1','phase590-fixed-predecessor-restore-request/1')
                normalized['main']=normalized['main'].replace('phase625-restore-','phase590-restore-').replace('phase625-fixed002-predecessor-restore-result/1','phase590-fixed-predecessor-restore-result/1')
            else:
                normalized['readback']=normalized['readback'].replace('817696','817389').replace('phase625-fixed002-predecessor-readback-request/1','phase590-fixed-predecessor-readback-request/1')
                normalized['main']=normalized['main'].replace('phase625-readback-','phase590-readback-').replace('phase625-independent-fixed002-readback-result/1','phase590-independent-readback-result/1')
            assert normalized==old,'all bodies exact after enumerated identity/count normalization'
            census.append(dict(role=role,source=pin(TARGETS[role]),changed_functions=changed,exact_functions=[n for n in old if n not in changed],all_bodies_exact_after_declared_normalization=True,full_inverse=True))
        # Requests are unbound templates, never actual runtime material or authorization.
        writer_evidence={name:None for name in ('controls_manifest','patch_inventory','install_journal','pool_before','previous_bundle_manifest','previous_proof','previous_provenance','previous_project','previous_baseline','previous_staged','previous_host_manifest','pending_state')}
        reader_evidence={name:None for name in ('restore_receipt','restore_owner','controls_manifest','patch_inventory','install_journal','previous_proof','previous_bundle_manifest','pending_state')}
        save(OUT/'restore-request-template.json',dict(schema='phase625-fixed002-predecessor-restore-request/1',case_id='NATIVE-030-MIXED-MODIFIERS-A',previous_run=None,writer=pin(TARGETS['writer']),source_freeze=freeze,evidence=writer_evidence,root_restore_authorized=False))
        save(OUT/'readback-request-template.json',dict(schema='phase625-fixed002-predecessor-readback-request/1',case_id='NATIVE-030-MIXED-MODIFIERS-A',run='/workspace/native-combat-20261013/runs/original030-mixed-modifiers-A-single-002',pool='/workspace/native-combat-20261013/pool',baseline='/workspace/godotsteam-startup-20261013/baseline/Backpack Battles',previous_run=None,relocations={},host_source_freeze=freeze,evidence=reader_evidence))
        save(OUT/'conservation.json',dict(schema='phase625-success-pending-conservation/1',modules=census,pending_association_unchanged=True,failure_authority_added=False,all_kernels_body_exact_after_declared_count_namespace_only=True,case='NATIVE-030-MIXED-MODIFIERS-A',Source_run='original030-mixed-modifiers-A-single-002',project_targets=79,project_bytes=817696,state_writes=0,READY_writes=0))
        save(OUT/'compile-only.json',dict(schema='phase625-source-compile/1',objects=compiled,generation_attempts=1,imports=0,helpers=0,tests=0,resources=0,pool=0,GD=0,Native=0,Expected=0))
        dependencies=[pin(p) for p in OLD.values()]+[freeze,storage,pin(ROOT/'tests/native_run_compaction.py'),pin(Path(__file__)),pin(ROOT/'docs/phase625_fixed002_success_recovery_implementation_spec.md'),pin(ROOT/'data/phase625-root-002-recovery-source-release/release.json'),pin(ROOT/'data/phase624-independent-recovery-design-review/review.json'),pin(ROOT/'data/phase620-root-source-run-selection/selection.json')]
        save(OUT/'source-freeze.json',dict(schema='phase625-fixed002-success-recovery-source-freeze/1',status='SOURCE_ONLY_NOT_OPERATIONAL',modules={k:pin(v) for k,v in TARGETS.items()},dependencies=dependencies,host_source_freeze=freeze,actualprevious=None,actual_requests=None,failure_route_supported=False))
        save(OUT/'api.json',dict(schema='phase625-success-recovery-source-api/1',writer=pin(TARGETS['writer']),reader=pin(TARGETS['reader']),CLI=['--config','--config-sha256','--output-new'],writer_output_prefix='phase625-restore-',reader_output_prefix='phase625-readback-',writer_request_keys=7,writer_evidence=12,reader_request_keys=9,reader_evidence=8,actualprevious=None,root_restore_authorized=False,requires_complete_actual_PENDING=True,failure_route='NOT_AUTHORIZED_OR_SUPPORTED; newactualRootauthority+separateSource required after failure',restore_calls=0,readback_calls=0))
        rows=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in TARGETS.values()]+dependencies
        save(OUT/'owned-files.json',dict(schema='phase625-source-owner/1',files=rows,no_more_writes=True))
        print(json.dumps(dict(status='SOURCE_GENERATED_COMPILED_NOT_IMPORTED',owner=pin(OUT/'owned-files.json'),freeze=pin(OUT/'source-freeze.json'),modules=2)))
    except BaseException as exc:
        save(OUT/'first-error.json',dict(schema='phase625-source-first-error/1',type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),generation_attempts=1,imports=0,helpers=0,tests=0,pool=0,resources=0,GD=0,Native=0,Expected=0))
        save(OUT/'partial-owner.json',dict(schema='phase625-source-partial-owner/1',files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]+[pin(p) for p in generated]+[pin(Path(__file__)),pin(ROOT/'docs/phase625_fixed002_success_recovery_implementation_spec.md')],no_more_writes=True))
        raise


if __name__=='__main__':main()
