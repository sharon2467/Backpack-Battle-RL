"""Independent static395 audit only. Never imports or executes reviewed SOURCE."""
import ast
import hashlib
import json
from pathlib import Path
import stat

R = Path(__file__).absolute().parents[1]
D = R / 'data/phase396-independent-static-first-001'
reads = {}


def actual(relative):
    p = R / relative
    s = p.lstat()
    assert stat.S_ISREG(s.st_mode) and s.st_nlink == 1
    assert not any(q.is_symlink() for q in (p, *p.parents))
    raw = p.read_bytes()
    t = p.lstat()
    assert (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns) == (t.st_dev, t.st_ino, t.st_size, t.st_mtime_ns, t.st_ctime_ns)
    row = dict(path=relative, size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    reads[relative] = row
    return raw, row


def load(relative):
    return json.loads(actual(relative)[0])


def check(row):
    got = actual(row['path'])[1]
    assert got == {k:row[k] for k in ('path', 'size', 'sha256')}, (row, got)
    return got


def save(name, value):
    with (D / name).open('x') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def functions(relative):
    raw, _ = actual(relative)
    tree = ast.parse(raw, filename=relative)
    return {n.name:n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}, tree


def digest_ast(node):
    return hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()


def main():
    assert not D.exists()
    D.mkdir()
    expected = [
        ('data/phase396-independent-recovery-preparation/owned-files.json',998,'2225f29f886c94cc20bebbdb1ca84b6415f9f4ebe0d3fa3a52b4f0afd03531e1'),
        ('data/phase396-independent-recovery-preparation/contract.json',23068,'bde88c41327e48c0538d43bc43d742a7ad8296abc2787861046378accf819bdd'),
        ('data/phase395-source-handoff/owned-files.json',87991,'8a905f376b83bfc0a8b636044ecf80419978e0145e1d91a8fb853f86e551d3cf'),
        ('data/phase395-attempt05-recovery-source/combined-source-freeze.json',82219,'5bd5ad0d6952bb6b5f37748f7414eaf8bbd96ee9abb052f7749cfca2a2912e98'),
        ('data/phase395-attempt05-recovery-source/source-owner.json',87048,'51f456ecf8429838f3536ecddfbdc7aa272353a54c4784edcfc2c4e6f1eb7a0a'),
        ('data/phase395-independent-readback-source/source-owner.json',87632,'b6b7a626a9af38fff3b2f80d05f503359ecce1f9e8c6ce1c0e204fa11a98606e'),
    ]
    for path,size,sha in expected: check(dict(path=path,size=size,sha256=sha))
    owners = []
    for name in (expected[0][0], expected[2][0], expected[4][0], expected[5][0]):
        value = load(name)
        rows = [check(row) for row in value['files']]
        assert len({r['path'] for r in rows}) == len(rows)
        owners.append(dict(owner=actual(name)[1], ordinary_single_link_leaves=len(rows), bytes=sum(r['size'] for r in rows)))
    handoff = owners[1]
    assert handoff['ordinary_single_link_leaves'] == 387 and handoff['bytes'] == 5956317
    freeze = load(expected[3][0])
    for row in freeze['files']: check(row)
    source_owner = {r['path']:r for r in load(expected[4][0])['files']}
    declared = {r['path']:r for r in freeze['files']}
    closure, graph, todo = {}, [], ['tests/phase395_pool_recovery.py']
    while todo:
        name = todo.pop()
        if name in closure: continue
        closure[name] = actual(name)[1]
        _, tree = functions(name)
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import): modules.extend(a.name for a in node.names)
            if isinstance(node, ast.ImportFrom) and node.module: modules.append(node.module)
        local = sorted({'tests/' + m + '.py' for m in modules if (R/'tests'/(m+'.py')).is_file()})
        graph.append(dict(path=name, local_imports=local))
        todo.extend(local)
    assert closure == {r['path']:r for r in freeze['import_closure']}
    assert all(source_owner.get(k) == v == declared.get(k) for k,v in closure.items())
    inverse_results = []
    for stem in ('phase395_pool_recovery','phase395_prepare_attempt05_restore_map','phase395_independent_restored_readback'):
        value = load('data/phase395-attempt05-recovery-source/'+stem+'-inverse.json')
        check(value['before']);check(value['after'])
        text = actual(value['after']['path'])[0].decode()
        for row in reversed(value['edits']):
            for pos in reversed(row['positions']):
                assert text[pos:pos+len(row['after'])] == row['after']
                text = text[:pos]+row['before']+text[pos+len(row['after']):]
        assert text.encode() == actual(value['before']['path'])[0]
        old,_ = functions(value['before']['path']); new,_ = functions(value['after']['path'])
        conserved = sorted(k for k in old if k in new and digest_ast(old[k]) == digest_ast(new[k]))
        changed = sorted(k for k in old if k in new and digest_ast(old[k]) != digest_ast(new[k]))
        assert conserved == value['conserved_functions'] and changed == value['changed_functions']
        inverse_results.append(dict(source=value['after'], origin=value['before'], inverse='INDEPENDENT_EXACT_BYTES', conserved=conserved, changed=changed, added=sorted(set(new)-set(old))))
    origins = load('data/phase396-independent-recovery-preparation/source-evidence.json')
    origin_checks=[]
    for entry in origins['AST_origins']:
        check(entry['source']); fn,_ = functions(entry['source']['path'])
        for row in entry['functions']:
            assert digest_ast(fn[row['name']]) == row['AST_sha256']
        origin_checks.append(dict(source=entry['source'], verified_function_names=[r['name'] for r in entry['functions']]))
    api = load('data/phase395-attempt05-recovery-source/api-contract.json')
    assert api['source_freeze'] == actual(expected[3][0])[1]
    signatures = []
    for path in ('tests/phase395_saved_complete_evidence.py','tests/phase395_prepare_attempt05_restore_map.py','tests/phase395_pool_recovery.py','tests/phase395_independent_restored_readback.py'):
        fn,_ = functions(path)
        signatures.append(dict(path=path,functions=[dict(name=k,arguments=ast.unparse(n.args),line=n.lineno,end_line=n.end_lineno,AST_sha256=digest_ast(n)) for k,n in fn.items() if isinstance(n,ast.FunctionDef)]))
    contract = load('data/phase395-independent-readback-source/source-contract.json')
    reader_owner = load(expected[5][0])
    assert expected[5][0] not in {r['path'] for r in reader_owner['files']}
    inspector=check(contract['process_inspector_source'])
    assert inspector in reader_owner['files']
    assert {k:inspector[k] for k in ('size','sha256')} == {k:contract['process_inspector_origin'][k] for k in ('size','sha256')}
    capsule=load(contract['failed_capsule_manifest']['path'])
    partitions={prefix:sum(k.startswith(prefix) for k in capsule['files']) for prefix in ('run/output/','run/data/','root-control/','repo/')}
    assert partitions == {'run/output/':364,'run/data/':3,'root-control/':10,'repo/':3}
    assert len(capsule['files'])==380 and sum(r['size'] for r in capsule['files'].values())==185529438
    assert set(contract['capsule_non_run_members']) == {k for k in capsule['files'] if not k.startswith('run/')}
    assert all(set(v)=={'size','sha256','mode','mtime_ns'} for v in capsule['files'].values())
    assert contract['capsule_archive']['size']==capsule['archive_size'] and contract['capsule_archive']['sha256']==capsule['archive_sha256']
    mapping=load(api['MAP']);pins=load(api['INPUT_PINS'])
    assert len(pins['files'])==524 and set(r['root'] for r in pins['files'])=={'failed_run','previous_run'}
    assert len(mapping['file_differences'])==78 and len(mapping['directory_differences'])==7 and len(mapping['staged_files'])==2
    for row in pins['files']:
        assert Path(row['path']).as_posix()==row['path'] and not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
    for row in mapping['file_differences']:
        assert row['before_preserved']['kind']==row['target']['kind']=='file'
    source_paths = ['tests/phase395_pool_recovery.py','tests/phase395_recovery_gate_source.py','tests/phase395_independent_restored_readback.py','tests/phase375_oracle_host.py','tests/phase363_oracle_storage.py']
    snapshot=[]
    (D/'source-snapshots').mkdir()
    for name in source_paths:
        raw,row=actual(name)
        p=D/'source-snapshots'/Path(name).name
        with p.open('xb') as f:f.write(raw)
        snapshot.append(dict(origin=row,snapshot=actual(str(p.relative_to(R)))[1]))
    save('evidence.json',dict(schema='phase396-independent-static-evidence/1',owners=owners,import_closure=list(closure.values()),import_graph=graph,inverse_checks=inverse_results,old_AST_origin_checks=origin_checks,actual_API_signatures=signatures,source_freeze=api['source_freeze'],capsule_manifest_only=dict(partitions=partitions,members=380,bytes=185529438,archive_streamed=False),map_descriptive_counts=dict(project_files=78,directories=7,staged_files=2,writer_by_conserved_algorithm=80,pins=524,saved_external_inputs_read=False),reader_source_owner_self_included=False,inspector=inspector,source_snapshots=snapshot,SUT_imports=0,SUT_calls=0,native=0,models=0,actual_pool=0,proc_inspection=0))
    save('read-set.json',dict(schema='phase396-static-read-set/1',files=[reads[k] for k in sorted(reads)],external_reads=0,SUT_imports=0,SUT_calls=0))
    print(json.dumps(dict(owners=owners,local_import_closure=len(closure),inverse_checks=[dict(source=x['source']['path'],conserved=len(x['conserved']),changed=x['changed']) for x in inverse_results],SUT_calls=0)))


if __name__ == '__main__':
    main()
