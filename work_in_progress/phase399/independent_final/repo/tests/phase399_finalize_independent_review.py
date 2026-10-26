"""Seal existing static/dynamic observations; never rerun SUT controls."""
import hashlib,json,stat
from pathlib import Path
R=Path(__file__).absolute().parents[1]
D=R/'data/phase399-independent-final';P=R/'data/phase399-independent-execution-preparation';T=R/'data/phase399-independent-dynamic-first-001'
def read(p):return json.loads(p.read_text())
def desc(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 return dict(path=str(p.relative_to(R)),size=s.st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def check(row):assert desc(R/row['path'])=={k:row[k]for k in('path','size','sha256')}
def save(p,v):
 with p.open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')

def main():
 assert not D.exists();D.mkdir()
 prep=read(R/'data/phase399-independent-repair-preparation/contract.json');bound=read(P/'execution-contract.json');dynamic=read(T/'result.json');static=read(R/'data/phase399-independent-static/review.json');api=read(R/'data/phase398-attempt05-recovery-source/api-contract.json')
 assert static['status']=='STATIC_PASS_CONDITIONAL_NINE_CALL_RELEASE'and dynamic['status']=='PASS_NINE_REAL_PUBLIC_COMPONENT_CALLS'and dynamic['failure']is None
 assert len(dynamic['results'])==dynamic['top_level_API_calls']==9 and dynamic['logical_dynamic_cases']==6
 assert api['source_freeze']==bound['source_freeze']==static['source_freeze']
 sourceowner=read(R/'data/phase398-source-handoff/owned-files.json')
 for row in sourceowner['files']:check(row)
 assert len(sourceowner['files'])==433 and sum(r['size']for r in sourceowner['files'])==7067200
 for ownerpath in('data/phase399-independent-repair-preparation/owned-files.json','data/phase399-independent-static/owned-files.json','data/phase399-independent-execution-preparation/owned-files.json'):
  for row in read(R/ownerpath)['files']:check(row)
 case_results={};aggregate={};raw_descriptors=[];calls=[]
 for result in dynamic['results']:
  assert result['status']=='PASS';rawpath=T/result['raw'];raw=read(rawpath)
  assert raw['before']==raw['after'] and raw['id']==result['id']
  case_results.setdefault(result['logical_case'],[]).append(result)
  for name,num in result['selected_delegated_SUT_calls'].items():aggregate[name]=aggregate.get(name,0)+num
  raw_descriptors.append(desc(rawpath));calls.append(dict(result,raw_record=desc(rawpath),exception=raw['exception'],elapsed_seconds=raw['elapsed_seconds']))
 aliases=[c for c in calls if c['id']in('R10-F01-symlink','R10-F01-hardlink','R20-F02-symlink','R20-F02-hardlink')]
 assert len(aliases)==4 and all(c['total_content_open_attempts']==c['target_content_open_attempts']==0 for c in aliases)
 skip={
 'R01':['Whole verify_evidence/recover positive needs real Root/baseline/retained/live targets; not executed.'],
 'R02':['Omitted-journal mutation not executed; complete-set checks retained by exact SOURCE identity.'],
 'R03':['Current-missing-target tinyFS mutation not replayed; unchanged restore_exact/regular_target safety kernel retained.'],
 'R04':['Saved metadata symlink/mutable-output negative not executed; unchanged saved-only SOURCE gates retained.'],
 'R05':['Target-kind map corruption not executed; full runtime baseline/retained proof remains Root actual gate.'],
 'R06':['Wrong74 writer-count claim negative not executed; saved helper genuinely derived78+2=80 and independent SOURCE counts retained.'],
 'R07':['Missing unselected backup negative not executed; genuine saved positive checked all76 install and73 prior backups including unselected sources.'],
 'R08':['Archive-corruption fixture/full overlay stream not executed; unchanged accepted archive functions reused by SOURCE identity.'],
 'R09':['Missing-authority source_gate negative/full positive not executed; no accepted review or Root authority fabricated.'],
 'R10':['Omitted363storage-closure descriptor mutation not executed; actual full closure statically verified.','Malformed descriptor/special/noncanonical field families were not added to original nine candidates.'],
 'R11':['No old375/384/363 safety regression replays; source byte/AST identity only.'],
 'R12':['Atomic existing-target mutation not replayed; exact unchanged writer kernel identity reused.'],
 'R13':['Changed inspector SHA negative/proc inspector execution not performed.','Ordinary descriptor helper success is not full bootstrap/reader success.'],
 'R14':['Wrong receipt status/READYtrue/74count negatives and actual successful restore receipt unavailable/not executed.'],
 'R15':['Current process inspection and process launching not executed; historical control parsing only.'],
 'R16':['No PID-reuse/current-zombie lifecycle test; only exact BOOL-to-INT metadata corruption was executed.'],
 'R17':['Old377 capsule selection negative/full380 archive stream/physical failed-tree equality not executed.'],
 'R18':['Cross-root capsule original metadata/full archive bytes not newly inspected by runtime399; SOURCE conservation only.'],
 'R19':['Actual restore80 writes, independent physical acceptance and separate Root READY all not executed.'],
 'R20':['Full ordinary source-owner bootstrap/prepare_contract positive requires actual398 Root config and successful restore receipt; not executed.','Full physical reader main, pool/baseline/retained/capsule/proc inventory not executed.']}
 cases=[]
 prior=read(R/'data/phase396-independent-static-first-001/review.json');prior_cases={x['id']:x for x in prior['cases']}
 for p in prep['cases']:
  cid=p['id'];executed=case_results.get(cid,[])
  cases.append(dict(id=cid,design_obligations=p['original_case_verbatim']['design_obligations'],obligation=p['original_case_verbatim']['obligation'],original_case_canonical_sha256=p['original_case_canonical_sha256'],static_status='PASS',static_basis='Frozen398 exact byte inverse/allowed protocol metadata plus F01/F02 consumer repairs; previous396 SOURCE evidence reused by unchanged identity.',prior396_status=prior_cases[cid]['static_status'],evidence_mode='DYNAMIC_COMPONENT_AND_SOURCE'if executed else'SOURCE_ONLY',dynamic_candidates_passed=[x['id']for x in executed],actual_top_level_API_calls=len(executed),not_executed=skip[cid]))
 assert len(cases)==20 and sum(c['actual_top_level_API_calls']for c in cases)==9
 imports=read(T/'imports.json')
 save(D/'source-post-readback.json',dict(schema='phase399-frozen-source-post-readback/1',status='ALL433_HANDOFF_LEAVES_ORDINARY_NLINK1_SHA_UNCHANGED',owner=desc(R/'data/phase398-source-handoff/owned-files.json'),files=433,bytes=7067200,map=api['map'],input_pins=api['input_pins'],readback_only_no_reexecution=True))
 save(D/'observed-calls.json',dict(schema='phase399-observed-public-controls/1',calls=calls,top_level_API_calls=9,accept=4,reject=5,alias_negatives_content_open_attempts=0,all_python_profile_call_events=sum(aggregate.values()),profile_note='Call events include generator reentries and nested predicates, not additional API cases or tests.',profile_by_code_function=aggregate,raw_records_are_pre_assertion_snapshots=True,result_files_record_completed_assertions=True,imports=imports))
 review=dict(schema='phase399-independent-complete-recovery-source-review/1',status=api['source_review_status'],source_freeze=api['source_freeze'],source_API=desc(R/'data/phase398-attempt05-recovery-source/api-contract.json'),source_owner=desc(R/'data/phase398-attempt05-recovery-source/source-owner.json'),reader_source_owner=desc(R/api['reader_source_owner']),map=api['map'],input_pins=api['input_pins'],static_review=desc(R/'data/phase399-independent-static/review.json'),static_checker_first_failure=desc(R/'data/phase399-independent-static/first-failure.json'),static_checker_resolution=desc(R/'data/phase399-independent-static/static-finding-resolution.json'),sealed_execution_owner=desc(P/'owned-files.json'),dynamic_result=desc(T/'result.json'),observed_calls=desc(D/'observed-calls.json'),source_post_readback=desc(D/'source-post-readback.json'),cases=cases,logical_cases=20,logical_limit=24,original_design_obligations=12,static_pass=20,dynamic_logical_cases=6,SOURCE_only_logical_cases=14,top_level_API_calls=9,accept=4,reject=5,SUT_direct_module_loads=4,SUT_module_instances=9,distinct_SUT_source_identities=7,pure_imports_not_main_or_operation=True,F01='Three real calls: ordinary accepts with read; symlink and hardlink reject with0 content opens.',F02='Two full exact-byte consumer mirror prepare_contract calls: symlink/hardlink owner rejected with0 content opens including genuine historical383 syntax arguments. No full bootstrap positive.',genuine_saved_association='One actual395 saved helper call through398 binding matches entire524-pin ledger and complete-install summary78project+7dirs+2staged/writer80;76install+73prior/routes73+1+4.',historical_process_controls='One genuine actual05 record positive plus one local parse_only BOOLtrue->INT1 rejection; no /proc.',native=0,models=0,Godot=0,Game=0,FrameDriver=0,RNG=0,inputbuild=0,projection=0,actual_pool=0,baseline_inventory=0,proc_inspection=0,restore=0,READY=0,map_generation=0,source_gate_calls=0,verify_evidence_calls=0,recover_calls=0,reader_main_calls=0,process_launches=0,whole_prepare_positive=False,whole_physical_positive=False,King_admission=False,remaining_gates=['Genuine Root398 restore authorization','Actual complete evidence/current target gates and80 target writes while original failed state remains','Real successful restore receipt and separately released independent398 full physical readback','Separate Root READY action','Fresh native budget/fixed06 release; King/model admission still open'],first_failure_policy='No dynamic failure and no retries. First static checker omitted the equal-byte inspector-origin provenance path; script/error preserved and narrowly closed in same static frame without SUT changes or rerunning original script.',no_more_writes=True)
 save(D/'review.json',review)
 doc=R/'docs/phase399_independent_frozen398_acceptance_result.md'
 with doc.open('x')as f:f.write('''# 399 independent frozen398 SOURCE acceptance

398 SOURCE is accepted with Root operations pending. All20 original logical obligations have static evidence; six also have bounded dynamic evidence and14 remain SOURCE-only. Exactly nine first public API calls passed: four accepts and five expected rejects. No dynamic failure or retry occurred.

F01 ordinary file accepts after one content open; its symlink and hardlink inputs reject with zero opens. F02 uses the complete unchanged reader in owned mirrors with natural paths: both owner alias forms reject before any content open, including zero reads of genuine historical383 CLI arguments. This proves the early consumer rejection only; full prepare_contract success is still unexecuted.

The real saved-only helper matched all524 input pins and the complete78/7/2/80 association, including76 install backups,73 prior patches and73+1+4 target routes. Actual05 process records passed their metadata helper; changing parse_only from BOOLtrue to INT1 was rejected. No current process inspection occurred.

All433 original398 handoff leaves /7067200 bytes were independently checked before and after. Old11 recovery and10 reader safety functions remain exact. Nine module instances were imported (four direct loads, five transitive); no SUT main or operation ran. The first static checker error about an equal-byte inspector-origin path is preserved with its narrow resolution.

Actual pool/baseline inventory, restore, independent physical main, READY, native/Godot, model/FrameDriver/RNG and input/projection calls are zero. A genuine Root restore, actual successful receipt, separately released full independent readback and READY remain required. King is not admitted. The JSON review records every unexecuted branch; no metadata-only or component result is presented as physical recovery success.
''')
 #All ordinary artifacts are owned; retained alias nodes are explicitly separate.
 roots=[R/'data/phase399-independent-repair-preparation',R/'data/phase399-independent-static',P,T,D]
 leaves=set();aliases=[]
 for root in roots:
  for p in root.rglob('*'):
   s=p.lstat()
   if stat.S_ISREG(s.st_mode)and s.st_nlink==1:leaves.add(p)
   elif stat.S_ISLNK(s.st_mode)or(stat.S_ISREG(s.st_mode)and s.st_nlink!=1):aliases.append(dict(path=str(p.relative_to(R)),kind='symlink'if stat.S_ISLNK(s.st_mode)else'hardlink',nlink=s.st_nlink))
 leaves.update(R.glob('tests/phase399*.py'));leaves.update(R.glob('docs/phase399*.md'))
 rows=[desc(p)for p in sorted(leaves)]
 save(D/'owned-files.json',dict(schema='phase399-independent-final-owner/1',files=rows,leaf_count=len(rows),byte_count=sum(r['size']for r in rows),excluded_physical_alias_nodes=aliases,alias_evidence_ledger=desc(P/'physical-fixture-ledger.json'),no_more_writes=True))
 for row in rows:check(row)
 print(json.dumps(dict(status=review['status'],review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),files=len(rows),bytes=sum(r['size']for r in rows),aliases=len(aliases),logical=20,dynamic=6,SOURCE_only=14,top_API=9,accept=4,reject=5,native=0,models=0)))
if __name__=='__main__':main()
