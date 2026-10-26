"""370 actual frozen delta review and fixture preparation, no SUT import."""
from pathlib import Path
import hashlib,json,re

R=Path(__file__).resolve().parents[1];D=R/'data/phase370-independent-execution';A=R/'data/phase370-oracle-source'
def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def fn(text,name):
 start=text.index('func '+name+'(');m=re.search(r'^func ',text[start+5:],re.M)
 return text[start:start+5+m.start()] if m else text[start:]

def main():
 D.mkdir();p=D/'language-project';p.mkdir();(D/'SOURCE').mkdir()
 assert pin(A/'source-owner.json')==dict(size=3194,sha256='df3cad7102ee63936f4b5d9c870f5829670eb74f858fadb9bcd924a61de42720')
 for row in read(A/'source-owner.json')['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
 new_proofs=[]
 for ledger in ('GD-inverse-ledger.json','Python-inverse-ledger.json'):
  for row in read(A/ledger)['files']:
   after=(R/row['after']['path']).read_text();before=(R/row['before']['path']).read_text();inverse=after
   for old,new in reversed(row['literal_pairs']):inverse=inverse.replace(new,old)
   assert inverse==before
   new_proofs.append(dict(after=row['after'],before=row['before'],exact_new_delta_inverse=True))
 sink=(A/'after-source/native_random_observer_sink_v7.gd').read_text();collector=(A/'collector.gd').read_text()
 assert 'control.emit_error' not in collector and 'source_cut_emit_error' not in sink
 assert 'source_cut_script_return = emit_signal("source_idle_cut_ready")\n\tsource_cut_script_return_observed = true' in sink
 assert '"native_emit_error_available": false, "native_emit_error": null' in sink
 cut=fn(collector,'on_idle_source_cut');finish=fn(collector,'finish_source_cut')
 assert cut.index('source_cut_frozen = true')<cut.index('stable_snapshot()')
 finishcode='\n'.join(row.split('#',1)[0] for row in finish.splitlines())
 assert not re.search(r'\b(stable_snapshot|state_snapshot|source_runtime_snapshot|getStats|check_barrier)\(',finishcode)
 assert 'typeof(control.script_emit_return_observed) != TYPE_BOOL' in cut and 'control.script_emit_return_observed or' in cut
 assert 'not control.script_emit_return_observed or typeof(control.script_emit_return) != TYPE_NIL' in finish
 f=read(A/'combined-source-freeze.json');old=read(R/'data/phase369-oracle-source/combined-source-freeze.json')
 assert f['paths'].keys()==old['paths'].keys()
 assert {k for k in f['paths'] if f['paths'][k]!=old['paths'][k]}=={'native_random_observer_sink_v7.gd'}
 assert pin(R/'data/phase368-attempt02-recovery-source/restore-map.json')==dict(size=68355,sha256='f07ac2295c90f7a0b0a770a4c71dcb5bee3613cf3b7b9057467fa0d0a605919d')
 save(D/'static-review.json',dict(schema='phase370-independent-static/1',status='NEW_SOURCE_DELTA_NO_DEFINITE_STATIC_BLOCK_LANGUAGE_LOAD_PENDING',
  new_inverse_proofs=new_proofs,old_success_reused=desc(R/'data/phase369-independent-execution/static-review.json'),
  sink_related_branches_read=['clock_idle_signal','source_cut_control','source_cut_reject','source_cut_receiver','ack_source_idle_cut','emit_source_idle_cut_once','source_control_rows','source_diagnostic'],
  collector_related_branches_read=['ensure_source_window','attach_source_listener','check_source_listener_order','source_control_snapshot','source_window_reject','on_idle_source_cut','finish_source_cut'],
  once_before_sampling=True,finish_resampling=False,original_clock_other_methods_conserved=True,ABI12_17key_unchanged=True,
  resource_parse='NOT_EXECUTED; full script binding/parser assignment validity must be actually loaded, not inferred',
  aggregated_definite_static_blockers=[],potential_runtime_questions=['Complete script parse/load of concrete emit assignment and other control methods','Actual NIL+observed/BOOL/private receiver/ack state transitions'],
  full_native_positive=False,SUT_imports=0,Godot=0))
 (p/'full-collector.gd').write_bytes((A/'collector.gd').read_bytes());(p/'full-sink.gd').write_bytes((A/'after-source/native_random_observer_sink_v7.gd').read_bytes())
 assert not re.search(r'^tool\b|\bpreload\(',sink,re.M) and not re.search(r'^tool\b|\bpreload\(',collector,re.M)
 names=['source_diag_valid','source_diag_secondary','source_diagnostic','source_control_target','source_control_bound_value','source_control_rows','source_cut_control','source_cut_reject','source_cut_receiver','ack_source_idle_cut','emit_source_idle_cut_once','float_bits','fail']
 declarations=sink[sink.index('signal source_idle_cut_ready'):sink.index('func source_diag_valid')]
 caps=next(line for line in sink.splitlines() if line.startswith('const CAPS = '))
 unit='extends Node\n'+caps+'\nvar OUT = "user://unused"\nvar sequence = 23\nvar ui_sequence = 17\nvar king_clock_count = 9\nvar failed = false\nvar closed = true\nvar source_window_complete = true\nvar king_clock_closed = true\nvar ui_closed = true\nvar first_error = null\nvar source_cleanup = null\n'+declarations+'\n'
 for name in names:unit+=fn(sink,name)+'\n'
 (p/'unit-sink.gd').write_text(unit)
 (p/'extra.gd').write_text('extends Node\nfunc noop():\n\tpass\n')
 (p/'project.godot').write_text('config_version=4\n\n[application]\nconfig/name="Independent370LanguageControls"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="Independent370LanguageControls"\n\n[rendering]\nquality/driver/driver_name="GLES2"\n')
 for src,name in [('tests/native_run_compaction.py','compaction.py'),('tests/phase363_oracle_storage.py','storage.py'),('tests/phase363_oracle_process.py','process.py')]:
  (D/'SOURCE'/name).write_bytes((R/src).read_bytes())
 save(D/'source-unit-boundary.json',dict(complete_resources=[desc(p/'full-collector.gd'),desc(p/'full-sink.gd')],
  production_resource_instances=0,lifecycle_calls=0,exact_extracted_sink_methods=names,excluded=['_ready','clock_idle_signal','production collector oncut/finish'],
  unit_receiver='Actual main SceneTree, unit-only primitive payload/ack/finish. Not a production sampling or native-input positive.',
  manual_globals='Explicit completion-control prestate only. Actual Engine frames/IDs; no native carrier or business state fabricated.'))
 print(json.dumps(dict(static='NO_DEFINITE_BLOCK',new_inverses=len(new_proofs),full_resources=2,SUT_imports=0,Godot=0)))

if __name__=='__main__':main()
