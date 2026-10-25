"""Bounded SOURCE identities/inverse/purity review; no operational module import."""
import ast
import hashlib
import json
from pathlib import Path
import re

R=Path(__file__).resolve().parents[1];D=R/'data/phase362-independent-source-review';A=R/'data/phase362-oracle-capture-source'
def pin(p):
 b=p.read_bytes();return dict(path=str(p),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def blocks(s):
 lines=s.splitlines(keepends=True);out={}
 for i,line in enumerate(lines):
  m=re.match(r'^func (\w+)\(',line)
  if not m:continue
  z=i+1
  while z<len(lines) and (not lines[z].strip() or lines[z].startswith(('\t','#'))):z+=1
  assert m[1] not in out;out[m[1]]=''.join(lines[i:z])
 return out

def main():
 contract=json.loads((D/'static-contract.json').read_text())
 for row in contract['files']:
  p=R/row['path'];got=pin(p);assert {k:got[k] for k in ('size','sha256')}=={k:row[k] for k in ('size','sha256')}
 out=D/'static-first-001';out.mkdir(exist_ok=False);results=[]
 def check(name,fn):
  try:detail=fn()
  except Exception as e:row=dict(label=name,pass_=False,error=dict(type=type(e).__name__,message=str(e)))
  else:row=dict(label=name,pass_=True,detail=detail)
  results.append(row)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row,sort_keys=True)+'\n')
 def owner():
  v=json.loads((A/'source-owner.json').read_text())
  for row in v['files']:
   p=R/row['path'];got=pin(p);assert {k:got[k] for k in ('size','sha256')}=={k:row[k] for k in ('size','sha256')}
  return dict(leaves=len(v['files']),bytes=sum(x['size'] for x in v['files']))
 check('frozen19leaf-owner',owner)
 freeze=json.loads((A/'combined-source-freeze.json').read_text());collector=(A/'collector.gd').read_text();b=blocks(collector)
 def source_paths():
  old=json.loads((R/'data/phase359-king-producer-source/producer-source-freeze.json').read_text());assert len(freeze['paths'])==75
  for name,row in freeze['paths'].items():
   assert row['after']==old['files'][name]['after'] and row['before']==old['files'][name]['before']
   got=pin(R/row['after_path']);assert {k:got[k] for k in ('size','sha256')}==row['after']
  for row in freeze['files']:
   got=pin(R/row['path']);assert {k:got[k] for k in ('size','sha256')}=={k:row[k] for k in ('size','sha256')}
  return dict(paths75_exact359=True,combined_payloads=len(freeze['files']))
 check('unchanged35975-and-combined-payloads',source_paths)
 def inverse():
  ledger=json.loads((A/'collector-inverse-ledger.json').read_text());s=collector
  for edit in reversed(ledger['edits']):assert s==edit['after'];s=edit['before']
  assert s==(R/'tests/phase298_native_collector.gd').read_text()
  return dict(edits=len(ledger['edits']),exact_full_source_inverse=True)
 check('collector-whole-inverse',inverse)
 def fixture():
  for side,name in [('P','custom_player.json'),('O','custom_opponent.json')]:
   c=json.loads(re.search('^const SOURCE_'+side+r' = (.*)$',collector,re.M)[1]);assert c==json.loads((A/'case-A'/name).read_text())
  assert len(json.loads((A/'case-A/custom_player.json').read_text())['items'])==20
  assert len(json.loads((A/'case-A/custom_opponent.json').read_text())['items'])==19
  assert 'slot_spec(side, slot).instance_id' in b['register_inventory']
  assert b['place_player_items'].index('ensure_source_window()')<b['place_player_items'].index('book.instantiateItem(')
  assert 'observer.bind_fixed_inventory(observer.SOURCE_SLOT_TABLE.duplicate(true))' in b['observer7_precondition']
  return dict(fixed20and19=True,SOURCE_slot_roles_not_enumerated=True,birth_window_before_selected_P=True,actual_birth_O_and_native_binding='NOT_EXECUTED')
 check('fixture-slot-and-window-source',fixture)
 def getters():
  evidence=json.loads((A/'snapshot-readonly-source-evidence.json').read_text());base=Path('/workspace/godotsteam-startup-20261013/baseline/Backpack Battles')
  for name,row in evidence['original_files'].items():
   p=base/name;got=pin(p);assert {k:got[k] for k in ('size','sha256')}==row
   s=p.read_text();assert 'setget' not in s and not re.search(r'^func _get(?:\(|_property_list\()',s,re.M)
  char=(base/'Core/Character.gd').read_text();cb=blocks(char)
  for method in evidence['methods']:
   raw=cb[method['method']].encode();assert dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())=={k:method[k] for k in ('size','sha256')}
   assert cb[method['method']]==method['body'];assert not re.search(r'(?<![=!<>])=(?!=)',method['body'])
  assert not any(token in collector for token in ('get_property_list(', 'getAffectedItems(', 'getAffectedItems_nocache(', 'getItemsInside('))
  return dict(direct_original_smallGD_readback=len(evidence['original_files']),Character_readonly_functions=len(evidence['methods']),no_unknown_property_getter_pass=True,actual_GD_getter_calls=0,limits='Only literal SOURCE fields/getter closure, no native sample or Godot parse.')
 check('snapshot-readonly-source-closure',getters)
 def cut():
  s=b['on_idle_source_cut'];assert s.count('stable_snapshot()')==1 and 'source_cut_frozen = true' in s
  assert s.index('source_completion_receipt()')<s.index('source_cut_frozen = true')<s.index('stable_snapshot()')
  assert 'collector_index != sink_index + 1' in b['check_source_listener_order']
  assert 'seen[sink_index].flags != 0' in b['check_source_listener_order'] and 'seen[collector_index].flags != 0' in b['check_source_listener_order']
  assert 'receipt.cleanup.physics_frame + 2' in s and 'Engine.is_in_physics_frame()' in s
  assert 'call_deferred' not in s and 'finish_capture' not in b
  return dict(same_idle_source_guard=True,one_full_snapshot_call=True,connection_order_and_cut_native='NOT_EXECUTED',actual_source_counters='Not invented')
 check('same-idle-and-one-freeze-source',cut)
 def host_archive():
  st=ast.parse((D/'SOURCE/storage.py').read_text());ht=ast.parse((D/'SOURCE/host.py').read_text())
  for t in [st,ht]:
   names=[ast.unparse(n.func) for n in ast.walk(t) if isinstance(n,ast.Call)];assert not any(x.endswith(('copytree','_reconstruct')) for x in names)
  text=(D/'SOURCE/storage.py').read_text();assert "logical-overlay-and-live-tree-equality/1" in text and "physical_reconstruction=False" in text
  assert 'c.validate_archive(' in text and 'c.inventory(pool / \'project\')' in text
  assert "RESERVE = 4 * 1024**3" in text and "ATTEMPT = 1536 * 1024**2" in text
  host=(D/'SOURCE/host.py').read_text();assert 'actual root oracle-only authorization required' in host and 'strictINT0 model/inputbuild/expected permissions' in host
  assert 'source_gate(' in host and 'REVIEW_STATUS' in host
  return dict(no_second_Game_copy_SOURCE=True,new_vs_old_READY_declared=True,actual_ROOT_missing_guard_SOURCE=True,streamCRC_or_READY_units='NOT_EXECUTED',real_hostplan_or_lease=0)
 check('host-and-stream-storage-source-surface',host_archive)
 report=dict(schema='phase362-independent-static-review/1',checks=results,failures=[x for x in results if not x['pass_']],operational_imports=0,GD_parse_or_VM=0,processes=0,native=0,models=0,scope='SOURCE identities/lexical control flow only. Known process/installer blockers are separate; these static checks cannot grant acceptance.')
 with (out/'report.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(dict(checks=len(results),failures=[x['label'] for x in results if not x['pass_']])))
if __name__=='__main__':main()
