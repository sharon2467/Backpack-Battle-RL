"""Execute presealed bounded pure schema controls; no simulation or actual source bundle."""
import copy
from collections import Counter
import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import sysconfig
import types

R=Path(__file__).resolve().parents[1]
D=R/'data/phase360-independent-schema-review'

def desc(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def main():
    contract=json.loads((D/'execution-contract.json').read_text())
    for row in contract['files']:assert desc(R/row['path'])==row
    owner_pin=desc(D/'source-owner.json')
    cases=json.loads((D/'cases.json').read_text());assert len(cases)==56
    out=D/'controls-first-001';out.mkdir(exist_ok=False)
    allowed={str((R/row['path']).resolve()) for row in contract['files']}|{str((D/'execution-contract.json').resolve()),str((D/'source-owner.json').resolve())}
    stdlib=Path(sysconfig.get_path('stdlib')).resolve();root=out.resolve();audit=dict(reads=[],writes=[],blocked=[])
    def below(p,r):return p==r or r in p.parents
    def hook(event,args):
        if event=='open':
            if isinstance(args[0],int):return
            p=Path(os.fsdecode(args[0])).absolute().resolve();mode,flags=args[1:3]
            writing=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)) if isinstance(flags,int) else bool(mode and any(c in mode for c in 'wax+'))
            ok=below(p,root) if writing else str(p) in allowed or below(p,root) or (below(p,stdlib) and not {'site-packages','dist-packages'}&set(p.parts))
            if not ok:
                audit['blocked'].append(dict(event=event,path=str(p),writing=writing));raise PermissionError('phase360 source file boundary')
            audit['writes' if writing else 'reads'].append(str(p))
        elif event.startswith('socket.') or event in ('subprocess.Popen','os.system','os.posix_spawn','os.posix_spawnp','os.fork','os.exec'):
            audit['blocked'].append(dict(event=event));raise PermissionError('phase360 network/process boundary')
    sys.addaudithook(hook)
    p=D/'SOURCE/schema.py';module=types.ModuleType('__independent360_real_schema__');module.__file__=str(p);sys.modules[module.__name__]=module
    exec(compile(p.read_bytes(),str(p),'exec'),module.__dict__)
    plan=json.loads((D/'SOURCE/fixed-slot-map.json').read_text());source_contract=json.loads((D/'SOURCE/source-contract.json').read_text())
    baseline=next(c['data'] for c in cases if c['label']=='local39-SOURCE-shape-and-shared-descriptors')
    calls=Counter();results=[]
    def invoke(name,*args):calls[name]+=1;return getattr(module,name)(*args)
    with (out/'journal.jsonl').open('x') as journal:
        for case in cases:
            data=copy.deepcopy(case['data']);op=case['operation'];before=canonical(data);original=copy.deepcopy(data)
            detail={}
            try:
                if op=='RECORD':value=invoke('validate_record',data)
                elif op=='OBSERVATIONS':value=invoke('validate_observation_records',data,dict(native_to_role={},role_to_native={}))
                elif op=='LOCAL':
                    raw=canonical(data)+b'\n';raw_before=bytes(raw);value=invoke('validate_binding_carrier',raw,plan);assert raw==raw_before
                    if value is data:raise AssertionError('parser returned caller object')
                elif op=='RAW':value=invoke('validate_binding_carrier',data.encode(),plan)
                elif op in ('JOIN','JOIN_CONTRACT'):
                    sc=copy.deepcopy(source_contract)
                    if op=='JOIN_CONTRACT':sc['evidence_policy']='CALLER_VERIFIED'
                    b=copy.deepcopy(baseline);b_before=canonical(b);sc_before=canonical(sc)
                    value=invoke('join_binding_provenance',data,b,sc)
                    assert canonical(b)==b_before and canonical(sc)==sc_before
                    assert value['input_bundle_created'] is False and value['native_admitted'] is False and type(value['model_calls']) is int and value['model_calls']==0
                    assert value['input_order']['O'][12]=='O:13' and 'O:12' not in value['evidence_refs'] and len(value['evidence_refs'])==39
                    assert len(value['role_to_native'])==80
                    detail['relation_evidence_refs']=39;detail['whole11_positive']=False
                elif op=='FULL_REFUSAL':
                    raw={name:(canonical(rows)+b'\n' if not name.endswith('.jsonl') else b''.join(canonical(row)+b'\n' for row in rows)) for name,rows in data.items()}
                    raw_before=copy.deepcopy(raw);value=invoke('validate_sources_with_binding',raw,canonical(baseline)+b'\n',source_contract);assert raw==raw_before
                else:raise AssertionError('unsealed operation')
            except (ValueError,TypeError,KeyError,UnicodeError) as exc:
                accepted=False;detail.update(type=type(exc).__name__,message=str(exc))
            except Exception as exc:
                accepted=None;detail.update(checker_error=dict(type=type(exc).__name__,message=str(exc)))
            else:
                accepted=True;detail['return_type']=type(value).__name__
            immutable=canonical(data)==before and data==original
            row=dict(id=case['id'],label=case['label'],expected=case['expected'],accepted=accepted,unchanged=immutable,pass_=immutable and accepted==(case['expected']=='accept'),detail=detail)
            results.append(row);journal.write(json.dumps(row,sort_keys=True)+'\n');journal.flush()
    failures=[r for r in results if not r['pass_']]
    report=dict(schema='phase360-independent-pure-schema-controls/1',status='FINITE_BINDING_SCHEMA_CONTROLS_PASS' if not failures else 'BLOCKED_SOURCE_OR_CONTROL_COUNTEREXAMPLE',unique_cases=len(cases),executed=len(results),accepted=sum(r['accepted'] is True for r in results),rejected=sum(r['accepted'] is False for r in results),controls=results,failures=failures,top_level_calls=dict(calls),top_level_call_total=sum(calls.values()),recursive_internal_calls='NOT_COUNTED',pure_schema_module_imports=1,synthetic_only=True,actual_native_source_evidence=False,synthetic_relation_join_positive=any(r['label']=='synthetic-relation-join-positive-immutable' and r['pass_'] for r in results),full_eleven_or_twelve_source_positive=False,candidate_imports=0,RNG_constructions=0,Engine_constructions=0,models=0,input_bundle_builds=0,native=0,capture_reads=0,expected_file_reads=0,admission='356_UNCONDITIONAL_CLOSED')
    with (out/'report.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
    files=[desc(out/n) for n in ('journal.jsonl','report.json')]
    with (out/'open-audit.json').open('x') as f:
        json.dump(dict(schema='phase360-independent-source-audit/1',**audit,trusted_bootstrap='Script/stdlib and manifest metadata pinned before audit; real schema loaded from manifested source after audit.',stdlib=str(stdlib),recording_cut='Opening this audit file; later only own output readback and joint seal/stdout. Hook remains active.',no_explicit_attack_test_claim=True),f,indent=2,sort_keys=True);f.write('\n')
    files.append(desc(out/'open-audit.json'))
    with (out/'joint-seal.json').open('x') as f:json.dump(dict(schema='phase360-independent-schema-jointseal/1',files=files,source_owner=owner_pin),f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(dict(status=report['status'],executed=len(results),failures=[r['label'] for r in failures],calls=sum(calls.values()),blocked=len(audit['blocked']))))
if __name__=='__main__':main()
