"""Only the Root-authorized second lexical control and unchanged producer compile."""
import ast
import hashlib
import json
from pathlib import Path
import re


root = Path(__file__).resolve().parents[1]
out = root / 'data/phase462-v3-lexical-anchor-followup'
out.mkdir(exist_ok=False)
source = root / 'tests/phase462_prepare_joint_observer_source_v3.py'
raw = source.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '284453b399afb68a6c8ada19cbcb1cedba972cfbeb2b1aad5cd10080148c9db3'
first = root / 'data/phase462-joint-observer-repair-v3/first-error-owner.json'
assert hashlib.sha256(first.read_bytes()).hexdigest() == '5125dd71925bfdde50d383fbed24cdf518c7b2282adcec1784457785e628944c'
helper = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'gd_functions')
namespace = {'re': re}
exec(compile(ast.Module(body=[helper], type_ignores=[]), '<v3-own-lexical-helper-second-control>', 'exec'), namespace)
extract = namespace['gd_functions']
sink = (root / 'data/phase391-terminal-source/after-source/native_random_observer_sink_v7.gd').read_bytes().decode()
before = extract(sink)
body = before['ui_close']
assert body.count('\tui_closed = ok') == 1
modified = sink.replace(body, body.replace('\tui_closed = ok', '\tui_closed = false', 1), 1)
after = extract(modified)
changed = [name for name in before if before[name] != after[name]]
assert changed == ['ui_close']
compile(raw, str(source), 'exec', dont_inherit=True)
assert source.read_bytes() == raw
result = dict(schema='phase462-v3-body-control-followup/1', status='PASS_BODY_LEXICAL_CONTROL_AND_UNCHANGED_PRODUCER_COMPILE',
              producer_sha256=hashlib.sha256(raw).hexdigest(), changed_functions=changed,
              actual_body_anchor='ui_closed = ok -> ui_closed = false in memory only',
              first_control='REUSED_PASS_FROM_PRESERVED_OWNER_NOT_REEXECUTED', second_control_calls=1,
              helper_definition_compile_objects=1, producer_precompile_objects=1,
              observer_function_calls=0, generator_main_calls=0, generated_schema_imports=0,
              models=0, Godot=0, Expected_reads=0, pool_operations=0)
with (out / 'result.json').open('x') as stream:
    stream.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
print(json.dumps(result, sort_keys=True))
