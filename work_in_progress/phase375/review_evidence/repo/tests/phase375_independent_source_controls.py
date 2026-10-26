"""Finite SOURCE/schema unit gate; never imports runtime/host/recovery."""
import ast
import copy
import dataclasses
import hashlib
import importlib.util
import json
import re
import struct
import sys
import traceback
from pathlib import Path

R=Path(__file__).resolve().parents[1]
SD=R/'data/phase375-independent-execution-source'
D=R/'data/phase375-independent-first-001'
FOOD='Items/Food.gd::prepare'
NEW='tests/phase375_king_observer_schema.py'
OLD='tests/phase360_king_observer_schema.py'
RESULTS=[]
CALLS=[]
AUDIT={'blocked':[],'scope':'Hook installed after trusted stdlib bootstrap/static SOURCE reads; dynamic reads only own mirrors/stdlib, writes only own output.'}

def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=p.relative_to(R).as_posix(),**pin(p))
def read(p):return json.loads(p.read_text())
def save(p,x):
    with p.open('x') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')
def require(x,why):
    if not x:raise ValueError(why)
def assignment(tree,name):
    return next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
def value(tree,name):return ast.literal_eval(assignment(tree,name).value)

def static():
    owner=read(R/'data/phase375-food-hook-source/source-owner.json')
    for row in owner['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'author source drift '+row['path'])
    freeze=read(R/'data/phase375-food-hook-source/combined-source-freeze.json')
    oldfreeze=read(R/'data/phase370-oracle-source/combined-source-freeze.json')
    for name,row in freeze['paths'].items():require(pin(R/row['after_path'])==row['after'],'frozen path '+name)
    require(set(freeze['paths'])==set(oldfreeze['paths']),'frozen pathset')
    RESULTS.append(dict(id='S01',status='PASS',source_leaves=len(owner['files']),frozen_GD_paths=len(freeze['paths'])))
    a=(R/'data/phase370-oracle-source/after-source/native_random_observer_sink_v7.gd').read_text()
    b=(R/'data/phase375-food-hook-source/after-source/native_random_observer_sink_v7.gd').read_text()
    line=lambda t:re.search(r'^const SITES = (.*)$',t,re.M)
    oldsites=json.loads(line(a).group(1));newsites=json.loads(line(b).group(1))
    require(newsites[FOOD]==dict(channel='runtime',state_schema='item'),'new sink declaration')
    shadow=copy.deepcopy(newsites);del shadow[FOOD]
    require(shadow==oldsites and b.replace(line(b).group(0),line(a).group(0))==a,'sink only one constant line')
    for name,row in freeze['paths'].items():
        if name!='native_random_observer_sink_v7.gd':require(row==oldfreeze['paths'][name],'non-sink GD drift')
    RESULTS.append(dict(id='S02',status='PASS',sink_inverse='EXACT_FULL_BYTES_AFTER_SINGLE_CONSTANT_LINE_REPLACEMENT',other_GD_paths=74))
    oldtree=ast.parse((R/OLD).read_text());newtree=ast.parse((R/NEW).read_text())
    om=value(oldtree,'MATRIX');nm=value(newtree,'MATRIX')
    expected=dict(channel='runtime',state_schema='item',arguments_exact=[],argument_types={},explicit_returns=[])
    require(nm['sites'][FOOD]==expected,'complete schema row')
    restored=copy.deepcopy(nm);del restored['sites'][FOOD]
    require(restored==om and len(om['sites'])==106,'old106/otherMATRIX values')
    RESULTS.append(dict(id='S03',status='PASS',old_entries=106,new_entries=len(nm['sites'])))
    shadow=copy.deepcopy(newtree);assignment(shadow,'MATRIX').value=copy.deepcopy(assignment(oldtree,'MATRIX').value)
    removed=[]
    class RemoveFoodGuard(ast.NodeTransformer):
        def visit_If(self,node):
            if isinstance(node.test,ast.BoolOp) and ast.dump(node.test,include_attributes=False).find(repr(FOOD))>=0:
                require(len(node.body)==1 and isinstance(node.body[0],ast.Raise) and not node.orelse,'exact Food guard shape')
                wanted=ast.parse("if site == 'Items/Food.gd::prepare' and state['descriptorIndex'] != {'type':'int','decimal':'22'}:\n raise ValueError('x')").body[0].test
                require(ast.dump(node.test,include_attributes=False)==ast.dump(wanted,include_attributes=False),'strict Food descriptor predicate')
                removed.append(node.lineno);return None
            return self.generic_visit(node)
    shadow=RemoveFoodGuard().visit(shadow)
    require(len(removed)==1 and ast.dump(shadow,include_attributes=False)==ast.dump(oldtree,include_attributes=False),'whole module inverse except MATRIX/oneguard')
    guard_parent=next(n for n in newtree.body if isinstance(n,ast.FunctionDef) and n.name=='validate_record')
    require(guard_parent.lineno<removed[0]<guard_parent.end_lineno,'guard belongs public record function')
    RESULTS.append(dict(id='S04',status='PASS',changed_function='validate_record',whole_AST_inverse=True,guard_line=removed[0]))
    audit=read(R/'data/phase373-independent-attempt03-triage-v2/source-dispatch-audit.json')
    emitted=set(audit['selected_literal_sites']);require(len(emitted)==38 and emitted<=newsites.keys() and emitted<=nm['sites'].keys(),'selected emitter closure')
    RESULTS.append(dict(id='S05',status='PASS',selected_emitted=38,all_declared=True,other93_not_admitted=True))
    # Complete AST inversion above conserves every unchanged dataflow function.
    require('EXPECTED-only' in (R/NEW).read_text() or 'Expected-only' in (R/NEW).read_text(),'source expected-only marker')
    boundary=read(R/'data/phase375-food-hook-source/binding-boundaries.json')
    require(boundary['genuine356_opened'] is False and boundary['reader361_opened'] is False,'admission metadata closed')
    RESULTS.append(dict(id='S06',status='PASS',basis='whole AST inverse + sink methods exact; no projection/runtime change',actual12positive=False))
    for name in ['_base_validate_record','_validate_call_pairs','validate_observation_records','_transport_only_decode','decode_sources','validate_sources_with_binding']:
        n=next(n for n in newtree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        if name=='validate_observation_records':require(any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='validate_record' for x in ast.walk(n)),'public observation delegate')
    RESULTS.append(dict(id='S07',status='PASS',basis='unchanged real delegates/transport AST plus full module inversion; actual exported identity checked dynamically'))
    pairs=[('data/phase370-oracle-source','data/phase375-food-hook-source'),('INDEPENDENT370_SCRIPT_SIGNAL_RETURN_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING','INDEPENDENT375_FOOD_HOOK_SOURCE_REPAIR_ACCEPTED_ROOT_PENDING'),('phase370-root-oracle-acceptance/1','phase375-root-oracle-acceptance/1'),('original027-king-single-A-20261025-attempt03','original027-king-single-A-20261025-attempt04'),('attempt=3','attempt=4')]
    text=(R/'tests/phase370_oracle_host.py').read_text()
    for old,new in pairs:text=text.replace(old,new)
    require(text==(R/'tests/phase375_oracle_host.py').read_text(),'host binding-only exact')
    pairs=[('from phase370_oracle_host import','from phase375_oracle_host import'),('INDEPENDENT370_RESTORED_POOL_EXACT_TARGET_READBACK_PASS','INDEPENDENT375_RESTORED_POOL_EXACT_TARGET_READBACK_PASS'),('phase370-root-pool-recovery/1','phase375-root-pool-recovery/1'),('data/phase368-attempt02-recovery-source','data/phase375-attempt03-recovery-source-v2'),('phase368-attempt02-exact-restore-source-map/1','phase375-attempt03-exact-restore-source-map/1'),('attempt02-failed-pool-preservation/1','attempt03-failed-pool-preservation/1')]
    text=(R/'tests/phase370_pool_recovery.py').read_text()
    for old,new in pairs:text=text.replace(old,new)
    require(text==(R/'tests/phase375_pool_recovery_v2.py').read_text(),'recovery binding-only exact')
    mapping=read(R/'data/phase375-attempt03-recovery-source-v2/restore-map.json');pins=read(R/'data/phase375-attempt03-recovery-source-v2/source-input-pins.json')
    require(mapping['schema']=='phase375-attempt03-exact-restore-source-map/1' and Path(mapping['roots']['failed_run']).name.endswith('attempt03'),'attempt03 map origin')
    require(len(mapping['file_differences'])==78 and len(mapping['directory_differences'])==7 and len(mapping['staged_files'])==2,'derived map scope')
    checked=[]
    for row in pins['files']:
        require(row['root'] in ('failed_run','previous_run','source_root'),'never livepool pins')
        p=Path(mapping['roots'][row['root']])/row['path'];require(pin(p)=={k:row[k] for k in ('size','sha256')},'saved source pin')
        checked.append(dict(root=row['root'],path=row['path'],**pin(p)))
    receipt_path=mapping['failed_preservation'];rp=Path(mapping['roots'][receipt_path['root']])/receipt_path['path'];receipt=read(rp)
    require(receipt['schema']=='attempt03-failed-pool-preservation/1' and receipt['restore']==0 and type(receipt['restore']) is int,'saved real attempt03 receipt')
    gen=(R/'tests/phase375_prepare_attempt03_restore_map_v2.py').read_text()
    oldgen=(R/'tests/phase368_prepare_attempt02_restore_map.py').read_text()
    expected=oldgen.replace("RECEIPT = dict(size=335,sha256='f34d7e1f00094f9cfbf99bb8947f8cd69b375b1cff98395b74ab4bff9fe3d4f1')","RECEIPT = {'size': 335, 'sha256': '355d5615d3d0ef86a79cd0ea9f7460eb9dd24bb9d7b30c07bd872f36db360e03'}").replace("OVERLAY = dict(size=197087,sha256='2418e6d2c413e64bc860684d3f20edde223f97343dfd438d9d896d577be85a24')","OVERLAY = dict(size=202992,sha256='6ed9cf9be0afe81938e552c2623ff141fd978b8162ef61f2e5dd18b181fdd0b9')").replace('attempt02','attempt03').replace('phase368-attempt03','phase375-attempt03').replace('failed-staged-bytes/','staged-bytes/')
    require(gen==expected,'saved-map algorithm unchanged except explicit identity/path delta')
    RESULTS.append(dict(id='S08',status='PASS',host_recovery_full_byte_derivation=True,saved_pins=len(checked),map_generation_calls=0,pool_inventory=0))
    save(D/'saved-pin-readback.json',checked)
    save(D/'static-results.json',RESULTS)

def audit_hook(event,args):
    if event in ('subprocess.Popen','os.system','os.fork','socket.__new__','socket.connect'):
        AUDIT['blocked'].append(dict(event=event));raise PermissionError('no process/network')
    if event=='open' and isinstance(args[0],(str,bytes)):
        p=Path(args[0]).absolute();mode=args[1];flags=args[2]
        write=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and bool(flags & (1|2|64|512|1024)))
        allowed=p.is_relative_to(D) if write else (p.is_relative_to(SD/'SOURCE') or p.is_relative_to(D) or p.is_relative_to(Path(sys.base_prefix)/'lib'))
        if not allowed or (not write and any(x in p.parts for x in ('site-packages','dist-packages'))):
            AUDIT['blocked'].append(dict(event=event,path=str(p),write=write));raise PermissionError('outside dynamic unit scope')

def load(name,file):
    spec=importlib.util.spec_from_file_location(name,SD/'SOURCE'/file);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def run_call(label,fn,args,accept):
    before=copy.deepcopy(args)
    try:
        result=fn(*args)
    except ValueError as e:
        CALLS.append(dict(label=label,outcome='reject',exception=str(e)))
        require(not accept,'unexpected rejection '+label+': '+str(e))
    else:
        CALLS.append(dict(label=label,outcome='accept',result_type=type(result).__name__))
        require(accept,'unexpected acceptance '+label)
    require(args==before,'raw synthetic arguments mutated '+label)

def units():
    fixture=read(SD/'unit-inputs.json');sys.addaudithook(audit_hook)
    m=load('phase375_independent_real_schema','new_schema.py');old=load('phase375_independent_old_schema','old_schema.py')
    require(m.schema.MATRIX is m.MATRIX and m.schema.validate_record is m.validate_record,'export real table/function')
    require(m._base_validate_record.__globals__['MATRIX'] is m.MATRIX and m._validate_call_pairs.__globals__['MATRIX'] is m.MATRIX,'captured delegates share real table')
    base=fixture['enter'];ret=fixture['return'];identity=fixture['identity']
    calls=[('U01',m.validate_record,[base],True),('U02',m.validate_record,[ret],True)]
    for id,fn,args,accept in calls:run_call(id,fn,copy.deepcopy(args),accept);RESULTS.append(dict(id=id,status='PASS'))
    run_call('U03.module',m.validate_record,[copy.deepcopy(base)],True);run_call('U03.export',m.schema.validate_record,[copy.deepcopy(base)],True);RESULTS.append(dict(id='U03',status='PASS',calls=2))
    for role in fixture['Food_roles']:
        row=copy.deepcopy(base);row['subject']['role']=role;run_call('U04.'+role,m.validate_record,[row],True)
    RESULTS.append(dict(id='U04',status='PASS',calls=8))
    for case in fixture['mutations']:
        run_call(case['id'],m.validate_record,[copy.deepcopy(case['row'])],case['accept']);RESULTS.append(dict(id=case['id'],status='PASS'))
    nested=fixture['nested'];run_call('U22',m.validate_observation_records,[copy.deepcopy(nested),copy.deepcopy(identity)],True);RESULTS.append(dict(id='U22',status='PASS'))
    for case in fixture['observation_mutations']:
        run_call(case['id'],m.validate_observation_records,[copy.deepcopy(case['rows']),copy.deepcopy(identity)],False);RESULTS.append(dict(id=case['id'],status='PASS'))
    run_call('U27',old.validate_record,[copy.deepcopy(base)],False);RESULTS.append(dict(id='U27',status='PASS'))
    run_call('U28.old',old.validate_record,[copy.deepcopy(fixture['old_record'])],True);run_call('U28.new',m.validate_record,[copy.deepcopy(fixture['old_record'])],True);RESULTS.append(dict(id='U28',status='PASS',calls=2))

def main():
    D.mkdir(exist_ok=False)
    for row in read(SD/'source-owner.json')['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'independent source drift')
    failure=None
    try:static();units()
    except Exception as e:
        failure=dict(type=type(e).__name__,message=str(e),traceback=traceback.format_exc());(D/'stderr.txt').write_text(failure['traceback'])
    report=dict(status='PASS' if failure is None else 'FAIL',results=RESULTS,calls=CALLS,failure=failure,actual_source_obligations=sum(x['id'].startswith('S') for x in RESULTS),actual_unit_definitions=sum(x['id'].startswith('U') for x in RESULTS),top_level_schema_API_calls=len(CALLS),schema_imports=2 if CALLS else 0,synthetic_record_fixtures=True,full12positive=False,actual_inputbuilds=0,models=0,native=0,Godot=0,restore=0,pool_writes=0,audit=AUDIT)
    save(D/'report.json',report)
    save(D/'raw-joint-seal.json',dict(files=[desc(p) for p in sorted(D.iterdir()) if p.is_file()]))
    print(json.dumps(dict(status=report['status'],source=report['actual_source_obligations'],unit_definitions=report['actual_unit_definitions'],calls=len(CALLS),failure=failure)))
    if failure:raise SystemExit(1)

if __name__=='__main__':main()
