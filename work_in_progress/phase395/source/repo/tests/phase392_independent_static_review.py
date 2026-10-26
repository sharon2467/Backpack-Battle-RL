"""392 finite SOURCE inspection only; never imports a schema or candidate."""
from pathlib import Path
import ast
import hashlib
import json
import re
import stat
import traceback

R = Path(__file__).resolve().parents[1]
S = R / 'data/phase391-terminal-source'
D = R / 'data/phase392-independent-static-review'


def pin(path):
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(R)), size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def verify(row):
    path = R / row['path']
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path, *path.parents))
    info = path.stat()
    assert stat.S_ISREG(info.st_mode) and info.st_nlink == 1
    assert pin(path) == {key: row[key] for key in ('path', 'size', 'sha256')}
    return path


def py_functions(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def gd_functions(text):
    found = list(re.finditer(r'^func (\w+)\(', text, re.M))
    result = {}
    for i, match in enumerate(found):
        # Function body is the indented body; following module declarations are excluded.
        block = text[match.start():found[i + 1].start() if i + 1 < len(found) else len(text)]
        lines = block.splitlines(True)
        body = [lines[0]]
        for line in lines[1:]:
            if line.strip() and not line.startswith(('\t', ' ')):
                break
            body.append(line)
        result[match.group(1)] = ''.join(body).rstrip()
    return result


def main():
    D.mkdir(exist_ok=False)
    report = dict(schema='phase392-actual-static-review/1', SUT_imports=0, API_calls=0,
                  Godot=0, native=0, models=0, checks=[], failure=None)
    try:
        owner_path = S / 'source-owner.json'
        assert pin(owner_path)['size'] == 9902
        assert pin(owner_path)['sha256'] == '091b59305608472bc41f3f9a51445dd765c62df25315de7dd1d0fb2363ce195e'
        owner = json.loads(owner_path.read_text())
        for row in owner['files']:
            verify(row)
        freeze_path = S / 'combined-source-freeze.json'
        assert pin(freeze_path)['size'] == 65361
        assert pin(freeze_path)['sha256'] == 'e55a602c9d7087a71a2fe6b78a3a143663fc8f0f659c0fe3fb690019ba8173c9'
        freeze = json.loads(freeze_path.read_text())
        for row in freeze['files']:
            verify(row)
        for key in ('collector', 'schema_module', 'active_source_tuple', 'native_source_origin'):
            verify(freeze[key])
        report['checks'].append(dict(check='actual_source_pins', owner_leaves=len(owner['files']), freeze_leaves=len(freeze['files']), result='PASS'))
        for path in sorted(S.glob('*-inverse.json')):
            ledger = json.loads(path.read_text())
            before = verify(ledger['before']).read_text()
            after = verify(ledger['after']).read_text()
            inverse = after
            for edit in reversed(ledger['edits']):
                if 'suffix' in edit:
                    assert inverse.endswith(edit['suffix'])
                    inverse = inverse[:-len(edit['suffix'])]
                else:
                    assert len(edit['after_positions']) == edit['occurrences']
                    for pos in reversed(edit['after_positions']):
                        assert inverse[pos:pos + len(edit['after'])] == edit['after']
                        inverse = inverse[:pos] + edit['before'] + inverse[pos + len(edit['after']):]
            assert inverse == before
            funcs = py_functions if ledger['check'] == 'PYTHON_AST' else gd_functions
            old, new = funcs(before), funcs(after)
            changed = sorted(name for name in old if old[name] != new[name])
            assert changed == ledger['changed_functions']
            assert sorted(set(new) - set(old)) == ledger['added_functions']
            report['checks'].append(dict(check='inverse_and_old_function_identity', ledger=pin(path),
                changed=changed, conserved=len(old)-len(changed), result='PASS'))
        sink = (S / 'after-source/native_random_observer_sink_v7.gd').read_text()
        collector = (S / 'collector.gd').read_text()
        sf, cf = gd_functions(sink), gd_functions(collector)
        assert sf['clock_pass'].index('source_tail_first_idle != null') < sf['clock_pass'].index('File.new()')
        assert sf['clock_pass'].index('file.flush()') < sf['clock_pass'].index('source_tail_note_pass(')
        assert sf['source_tail_note_pass'].index('source_tail_first_idle != null') < sf['source_tail_note_pass'].index('source_tail_last =')
        assert 'source_tail_count >= 2' in sf['source_tail_note_pass']
        assert 'source_cleanup != null' in sf['source_mark_cleanup']
        assert 'source_tail_anchor = 0' in sf['source_tail_mark_cleanup']
        assert cf['on_idle_source_cut'].index('source_cut_frozen = true') < cf['on_idle_source_cut'].index('stable_snapshot()')
        assert all(token not in cf['finish_source_cut'] for token in ('stable_snapshot(', 'getStats(', 'source_runtime_snapshot(', 'call_deferred('))
        assert 'EXPECTED_ONLY_NOT_MODEL_INPUT' in sf['source_runtime_snapshot']
        assert 'SOURCE_MISSED_FIRST_IDLE_CUT' not in sink
        assert 'two_future_physics_signals' not in sink
        report['checks'].append(dict(check='C07_C20_C23_C26_producer_once_latch_and_readonly', result='SOURCE_PASS_NO_LANGUAGE_EXECUTION'))
        old_sink = gd_functions((R/'data/phase375-food-hook-source/after-source/native_random_observer_sink_v7.gd').read_text())
        old_collector = gd_functions((R/'data/phase370-oracle-source/collector.gd').read_text())
        for name in ('king_runtime_snapshot', 'source_runtime_snapshot', 'ui_controls'):
            assert sf[name] == old_sink[name]
        assert cf['stable_snapshot'] == old_collector['stable_snapshot']
        schema = (R/'tests/phase391_king_observer_schema.py').read_text()
        old_schema = (R/'tests/phase375_king_observer_schema.py').read_text()
        def assignment(text, name):
            n = next(n for n in ast.parse(text).body if isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
            return ast.dump(n.value, include_attributes=False)
        assert assignment(schema, 'MATRIX') == assignment(old_schema, 'MATRIX')
        def prefix(text):
            return text[:text.index('func ')]
        assert re.search(r'const SITES = (.*?)(?=\n\n)', prefix(sink), re.S).group(1) == re.search(r'const SITES = (.*?)(?=\n\n)', prefix((R/'data/phase375-food-hook-source/after-source/native_random_observer_sink_v7.gd').read_text()), re.S).group(1)
        report['checks'].append(dict(check='C23_C31_getters_107_sites_matrix_UI_conserved', result='SOURCE_PASS_OLD_SUCCESS_NOT_RERUN'))
        tuple_value = json.loads(verify(freeze['active_source_tuple']).read_text())
        declared = {row['path']:row for row in freeze['files']}
        for key, row in tuple_value.items():
            if type(row) is dict:
                assert declared[row['path']] == row
                verify(row)
        assert tuple_value['collector'] == freeze['collector'] and tuple_value['schema_module'] == freeze['schema_module']
        host = (R/'tests/phase391_oracle_host.py').read_text()
        hf = py_functions(host)
        assert 'validate_terminal_receipt' in hf['read_terminal_expected_controls']
        assert 'validate_terminal_diagnostics' in hf['read_terminal_expected_controls']
        assert 'validate_active_source_tuple' in hf['load_terminal_schema']
        assert 'read_terminal_expected_controls' in hf['collect_capture_metadata']
        assert 'terminal is not None' in host
        report['checks'].append(dict(check='C18_C31_real_tuple_host_consumer_paths', result='SOURCE_PASS_NOT_WHOLEHOST'))
        prep = ast.parse((R/'tests/phase391_prepare_source.py').read_text())
        whitelist = next(ast.literal_eval(n.value) for n in prep.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HISTORICAL_HARDLINK_FIXTURES' for t in n.targets))
        assert whitelist == {'data/phase362-independent-source-review/installer-first-001/alias.txt', 'data/phase362-independent-source-review/installer-first-001/tiny-target/example.txt'}
        df = next(n for n in prep.body if isinstance(n,ast.FunctionDef) and n.name=='desc')
        assert ast.literal_eval(df.args.defaults[0]) is False
        assert 'info.st_nlink == 2' in ast.unparse(df) and 'info.st_nlink == 1' in ast.unparse(df)
        assert 'historical_fixture' not in schema and 'historical_fixture' not in host
        report['checks'].append(dict(check='author_only_two_historical_aliases_no_active_bypass', result='SOURCE_PASS'))
        origins=json.loads((R/'data/phase392-independent-preparation/source-evidence.json').read_text())
        for row in origins['selected_old_sources_actual_pins']:
            verify(row)
        assert tuple_value['projector_source_origin']['path']=='tests/phase361_king_projection_sealer.py'
        assert 'no_model_stop_command=True' in schema
        report['checks'].append(dict(check='C32_old_model_driver_and_closed_projection_origins', result='SOURCE_ONLY_NO_MODEL_OR_ACTIVATION_DEATH_POSITIVE'))
        report['status']='STATIC392_FROZEN391_COMPONENT_BOUNDARY_PASS_DYNAMIC_PENDING'
    except BaseException as exc:
        report['status']='STATIC392_BLOCKED'
        report['failure']=dict(error=repr(exc), traceback=traceback.format_exc())
    (D/'review.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),failure=report['failure']),indent=2))
    if report['failure']:
        raise SystemExit(1)


if __name__=='__main__':
    main()
