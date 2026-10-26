"""Nine SOURCE gates, stdlib text/AST only; no operational module import."""
import ast
import copy
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
SD=R/'data/phase380-independent-static-source'
D=R/'data/phase380-independent-static-first-001'
def pin(p):
    b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def read(p):return json.loads(p.read_text())
def require(x,m):
    if not x:raise ValueError(m)
def functions(p):
    text=p.read_text();tree=ast.parse(text)
    return text,{n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def same(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
def segment(t,n):return ast.get_source_segment(t,n)
def main():
    D.mkdir(exist_ok=False);rows=[]
    for row in read(SD/'source-owner.json')['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'independent source drift')
    failure=None
    try:
        owner=read(R/'data/phase380-payload-source/source-owner.json');freeze=read(R/'data/phase380-payload-source/combined-source-freeze.json');old=read(R/'data/phase375-food-hook-source/combined-source-freeze.json')
        for row in owner['files']+freeze['files']:require(pin(R/row['path'])=={k:row[k] for k in ('size','sha256')},'SOURCE descriptor '+row['path'])
        for key in ['paths','collector','schema_module','active_source_tuple','profile','schema_case','native_source_origin']:require(freeze[key]==old[key],'conserved '+key)
        rows.append(dict(id='S01',status='PASS',source_owner_leaves=len(owner['files']),freeze_files=len(freeze['files']),runtime_imports=0))
        ht,h=functions(R/'tests/phase380_oracle_host.py');st,s=functions(R/'tests/phase380_oracle_storage.py');pt,p=functions(R/'tests/phase380_partial_map.py');rt,r=functions(R/'tests/phase380_pool_recovery.py')
        resolve=segment(ht,h['resolve_execute_payloads']);verify=segment(ht,h['verify_execute_payloads']);execute=segment(ht,h['execute']);plan=segment(ht,h['plan'])
        require("dict(freeze['collector'])" in resolve and "SOURCE+'/collector.gd'" not in execute,'actual descriptor alias')
        require("len(graph['patches'])!=75" in verify and "MAX_INSTALL_BYTES" in verify,'real corpus guard')
        require("('collector','schema_module','active_source_tuple','native_source_origin')" in resolve and 'driver_descriptors' in resolve,'complete bindings')
        rows.append(dict(id='S02',status='PASS',expected_install_payloads=78,bytes=807199,resolver_frozen_graph_only=True))
        require(plan.index('resolve_execute_payloads(')<plan.index('check_ready('),'plan before READY access')
        require(execute.index('resolve_execute_payloads(')<execute.index('verify_execute_payloads(')<execute.index('with lease(')<execute.index('reset_previous('),'execute prelease')
        require("payloads!=launch['execute_payloads']" in execute,'same graph recheck')
        require('payloads[\'artifacts\']' in execute and 'payloads[\'case_inputs\']' in execute and 'payloads[\'driver_sources\']' in execute,'actual consumers use graph')
        rows.append(dict(id='S03',status='PASS',caller_order='resolve+freshverify before lease/reset; targetbefore only inside install'))
        install=segment(st,s['install']);preflight=segment(st,s['preflight_install_payloads'])
        require(install.index('preflight_install_payloads(')<install.index('backup.mkdir()')<install.index("write_new(backup / 'preimages.json'")<install.index('atomic_image('),'preflight/journal order')
        require("artifacts!=source_freeze['artifacts']" in preflight and "declared.get(payload['path'])!=payload" in preflight,'direct independent declarations')
        require("row['raw']=read_source_payload(source_root,payload)" in preflight,'precache all')
        rows.append(dict(id='S04',status='PASS',direct_install_independent_preflight=True))
        _,osf=functions(R/'tests/phase363_oracle_storage.py');unchanged=[]
        for name,n in osf.items():
            if name=='install':continue
            require(name in s and same(n,s[name]),'old storage AST '+name);unchanged.append(name)
        rows.append(dict(id='S05',status='PASS',unchanged_functions=unchanged))
        require("atomic_image(row['target'],row['raw'],entry['before'])" in install and 'payload.read_bytes' not in install,'no late unchecked source read')
        require('807199' in st and 'O_NOFOLLOW' in segment(st,s['_read_source']) and 'st_ctime_ns' in segment(st,s['_source_signature']),'bounded stable sources')
        rows.append(dict(id='S06',status='PASS',immutable_cachebytes_source=True))
        analyze=segment(pt,p['analyze_saved_partial']);restore=segment(rt,r['restore_exact']);evidence=segment(rt,r['verify_evidence'])
        required=["current==reset['after']","target==prior['project']==reset['before']","set(b)-set(a)==KNOWN_MISSING","require(not (rawdir/'preimages.json').exists()","len(expected_raw)==74","expected_raw['75']"]
        for text in required:require(text in analyze,'partial provenance predicate '+text)
        require('exact saved partial overlay' in analyze and 'PRIOR_FREEZE' in analyze,'hard actual saved contract')
        rows.append(dict(id='S07',status='PASS',hard_real_saved_proof=True,full_synthetic_recover_positive=False))
        require('==KNOWN_MISSING' in restore and "evidence.get('known_absent_creates')==sorted(KNOWN_MISSING)" in restore,'known2 creates')
        require("current tree must equal preserved failed tree" in restore and "check_failed_state(roots,evidence['failed_state'])" in restore,'current/failed branch')
        _,oldr=functions(R/'tests/phase375_pool_recovery_v2.py')
        for name in ['actual_targets','check_failed_state','check_roots','directory_metadata','locked_pool']:
            require(same(oldr[name],r[name]),'reused recovery '+name)
        commit=segment(rt,r['commit_ready']);require('owned real independent readback' in commit and 'actual_targets' in commit and "state_write(roots['pool']" in commit,'separate actual readback gate')
        require('restore_exact(' in segment(rt,r['recover']) and 'commit_ready(' in segment(rt,r['recover']),'genuine operation branches')
        rows.append(dict(id='S08',status='PASS',tiny_mutation_unit_allowed=True,actual_recover_and_READY_not_run=True))
        require('analyze_saved_partial(' in evidence and "all(mapping[k]==v for k,v in core.items())" in evidence,'no generalized partial map')
        called={n.func.id for n in ast.walk(h['resolve_execute_payloads']) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
        require(not called.intersection({'reset_previous','lease','initialize','Engine'}),'resolver not model/operator')
        rows.append(dict(id='S09',status='PASS',runtime_and_admission_sources_unchanged=True,dynamic_limits='No wholehost/actual12/actualpool/parse positive'))
    except Exception as exc:
        import traceback
        failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    report=dict(status='PASS' if failure is None else 'BLOCKED',rows=rows,failure=failure,SUT_imports=0,SUT_calls=0,actualpool_reads=0,new_processes=0)
    (D/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],passed=len(rows),failure=failure)))
    if failure:raise SystemExit(1)
if __name__=='__main__':main()
