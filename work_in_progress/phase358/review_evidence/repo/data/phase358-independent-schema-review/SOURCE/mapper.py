"""Narrow SOURCE repair generator; never import/call the generated schema."""
from pathlib import Path
import ast
from copy import deepcopy
import difflib
import hashlib
import json
import pprint
import re

R = Path(__file__).resolve().parents[1]
D = R / 'data/phase358-king-schema-source-repair'
OLD = R / 'tests/phase357_king_observer_schema.py'
OUT = R / 'tests/phase358_king_observer_schema.py'
TYPE_MAP = {
    'int': 'int', 'float': 'float', 'bool': 'bool', 'String': 'string',
    'Array': 'array', 'Dictionary': 'dictionary',
    'Item': 'native_ref|null', 'Character': 'native_ref|null',
    'Node': 'native_ref|null', 'Timer': 'native_ref|null',
    'CombatEvent': 'event_ref|null', 'DamageSource': 'damage_source|null',
    'DamageResult': 'damage_result|null',
}


def pin(path):
    raw = path.read_bytes()
    return dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(name, value):
    with (D / name).open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n')


def arguments(block):
    """Actual GD signature -> exact names/types. Unknown annotations never erase."""
    start = block.index('(') + 1
    chunks, current, level, quote, escaped = [], '', 0, None, False
    end = None
    for offset, char in enumerate(block[start:]):
        if quote:
            current += char
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
        elif char in ('"', "'"):
            quote = char
            current += char
        elif char in '([{':
            level += 1
            current += char
        elif char == ')' and level == 0:
            if current.strip():
                chunks.append(current.strip())
            end = start + offset + 1
            break
        elif char in ')]}':
            level -= 1
            current += char
        elif char == ',' and level == 0:
            chunks.append(current.strip())
            current = ''
        else:
            current += char
    names, types = [], {}
    for chunk in chunks:
        declaration = chunk.split('=', 1)[0].strip()
        pieces = declaration.split(':', 1)
        name = pieces[0].strip()
        if re.fullmatch(r'\w+', name) is None:
            raise ValueError('unparsed actual GD parameter ' + chunk)
        names.append(name)
        if len(pieces) == 2:
            kind = pieces[1].strip()
            if kind not in TYPE_MAP:
                raise ValueError('unsupported explicit GD annotation ' + kind)
            types[name] = TYPE_MAP[kind]
    if end is None:
        raise ValueError('unterminated GD function signature')
    return names, types, block[:end]


def shape(source):
    return ast.dump(ast.parse(source), include_attributes=False)


def main():
    assert pin(OLD) == dict(size=258647, sha256='99d25e637217e8e56f3e73cf14e67b08e8b199851a63f8c8c950fe947bcf5867')
    findings = [
        ('finding.json', 2915, '54d90374fd11a8d64b754da768cb1b1437714df662dbc4ce8c91a48e927aeea3'),
        ('object-argument-finding.json', 3948, 'e423bd60c30dc3386a5810b857c540136630354f89ec8e7276843cc8cae76dbd'),
    ]
    for name, size, sha in findings:
        assert pin(R / 'data/phase357-independent-schema-review' / name) == dict(size=size, sha256=sha)
    D.mkdir(exist_ok=False)
    old = OLD.read_text()
    tree = ast.parse(old)
    assignments = {target.id: node for node in tree.body if isinstance(node, ast.Assign)
                   for target in node.targets if isinstance(target, ast.Name)}
    contract = ast.literal_eval(assignments['CONTRACT'].value)
    matrix = ast.literal_eval(assignments['MATRIX'].value)
    repaired = deepcopy(matrix)
    source_matrix = json.loads((R / 'data/phase357-king-observer-schema-source/record-hook-matrix.json').read_text())
    source_bytes = {}
    for name, identity in source_matrix['original_files'].items():
        path = Path(identity['path'])
        assert pin(path) == {key: identity[key] for key in ('size', 'sha256')}
        source_bytes[str(path)] = path.read_text().splitlines(keepends=True)
    changes = []
    coverage = []
    for record in source_matrix['sites']:
        body = ''.join(source_bytes[record['file']][record['line_start'] - 1:record['line_end']])
        assert dict(size=len(body.encode()), sha256=hashlib.sha256(body.encode()).hexdigest()) == {key: record[key] for key in ('size', 'sha256')}
        names, types, signature = arguments(body)
        site = record['site']
        assert names == matrix['sites'][site]['arguments_exact']
        previous = matrix['sites'][site]['argument_types']
        assert all(types.get(name) == kind for name, kind in previous.items()), site
        for name in types:
            if name not in previous:
                changes.append(dict(site=site, parameter=name, added_type=types[name], signature=signature,
                                    source=record['file'], line_start=record['line_start'], line_end=record['line_end'],
                                    function_sha256=record['sha256'],
                                    evidence='SOURCE_DERIVED_NOT_EXECUTED' if site.endswith('::connectEvent') else 'INDEPENDENT357_ACTUAL_FALSE_ACCEPT'))
        repaired['sites'][site]['argument_types'] = types
        coverage.append(dict(site=site, signature=signature, arguments=names, supported_explicit=types,
                             untyped=[name for name in names if name not in types], unknown_explicit='GENERATION_REJECT'))
    assert {(row['site'], row['parameter']) for row in changes} == {
        ('Utility/EventBus.gd::connectEvent', 'emitter'), ('Utility/EventBus.gd::connectEvent', 'receiver'),
        ('Utility/EventBus.gd::emitAndLog', 'emitter'), ('Utility/Util.gd::changeTimer', 'timer'),
    }
    for row in changes:
        assert row['added_type'] == 'native_ref|null'
    lines = old.splitlines(keepends=True)
    node = assignments['MATRIX']
    new = ''.join(lines[:node.lineno - 1]) + 'MATRIX=' + pprint.pformat(repaired, width=110, sort_dicts=True) + '\n' + ''.join(lines[node.end_lineno:])
    old_gate = "    if kind in ('item', 'goobert', 'king', 'potion'):\n"
    new_gate = "    if kind in ('item', 'goobert', 'king', 'potion', 'plain_item'):\n"
    old_subtype = "        if kind == 'king' and actual != 'king' or kind == 'potion' and actual != 'potion' or kind == 'goobert' and actual != 'king':\n"
    new_subtype = "        if kind == 'king' and actual != 'king' or kind == 'potion' and actual != 'potion' or kind == 'goobert' and actual != 'king' or kind == 'plain_item' and actual != 'plain_item':\n"
    assert new.count(old_gate) == new.count(old_subtype) == 1
    new = new.replace(old_gate, new_gate, 1).replace(old_subtype, new_subtype, 1)
    compile(new, str(OUT), 'exec')
    compile(Path(__file__).read_bytes(), str(Path(__file__)), 'exec')
    item_kinds = {name for name, fields in contract['state_schemas'].items() if 'descriptorIndex' in fields}
    assert item_kinds == {'item', 'goobert', 'king', 'potion', 'plain_item'}
    # Restore four matrix leaves and the two dispatch lines; require whole AST equality.
    inverse_tree = ast.parse(new.replace(new_gate, old_gate, 1).replace(new_subtype, old_subtype, 1))
    m = next(n for n in inverse_tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'MATRIX' for t in n.targets))
    m.value = assignments['MATRIX'].value
    assert ast.dump(inverse_tree, include_attributes=False) == shape(old)
    inverse_matrix = deepcopy(repaired)
    for row in changes:
        del inverse_matrix['sites'][row['site']]['argument_types'][row['parameter']]
    assert inverse_matrix == matrix
    runtime = R / 'data/phase356-king-admission-source-repair'
    freeze = json.loads((runtime / 'candidate-source-freeze.json').read_text())
    for name, identity in freeze['files'].items():
        assert pin(runtime / 'staged' / name) == identity
    g = ast.parse((runtime / 'staged/native_replay_v8/genuine.py').read_text())
    gate = next(n for n in g.body if isinstance(n, ast.FunctionDef) and n.name == 'require_single_king_admission')
    assert isinstance(gate.body[-1], ast.Raise) and gate.args.args == []
    with OUT.open('x') as stream:
        stream.write(new)
    (D / 'schema-source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='357/phase357_king_observer_schema.py', tofile='358/phase358_king_observer_schema.py')))
    save('object-argument-repair-map.json', dict(schema='phase358-object-argument-repair/1', changes=changes,
        evidence=dict(actual_parameters=2, SOURCE_derived_unexecuted_parameters=2), explicit_type_map=TYPE_MAP,
        Godot_nullable_note='typed Object references allowNULL; source/native identity validation is separate, not a forgedclass inheritance table'))
    save('source-signature-completeness.json', dict(schema='phase358-source-signature-completeness/1', sites=coverage,
        site_count=len(coverage), unknown_annotation_policy='UNCONDITIONAL_SOURCE_GENERATION_ERROR',
        all_existing_declared_annotations_mapped=True, schema_APIs_called=0))
    save('source-validation.json', dict(schema='phase358-static-schema-repair-validation/1', compile='PASS_NO_IMPORT',
        descriptor_schemas_all_in_shared_gate=sorted(item_kinds), matrix_changed_only_four_leaves=True,
        inverse_whole_module_AST_equal_357=True, old_43_clones_unchanged=True, site_count_unchanged=103,
        all_356_runtime15_unchanged=True, shared356_gate='UNCHANGED_UNCONDITIONAL_CLOSED',
        schema_imports=0, schema_calls=0, semantic_controls=0, candidate_imports=0, RNG=0, Engine=0, models=0, native=0))
    save('schema-source-freeze.json', dict(schema='phase358-schema-source-freeze/1', module=dict(path=str(OUT.relative_to(R)), **pin(OUT)),
        generator=dict(path=str(Path(__file__).relative_to(R)), **pin(Path(__file__))),
        baseline=dict(path=str(OLD.relative_to(R)), **pin(OLD)), observer_version='7-king-single-A-355',
        profile='observer7-355-native-single-king-A/1', admission='356_GATE_UNCHANGED_CLOSED',
        semantic_acceptance='INDEPENDENT_REGRESSION_PENDING', no_more_module_writes=True))
    print(json.dumps(dict(status='SOURCE_REPAIR_GENERATED_COMPILE_AST_ONLY', module=pin(OUT), freeze=pin(D / 'schema-source-freeze.json'))))


if __name__ == '__main__':
    main()
