"""Independent369 SOURCE review and language fixtures. Text/AST only, no SUT import."""
import ast
import hashlib
import json
from pathlib import Path
import re

R=Path(__file__).resolve().parents[1];D=R/'data/phase369-independent-execution';A=R/'data/phase369-oracle-source'
def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def read(p):return json.loads(p.read_text())
def function(text,name):
 start=text.index('func '+name+'(');m=re.search(r'^func ',text[start+5:],re.M)
 return text[start:start+5+m.start()] if m else text[start:]
def inverse(text,ledger):
 suffix=ledger['removable_suffix'];assert text.endswith(suffix);text=text[:-len(suffix)]
 for row in reversed(ledger['replacements']):
  assert text.count(row['after'])==1;text=text.replace(row['after'],row['before'],1)
 assert hashlib.sha256(text.encode()).hexdigest()==ledger['before_sha256'];return text

def main():
 D.mkdir();(D/'SOURCE').mkdir();p=D/'language-project';p.mkdir()
 assert pin(A/'source-owner.json')==dict(size=3796,sha256='7aa81b718bc049211a129a3065e0ed6a23d17d00b69ded06c410861befeef96a')
 for row in read(A/'source-owner.json')['files']:assert pin(R/row['path'])=={k:row[k] for k in ('size','sha256')}
 old=R/'data/phase368-oracle-source';new=(A/'collector.gd').read_text();oldc=(old/'collector.gd').read_text()
 before=function(oldc,'source_control_snapshot');after=function(new,'source_control_snapshot')
 assert before.count('get_tree()')==3 and after==before.replace('get_tree()','self')
 assert new==oldc.replace(before,after,1)
 assert inverse(oldc,read(old/'collector-inverse-ledger.json'))==(R/'data/phase365-control-recovery-source/collector.gd').read_text()
 sink=(old/'after-source/native_random_observer_sink_v7.gd').read_text()
 assert inverse(sink,read(old/'sink-inverse-ledger.json'))==(R/'data/phase359-king-producer-source/after-source/native_random_observer_sink_v7.gd').read_text()
 proof=read(A/'source-delta-proof.json')
 for name,v in proof['Python'].items():
  a=(R/v['after']['path']).read_text()
  for oldliteral,newliteral in reversed(v['literal_pairs']):a=a.replace(newliteral,oldliteral)
  assert a==(R/v['before']['path']).read_text()
 f369=read(A/'combined-source-freeze.json');f368=read(old/'combined-source-freeze.json');f365=read(R/'data/phase365-control-recovery-source/combined-source-freeze.json')
 assert f369['paths']==f368['paths']
 assert len(f369['paths'])==len(f365['paths'])==75
 # Path identities include exact before/after/source metadata; only sink may differ.
 rows369=f369['paths'];rows365=f365['paths']
 assert rows369.keys()==rows365.keys()
 assert {k for k in rows369 if rows369[k]!=rows365[k]}=={'native_random_observer_sink_v7.gd'}
 assert pin(R/'data/phase368-attempt02-recovery-source/restore-map.json')==dict(size=68355,sha256='f07ac2295c90f7a0b0a770a4c71dcb5bee3613cf3b7b9057467fa0d0a605919d')
 assert 'connect("idle_frame", self, "on_idle_source_cut")' not in new
 assert 'connect("idle_frame", self, "observe")' in new
 finish=function(new,'finish_source_cut');code='\n'.join(line.split('#',1)[0] for line in finish.splitlines())
 assert not re.search(r'\b(stable_snapshot|state_snapshot|source_runtime_snapshot|getStats|check_barrier)\(',code)
 assert new.count('var snapshot = stable_snapshot()')==1
 assert 'source_cut_frozen = true' in function(new,'on_idle_source_cut')
 assert function(new,'on_idle_source_cut').index('source_cut_frozen = true')<function(new,'on_idle_source_cut').index('stable_snapshot()')
 assert 'source_cut_emit_error = emit_signal("source_idle_cut_ready")' in sink
 assert sink.index('source_cut_phase = "RETURNED"')<sink.index('source_cut_finish_return = receiver.finish_source_cut()')
 save(D/'static-review.json',dict(schema='phase369-independent-static/1',status='SOURCE_DELTA_REVIEWED_DYNAMIC_PENDING',owner20pins=True,
  collector_three_expression_inverse=True,collector368_inverse365_bytes=True,sink368_inverse359_bytes=True,
  host_recovery_binding_inverse_bytes=True,patch75paths=75,unchanged_old_paths=74,sink_map_byte_reused=True,
  unchanged_restore_READY_functions='SOURCE exact inverse through365 except new schema/preservation verifier; not rerun',
  once_before_sampling=True,finalizer_resampling_calls=False,original_SceneTree_business_connections_preserved=True,
  closed_entry='No second dispatch is accepted; explicit closed/reentry controls measured below. No claim of quiet closed return without actual control result.',
  full_business_snapshot_positive=False,SUT_imports=0,Godot=0))
 # Full resources are byte-for-byte mirrors, loaded but never instantiated.
 (p/'full-collector.gd').write_bytes((A/'collector.gd').read_bytes())
 (p/'full-sink.gd').write_bytes((old/'after-source/native_random_observer_sink_v7.gd').read_bytes())
 assert not re.search(r'^tool\b|\bpreload\(',new,re.M) and not re.search(r'^tool\b|\bpreload\(',sink,re.M)
 names=['source_diag_valid','source_diag_secondary','source_diagnostic','source_control_target','source_control_bound_value','source_control_rows','source_cut_control','source_cut_reject','source_cut_receiver','ack_source_idle_cut','emit_source_idle_cut_once','float_bits','fail']
 declarations=sink[sink.index('signal source_idle_cut_ready'):sink.index('func source_diag_valid')]
 caps=next(line for line in sink.splitlines() if line.startswith('const CAPS = '))
 unit='extends Node\n'+caps+'\nvar OUT = "user://unused-unit"\nvar sequence = 23\nvar ui_sequence = 17\nvar king_clock_count = 9\nvar failed = false\nvar closed = true\nvar source_window_complete = true\nvar king_clock_closed = true\nvar ui_closed = true\nvar first_error = null\nvar source_cleanup = null\n'+declarations+'\n'
 for name in names:unit+=function(sink,name)+'\n'
 (p/'unit-sink.gd').write_text(unit)
 (p/'extra.gd').write_text('extends Node\nfunc noop():\n\tpass\n')
 (p/'project.godot').write_text('config_version=4\n\n[application]\nconfig/name="Independent369LanguageControls"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="Independent369LanguageControls"\n\n[rendering]\nquality/driver/driver_name="GLES2"\n')
 # Python test dependencies remain exact files and are not imported during preparation.
 for source,target in [('tests/phase369_oracle_host.py','host.py'),('tests/phase369_pool_recovery.py','recovery.py'),('tests/phase363_oracle_process.py','process.py'),('tests/phase363_oracle_storage.py','storage.py'),('tests/native_run_compaction.py','compaction.py'),('tests/phase365_independent_tiny_evidence.py','tiny_evidence.py')]:
  (D/'SOURCE'/target).write_bytes((R/source).read_bytes())
 save(D/'language-source-contract.json',dict(full_script_resources=[desc(p/'full-collector.gd'),desc(p/'full-sink.gd')],
  exact_extracted_sink_methods=names,lifecycle_methods_excluded=['_ready','clock_idle_signal'],
  control_globals='Explicit synthetic completion-control prestate; actual Engine frames/IDs, real private connection API. No Game/buff/Timer/model/native state fabricated.',
  receiver='Actual main SceneTree with explicit unit-only callback/finish implementation; NOT production fullsnapshot/finish execution.',
  original_complete_script_instances=0,full_native_positive=False))
 print(json.dumps(dict(static='PASS',prepared=str(D.relative_to(R)),full_resources=2,extracted_methods=len(names),SUT_imports=0,Godot=0)))

if __name__=='__main__':main()
