extends SceneTree

const SOURCE_CONFIG = {"schema": "native-combat-capture/1", "case_id": "NATIVE-027-KING-A", "global_seed": 35301, "util_seed": 35302, "player_fixture_enabled": true, "timeouts": {"battle_seconds": 120, "total_seconds": 295}}

func config_matches_source(value):
	if typeof(value) != TYPE_DICTIONARY or value.size() != SOURCE_CONFIG.size():
		return false
	for key in SOURCE_CONFIG:
		if not value.has(key):
			return false
	if typeof(value.player_fixture_enabled) != TYPE_BOOL or value.player_fixture_enabled != true:
		return false
	var actual_rest = value.duplicate()
	var source_rest = SOURCE_CONFIG.duplicate()
	actual_rest.erase("player_fixture_enabled")
	source_rest.erase("player_fixture_enabled")
	return get_root().get_node("NativeRandomObserver").source_same_slot_value(actual_rest, source_rest)


func _initialize():
	var original = load("res://helper.gd").new()
	original.name = "NativeRandomObserver"
	get_root().add_child(original)
	var f = File.new()
	if f.open("res://config.json", File.READ) != OK:
		quit(2)
		return
	var parsed = JSON.parse(f.get_as_text())
	f.close()
	if parsed.error != OK:
		quit(2)
		return
	var base = parsed.result
	var cases = []
	var value = base.duplicate(true)
	cases.append({"id": 1, "label": "exact-JSON-true-config", "value": value, "expected": true})
	var mutations = [false, 1, 1.0, "true", null]
	var labels = ["BOOLfalse", "INT1-flag", "REAL1-flag", "STRING-flag", "NULL-flag"]
	for i in range(mutations.size()):
		value = base.duplicate(true)
		value.player_fixture_enabled = mutations[i]
		cases.append({"id": cases.size()+1, "label": labels[i], "value": value, "expected": false})
	value = base.duplicate(true)
	value.erase("player_fixture_enabled")
	cases.append({"id": 7, "label": "missing-key", "value": value, "expected": false})
	value = base.duplicate(true)
	value.extra_key = true
	cases.append({"id": 8, "label": "extra-key", "value": value, "expected": false})
	value = base.duplicate(true)
	value.global_seed = 35300
	cases.append({"id": 9, "label": "wrong-global-seed", "value": value, "expected": false})
	value = base.duplicate(true)
	value.util_seed = 35303
	cases.append({"id": 10, "label": "wrong-util-seed", "value": value, "expected": false})
	value = base.duplicate(true)
	value.timeouts.battle_seconds = 121
	cases.append({"id": 11, "label": "wrong-battle-timeout", "value": value, "expected": false})
	value = base.duplicate(true)
	value.timeouts.total_seconds = 296
	cases.append({"id": 12, "label": "wrong-total-timeout", "value": value, "expected": false})
	value = base.duplicate(true)
	value.schema = "SOURCE_UNIT_WRONG_SCHEMA"
	cases.append({"id": 13, "label": "wrong-schema-or-case", "value": value, "expected": false})
	cases.append({"id": 14, "label": "raw-and-helper-conservation", "value": base.duplicate(true), "expected": true})
	var results = []
	var failures = []
	for test in cases:
		var before = JSON.print(test.value)
		var constant_before = JSON.print(SOURCE_CONFIG)
		var actual = config_matches_source(test.value)
		var unchanged = before == JSON.print(test.value) and constant_before == JSON.print(SOURCE_CONFIG)
		var row = {"id": test.id, "label": test.label, "expected": test.expected, "actual": actual, "unchanged": unchanged, "pass": actual == test.expected and unchanged, "flag_type": typeof(test.value.player_fixture_enabled) if test.value.has("player_fixture_enabled") else -1}
		results.append(row)
		if not row["pass"]:
			failures.append(row)
	var autoloads = []
	for property in ProjectSettings.get_property_list():
		if str(property.name).begins_with("autoload/"):
			autoloads.append(property.name)
	var report = {"schema": "phase365-exact-GD-config-regression/1", "engine": Engine.get_version_info(), "cases": results, "failures": failures, "new_config_top_level_calls": cases.size(), "direct_original_helper_calls": 2, "old_original_BOOL_result": original.source_same_slot_value(true, true), "old_original_full_config_result": original.source_same_slot_value(base, SOURCE_CONFIG), "exact_source_callee_Node_instances": 1, "autoloads": autoloads, "Game_node_present": get_root().has_node("Game"), "actual_Game": false}
	if f.file_exists("res://regression-report.json") or f.open("res://regression-report.json", File.WRITE) != OK:
		quit(2)
		return
	f.store_string(JSON.print(report)+"\n")
	f.flush()
	f.close()
	print("SOURCE_CONFIG_REGRESSION_WRITTEN")
	quit(0 if failures.empty() else 2)
