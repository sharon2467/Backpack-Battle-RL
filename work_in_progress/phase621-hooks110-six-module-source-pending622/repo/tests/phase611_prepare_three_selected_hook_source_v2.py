"""One isolated Source derivation; never imports the generated schema."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import re
import traceback

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'data/phase572-mixed-observer-source-v2'
OUT = ROOT / 'data/phase610-three-selected-hook-source-v2'
VERSION = '7-mixed-modifiers-A-610-hooks110'
PROFILE = 'observer7-mixed-modifiers-A-hooks110-native-tape/1'


def pin(path):
    path = Path(path)
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    with Path(path).open('x') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def py_functions(text):
    return {n.name: ast.get_source_segment(text, n) for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}


def gd_functions(text):
    lines = text.splitlines(keepends=True)
    result = {}
    for start, line in enumerate(lines):
        m = re.match(r'^func ([A-Za-z_][A-Za-z0-9_]*)\(', line)
        if not m:
            continue
        end = start + 1
        while end < len(lines) and (not lines[end].strip() or lines[end].startswith(('\t', ' '))):
            end += 1
        assert m.group(1) not in result, 'unique top-level GD function'
        result[m.group(1)] = ''.join(lines[start:end])
    return result


class Delta:
    def __init__(self, text):
        self.text, self.changes = text, []

    def replace(self, before, after, label):
        assert before != after and self.text.count(before) == 1, label
        at = self.text.index(before)
        self.text = self.text[:at] + after + self.text[at + len(before):]
        self.changes.append(dict(offset=at, before=before, after=after, label=label))

    def py_assignment(self, name, value):
        nodes = [n for n in ast.parse(self.text).body if isinstance(n, ast.Assign)
                 and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
        assert len(nodes) == 1, 'one exact top-level assignment:' + name
        node = nodes[0]
        assert node.col_offset == 0, 'top-level physical line starts at column0:' + name
        lines = self.text.splitlines(keepends=True)
        start = sum(len(line) for line in lines[:node.lineno - 1])
        end = sum(len(line) for line in lines[:node.end_lineno])
        assert start > 0 and self.text[start - 1] == '\n', 'preceding full-line LF:' + name
        assert self.text[end - 1] == '\n', 'terminating full-line LF:' + name
        assert node.end_col_offset == len(lines[node.end_lineno - 1].removesuffix('\n').encode('utf-8')), 'complete statement line:' + name
        before = self.text[start - 1:end]
        self.replace(before, '\n' + name + ' = ' + repr(value) + '\n', 'exact AST physical-line assignment:' + name)

    def inverse(self):
        text = self.text
        for row in reversed(self.changes):
            at = row['offset']
            assert text[at:at + len(row['after'])] == row['after']
            text = text[:at] + row['before'] + text[at + len(row['after']):]
        return text


def main():
    assert not OUT.exists(), 'immutable new output namespace'
    OUT.mkdir()
    try:
        (OUT / 'after-source').mkdir()
        (OUT / 'schema').mkdir()
        (OUT / 'inverse').mkdir()
        source_freeze = read(OLD / 'combined-source-freeze.json')
        assert pin(OLD / 'combined-source-freeze.json')['sha256'] == '8db47db5bfa19a2bd3607192a5f1e9b3054f65951f44ba0fed9447715f09e254'
        host_freeze = read(ROOT / 'data/phase590-case030-host-restore-source/combined-source-freeze.json')
        gaps = read(ROOT / 'data/phase604-selected-hook-gap-design/hook-gaps.json')
        census = read(ROOT / 'data/phase604-selected-hook-gap-design/selected-script-census.json')
        assert len(gaps['new_sites']) == 3 and census['unique_root_and_ancestor_scripts'] == 15
        additions = {row['site']: row['descriptor'] for row in gaps['new_sites']}
        assert additions == {'Items/MagicStaff.gd::onPreDealDamage_early': 32,
                             'Items/Exclusive/ThornShortbow.gd::onDealtDamage': 233,
                             'Items/Exclusive/LuckyShortbow.gd::onPreDealDamage_early': 234}
        old_sink_path = ROOT / source_freeze['paths']['native_random_observer_sink_v7.gd']['after_path']
        old_sink = old_sink_path.read_text()
        assert {k: pin(old_sink_path)[k] for k in ('size', 'sha256')} == source_freeze['paths']['native_random_observer_sink_v7.gd']['after']
        old_schema_path = ROOT / source_freeze['schema_module']['path']
        old_schema = old_schema_path.read_text()
        assert pin(old_schema_path) == source_freeze['schema_module']
        sink_delta, schema_delta = Delta(old_sink), Delta(old_schema)
        site_lines = [line for line in old_sink.splitlines() if line.startswith('const SITES = ')]
        assert len(site_lines) == 1
        old_sites = json.loads(site_lines[0].split(' = ', 1)[1])
        old_matrix_node = next(n for n in ast.parse(old_schema).body if isinstance(n, ast.Assign)
                               and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'MATRIX')
        old_matrix = ast.literal_eval(old_matrix_node.value)
        assert len(old_sites) == len(old_matrix['sites']) == 107 and set(old_sites) == set(old_matrix['sites'])
        assert not set(additions) & set(old_sites)
        new_sites, new_matrix = copy.deepcopy(old_sites), copy.deepcopy(old_matrix)
        method_proofs = []
        for site, descriptor in additions.items():
            target, function = site.split('::')
            installed = host_freeze['paths'][target]
            assert installed == source_freeze['paths'][target]
            path = ROOT / installed['after_path']
            assert {k: pin(path)[k] for k in ('size', 'sha256')} == installed['after']
            text = path.read_text()
            segment = gd_functions(text)[function]
            assert len(re.findall(r'NativeRandomObserver\.entry\("' + re.escape(site) + r'"', segment)) == 1
            assert len(re.findall(r'NativeRandomObserver\.leave\("' + re.escape(site) + r'"', segment)) == 1
            assert 'func ' + function + '(damageRes: DamageResult):' in segment
            stripped = ''.join(line for line in text.splitlines(keepends=True)
                               if not re.match(r'^\tNativeRandomObserver\.(?:entry|leave)\(', line))
            # The accepted359 instrumenter also appended exactly one blank EOF LF.
            # This is its exact inverse, never a general rstrip/whitespace fallback.
            assert stripped.endswith('\n\n')
            stripped = stripped[:-1]
            assert dict(size=len(stripped.encode()), sha256=hashlib.sha256(stripped.encode()).hexdigest()) == installed['before']
            original_segment = gd_functions(stripped)[function]
            assert not re.search(r'^\s+return(?:\s|$)', original_segment, re.M), 'only implicit return'
            new_sites[site] = dict(channel='runtime', state_schema='item')
            new_matrix['sites'][site] = dict(channel='runtime', state_schema='item',
                arguments_exact=['damageRes'], argument_types={'damageRes': 'damage_result'}, explicit_returns=[],
                edges=['enter', 'return_implicit'], source=target, function=function,
                function_sha256=hashlib.sha256(original_segment.encode()).hexdigest(),
                function_size=len(original_segment.encode()))
            method_proofs.append(dict(site=site, descriptor=descriptor, installed_source=pin(path),
                original_file=installed['before'], instrumented_method_sha256=hashlib.sha256(segment.encode()).hexdigest(),
                original_method_sha256=hashlib.sha256(original_segment.encode()).hexdigest(),
                instrumentation_removed_full_file_equals_original=True, old_instrumenter_extra_EOF_LF_removed=1,
                new_instrumentation=0,
                Native_hit=(descriptor == 233), evidence='600 unknown selected site seq4906' if descriptor == 233 else 'STATIC_ONLY'))
        assert len(new_sites) == len(new_matrix['sites']) == 110
        assert {key: new_sites[key] for key in old_sites} == old_sites
        assert {key: new_matrix['sites'][key] for key in old_matrix['sites']} == old_matrix['sites']
        assert new_matrix['Timer_API_statement_sites'] == old_matrix['Timer_API_statement_sites']
        assert new_matrix['extra_edges'] == old_matrix['extra_edges']
        sink_delta.replace(site_lines[0], 'const SITES = ' + json.dumps(new_sites, sort_keys=True), 'old107 plus exact3 runtime/item entries')
        sink_delta.replace('const RNG_INITIAL_PROFILE = "7-mixed-modifiers-A-572"',
                           'const RNG_INITIAL_PROFILE = "' + VERSION + '"', 'declared observer Source version only')
        sink_delta.replace('#111 passive source hooks plus readonly SceneTree frame-signal clock sampler; no gameplay signal subscriptions.',
                           '#110 accepted method sites (old107 plus selected3); readonly clock sampler; no gameplay signal subscriptions.',
                           'correct declared accepted-method count only')
        schema_delta.py_assignment('MATRIX', new_matrix)
        for name, value in [('VERSION', VERSION), ('PROFILE', PROFILE),
                            ('SINGLE_KING_GENUINE_PROFILE', PROFILE), ('SINGLE_KING_OBSERVER_VERSION', VERSION)]:
            schema_delta.py_assignment(name, value)
        nodes = [n for n in ast.parse(schema_delta.text).body if isinstance(n, ast.FunctionDef) and n.name == 'validate_record']
        assert len(nodes) == 1
        old_record = ast.get_source_segment(schema_delta.text, nodes[0])
        anchor = "        state = payload['state']\n"
        assert old_record.count(anchor) == 1
        receiver_gate = """        selected_damage_receivers = {
            'Items/MagicStaff.gd::onPreDealDamage_early': 32,
            'Items/Exclusive/ThornShortbow.gd::onDealtDamage': 233,
            'Items/Exclusive/LuckyShortbow.gd::onPreDealDamage_early': 234,
        }
        if site in selected_damage_receivers:
            if row['subject']['class'] != 'RigidBody2D':
                raise ValueError('selected damage hook receiver class must be exact RigidBody2D')
            expected_descriptor = {'type': 'int', 'decimal': str(selected_damage_receivers[site])}
            if state['descriptorIndex'] != expected_descriptor:
                raise ValueError('selected damage hook strict INT descriptor mismatch')
"""
        new_record = old_record.replace(anchor, anchor + receiver_gate)
        schema_delta.replace(old_record, new_record, 'only three selected receivers strict INT and exact native class')
        sink_path = OUT / 'after-source/native_random_observer_sink_v7.gd'
        schema_path = OUT / 'schema/phase610_mixed_observer_schema.py'
        sink_path.write_text(sink_delta.text)
        schema_path.write_text(schema_delta.text)
        assert sink_delta.inverse() == old_sink and schema_delta.inverse() == old_schema
        old_gd, new_gd = gd_functions(old_sink), gd_functions(sink_delta.text)
        assert old_gd == new_gd, 'all sink method bodies exact'
        old_py, new_py = py_functions(old_schema), py_functions(schema_delta.text)
        assert set(old_py) == set(new_py)
        changed_py = [name for name in old_py if old_py[name] != new_py[name]]
        assert changed_py == ['validate_record'], changed_py
        assert new_record.replace(receiver_gate, '') == old_py['validate_record']
        # Parse/compile only. Never exec or import generated Python.
        compile(schema_path.read_bytes(), str(schema_path), 'exec')
        for label, delta, before, target in [('sink', sink_delta, old_sink, sink_path), ('schema', schema_delta, old_schema, schema_path)]:
            save(OUT / 'inverse' / (label + '.json'), dict(schema='phase610-full-inverse/1', target=pin(target),
                  before_sha256=hashlib.sha256(before.encode()).hexdigest(), replacements=delta.changes, exact=True))
            (OUT / 'inverse' / (label + '.patch')).write_text(''.join(difflib.unified_diff(before.splitlines(keepends=True), delta.text.splitlines(keepends=True), fromfile='old573v2', tofile=str(target.relative_to(ROOT)))))
        paths = copy.deepcopy(source_freeze['paths'])
        paths['native_random_observer_sink_v7.gd']['after_path'] = str(sink_path.relative_to(ROOT))
        paths['native_random_observer_sink_v7.gd']['after'] = {k: pin(sink_path)[k] for k in ('size', 'sha256')}
        assert len(paths) == 76
        exact_old_targets = [name for name in paths if paths[name] == source_freeze['paths'][name]]
        assert len(exact_old_targets) == 75
        artifacts = copy.deepcopy(source_freeze['artifacts'])
        count = len(paths) + len(artifacts)
        total = sum(row['after']['size'] for row in paths.values()) + sum(row['size'] for row in artifacts.values())
        assert count == 79
        producer = pin(Path(__file__))
        native_patch = dict(schema='phase610-selected-three-hook-native-patch-source/1', observer_version=VERSION,
                            profile=PROFILE, paths=paths, sink=pin(sink_path), producer=producer,
                            terminal_policy=source_freeze['terminal_policy'], status='SOURCE_ONLY_NOT_OPERATIONAL')
        save(OUT/'native-patch-source.json', native_patch)
        old_tuple = read(OLD/'source-tuple.json')
        new_tuple = copy.deepcopy(old_tuple)
        new_tuple.update(schema='phase610-selected-three-hook-source-tuple/1', observer_version=VERSION, profile=PROFILE,
                         producer=producer, sink=pin(sink_path), schema_module=pin(schema_path),
                         native_patch=pin(OUT/'native-patch-source.json'), project_install_count=count,
                         project_install_source_bytes=total, proposed_run=None,
                         actual_Native_UID_cut_cache_clock_setup='UNOBSERVED_FOR_FUTURE_COMPLETE_RECORD;partial030_not_admitted')
        assert new_tuple['host_execution_ready'] is False and new_tuple['operational_authority'] is False
        save(OUT/'source-tuple.json', new_tuple)
        old_install = read(OLD/'install-targets.json')
        for row in artifacts.values():
            assert pin(ROOT / row['path']) == row, 'exact reused project artifact'
        for row in old_install['case_inputs']:
            assert pin(ROOT / row['source']['path']) == row['source'], 'exact reused case input'
        targets = []
        for target, row in paths.items():
            targets.append(dict(target=target, source=dict(path=row['after_path'], **row['after']), before=row['before']))
        for target, row in artifacts.items():
            targets.append(dict(target=target, source=row, before='ACTUAL_INSTALL_PREIMAGE_UNOBSERVED'))
        save(OUT/'install-targets.json', dict(schema='phase610-source-install-targets/1', project=targets,
             case_inputs=old_install['case_inputs'], project_install_count=count,project_install_source_bytes=total,
             actual_pool_preimages_verified=False,install_or_execute_authorized=False,host_ready=False))
        save(OUT/'site-census.json', dict(schema='phase610-method-site-census/1',old_sites=107,new_sites=110,
             old_sites_deep_equal=True,old_MATRIX_deep_equal=True,selected_descriptor_ids=[1,5,11,14,22,32,162,164,231,233,234,385],
             selected_script_count=15,selected_inserted_item_sites=26,selected_missing_after=[],additions=method_proofs,
             all_sites=new_sites,new_method_instrumentation=0,global_unselected_hooks_added=0,
             evidence=pin(ROOT/'data/phase604-selected-hook-gap-design/selected-script-census.json')))
        save(OUT/'conservation.json', dict(schema='phase610-source-conservation/1',all_sink_functions_exact=sorted(old_gd),
             all_schema_helpers_exact=[name for name in old_py if name not in changed_py],schema_changed_functions=changed_py,
             receiver_gate_removal_restores_old_function=True,old107_SITES_deep_equal=True,old107_MATRIX_deep_equal=True,
             Timer_API_statement_sites_exact=True,MATRIX_extra_edges_exact=True,CONTRACT_exact=True,
             exact_old_project_targets=exact_old_targets,exact_old_project_target_count=75,
             changed_project_targets=['native_random_observer_sink_v7.gd'],artifacts_exact=True,collector_exact=True,
             case_inputs_exact=True,all3_method_sources_exact=method_proofs,full_inverse=True,
             identity_changes=dict(sink=['RNG_INITIAL_PROFILE','header_count'],schema=['VERSION','PROFILE','SINGLE_KING_GENUINE_PROFILE','SINGLE_KING_OBSERVER_VERSION']),
             future_attempt_selected=False))
        save(OUT/'metadata-rebinding.json',dict(schema='phase610-metadata-rebinding/1',
             old_tuple=old_tuple,new_tuple=new_tuple,old_source_freeze=pin(OLD/'combined-source-freeze.json'),
             old_source_owner=pin(OLD/'source-owner.json'),old_native_patch=pin(OLD/'native-patch-source.json'),
             historical_single001_authority_exhausted=True,new_attempt=None,
             implementation_scope_excludes=['consumer','host','restore','Original','pool']))
        save(OUT/'compile-only.json',dict(schema='phase610-source-compile/1',objects=[pin(schema_path)],
             schema_imports=0,helper_calls=0,tests=0,GD_parse=0,Native=0,models=0,Expected=0,pool_operations=0,generation_attempts=1,cumulative_generation_attempts=2))
        save(OUT/'source-authority.json',dict(schema='phase610-source-authority/1',
             old_source_owner=pin(OLD/'source-owner.json'),old_source_freeze=pin(OLD/'combined-source-freeze.json'),
             design_owner=pin(ROOT/'data/phase604-selected-hook-gap-design/owned-files.json'),
             independent_design=pin(ROOT/'data/phase609-independent-hook-design-review/review.json'),
             release=pin(ROOT/'data/phase610-root-three-hook-source-release/release.json'),
             current_run_authority=None,scope='SOURCE_ONLY_NO_NEW_ATTEMPT_AUTHORITY'))
        # Tuple has no containing freeze/owner hash. Keep the inherited closed Source graph as provenance.
        new_files = list(source_freeze['files']) + [pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
        new_files += [producer,pin(ROOT/'docs/phase610_three_selected_hook_source_spec.md'),
                      pin(ROOT/'data/phase610-root-three-hook-source-release/release.json'),
                      pin(ROOT/'data/phase609-independent-hook-design-review/review.json'),
                      pin(ROOT/'data/phase604-selected-hook-gap-design/owned-files.json'),
                      pin(ROOT/'docs/phase611_three_hook_source_preparer_repair_spec.md'),
                      pin(ROOT/'data/phase611-root-three-hook-producer-v2-release/release.json'),
                      pin(ROOT/'data/phase610-source-first-error-freeze/owned-files.json')]
        unique = {}
        for row in new_files:
            assert row['path'] not in unique or unique[row['path']] == row, 'one fixed Source identity per path'
            unique[row['path']] = row
        new_freeze = copy.deepcopy(source_freeze)
        new_freeze.update(schema='phase610-selected-three-hook-source-freeze/1',observer_version=VERSION,profile=PROFILE,
                          active_source_tuple=pin(OUT/'source-tuple.json'),paths=paths,artifacts=artifacts,
                          schema_module=pin(schema_path),files=list(unique.values()),project_install_count=count,
                          project_install_source_bytes=total)
        save(OUT/'combined-source-freeze.json',new_freeze)
        save(OUT/'future-binding-pins.json',dict(schema='phase610-future-binding-pins/1',
             sink=pin(sink_path),schema_module=pin(schema_path),active_source_tuple=pin(OUT/'source-tuple.json'),
             observer_source_freeze=pin(OUT/'combined-source-freeze.json'),producer=producer,
             source_acceptance_receipt=None,new_run=None,new_host_source=None,new_Root_config=None,
             current_closed_reader_context=pin(ROOT/'data/phase582-root-candidate-context-binding/source-context-candidate-bound.json'),
             changes_later='New immutable reader context/schema identity binding;exact host run/config requires separate explicit Root release. No consumer/host code changed here.',
             missing_operational_binding_is_rejection=True,Native_authorized=False))
        # Owner covers all generated files and inherited Source descriptors, never itself.
        owner_rows = list(unique.values()) + [pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()]
        final_rows = {}
        for row in owner_rows:
            assert row['path'] not in final_rows or final_rows[row['path']] == row
            final_rows[row['path']] = row
        save(OUT/'source-owner.json',dict(schema='phase610-source-owner/1',files=list(final_rows.values()),
             no_more_writes=True,status='SOURCE_GENERATED_NOT_INDEPENDENTLY_ACCEPTED'))
        print(json.dumps(dict(status='GENERATED_COMPILED_NOT_IMPORTED',owner=pin(OUT/'source-owner.json'),
                              freeze=pin(OUT/'combined-source-freeze.json'),target_count=count,install_bytes=total)))
    except BaseException as exc:
        save(OUT/'first-error.json',dict(schema='phase610-source-first-error/1',type=type(exc).__name__,
             message=str(exc),traceback=traceback.format_exc(),generation_attempts=1,cumulative_generation_attempts=2,schema_imports=0,
             helper_calls=0,GD_parse=0,Native=0,Expected=0,pool=0))
        save(OUT/'partial-owner.json',dict(schema='phase610-partial-source-owner/1',
             files=[pin(p) for p in sorted(OUT.rglob('*')) if p.is_file()],no_more_writes=True))
        raise


if __name__ == '__main__':
    main()
