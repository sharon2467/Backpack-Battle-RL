"""391 SOURCE text derivation/AST/inverse/pins only. Never imports generated modules."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import re
import stat
import traceback

R = Path(__file__).resolve().parents[1]
D = R/'data/phase391-terminal-source'
POLICY = 'first-actual-idle-after-at-least-two-future-physics/1'
VERSION = '7-king-single-A-390'
PROFILE = 'observer7-390-native-single-king-A/1'
ORIGIN = R/'data/phase380-payload-source/combined-source-freeze.json'
HISTORICAL_HARDLINK_FIXTURES = {'data/phase362-independent-source-review/installer-first-001/alias.txt',
    'data/phase362-independent-source-review/installer-first-001/tiny-target/example.txt'}


def desc(path, historical_fixture=False):
    assert path.is_relative_to(R) and not any(p.is_symlink() for p in (path, *path.parents))
    info = path.stat(); assert stat.S_ISREG(info.st_mode)
    if historical_fixture:
        assert str(path.relative_to(R)) in HISTORICAL_HARDLINK_FIXTURES and info.st_nlink == 2
    else:
        assert info.st_nlink == 1
    raw = path.read_bytes()
    return dict(path=str(path.relative_to(R)), size=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def save(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def write(path, text):
    with path.open('x') as stream: stream.write(text)


def py_functions(text):
    return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(text).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


def py_span(text, name):
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ''.join(text.splitlines(True)[node.lineno-1:node.end_lineno])


def gd_functions(text):
    # SOURCE lexical function-body conservation; no Godot parser/process is invoked.
    result = {}
    for match in re.finditer(r'^func (\w+)\([^\n]*\):\n(?:[\t ][^\n]*\n|\n)*', text, re.M):
        assert match.group(1) not in result
        result[match.group(1)] = match.group(0).rstrip()
    assert len(result) == len(re.findall(r'^func ', text, re.M))
    return result


class Delta:
    def __init__(self, path, kind):
        self.path = path; self.before = path.read_text(); self.text = self.before; self.edits = []; self.kind = kind
    def edit(self, before, after, count=1):
        assert self.text.count(before) == count, (self.path, before[:160], self.text.count(before), count)
        self.text = self.text.replace(before, after)
        self.edits.append(dict(before=before, after=after, occurrences=count))
    def append(self, text):
        self.text += text; self.edits.append(dict(suffix=text))
    def finish(self, path, exceptions):
        inverse = self.text
        for row in reversed(self.edits):
            if 'suffix' in row:
                assert inverse.endswith(row['suffix']); inverse = inverse[:-len(row['suffix'])]
            else:
                assert inverse.count(row['after']) == row['occurrences'], row['after'][:100]
                inverse = inverse.replace(row['after'], row['before'])
        assert inverse == self.before
        funcs = py_functions if self.kind == 'python' else gd_functions
        old, new = funcs(self.before), funcs(self.text)
        changed = sorted(k for k in old if old[k] != new[k])
        assert set(changed) == set(exceptions), (path, changed, exceptions)
        if self.kind == 'python': compile(self.text, str(path), 'exec')
        write(path, self.text)
        stem = path.stem
        save(D/(stem+'-inverse.json'), dict(before=desc(self.path), after=desc(path), edits=self.edits,
             inverse='EXACT_COMPLETE_BYTES', check='PYTHON_AST' if self.kind == 'python' else 'GD_FUNCTION_SOURCE_BYTES',
             changed_functions=changed, added_functions=sorted(set(new)-set(old)), conserved_functions=sorted(set(old)-set(changed))))
        write(D/(stem+'-source.patch'), ''.join(difflib.unified_diff(self.before.splitlines(True), self.text.splitlines(True), fromfile=str(self.path.relative_to(R)), tofile=str(path.relative_to(R)))))
        return desc(path)


def generate():
    assert not (D/'source-owner.json').exists()
    (D/'after-source').mkdir(exist_ok=False)
    origin = json.loads(ORIGIN.read_text())
    old = {str(ORIGIN.relative_to(R)): desc(ORIGIN)}
    for row in origin['files']:
        assert desc(R/row['path']) == row; old[row['path']] = row
    for row in json.loads((R/'data/phase380-payload-source/old-source-readback.json').read_text())['files']:
        assert desc(R/row['path'], historical_fixture=row['path'] in HISTORICAL_HARDLINK_FIXTURES) == row; old[row['path']] = row
    for path in (R/'docs/phase390_first_actual_eligible_idle_terminal_contract_design_spec.md', R/'data/phase390-first-eligible-idle-source-design/owned-files.json'):
        old[str(path.relative_to(R))] = desc(path)
    for row in json.loads((R/'data/phase390-first-eligible-idle-source-design/owned-files.json').read_text())['files']:
        assert desc(R/row['path']) == row; old[row['path']] = row
    save(D/'old-source-before.json', dict(files=list(old.values())))

    sink = Delta(R/origin['paths']['native_random_observer_sink_v7.gd']['after_path'], 'gd')
    sink.edit('const RNG_INITIAL_PROFILE = "7-king-single-A-355"', 'const RNG_INITIAL_PROFILE = "'+VERSION+'"')
    sink.edit('"phase368-source-control/1"', '"phase391-source-control/1"')
    sink.edit('\tking_clock_active = true\n\treturn true', '\tsource_tail_begin()\n\tking_clock_active = true\n\treturn true')
    before = '\t\tif source_cleanup != null and Engine.get_physics_frames() >= source_cleanup.physics_frame + 2:\n\t\t\tif Engine.get_physics_frames() != source_cleanup.physics_frame + 2:\n\t\t\t\tsource_cut_reject("SOURCE_MISSED_FIRST_IDLE_CUT", "clock_idle_signal")\n\t\t\t\treturn'
    after = '\t\tif source_tail_first_idle != null:\n\t\t\tif not source_terminal_current():\n\t\t\t\tsource_cut_reject("SOURCE_FIRST_ELIGIBLE_IDLE_CONTEXT", "clock_idle_signal")\n\t\t\t\treturn'
    sink.edit(before, after)
    sink.edit('\tif failed or not king_clock_active or king_clock_closed:\n\t\treturn\n', '\tif failed or not king_clock_active or king_clock_closed:\n\t\treturn\n\tif source_tail_first_idle != null:\n\t\tfail("SOURCE_MISSED_FIRST_ELIGIBLE_IDLE", "clock_pass")\n\t\treturn\n')
    sink.edit('\t\tking_clock_i += 1\n', '\t\tking_clock_i += 1\n\tsource_tail_note_pass(kind, Engine.get_physics_frames(), Engine.get_idle_frames(), king_clock_count)\n')
    sink.edit('if not king_clock_active or king_clock_closed or king_clock_last_kind != "idle":', 'if not king_clock_active or king_clock_closed or king_clock_last_kind != "idle" or not source_terminal_current():')
    sink.edit('"schema": "phase111-fixed-endpoint/1", "phase":', '"schema": "phase390-first-eligible-idle-endpoint/1", "terminal_policy": TERMINAL_POLICY, "phase":')
    sink.edit('"two_future_physics_signals": 2', '"minimum_future_physics_signals": 2, "observed_future_physics_signals": source_tail_count, "cleanup_anchor_pass": source_tail_anchor, "first_eligible_idle_pass": source_tail_first_idle.ordinal')
    sink.edit('\treturn write_king_json("king-post-cleanup-source.json", source_runtime_snapshot())', '\tif not source_tail_mark_cleanup():\n\t\treturn false\n\treturn write_king_json("king-post-cleanup-source.json", source_runtime_snapshot())')
    sink.edit('func source_completion_receipt():\n', 'func source_completion_receipt():\n\tif source_window_complete and not source_terminal_current():\n\t\tfail("SOURCE_RECEIPT_TERMINAL_CONTEXT", "source_completion_receipt")\n')
    sink.edit('"collector_archive_pending": true}', '"collector_archive_pending": true, "terminal_cut": source_terminal_cut()}')
    sink.edit('"diagnostic_error": source_diag_error}', '"diagnostic_error": source_diag_error, "terminal_cut": source_terminal_cut()}')
    sink.edit('or Engine.get_idle_frames() != idle_frame or failed:', 'or Engine.get_idle_frames() != idle_frame or failed or not source_terminal_current():')
    sink.edit('or source_cleanup == null or Engine.is_in_physics_frame() or Engine.get_physics_frames() != source_cleanup.physics_frame + 2:', 'or not source_terminal_current():')
    sink.edit('or source_cut_receiver() != receiver:', 'or source_cut_receiver() != receiver or not source_terminal_current():')
    sink.edit('or Engine.get_idle_frames() != source_cut_idle:\n\t\treturn source_cut_reject("CUT_FINALIZER_RETURN"', 'or Engine.get_idle_frames() != source_cut_idle or not source_terminal_current():\n\t\treturn source_cut_reject("CUT_FINALIZER_RETURN"')
    sink.append('\n'+(R/'tests/phase391_sink_terminal_source.gd').read_text())
    sink_desc = sink.finish(D/'after-source/native_random_observer_sink_v7.gd', ['begin_king_clock','clock_idle_signal','clock_pass','close_king_clock','source_mark_cleanup','source_completion_receipt','source_cut_control','ack_source_idle_cut','emit_source_idle_cut_once','source_diagnostic'])
    site_line = lambda t: next(l for l in t.splitlines() if l.startswith('const SITES ='))
    assert site_line(sink.before) == site_line(sink.text)
    assert len(json.loads(site_line(sink.text).split('=',1)[1])) == 107

    collector = Delta(R/origin['collector']['path'], 'gd')
    collector.edit('if receipt.cleanup == null or Engine.get_physics_frames() != receipt.cleanup.physics_frame + 2:\n\t\treturn source_cut_reject_collector("CUT_TWO_FUTURE_PHYSICS")', 'if not source_terminal_receipt_matches(receipt, control) or not observer.source_terminal_current():\n\t\treturn source_cut_reject_collector("CUT_FIRST_ACTUAL_ELIGIBLE_IDLE")')
    collector.edit('"collector_source": "phase362-single-King-oracle-only"', '"collector_source": "phase391-single-King-oracle-only"')
    collector.edit('"full_snapshot_reads": 1}', '"full_snapshot_reads": 1, "terminal_cut": receipt.terminal_cut.duplicate(true)}')
    collector.edit('\tsource_cut_finish_entered = true\n', '\tif not source_terminal_receipt_matches(source_cut_payload.receipt, control) or not observer.source_terminal_current():\n\t\treturn source_cut_reject_collector("CUT_FINALIZER_TERMINAL_IDENTITY")\n\tsource_cut_finish_entered = true\n')
    collector.append('\n'+(R/'tests/phase391_collector_terminal_source.gd').read_text())
    collector_desc = collector.finish(D/'collector.gd', ['on_idle_source_cut', 'finish_source_cut'])

    schema = Delta(R/origin['schema_module']['path'], 'python')
    schema.edit('7-king-single-A-355', VERSION, count=2)
    schema.edit('observer7-355-native-single-king-A/1', PROFILE, count=2)
    schema.edit('source-two-physics-idle-pre-internal/1', POLICY)
    schema.edit(py_span(schema.text, 'validate_terminal_evidence'), (R/'tests/phase391_schema_terminal_source.py').read_text().rstrip())
    schema.edit('schema = SimpleNamespace(\n', 'schema = SimpleNamespace(\n    validate_terminal_evidence=validate_terminal_evidence, validate_terminal_receipt=validate_terminal_receipt,\n    validate_terminal_diagnostics=validate_terminal_diagnostics,\n')
    schema_desc = schema.finish(R/'tests/phase391_king_observer_schema.py', ['validate_terminal_evidence'])
    matrix = lambda t: ast.dump(next(n for n in ast.parse(t).body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='MATRIX' for x in n.targets)),include_attributes=False)
    assert matrix(schema.before) == matrix(schema.text)

    freeze = copy.deepcopy(origin)
    row = freeze['paths']['native_random_observer_sink_v7.gd']; row['after_path'] = sink_desc['path']; row['after'] = {k:sink_desc[k] for k in ('size','sha256')}
    freeze['collector'] = collector_desc; freeze['artifacts']['native_combat_capture.gd'] = collector_desc
    cap = sum(r['after']['size'] for r in freeze['paths'].values()) + sum(r['size'] for r in freeze['artifacts'].values())
    assert len(freeze['paths']) == 75 and len(freeze['artifacts']) == 3
    storage = Delta(R/'tests/phase380_oracle_storage.py','python')
    storage.edit('MAX_INSTALL_BYTES = 807199', 'MAX_INSTALL_BYTES = '+str(cap))
    storage_desc = storage.finish(R/'tests/phase391_oracle_storage.py', [])

    host = Delta(R/'tests/phase380_oracle_host.py','python')
    for a,b in [('from phase380_oracle_storage import', 'from phase391_oracle_storage import'),
                ("SOURCE = 'data/phase380-payload-source'", "SOURCE = 'data/phase391-terminal-source'"),
                ('INDEPENDENT380_PAYLOAD_PREFLIGHT_PARTIAL_SOURCE_ACCEPTED_ROOT_PENDING', 'INDEPENDENT392_FIRST_ELIGIBLE_IDLE_SOURCE_ACCEPTED_ROOT_PENDING'),
                ('phase380-root-oracle-acceptance/1', 'phase391-root-oracle-acceptance/1'),
                ('original027-king-single-A-20261025-attempt05', 'original027-king-single-A-20261026-attempt06')]:
        host.edit(a,b)
    host.edit('attempt=5', 'attempt=6', count=2)
    host.edit('phase362-oracle-single-King', 'phase391-oracle-single-King')
    host.edit('phase362-oracle-host/1', 'phase391-oracle-host/1')
    host.edit('phase362-oracle-readonly-plan/1', 'phase391-oracle-readonly-plan/1')
    host.edit("    for row in freeze['accepted_source_controls']: descriptor(root,row)", "    if config.get('active_source_tuple') != freeze['active_source_tuple']:\n        raise ValueError('Root must pin actual391 source tuple')\n    validate_active_source_tuple(root,freeze)\n    if freeze['accepted_source_controls'] != []:\n        raise ValueError('historical controls cannot approve new SOURCE')\n    for row in freeze['historical_source_controls']: check_source_descriptor(root,row)")
    host.edit('partition=collect_capture_metadata(run,result)', 'partition=collect_capture_metadata(run,result,root,freeze)')
    host.edit('def collect_capture_metadata(run,result):', 'def collect_capture_metadata(run,result,source_root,freeze):')
    host.edit('secondary=[]; primary=None; capture=None; present={}; expected={}; validation=None; partial={}; control_files={}', 'secondary=[]; primary=None; capture=None; present={}; expected={}; validation=None; partial={}; control_files={}; terminal=None')
    host.edit("    complete=process_ok and primary is None and not missing and validation is not None and validation.get('native_checks_pass') is True and not secondary", "    if capture is not None:\n        try: terminal=read_terminal_expected_controls(source_root,freeze,capture)\n        except Exception as exc:\n            secondary.append(dict(code='terminal_expected_control_failure',error=repr(exc)))\n            if primary is None: primary=dict(kind='terminal_expected_control_failure',error=repr(exc))\n    complete=process_ok and primary is None and not missing and validation is not None and validation.get('native_checks_pass') is True and terminal is not None and not secondary")
    host.edit('expected_semantics_read=False,models=0,projection=0)', 'expected_semantics_read=False,terminal_expected_control=terminal,models=0,projection=0)')
    host.edit('\ndef main():\n', '\n'+(R/'tests/phase391_host_terminal_source.py').read_text()+'\ndef main():\n')
    host_desc = host.finish(R/'tests/phase391_oracle_host.py', ['source_gate','plan','execute','collect_capture_metadata'])

    patch = dict(schema='phase391-native-patch-source/1',paths=freeze['paths'],producer=desc(Path(__file__)),sink=sink_desc,
                 profile=PROFILE,observer_version=VERSION,terminal_policy=POLICY)
    save(D/'native-patch-source.json', patch)
    source_tuple = dict(schema='phase391-terminal-source-tuple/1',profile=PROFILE,observer_version=VERSION,terminal_policy=POLICY,
        fixed_fixture=desc(R/'data/phase355-king-finite-source/fixed-A-v8-fixture.json'), native_patch=desc(D/'native-patch-source.json'),
        producer=desc(Path(__file__)),sink=sink_desc,collector=collector_desc,schema_module=schema_desc,
        projector_source_origin=desc(R/'tests/phase361_king_projection_sealer.py'))
    save(D/'source-tuple.json',source_tuple)
    replacements = {origin['paths']['native_random_observer_sink_v7.gd']['after_path']:sink_desc,
                    origin['collector']['path']:collector_desc, origin['schema_module']['path']:schema_desc,
                    'tests/phase380_oracle_host.py':host_desc,'tests/phase380_oracle_storage.py':storage_desc,
                    origin['active_source_tuple']['path']:desc(D/'source-tuple.json')}
    files = {r['path']:r for r in origin['files'] if r['path'] not in replacements}
    for value in replacements.values():files[value['path']]=value
    new_sources = [Path(__file__),R/'docs/phase391_terminal_contract_implementation_addendum.md',D/'native-patch-source.json']
    new_sources += [R/'tests'/name for name in ('phase391_sink_terminal_source.gd','phase391_collector_terminal_source.gd','phase391_schema_terminal_source.py','phase391_host_terminal_source.py')]
    new_sources += [R/source_tuple[k]['path'] for k in ('fixed_fixture','projector_source_origin')]
    for path in new_sources:files[str(path.relative_to(R))]=desc(path)
    freeze.update(schema='phase391-first-eligible-idle-SOURCE/1',profile=PROFILE,observer_version=VERSION,terminal_policy=POLICY,
        files=list(files.values()),schema_module=schema_desc,active_source_tuple=desc(D/'source-tuple.json'),
        repair_origin=desc(ORIGIN),repair_finding=desc(R/'docs/phase390_first_actual_eligible_idle_terminal_contract_design_spec.md'),
        historical_source_controls=origin['accepted_source_controls'],accepted_source_controls=[],
        run_name='original027-king-single-A-20261026-attempt06', install_payload_limits=dict(files=78,bytes=cap,source='actual final75patch+3artifact descriptor sum'),current_authorized_operations=0)
    for row in freeze['files']:assert desc(R/row['path'])==row
    for row in freeze['paths'].values():assert desc(R/row['after_path'])==dict(path=row['after_path'],**row['after'])
    assert {k:v for k,v in origin['paths'].items() if k!='native_random_observer_sink_v7.gd'} == {k:v for k,v in freeze['paths'].items() if k!='native_random_observer_sink_v7.gd'}
    save(D/'combined-source-freeze.json', freeze)
    save(D/'install-bytecap.json', dict(files=78,bytes=cap,patches=[dict(target=k,bytes=v['after']['size']) for k,v in freeze['paths'].items()],artifacts=freeze['artifacts'],storage=storage_desc,old_bytes=807199,functions_changed=[]))
    tokens = (VERSION,PROFILE,POLICY,'phase390-first-eligible-idle-endpoint/1','phase390-terminal-cut-control/1','phase391-source-control/1')
    inventory=[]
    for p in [R/sink_desc['path'],R/collector_desc['path'],R/schema_desc['path'],R/host_desc['path'],D/'source-tuple.json',D/'native-patch-source.json',D/'combined-source-freeze.json']:
        for number,line in enumerate(p.read_text().splitlines(),1):
            hits=[x for x in tokens if x in line]
            if hits:inventory.append(dict(path=str(p.relative_to(R)),line=number,literals=hits))
    save(D/'protocol-consumer-inventory.json',dict(consumers=inventory,conserved_record_envelope='observer7-record/1 has no VERSION/PROFILE field; channels remain exact',
        conserved_fact_ui_schemas=['phase355-king-input-facts/1','phase355-king-ui-authority/1'],rng='phase355-util-rng-checkpoint/1 stays; source_profile is new VERSION',
        default_and_ui_join='Existing original functions compare structure/17 keys; no additional version literal',old359_binding='SOURCE historical origin only; new actual tuple/Root/review mandatory',
        old_reader361_and_model356='UNCHANGED_CLOSED; no new exports into their admission paths'))
    api = dict(schema='phase391-actual-api-contract/1',module=schema_desc,host=host_desc,storage=storage_desc,tuple=desc(D/'source-tuple.json'),
        functions={'validate_terminal_evidence':'(endpoint: closed dict, clock: this module ClockSchedule, cleanup: closed dict) -> expected-only proof',
                   'validate_terminal_receipt':'(endpoint, clock, receipt: closed dict, control: closed FINALIZED dict, validation: collector dict) -> same expected-only proof',
                   'validate_terminal_diagnostics':'(rows: list[closed diagnostic dict], 1..64) -> actual FINALIZED control; no trailing rows',
                   'read_terminal_expected_controls':'(source_root: Path, freeze: actual391 combined dict, capture: Path) -> host terminal proof; actual descriptor-bound schema exec and same exported join',
                   'collect_capture_metadata':'(run: Path, result: process dict, source_root: Path, freeze: actual391 combined dict) -> partition; terminal join mandatory for complete'},
        exports='schema.validate_terminal_evidence/receipt/diagnostics are identical module function objects',
        host_root_schema='phase391-root-oracle-acceptance/1',root_required_tuple_field='active_source_tuple',
        review_status='INDEPENDENT392_FIRST_ELIGIBLE_IDLE_SOURCE_ACCEPTED_ROOT_PENDING',review_required_fields=['status','source_freeze','native: strictINT0','models: strictINT0'],
        diagnostic_schema='phase391-source-control/1',diagnostic_max_bytes=1048576,diagnostic_max_rows=64,run_name=freeze['run_name'],
        operational_calls=dict(SUT_import=0,schema_call=0,Godot=0,Game=0,model=0,pool_inventory=0,pool_write=0,restore=0,READY=0,inputbuild=0,projection=0),
        acceptance=None,model356='CLOSED',reader361='CLOSED')
    save(D/'api-contract.json',api)
    save(D/'source-constraints.json',dict(schema='phase391-source-constraints/1',operations=api['operational_calls'],controls='Independent392 pending; author did not read concrete expectation fixtures',
        scope='OriginalGD-authoritative combat only; no GUI/shop/economy/training',conserved='74 other instrumented original GD patches exact; sink SITES107 exact; schema MATRIX107/FoodINT22 exact; all other functions source/AST exact per inverse',
        dataflow='C/endpoint/terminal_cut/control remain EXPECTED; model later computes its own cleanup; runtime15/349FrameDriver unmodified and unexecuted',
        shared_sequence='No additional physical channels/records; diagnostic does not increment shared sequence',
        limits=dict(install_files=78,install_bytes=cap,legal_input_files=12,runtime_ui_keys=17),independent_final=False))
    for name,row in old.items():assert desc(R/name, historical_fixture=name in HISTORICAL_HARDLINK_FIXTURES)==row
    save(D/'old-source-readback.json',dict(status='ALL_PINNED_OLD_SOURCE_BYTES_IDENTICAL',files=list(old.values())))
    save(D/'summary.json',dict(status='SOURCE_FROZEN_INDEPENDENT_REVIEW_PENDING',freeze=desc(D/'combined-source-freeze.json'),
        api=desc(D/'api-contract.json'),source_tuple=desc(D/'source-tuple.json'),actual_install_bytes=cap,author_operational_calls=api['operational_calls'],
        code_compiled_without_import=True,byte_inverses=True,python_AST_conservation=True,GD_lexical_conservation=True,Godot_parse_test=False,independent_acceptance=False,no_more_writes=True))
    own = [Path(__file__),R/'docs/phase391_terminal_contract_implementation_addendum.md']+[R/'tests'/name for name in ('phase391_sink_terminal_source.gd','phase391_collector_terminal_source.gd','phase391_schema_terminal_source.py','phase391_host_terminal_source.py','phase391_king_observer_schema.py','phase391_oracle_host.py','phase391_oracle_storage.py')]
    own += sorted(p for p in D.rglob('*') if p.is_file())
    rows=[desc(p) for p in own];assert len({r['path'] for r in rows})==len(rows)
    for p in own:
        if p.suffix=='.py': compile(p.read_text(),str(p),'exec')
    save(D/'source-owner.json',dict(schema='phase391-source-owner/1',files=rows,scope='SOURCE ONLY; independent controls/Root acceptance/native not run'))
    for row in rows:assert desc(R/row['path'])==row
    print(json.dumps(dict(owner=desc(D/'source-owner.json'),freeze=desc(D/'combined-source-freeze.json'),api=desc(D/'api-contract.json'),leaves=len(rows),bytes=sum(r['size'] for r in rows),install_bytes=cap)))


if __name__ == '__main__':
    try:generate()
    except Exception:
        failure = next(D/('preparation-failure-%03d'%n) for n in range(1,100) if not (D/('preparation-failure-%03d'%n)).exists())
        failure.mkdir(exist_ok=False)
        for p in [Path(__file__)]+list(R.glob('tests/phase391_*')):
            if p.is_file() and not (failure/p.name).exists():
                write(failure/p.name,p.read_text())
        write(failure/'traceback.txt',traceback.format_exc())
        raise
