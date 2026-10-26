import json,pathlib
r=pathlib.Path('/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06')
for n in ['parse-process-result.json','native-process-result.json','source-partition.json','capture-relocation.json','pool-provenance.json','readonly-plan.json','host_manifest.json','compaction/bundle-manifest.json','compaction/retained-evidence.json','compaction/driver-files.json']:
 d=json.loads((r/'output'/n).read_text()); print('\n',n, 'keys',list(d))
 for k,v in d.items():
  if not isinstance(v,(dict,list)): print(k,repr(v))
  elif k in ['cleanup','terminal_control_proof']: print(k,str(v)[:2200])
  else: print(k,'shape',len(v),'sample',str(next(iter(v.items())) if isinstance(v,dict) and v else v[:1])[:350])
p=pathlib.Path('data/phase402-independent-attempt06-preparation/contract.json');d=json.loads(p.read_text());print('\nCONTRACT',str(d['source_driver_expected_descriptors'])[:600]);print('SOURCEEVIDENCE',d['source_evidence']);print('CASES',d['cases'])
