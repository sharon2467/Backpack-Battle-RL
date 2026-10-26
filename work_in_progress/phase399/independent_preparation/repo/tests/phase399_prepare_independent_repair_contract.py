"""Seal preparation metadata only; does not read398 or import/call any SUT."""
import hashlib
import json
from pathlib import Path
import stat
R=Path(__file__).absolute().parents[1]
D=R/'data/phase399-independent-repair-preparation'
consumed=[]

def desc(p):
 s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1 and not any(q.is_symlink()for q in(p,*p.parents))
 raw=p.read_bytes();t=p.lstat()
 assert(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)==(t.st_dev,t.st_ino,t.st_size,t.st_mtime_ns,t.st_ctime_ns)
 return dict(path=str(p.relative_to(R)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def checked(path,size,sha):
 row=dict(path=path,size=size,sha256=sha);assert desc(R/path)==row;consumed.append(row);return row

def load(row):return json.loads((R/row['path']).read_text())
def save(p,v):
 with p.open('x')as f:f.write(json.dumps(v,indent=2,sort_keys=True,allow_nan=False)+'\n')

def main():
 assert not D.exists()
 refs={}
 for key,path,size,sha in [
 ('original_contract','data/phase396-independent-recovery-preparation/contract.json',23068,'bde88c41327e48c0538d43bc43d742a7ad8296abc2787861046378accf819bdd'),
 ('original_preparation_owner','data/phase396-independent-recovery-preparation/owned-files.json',998,'2225f29f886c94cc20bebbdb1ca84b6415f9f4ebe0d3fa3a52b4f0afd03531e1'),
 ('blocked_review','data/phase396-independent-static-first-001/review.json',17867,'a3125598a959000943079e2c3b37c79bae66db07f83cfb89fff07dcd8df3d46f'),
 ('blocked_owner','data/phase396-independent-static-first-001/owned-files.json',3746,'11fe3c006e13b4fe5e4fa18fa5b6b07e2b9b38df43d5b23490e02623a695fd5d'),
 ('findings','data/phase396-independent-static-first-001/static-findings.json',5431,'af1313061f1ad8a69216033251913677feffa33cf089c56efcf1330f803ebd51'),
 ('old_source_identity_evidence','data/phase396-independent-static-first-001/evidence.json',21396,'b60d92082e4b7b04f3dc8820dbd56b984c6de23f29ddf78c27587656188cb8b5'),
 ('immutable395_map','data/phase395-attempt05-recovery-source/map/restore-map.json',68985,'b9fae3743994c3f5a3b3e590a4b849b914cf0422343fd42738e4d639b6b13dc1'),
 ('immutable395_pins','data/phase395-attempt05-recovery-source/map/source-input-pins.json',102475,'b1eae13cfcc3094a38c965cedc8785226a92c54ed9b87e86e6487509b1081510')]:
  refs[key]=checked(path,size,sha)
 old=load(refs['original_contract']);review=load(refs['blocked_review']);findings=load(refs['findings']);identity=load(refs['old_source_identity_evidence'])
 assert len(old['cases'])==20 and old['logical_limit']==24 and review['static_source_pass']==18 and review['static_blocked']==2
 assert [f['id']for f in findings['findings']]==['F01','F02']
 oldmap=load(refs['immutable395_map']);pins=load(refs['immutable395_pins'])
 assert len(pins['files'])==524 and len(oldmap['file_differences'])==78 and len(oldmap['directory_differences'])==7 and len(oldmap['staged_files'])==2
 for row in refs.values():
  if row['path'] in (refs['original_preparation_owner']['path'],refs['blocked_owner']['path']):continue
  source_owner=load(refs['original_preparation_owner'] if row['path']==refs['original_contract']['path'] else refs['blocked_owner'])
  if row['path'].startswith('data/phase396-'):assert row in source_owner['files']
 def candidate(cid,case,kind,input_,expect,condition):
  return dict(id=cid,original_case=case,kind=kind,input=input_,expected=expect,conditional_release=condition,actual398_module=None,actual398_function=None,actual398_signature=None,actual_descriptor=None,actual_status='PLANNED_NOT_EXECUTED',actual_top_level_calls=0)
 candidates=[
 candidate('R10-F01-ordinary','R10','REAL_LOCAL_SOURCE_LEAF_POSITIVE','Owned existing ordinary nlink1 file with known small bytes and its actually measured descriptor.','Actual repaired public leaf helper accepts matching identity and observer sees target content read; file metadata/bytes unchanged.','Frozen actual helper is callable with a local root/descriptor and does not require production authority; full import closure independently pinned.'),
 candidate('R10-F01-symlink','R10','REAL_LOCAL_SOURCE_LEAF_NEGATIVE','Owned symlink path to separate owned small ordinary referent with same measured content descriptor.','Actual SUT rejects physical alias before any content-open of operand or referent; no file writes.','Same real public helper; observer records but does not prevent targeted reads. No production alias.'),
 candidate('R10-F01-hardlink','R10','REAL_LOCAL_SOURCE_LEAF_NEGATIVE','Owned hardlinked path and owned companion, measured nlink2, same known bytes and descriptor.','Actual SUT rejects nlink2 before content-open of either alias; no file writes.','Same real public helper and complete alias ledger. No production inode linked.'),
 candidate('R20-F02-symlink','R20','REAL_BOOTSTRAP_EARLY_NEGATIVE_IF_REACHABLE','Actual reader own-owner operand represented by owned symlink to owned exact measured bytes; real source mirror only if naturally supported without constant changes.','Actual bootstrap rejects at physical owner consumer before any owner content read; no downstream authority read, proc or inventory.','Frozen public interface permits reaching this first gate with genuine available arguments and actual owner/source identities. If not, SOURCE-only; no fake Root/review/receipt.'),
 candidate('R20-F02-hardlink','R20','REAL_BOOTSTRAP_EARLY_NEGATIVE_IF_REACHABLE','Same bounded actual bootstrap operand as owned nlink2 alias, without linking production files.','Actual bootstrap rejects before owner bytes are read; no downstream authority read, proc or inventory.','Same genuine first-gate reachability condition; cannot manufacture a full prepare_contract positive.'),
 candidate('R13-owner-descriptor-ordinary','R13','REAL_DESCRIPTOR_HELPER_POSITIVE_ONLY','Owned ordinary nlink1 metadata leaf with actual measured descriptor passed to the real frozen strict descriptor helper.','Helper accepts exact ordinary bytes and reports observed reads; explicitly not a prepare_contract/owner-authority success.','Actual helper exposed without production authority; static consumer edge to bootstrap separately proven. At most one ordinary helper call.'),
 candidate('R01-saved-complete','R01','GENUINE_SAVED_ONLY_COMPONENT_POSITIVE','Actual immutable failed05/old026 saved roots and exact frozen allowset corresponding to preserved395524pins.','Real saved-only helper returns complete association/ledger and derived78+2 writer80,76install/73prior/routes73+1+4.','Root postfreeze release covers genuine saved reads; function has no baseline/pool/proc path and no capture business decode. Never call generator or whole verify_evidence.'),
 candidate('R15-actual-controls','R15','GENUINE_SAVED_PROCESS_CONTROL_COMPONENT_POSITIVE','The two actual descriptor-pinned05 parse/native process-control files, explicit readonly saved root.','Real helper reports parse BOOLtrue/oracleINT0 and native BOOLfalse/oracleINT1, actual exits/PGIDs/zombies separately. No process inspection.','Actual public helper consumes metadata only; exact original controls/read allowset sealed before call.'),
 candidate('R16-parse-bool-int','R16','REAL_PROCESS_CONTROL_COMPONENT_NEGATIVE','Owned exact copies of the two controls; mutate only parse_only from JSON true to integer1 and use the real resulting file descriptor.','Real helper rejects strict-type mismatch; no /proc, process operation, Root authority or record relabeling.','Component contract is local metadata only; actual helper directly called, no validator replacement or module constant changes.')]
 prior={row['id']:row for row in review['cases']};cases=[]
 for row in old['cases']:
  planned=[c['id']for c in candidates if c['original_case']==row['id']]
  cases.append(dict(id=row['id'],original_case_verbatim=row,original_case_canonical_sha256=hashlib.sha256(json.dumps(row,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),prior396_static_status=prior[row['id']]['static_status'],reuse='Verify frozen successor identity/diff; do not replay prior review or claim old dynamic success',actual398_binding='UNBOUND_UNTIL_FROZEN_SOURCE_REVIEW',planned_candidates=planned,next_evidence_mode='STATIC_FIRST_THEN_CONDITIONAL_COMPONENT'if planned else 'SOURCE_IDENTITY_AND_DIFF_ONLY',actual_status='PREPARED_NOT_EXECUTED'))
 assert len(candidates)==9 and len(cases)==20 and set(x for row in cases for x in row['original_case_verbatim']['design_obligations'])==set(range(1,13))
 counters={k:0 for k in ('SUT_imports','SUT_calls','dynamic_cases','top_level_API_calls','new398_source_reads','Godot','Game','native','models','FrameDriver','RNG','inputbuild','projection','actual_pool','baseline_inventory','proc_inspection','restore','READY','map_generation','external_saved_payload_reads','fixtures_created','SUT_runners_generated','archived_scripts_rerun')}
 D.mkdir()
 evidence=dict(schema='phase399-preparation-identity-evidence/1',verified_repository_metadata_descriptors=consumed,source_identity_basis=refs['old_source_identity_evidence'],prior_recovery_conserved_functions=identity['inverse_checks'][0]['conserved'],prior_reader_conserved_functions=identity['inverse_checks'][2]['conserved'],immutable_map_pin_observations=dict(project_file_rows=78,directory_rows=7,staged_file_rows=2,saved_pin_rows=524,external_payloads_read=False),old_checks_reexecuted=False,new398_content_read=False,actual_counts=counters)
 save(D/'source-evidence.json',evidence)
 contract=dict(schema='phase399-independent-repair-preparation-contract/1',status='PREPARED_ONLY_WAIT_FROZEN398_BINDING',original396=refs,source_evidence=desc(D/'source-evidence.json'),logical_prepared=20,logical_limit=24,original_design_obligations=12,new_logical_cases=0,candidate_logical_cases=6,maximum_direct_API_invocations=9,cases=cases,dynamic_candidates=candidates,future_bindings_pending=['Actual398 source owner/freeze/root schema/required independent SOURCE and physical statuses','Actual recovery and reader module paths/signatures and full transitive imports','Genuine Root execution release and allowed saved/component inputs','Concrete fixture/source mirrors, measured descriptors, expected errors and I/O observer read allowset','Actual own-owner first-gate reachability without fabricated production authority'],first_failure_policy='Static block prevents all runtime; first dynamic or harness failure preserves exact original script/input/metadata/event trace and stops batch, no repair or retry.',observer_policy=dict(target_reads='Observe open attempts on operand and every owned alias referent; do not block targeted reads or substitute SUT rejection.',window='Separate setup/sealing reads from real call window.',mutations='No mocked validator, modified SUT constant, extracted function, copied implementation, fake approval or fake successful receipt.',unsafe_fixture_preservation='Explicit symlink/hardlink physical ledger and ordinary byte snapshots, not an ordinary-owner claim for alias nodes.'),real_positive_not_planned=['Full source_gate approval','Full prepare_contract success','Whole verify_evidence/recover positive','Actual physical pool readback','READY'],actual_counts=counters,no_more_writes=True)
 save(D/'contract.json',contract)
 save(D/'preparation-result.json',dict(schema='phase399-independent-preparation-result/1',status=contract['status'],contract=desc(D/'contract.json'),source_evidence=desc(D/'source-evidence.json'),logical_cases=20,original_design_obligations=12,maximum_future_direct_API_invocations=9,actual_counts=counters,runner='No executable SUT runner authored before frozen API; stdlib preparation sealer only.',next_gate='Root readback of this owner, then frozen398 binding and static-first release. No self-initiated SOURCE reading or execution.',no_more_writes=True))
 leaves=sorted(p for p in D.iterdir()if p.is_file())+[R/'docs/phase399_independent_recovery_repair_preparation_spec.md',Path(__file__).absolute()]
 rows=[desc(p)for p in sorted(leaves)]
 save(D/'owned-files.json',dict(schema='phase399-independent-preparation-owner/1',files=rows,leaf_count=len(rows),byte_count=sum(r['size']for r in rows),no_more_writes=True))
 for row in rows:assert desc(R/row['path'])==row
 print(json.dumps(dict(status=contract['status'],owner=desc(D/'owned-files.json'),contract=desc(D/'contract.json'),leaves=len(rows),bytes=sum(r['size']for r in rows),SUT_calls=0,new398_reads=0)))
if __name__=='__main__':main()
