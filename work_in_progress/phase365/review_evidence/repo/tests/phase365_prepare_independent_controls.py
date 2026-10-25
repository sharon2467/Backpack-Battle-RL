"""Static365 delta and SOURCE unit preseal. No SUT imports or Godot/API calls."""
import ast
import copy
import hashlib
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/phase365-independent-source-review';A=R/'data/phase365-control-recovery-source'
def desc(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(R)),size=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,v):
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main():
 D.mkdir(exist_ok=False);(D/'SOURCE').mkdir();(D/'language-project').mkdir()
 owner=json.loads((A/'source-owner.json').read_text());assert desc(A/'source-owner.json')['sha256']=='ef9ec5a403c186094c7c07d5d3d47f4f9fb7b1a6618db2d94032867bffbce66c'
 for row in owner['files']:assert desc(R/row['path'])==row
 before=(R/'data/phase362-oracle-capture-source/collector.gd').read_text();after=(A/'collector.gd').read_text();newfunc=after[after.index('func config_matches_source(value):'):after.index('func _initialize():')]
 inverse=after.replace(newfunc,'',1).replace('\tvar source_config_input = {}\n','',1).replace('\t\tsource_config_input = parsed.result\n','',1).replace('if not config_matches_source(source_config_input):','if not get_root().get_node("NativeRandomObserver").source_same_slot_value(config, SOURCE_CONFIG):',1);assert inverse==before
 oldhost=(R/'tests/phase363_oracle_host.py').read_text();newhost=(R/'tests/phase365_oracle_host.py').read_text();ot,nt=ast.parse(oldhost),ast.parse(newhost);of={n.name:n for n in ot.body if isinstance(n,ast.FunctionDef)};nf={n.name:n for n in nt.body if isinstance(n,ast.FunctionDef)}
 assert {k for k in of if ast.dump(of[k],include_attributes=False)!=ast.dump(nf[k],include_attributes=False)}=={'source_gate','plan','execute'}
 normalized=newhost.replace("SOURCE = 'data/phase365-control-recovery-source'","SOURCE = 'data/phase363-oracle-repair-source'").replace('original027-king-single-A-20261025-attempt02','original027-king-single-A-20261025-attempt01').replace('INDEPENDENT365_CONTROL_RECOVERY_SOURCE_ACCEPTED_ROOT_PENDING','INDEPENDENT363_INSTALLER_MONITOR_SOURCE_ACCEPTED_ROOT_PENDING');t=ast.parse(normalized);t.body=[copy.deepcopy(of[n.name]) if isinstance(n,ast.FunctionDef) else n for n in t.body if not isinstance(n,ast.FunctionDef) or n.name in of];assert ast.dump(t,include_attributes=False)==ast.dump(ot,include_attributes=False)
 newfreeze=json.loads((A/'combined-source-freeze.json').read_text());oldfreeze=json.loads((R/'data/phase363-oracle-repair-source/combined-source-freeze.json').read_text());assert newfreeze['paths']==oldfreeze['paths']
 files=[('tests/phase365_oracle_host.py','host.py'),('tests/phase365_pool_recovery.py','recovery.py'),('tests/phase363_oracle_storage.py','storage.py'),('tests/phase363_oracle_process.py','process.py'),('tests/native_run_compaction.py','compaction.py')]
 for source,target in files:(D/'SOURCE'/target).write_bytes((R/source).read_bytes())
 (D/'SOURCE/new-config-function.gd.txt').write_text(newfunc)
 helper=(R/'data/phase364-independent-startup-diagnosis/SOURCE/original-comparator.gd.txt').read_text();assert len(helper.encode())==940
 (D/'language-project/helper.gd').write_text('extends Node\n\n'+helper)
 cfg=R/'data/phase362-oracle-capture-source/case-A/native_capture_config.json';(D/'language-project/config.json').write_bytes(cfg.read_bytes());constant=next(l for l in after.splitlines() if l.startswith('const SOURCE_CONFIG = '))
 project='config_version=4\n\n[application]\nconfig/name="Phase365SourceRegressionOnly"\nconfig/use_custom_user_dir=true\nconfig/custom_user_dir_name="Phase365SourceRegressionOnly"\n\n[rendering]\nquality/driver/driver_name="GLES2"\n';(D/'language-project/project.godot').write_text(project)
 script='extends SceneTree\n\n'+constant+'\n\n'+newfunc+'''func _initialize():
\tvar original = load("res://helper.gd").new()
\toriginal.name = "NativeRandomObserver"
\tget_root().add_child(original)
\tvar f = File.new()
\tif f.open("res://config.json", File.READ) != OK:
\t\tquit(2)
\t\treturn
\tvar parsed = JSON.parse(f.get_as_text())
\tf.close()
\tif parsed.error != OK:
\t\tquit(2)
\t\treturn
\tvar base = parsed.result
\tvar cases = []
\tvar value = base.duplicate(true)
\tcases.append({"id": 1, "label": "exact-JSON-true-config", "value": value, "expected": true})
\tvar mutations = [false, 1, 1.0, "true", null]
\tvar labels = ["BOOLfalse", "INT1-flag", "REAL1-flag", "STRING-flag", "NULL-flag"]
\tfor i in range(mutations.size()):
\t\tvalue = base.duplicate(true)
\t\tvalue.player_fixture_enabled = mutations[i]
\t\tcases.append({"id": cases.size()+1, "label": labels[i], "value": value, "expected": false})
\tvalue = base.duplicate(true)
\tvalue.erase("player_fixture_enabled")
\tcases.append({"id": 7, "label": "missing-key", "value": value, "expected": false})
\tvalue = base.duplicate(true)
\tvalue.extra_key = true
\tcases.append({"id": 8, "label": "extra-key", "value": value, "expected": false})
\tvalue = base.duplicate(true)
\tvalue.global_seed = 35300
\tcases.append({"id": 9, "label": "wrong-global-seed", "value": value, "expected": false})
\tvalue = base.duplicate(true)
\tvalue.util_seed = 35303
\tcases.append({"id": 10, "label": "wrong-util-seed", "value": value, "expected": false})
\tvalue = base.duplicate(true)
\tvalue.timeouts.battle_seconds = 121
\tcases.append({"id": 11, "label": "wrong-battle-timeout", "value": value, "expected": false})
\tvalue = base.duplicate(true)
\tvalue.timeouts.total_seconds = 296
\tcases.append({"id": 12, "label": "wrong-total-timeout", "value": value, "expected": false})
\tvalue = base.duplicate(true)
\tvalue.schema = "SOURCE_UNIT_WRONG_SCHEMA"
\tcases.append({"id": 13, "label": "wrong-schema-or-case", "value": value, "expected": false})
\tcases.append({"id": 14, "label": "raw-and-helper-conservation", "value": base.duplicate(true), "expected": true})
\tvar results = []
\tvar failures = []
\tfor test in cases:
\t\tvar before = JSON.print(test.value)
\t\tvar constant_before = JSON.print(SOURCE_CONFIG)
\t\tvar actual = config_matches_source(test.value)
\t\tvar unchanged = before == JSON.print(test.value) and constant_before == JSON.print(SOURCE_CONFIG)
\t\tvar row = {"id": test.id, "label": test.label, "expected": test.expected, "actual": actual, "unchanged": unchanged, "pass": actual == test.expected and unchanged, "flag_type": typeof(test.value.player_fixture_enabled) if test.value.has("player_fixture_enabled") else -1}
\t\tresults.append(row)
\t\tif not row["pass"]:
\t\t\tfailures.append(row)
\tvar autoloads = []
\tfor property in ProjectSettings.get_property_list():
\t\tif str(property.name).begins_with("autoload/"):
\t\t\tautoloads.append(property.name)
\tvar report = {"schema": "phase365-exact-GD-config-regression/1", "engine": Engine.get_version_info(), "cases": results, "failures": failures, "new_config_top_level_calls": cases.size(), "direct_original_helper_calls": 2, "old_original_BOOL_result": original.source_same_slot_value(true, true), "old_original_full_config_result": original.source_same_slot_value(base, SOURCE_CONFIG), "exact_source_callee_Node_instances": 1, "autoloads": autoloads, "Game_node_present": get_root().has_node("Game"), "actual_Game": false}
\tif f.file_exists("res://regression-report.json") or f.open("res://regression-report.json", File.WRITE) != OK:
\t\tquit(2)
\t\treturn
\tf.store_string(JSON.print(report)+"\\n")
\tf.flush()
\tf.close()
\tprint("SOURCE_CONFIG_REGRESSION_WRITTEN")
\tquit(0 if failures.empty() else 2)
'''
 (D/'language-project/probe.gd').write_text(script)
 for p in (D/'SOURCE').glob('*.py'):compile(p.read_bytes(),str(p),'exec')
 prep=json.loads((R/'data/phase365-independent-recovery-preparation/contract.json').read_text());save(D/'cases.json',prep['controls'])
 save(D/'source-review.json',dict(schema='phase365-independent-static-delta/1',status='SOURCE_DELTA_REVIEWED_UNIT_PENDING',collector_inverse_fullbytes=True,raw_parsed_config_gate=True,old359_helper_unchanged=True,P_O_literals_and75_source_paths_unchanged=True,host_inverse_AST=True,storage_process_reused=[desc(R/'tests/phase363_oracle_storage.py'),desc(R/'tests/phase363_oracle_process.py')],recovery_public_gate='Root exactSource/owner/review/map/input pins/action and independent readback required. Unit stage helpers do not authorize publicrecover.',module_imports=0,Godot=0,actual_recovery=0))
 print(json.dumps(dict(cases=40,language_cases=14,static='PASS',helper_bytes=940)))
if __name__=='__main__':main()
