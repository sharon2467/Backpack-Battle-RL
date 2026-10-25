"""Preseal only SOURCE/typed unit fixtures; does not import schema or projector."""
import ast
import copy
import hashlib
import json
from pathlib import Path

R=Path(__file__).resolve().parents[1];D=R/'data/phase361-independent-source-review';A=R/'data/phase361-projection-sealer-source'
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 D.mkdir(exist_ok=False);(D/'SOURCE').mkdir()
 owner=json.loads((A/'source-owner.json').read_text());assert pin(A/'source-owner.json')['sha256']=='37f5d012a2f0eb4587bc3681e3328f48b0337faaede62b9254709400455ee3d3'
 for row in owner['files']:assert pin(R/row['path'])==row
 p=R/'tests/phase361_king_projection_sealer.py';src=p.read_text();tree=ast.parse(src);compile(tree,str(p),'exec')
 a={x.id:n for n in tree.body if isinstance(n,ast.Assign) for x in n.targets if isinstance(x,ast.Name)};constants={k:ast.literal_eval(n.value) for k,n in a.items()}
 fn={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
 pending=fn['_require_future_capture_closure'];assert len(pending.body)==1 and isinstance(pending.body[0],ast.Raise)
 reader=fn['read_and_validate_sources'];names=[n.value.func.id for n in reader.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name)];assert names[0]=='_require_future_capture_closure'
 assert constants['RUNTIME_KEYS']==tuple(json.loads((R/'data/phase361-independent-projection-preparation/contract.json').read_text())['runtime_exact'])
 imports=[]
 for n in tree.body:
  if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
  elif isinstance(n,ast.ImportFrom):imports.append(n.module)
 assert set(imports)=={'hashlib','json','os','copy','pathlib','phase360_king_observer_schema'}
 calls=[n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
 assert not set(calls)&{'eval','exec','__import__','Engine','CombatEngine','TapeRandom','SeededRandom'}
 (D/'SOURCE/projector.py').write_bytes(p.read_bytes());(D/'SOURCE/schema.py').write_bytes((R/'tests/phase360_king_observer_schema.py').read_bytes())
 for name in ('projection-source-freeze.json','field-dataflow-matrix.json'):(D/'SOURCE'/name).write_bytes((A/name).read_bytes())
 cases=[]
 def add(label,op,data=None,expect='accept',expected_value=None):cases.append(dict(id=len(cases)+1,label=label,operation=op,data=data,expected=expect,expected_value=expected_value))
 I=lambda n:dict(type='int',decimal=str(n));F=lambda bits:dict(type='float',binary64_be=bits);N=lambda:dict(type='null');S=lambda v:dict(type='string',value=v)
 ref=lambda n,role:dict(type='native_ref',native_id=n,role=role,**{'class':'Node2D'})
 keys=['operation','item','target','ordinal','width','branch','stack','reflect_argument']
 def primitive(site,kind,label,args,value,**context):
  return dict(schema='observer7-record/1',sequence=200,channel='primitive',site=site,edge='return_native_primitive',subject=N(),stamp=dict(physics_frame='1',idle_frame='1',util_time=F('0000000000000000'),combat_time=F('0000000000000000'),phase='SOURCE_UNIT_NOT_NATIVE'),payload=dict(kind=kind,label=label,args=args,value=value,context=dict.fromkeys(keys)|context))
 add('actual-accepted-SOURCE-controls','VERIFY_SOURCE')
 add('reader-pending-before-release-capture-read','READER',expect='pending')
 add('reader-missing-source-control-refusal','BAD_SOURCE_READER',expect='reject')
 add('Buff-Mana105-symbol','ROLE','buff:P:105',expected_value='buff:P:Mana')
 add('Buff-Vamp103-symbol','ROLE','buff:O:103',expected_value='buff:O:Vampirism')
 add('Buff-unknown-category-refusal','ROLE','buff:P:111',expect='reject')
 old=json.loads((R/'data/phase360-independent-schema-review/cases.json').read_text());binding=next(c['data'] for c in old if c['label']=='local39-SOURCE-shape-and-shared-descriptors')
 aliases=dict(native_to_role={r['native_id']:r['instance_id'] for r in binding['actual_bindings']},role_to_native={r['instance_id']:r['native_id'] for r in binding['actual_bindings']})
 refs=[ref(r['native_id'],r['instance_id']) for r in binding['actual_bindings']]
 entry=dict(payload=dict(arguments=dict(type='dictionary',entries=[dict(key=S('items'),value=dict(type='array',values=refs))])))
 add('ordered39-native-alias-O-hole','ORDER',entry,expected_value=[r['instance_id'] for r in binding['actual_bindings']])
 bad=copy.deepcopy(entry);bad['payload']['arguments']['entries'][0]['value']['values'][32]['role']='O:12';add('reject-order-O-renumber','ORDER',bad,'reject')
 bad=copy.deepcopy(entry);bad['payload']['arguments']['entries'][0]['value']['values'][1]=copy.deepcopy(refs[0]);add('reject-order-duplicate','ORDER',bad,'reject')
 r=primitive('Utility/Util.gd::flip','randf','item_chance:P:13:primary',[],F('8000000000000000'));add('randf-negative-zero-bits','PRIMITIVE',r,expected_value=dict(kind='randf',label=r['payload']['label'],args=[],value_bits='8000000000000000'))
 r=primitive('Utility/Util.gd::randPitch','randf_range','invulnerability_pitch:P:12',[F('3feccccccccccccd'),F('3ff199999999999a')],F('3ff0000000000000'),item='P:12');pitch=copy.deepcopy(r);add('King-pitch-range-exactbits','PRIMITIVE',r,expected_value=dict(kind='randf_range',label=r['payload']['label'],args=['3feccccccccccccd','3ff199999999999a'],value_bits='3ff0000000000000'))
 r=primitive('Utility/Util.gd::roll','randf_range','buff:resist:P:P:13:Mana:0',[I(0),F('4059000000000000')],F('3ff0000000000000'),branch='resist',target='P',item='P:13',stack='Mana',ordinal=0,reflect_argument=False);add('roll-only-INT0-to-REAL0','PRIMITIVE',r,expected_value=dict(kind='randf_range',label=r['payload']['label'],args=['0000000000000000','4059000000000000'],value_bits='3ff0000000000000'))
 r=primitive('Utility/BalancedRange.gd::randIntRange','randi_range','damage:P:13',[I(1),I(1)],I(1));add('singleton-randi-row-kept','PRIMITIVE',r,expected_value=dict(kind='randi_range',label=r['payload']['label'],args=[1,1],value=1))
 bad=copy.deepcopy(r);bad['payload']['args'][0]=dict(type='bool',value=True);add('reject-BOOL-randi-endpoint','PRIMITIVE',bad,'reject')
 bad=copy.deepcopy(pitch);bad['payload']['args'][0]=I(0);add('reject-unknown-INT-to-REAL','PRIMITIVE',bad,'reject')
 r=primitive('fixed7fraction_shuffle','global_u32','fraction_shuffle:P:13:P:direct:0:7',[],I(0),item='P:13',target='P',operation='direct',ordinal=0,width=7);add('K1-global-u32-refused','PRIMITIVE',r,'reject')
 bad=copy.deepcopy(pitch);bad['payload']['label']='foreign_unapproved';add('reject-unknown-primitive-label','PRIMITIVE',bad,'reject')
 bad=copy.deepcopy(pitch);bad['payload']['value']=F('7ff8000000000000');add('reject-NaN-return','PRIMITIVE',bad,'reject')
 tape=dict(kind='randi_range',label='damage:P:13',args=[1,1],value=1);add('reject-extra-Tape-key','TAPE',dict(tape,proof=True),'reject');bad=copy.deepcopy(tape);bad['value']=True;add('reject-BOOL-Tape-return','TAPE',bad,'reject')
 decoded=next(c['data'] for c in old if c['label']=='synthetic-relation-join-positive-immutable')
 raw12={name:(json.dumps(v,separators=(',',':'))+'\n' if not name.endswith('.jsonl') else ''.join(json.dumps(row,separators=(',',':'))+'\n' for row in v)) for name,v in decoded.items()};raw12['king-slot-bindings.json']=json.dumps(binding,separators=(',',':'))+'\n'
 add('full-runtime-projection-incomplete-source-refusal','PROJECT_RUNTIME',expect='reject');add('full-Tape-projection-incomplete-source-refusal','PROJECT_DRAWS',expect='reject')
 for label,op,expect in [('engineering-codec-invalid-runtime-fixture-only','SEAL_OK','accept'),('existing-output-refusal-no-overwrite','SEAL_EXISTING','reject'),('symlink-output-refusal','SEAL_SYMLINK','reject'),('failed-proof-encoding-keeps-partial','SEAL_PARTIAL','reject'),('bundle-extra-key-refusal','SEAL_BAD_TOP','reject'),('bad-SOURCE-root-refusal','SEAL_BAD_ROOT','reject'),('synthetic-seed-refusal','SEAL_BAD_SEED','reject'),('runtime-extra-key-refusal','SEAL_BAD_RUNTIME','reject'),('proof-object-type-refusal','SEAL_BAD_PROOF','reject'),('pinned-path-traversal-refusal','BAD_PATH','reject')]:add(label,op,expect=expect)
 assert len(cases)==32
 save(D/'fixtures.json',dict(aliases=aliases,incomplete_raw12=raw12,codec_fixture='Non-executable engineering codec object only; runtime values deliberately invalid, never passed to a model/validator.'))
 save(D/'cases.json',cases)
 save(D/'static-review.json',dict(schema='phase361-independent-source-dataflow/1',status='SOURCE_REVIEWED_DYNAMIC_LIMITS_OPEN',author_leaves=len(owner['files']),author_bytes=sum(x['size'] for x in owner['files']),reader_pending_unconditional_before_capture=True,imports=imports,exact_RUNTIME17=True,models_or_battle_constructors_in_module=False,reviewed=['_validate_sources always calls exact real360 full validator and immutable alias compare','runtime writers enumerate actual external/fresh values and constant constructor limiters; no raw resources/charges/Mana/cache/RNGcheckpoint/endpoints projected','UI copied only for frozen validation-only ABI; no executor','Timer runtime configs not public time_left/private; SOURCE fresh provenance delegated before projection','full external clock copied; no endpoint stop profile','primitive row loop retains physical order and exact bits/strictINT with only declared roll INT0 conversion','seal_once is engineering codec, checks no Engine/runtime semantics, and returns no permission','SOURCE source-root and schema path/byte pins are verified; no arbitrary callable validator bypass'],not_dynamically_proved=['project_fixture_and_runtime complete-source positive','project_primitives full-source physical stream positive','resource/cache/default/terminal/RNGcheckpoint poison through valid full sources','actual12 input/source validity, cache business, runtime/profile patch binding'],new_API_calls=0))
 print(json.dumps(dict(cases=32,source_stage='presealed fixtures; no imports/APIs',positive=sum(c['expected']=='accept' for c in cases))))
if __name__=='__main__':main()
