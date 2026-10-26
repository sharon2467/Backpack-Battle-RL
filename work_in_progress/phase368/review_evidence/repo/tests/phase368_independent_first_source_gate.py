"""368 first static gate only. No SUT import, GD parser or runtime execution."""
from pathlib import Path
import hashlib
import json
import re

R=Path(__file__).resolve().parents[1]
D=R/'data/phase368-independent-source-review'
A=R/'data/phase368-oracle-source'

def pin(path):
    raw=path.read_bytes();return dict(size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def desc(path):return dict(path=str(path.relative_to(R)),**pin(path))
def save(path,value):
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
def read(path):return json.loads(path.read_text())
def excerpt(path,start,end):
    return dict(source=desc(path),start=start,end=end,text='\n'.join(path.read_text().splitlines()[start-1:end])+'\n')

def main():
    contract=read(D/'static-contract.json')
    for row in contract['files']:assert desc(R/row['path'])==row
    owner=read(A/'source-owner.json')
    for row in owner['files']:assert desc(R/row['path'])==row
    collector=A/'collector.gd';template=R/'tests/phase368_collector_control_delta.gd'
    text=collector.read_text();lines=text.splitlines();calls=[]
    for number,line in enumerate(lines,1):
        for match in re.finditer(r'(?<![.\w])get_tree\(\)',line):calls.append(dict(line=number,column=match.start()+1,text=line))
    assert text.startswith('extends SceneTree\n') and not re.search(r'^func get_tree\(',text,re.M)
    assert len(calls)==3 and [row['line'] for row in calls]==[974,974,985]
    stree_h=R/'data/phase027-implementation-design/full-source/upstream/scene/main/scene_tree.h'
    node_h=R/'data/phase027-implementation-design/full-source/upstream/scene/main/node.h'
    stree_cpp=R/'data/phase251-logic-reset-timer-source-plan/Godot3.6.2/scene/main/scene_tree.cpp'
    node_cpp=R/'data/phase251-logic-reset-timer-source-plan/Godot3.6.2/scene/main/node.cpp'
    assert 'class SceneTree : public MainLoop' in stree_h.read_text()
    assert 'class Node : public Object' in node_h.read_text()
    assert 'D_METHOD("get_tree"), &Node::get_tree' in node_cpp.read_text()
    assert 'D_METHOD("get_tree")' not in stree_cpp.read_text()
    assert 'D_METHOD("get_root"), &SceneTree::get_root' in stree_cpp.read_text()
    save(D/'first-static-counterexample.json',dict(schema='phase368-independent-static-api-counterexample/1',
        classification='SOURCE_INTERFACE_MISMATCH_NOT_EXECUTED_GD_PARSE',collector=desc(collector),template=desc(template),
        receiver='SceneTree collector self, not a Node',calls=calls,
        source=[excerpt(stree_h,74,80),excerpt(node_h,45,48),excerpt(stree_cpp,2057,2061),excerpt(node_cpp,3130,3134),excerpt(collector,971,986)],
        expected='Use the existing SceneTree self as tree emitter/ID in this collector diagnostic. Node sink get_tree() calls are valid and must remain untouched.',
        actual='New collector diagnostic calls Node-only get_tree() three times without a local helper on a SceneTree script.',
        reachability='ensure_source_window -> attach_source_listener -> source_control_record -> source_control_snapshot; diagnostic API is required before player fixture/source window admission.',
        Godot_error_message=None,Godot_parse_runs=0,SUT_imports=0,original_Game_runs=0))
    prep=read(R/'data/phase368-independent-source-preparation/contract.json')
    matrix=[dict(id=row['id'],label=row['label'],status='NOT_EXECUTED_BLOCKED_AT_SOURCE_GATE') for row in prep['controls']]
    matrix.append(dict(id=33,label='Frozen primitive DTO serialization and finish result',status='NOT_EXECUTED_BLOCKED_AT_SOURCE_GATE'))
    save(D/'coverage.json',dict(necessary_obligations=33,cases=matrix,
        source_checks_completed=['Exact frozen author owner22 payload identities','Exact merged/template receiver mismatch and primary class/binding anchors'],
        not_completed=['Independent whole inverse/module conservation proof','Signal/ack/finalizer/diagnostic dynamic controls','Python host controls','Saved-map and new recovery helper controls'],
        author_inverse_reports_are_independent_acceptance=False))
    review=dict(schema='phase368-independent-first-source-review/1',status='BLOCKED368_SCENETREE_COLLECTOR_NODE_ONLY_GET_TREE_CALL',
        source_freeze=desc(A/'combined-source-freeze.json'),source_owner=desc(A/'source-owner.json'),
        first_counterexample=desc(D/'first-static-counterexample.json'),coverage=desc(D/'coverage.json'),
        owner_payloads_read=len(owner['files']),owner_payload_bytes=sum(row['size'] for row in owner['files']),
        native=0,models=0,SUT_imports=0,Godot_language_processes=0,Godot_parse_runs=0,Python_candidate_calls=0,
        helper_semantic_calls=0,actual_input_builds=0,synthetic_bundles=0,process_launches=0,pool_operations=0,restore=0,READY=0,
        first_error_scope='Static SOURCE before any conditional language/helper execution; no observed parser/runtime failure fabricated.',
        required_repair='New frozen collector/template closure correcting these SceneTree receiver expressions, preserving old368 source. Do not change valid Node-sink get_tree calls or fixtures/seeds.',
        readback_adapter='Not prepared/executed after this blocker. Later minimal adaptation: new exact368 map/source/root schema, attempt02 failedstate/capsule source instead of attempt01, retain direct target/baseline/retained readback and separate ROOT READY. Actual fulltree still requires ROOT release.',
        runtime356='CLOSED',reader361='PENDING',full_actual12_positive=False,full_projection_positive=False,
        source_read_diagnostics=[dict(requested='data/phase368-oracle-source/source-delta-proof.json',status='NO_SUCH_FILE',resolution='Actual manifest filename delta-proof.json'),
            dict(requested='data/phase368-oracle-source/sink.gd',status='NO_SUCH_FILE',resolution='Actual manifest path after-source/native_random_observer_sink_v7.gd')],
        no_more_writes=True)
    save(D/'review.json',review)
    selected=[p for p in D.iterdir() if p.is_file()]
    selected.extend(R/row['path'] for row in contract['files'])
    save(D/'owned-files.json',dict(schema='phase368-independent-source-block-owner/1',files=[desc(p) for p in sorted(set(selected))],repo_only=True,no_more_writes=True))
    final=read(D/'owned-files.json')
    for row in final['files']:assert desc(R/row['path'])==row
    print(json.dumps(dict(review=desc(D/'review.json'),owner=desc(D/'owned-files.json'),leaves=len(final['files']),bytes=sum(row['size'] for row in final['files']),status=review['status'])))

if __name__=='__main__':main()
