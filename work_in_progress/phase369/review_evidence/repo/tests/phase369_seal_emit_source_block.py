"""Text-only script-binding counterexample. No SUT import or semantic execution."""
from pathlib import Path
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1];D=R/'data/phase369-independent-execution'
def pin(p):
 b=p.read_bytes();return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p):return dict(path=str(p.relative_to(R)),**pin(p))
def read(p):return json.loads(p.read_text())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def span(p,start,end):return dict(source=desc(p),start=start,end=end,text='\n'.join(p.read_text().splitlines()[start-1:end])+'\n')
def main():
 contract=read(D/'static-block-contract.json')
 for row in contract['files']:assert desc(R/row['path'])==row
 obj=R/'data/phase184-ranger-idle-sync-source/source/object.cpp';text=obj.read_text()
 wrapper=text[text.index('Variant Object::_emit_signal('):text.index('Error Object::emit_signal(')]
 assert 'emit_signal(signal, args, argc);' in wrapper and wrapper.rstrip().endswith('return Variant();\n}')
 assert 'return emit_signal(' not in wrapper
 assert '"emit_signal", &Object::_emit_signal' in text
 sink=R/'data/phase368-oracle-source/after-source/native_random_observer_sink_v7.gd';s=sink.read_text()
 assert 'source_cut_emit_error = emit_signal("source_idle_cut_ready")' in s
 assert 'typeof(source_cut_emit_error) != TYPE_INT or source_cut_emit_error != OK' in s
 collector=R/'data/phase369-oracle-source/collector.gd';c=collector.read_text()
 assert 'typeof(control.emit_error) != TYPE_INT or control.emit_error != OK' in c
 caller_rows=[dict(line=i,text=line) for i,line in enumerate(s.splitlines(),1) if 'source_cut_emit_error = emit_signal' in line or 'typeof(source_cut_emit_error)' in line]
 finalizer_rows=[dict(line=i,text=line) for i,line in enumerate(c.splitlines(),1) if 'typeof(control.emit_error)' in line]
 finding=dict(schema='phase369-independent-emit-return-static-counterexample/1',status='SOURCE_BINDING_CONTRADICTION',
  primary_SOURCE=[span(obj,1145,1171),span(obj,1698,1705)],sink=desc(sink),collector=desc(collector),
  script_binding='Object::_emit_signal vararg wrapper, not direct Error-returning C++ Object::emit_signal',
  actual_SCRIPT_return_SOURCE='Variant() / NIL; the wrapper discards native Error',native_Error_observable_to_script=False,
  sink_call_and_guards=caller_rows,collector_finalizer_guard=finalizer_rows,
  consequence='Even if the synchronous receiver sets an exact ack, the post-emit TYPE_INT/OK guard rejects NIL and finish_source_cut cannot be admitted.',
  classification='SOURCE_DERIVED_NOT_GODOT_RUNTIME_OBSERVED',synthetic_emitter_calls=0,Godot=0,
  necessary_repair='New approved contract/source must record real script NIL return and native Error unavailable; never insert OK0. Re-establish dispatch evidence through actual private connection/phase/exact ack/return controls.',
  legacy_mechanical_static_facts_preserved=desc(D/'static-review.json'))
 finding['finalizer_call_return_SOURCE']=dict(
  source=[span(obj,673,690),span(obj,869,912),span(obj,1706,1713)],
  distinction='Object::_call_bind returns Object::call result. Object::call returns script_instance->call Variant on CALL_OK, unlike _emit_signal discarding native Error.',
  caller='receiver.finish_source_cut() directly invokes the script method; collector success expression is BOOL and explicit false branches remain BOOL.',
  conclusion='No analogous SOURCE return-discard inconsistency identified for finish. Actual returned BOOL and acknowledgement still require the future real language controls.',
  classification='SOURCE_DERIVED_NOT_RUNTIME_OBSERVED')
 save(D/'first-source-block.json',finding)
 prep=read(R/'data/phase368-independent-source-preparation/contract.json')
 coverage=[dict(id=row['id'],label=row['label'],status='DYNAMIC_NOT_EXECUTED_SOURCE_BLOCK') for row in prep['controls']]
 coverage.append(dict(id=33,label='Frozen DTO serialization and finish return',status='DYNAMIC_NOT_EXECUTED_SOURCE_BLOCK'))
 save(D/'coverage.json',dict(cases=coverage,whole_script_resource_load='NOT_EXECUTED',
  completed_independent_SOURCE=['20author payloads pinned','collector369 inverse368 three expressions','collector368 inverse365 fullbytes','sink368 inverse359 fullbytes','host/recovery369 identity-only fullbyte inverses','75path identity comparison;74oldpaths conserved','sink/map exact368 reused','once guard before sampling and no resampling calls in finalizer'],
  overridden_source_requirement='Original design/33-contract INT Error expectation is invalid for this actual Godot3 script binding; new approved contract required.',
  partial_static_review=desc(D/'static-review.json'),not_completed=['Full control dataflow acceptance','Godot resource load/semantic controls','newhost observer failure cases','recovery new-schema/tinyFS/saved-map controls']))
 review=dict(schema='phase369-independent-source-final/1',status='BLOCKED369_GDSCRIPT_EMIT_SIGNAL_RETURNS_NIL_NOT_NATIVE_ERROR',
  source_freeze=desc(R/'data/phase369-oracle-source/combined-source-freeze.json'),
  first_counterexample=desc(D/'first-source-block.json'),coverage=desc(D/'coverage.json'),
  native=0,models=0,SUT_imports=0,Godot_language_processes=0,full_script_resource_loads=0,helper_semantic_calls=0,
  actual_input_builds=0,synthetic_projection=0,process_launches=0,pool_operations=0,restore=0,READY=0,projection=0,
  first_dynamic_exit=None,conditional_dynamic_permission_used=False,
  earlier_metadata_failure='Preparation-only inline freeze.paths[0] KeyError0 preserved separately; fixed mapping inspection before first preparer execution, no semantics rerun.',
  whole_runtime356='CLOSED',reader361='PENDING',actual12_positive=False,fullprojection_positive=False,
  no_more_writes=True)
 save(D/'review.json',review)
 files=[p for p in D.rglob('*') if p.is_file()]
 files+=[R/row['path'] for row in contract['files']]
 files+=list((R/'data/phase369-independent-execution-preparation-firstfacts').iterdir())
 save(D/'owned-files.json',dict(schema='phase369-independent-source-block-owner/1',files=[desc(p) for p in sorted(set(files))],repo_only=True,no_more_writes=True))
 owner=read(D/'owned-files.json')
 for row in owner['files']:assert desc(R/row['path'])==row
 print(json.dumps(dict(review=desc(D/'review.json'),finding=desc(D/'first-source-block.json'),owner=desc(D/'owned-files.json'),leaves=len(owner['files']),bytes=sum(row['size'] for row in owner['files']))))

if __name__=='__main__':main()
