"""New370 host/recovery delta units and saved-map reads, never livepool operations."""
from pathlib import Path
import copy,hashlib,json,os,sys,traceback,types,zipfile

R=Path(__file__).resolve().parents[1];D=R/'data/phase370-independent-execution';OUT=D/'helpers-first-001'
COUNTS=dict(SOURCE_definition_imports=0,host_calls=0,recovery_calls=0,saved_map_reads=0,synthetic_restore_calls=0,
 actual_pool_reads=0,actual_pool_mutations=0,Godot=0,processes=0,models=0,native=0,projection=0)
def pin(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return dict(size=p.stat().st_size,sha256=h.hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def module(name,p):
 m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m;exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);COUNTS['SOURCE_definition_imports']+=1;return m
def reject(fn):
 try:fn()
 except (ValueError,FileNotFoundError,zipfile.BadZipFile) as e:return dict(type=type(e).__name__,message=str(e))
 raise AssertionError('unexpected acceptance')
def rec_call(fn,*args):COUNTS['recovery_calls']+=1;return fn(*args)

def main():
 contract=read(D/'helper-execution-contract.json')
 for row in contract['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
 assert read(D/'language-first-001/interpretation.json')['status']=='PASS'
 OUT.mkdir();cases=[];failure=None
 def record(label,value):
  row=dict(label=label,status='PASS',evidence=value);save(OUT/('case-%02d.json'%(len(cases)+1)),row);cases.append(row)
 try:
  c=module('native_run_compaction',D/'SOURCE/compaction.py');module('phase363_oracle_storage',D/'SOURCE/storage.py');module('phase363_oracle_process',D/'SOURCE/process.py')
  host=module('phase370_oracle_host',D/'SOURCE/host370.py');rec=module('__independent370_recovery__',D/'SOURCE/recovery370.py')
  fixture=module('__independent370_neutral_fixture__',D/'SOURCE/tiny-evidence.py')
  for label in ('OBSERVER_ONLY','BOTH','OBSERVER_TOO_LARGE','OBSERVER_BAD_SCHEMA'):
   run=OUT/label;cap=run/'output/capture';cap.mkdir(parents=True)
   observer=dict(schema='observer7-failure/1',code='UNIT_OBSERVER_SOURCE_FAIL',capture_complete=False)
   if label=='OBSERVER_BAD_SCHEMA':observer['schema']='UNIT_WRONG'
   if label=='OBSERVER_TOO_LARGE':observer['padding']='x'*4100
   save(cap/'observer7_failure.json',observer)
   if label=='BOTH':save(cap/'collector-first-failure.json',dict(code='UNIT_COLLECTOR_SOURCE_FAIL',capture_complete=False))
   (cap/'opaque-unit.bin').write_bytes(b'\xff\x00NOT_JSON_NOT_BUSINESS_EVIDENCE')
   COUNTS['host_calls']+=1;value=host.collect_capture_metadata(run,dict(exit_code=2,abort_reason=None,timed_out=False))
   expected='collector_control_failure' if label=='BOTH' else 'invalid_observer_control_failure' if label in ('OBSERVER_TOO_LARGE','OBSERVER_BAD_SCHEMA') else 'observer_control_failure'
   assert value['primary_failure']['kind']==expected and value['capture_complete'] is False
   assert 'observer7_failure.json' in value['control_failures_opaque'] and 'observer7_failure.json' not in value['expected_observations_opaque']
   assert 'opaque-unit.bin' in value['expected_observations_opaque'] and value['expected_semantics_read'] is False
   if label=='BOTH':assert any(row.get('precedence')=='COLLECTOR_IF_PRESENT_NO_TIME_ORDER_INFERRED' for row in value['secondary_errors'])
   record(label,dict(scope='SYNTHETIC_CONTROL_DTO_NOT_NATIVE_CAPTURE',partition=value))
  f=fixture.create(OUT/'neutral',c,rec,save,pin);roots=f['roots'];mapping=f['mapping'];pins=f['pins']
  mapping['schema']='phase368-attempt02-exact-restore-source-map/1'
  receipt=roots['failed_run']/'output/failed-pool-preservation/receipt.json';old=read(receipt)
  value=dict(schema='attempt02-failed-pool-preservation/1',status='PRESERVED_NOT_RESTORED',restore=0,
   overlay_sha256=old['zip_sha256'],overlay_bytes=old['zip_bytes'],synthetic_scope='NEUTRAL_FS_ONLY_NOT_ACTUAL_ATTEMPT02')
  receipt.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
  mapping['failed_preservation'].update(pin(receipt));pins['files'][0]=copy.deepcopy(mapping['failed_preservation'])
  save(OUT/'new-schema-unit-map.json',mapping);save(OUT/'new-schema-unit-pins.json',pins)
  before_state=pin(roots['pool']/'state.json');before_tree=c.inventory(roots['pool']/'project')
  def verify(m=None):return rec_call(rec.verify_evidence,roots,m or mapping,pins)
  actual=verify();assert len(actual['payloads'])==80
  record('NEW_SCHEMA_PREFLIGHT_POSITIVE',dict(scope='REAL_NEUTRAL78_7_2_FS_EVIDENCE_ONLY_NO_ROOT_AUTH',payloads=len(actual['payloads']),state='failed',restore_calls=0))
  m=copy.deepcopy(mapping);m['schema']=read(R/'data/phase365-source-recovery-plan/restore-map.json')['schema'];record('OLD_MAP_REJECT',reject(lambda:verify(m)))
  raw=receipt.read_bytes();v=read(receipt);v['restore']=True;receipt.write_text(json.dumps(v))
  m=copy.deepcopy(mapping);m['failed_preservation'].update(pin(receipt));oldpin=copy.deepcopy(pins['files'][0]);pins['files'][0]=copy.deepcopy(m['failed_preservation'])
  record('BOOL_RESTORE_ZERO_REJECT',reject(lambda:verify(m)))
  receipt.write_bytes(raw);pins['files'][0]=oldpin
  m=copy.deepcopy(mapping);m['file_differences'][0]['target']['mtime_ns']+=1
  record('TARGET_MTIME_DRIFT_REJECT',reject(lambda:verify(m)))
  payload=roots['failed_run']/mapping['file_differences'][0]['payload']['path'];alias=payload.with_name('unit-alias')
  os.link(payload,alias);answer=reject(verify);alias.unlink();record('NEW_SCHEMA_PAYLOAD_LINK_REJECT',answer)
  archive=roots['failed_run']/'output/failed-pool-preservation/failed-project-overlay.zip';rawzip=archive.read_bytes();bad=bytearray(rawzip)
  at=bad.index(b'PK\x01\x02')+16;bad[at]^=1;archive.write_bytes(bad)
  answer=reject(verify);archive.write_bytes(rawzip);assert answer['type']=='BadZipFile' and 'CRC' in answer['message'];record('NEW_SCHEMA_BAD_CRC_REJECT',answer)
  missing=roots['source_root']/'old-root.json';save(missing,dict(schema='phase365-root-pool-recovery/1',action='restore',root_restore_authorized=True))
  record('OLD_ROOT_SCHEMA_REJECT',reject(lambda:rec_call(rec.source_gate,roots['source_root'],dict(path='old-root.json',**pin(missing)),'restore')))
  assert pin(roots['pool']/'state.json')==before_state and c.inventory(roots['pool']/'project')==before_tree
  record('NEUTRAL_PREIMAGES_UNCHANGED',dict(failed_state_same=True,project_bytes_mode_mtime_same=True,restore=0,READY=0))
  # Saved actual evidence only. Never permit a live pool or baseline filesystem read here.
  realmap=read(R/'data/phase368-attempt02-recovery-source/restore-map.json');realroots={k:Path(v) for k,v in realmap['roots'].items()}
  def saved(row):
   assert row['root'] in ('failed_run','previous_run','source_root')
   name=row['path'];p=realroots[row['root']]/name
   assert not Path(name).is_absolute() and '..' not in Path(name).parts and not any(q.is_symlink() for q in (p,*p.parents))
   assert not p.is_relative_to(realroots['pool'])
   assert pin(p)=={k:row[k] for k in ('size','sha256')};COUNTS['saved_map_reads']+=1;return p
  for row in read(R/'data/phase368-attempt02-recovery-source/source-input-pins.json')['files']:saved(row)
  assert realmap['schema']=='phase368-attempt02-exact-restore-source-map/1' and realroots['failed_run'].name.endswith('attempt02')
  preservation=read(saved(realmap['failed_preservation']));assert preservation['schema']=='attempt02-failed-pool-preservation/1' and preservation['status']=='PRESERVED_NOT_RESTORED' and type(preservation['restore']) is int and preservation['restore']==0
  failed=read(saved(realmap['failed_project_inventory']));target=read(saved(realmap['project_target']));staged=read(saved(realmap['staged_target']))
  fi=c.index(failed);ti=c.index(target);assert fi.keys()==ti.keys()
  cf={k for k in fi if fi[k]!=ti[k] and fi[k]['kind']=='file'};cd={k for k in fi if fi[k]!=ti[k] and fi[k]['kind']=='directory'}
  assert cf=={row['path'] for row in realmap['file_differences']} and cd=={row['path'] for row in realmap['directory_differences']}
  for row in realmap['file_differences']:
   assert row['before_preserved']==fi[row['path']] and row['target']==ti[row['path']]
   p=saved(row['payload']);assert pin(p)=={k:row['target'][k] for k in ('size','sha256')}
  for row in realmap['directory_differences']:assert row['before']==fi[row['path']] and row['target']==ti[row['path']]
  si=c.index(staged)
  for row in realmap['staged_files']:
   assert row['target']==si[row['target']['path']];p=saved(row['payload']);assert pin(p)=={k:row['target'][k] for k in ('size','sha256')}
  savedroot=realroots['failed_run']/'output/failed-pool-preservation';plan=read(savedroot/'overlay-manifest.json');base=read(savedroot/'baseline-files.json')
  assert c.overlay_plan(base,failed)==plan;c.validate_archive(savedroot/'failed-project-overlay.zip',failed,plan)
  assert pin(savedroot/'failed-project-overlay.zip')==dict(size=preservation['overlay_bytes'],sha256=preservation['overlay_sha256'])
  assert pin(savedroot/'failed-pool-state.json')==dict(size=250,sha256='ba1f6e24b2943bbd646f85f035e0dd3cebf3008666568e3c589418632282f630')
  record('ACTUAL_SAVED_MAP_ONLY',dict(derived_files=len(cf),derived_dirs=len(cd),derived_staged=len(realmap['staged_files']),payloads=80,CRC_SHA=True,failed_state_source='saved-only250B/ba1f6e24',livepool_access=False,restoration=False))
 except BaseException as exc:
  failure=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());save(OUT/'first-failure.json',failure)
 report=dict(schema='phase370-independent-new-helper-controls/1',status='PASS' if failure is None else 'FAIL',cases=cases,counts=COUNTS,failure=failure,full_actual12_positive=False,full_projection_positive=False)
 save(OUT/'report.json',report)
 save(OUT/'owned-files.json',dict(schema='phase370-independent-helper-output-owner/1',files=[desc(p) for p in sorted(OUT.rglob('*')) if p.is_file()]))
 for row in read(OUT/'owned-files.json')['files']:assert desc(R/row['path'])==row
 print(json.dumps(dict(status=report['status'],controls=len(cases),counts=COUNTS,failure=failure,report=desc(OUT/'report.json'),owner=desc(OUT/'owned-files.json'))))
 return 0 if failure is None else 1

if __name__=='__main__':raise SystemExit(main())
