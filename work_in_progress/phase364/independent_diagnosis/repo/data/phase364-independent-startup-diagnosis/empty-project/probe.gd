extends SceneTree

const SOURCE_CONFIG = {"schema": "native-combat-capture/1", "case_id": "NATIVE-027-KING-A", "global_seed": 35301, "util_seed": 35302, "player_fixture_enabled": true, "timeouts": {"battle_seconds": 120, "total_seconds": 295}}
var merged_defaults = {"global_seed": 10136021, "util_seed": 20261013, "case_id": "NATIVE-001", "player_fixture_enabled": false, "timeouts": {"battle_seconds": 120, "total_seconds": 295}}

func source_same_slot_value(actual, expected):
	# Native JSON numbers are REAL; accepting exact integral values here is a
	# SOURCE fixture representation rule, never a cast of observed typed values.
	match typeof(expected):
		TYPE_ARRAY:
			if typeof(actual) != TYPE_ARRAY or actual.size() != expected.size():
				return false
			for index in range(expected.size()):
				if not source_same_slot_value(actual[index], expected[index]):
					return false
		TYPE_DICTIONARY:
			if typeof(actual) != TYPE_DICTIONARY or actual.size() != expected.size():
				return false
			for key in expected:
				if not actual.has(key) or not source_same_slot_value(actual[key], expected[key]):
					return false
		TYPE_INT:
			if (typeof(actual) != TYPE_INT and typeof(actual) != TYPE_REAL) or actual != expected:
				return false
		TYPE_STRING:
			if typeof(actual) != TYPE_STRING or actual != expected:
				return false
		_:
			return false
	return true



func typed(value):
	var names = {TYPE_NIL: "NIL", TYPE_BOOL: "BOOL", TYPE_INT: "INT", TYPE_REAL: "REAL", TYPE_STRING: "STRING", TYPE_ARRAY: "ARRAY", TYPE_DICTIONARY: "DICTIONARY"}
	var row = {"typeof_code": typeof(value), "typeof_name": names.get(typeof(value), "OTHER"), "value": value}
	if typeof(value) == TYPE_REAL:
		var buffer = StreamPeerBuffer.new()
		buffer.big_endian = true
		buffer.put_double(value)
		row["binary64_be"] = buffer.data_array.hex_encode()
	return row

func _initialize():
	var f = File.new()
	if f.open("res://actual-config.json", File.READ) != OK:
		print("LANGUAGE_PROBE_ERROR config read")
		quit(2)
		return
	var raw = f.get_as_text()
	f.close()
	var parsed = JSON.parse(raw)
	if parsed.error != OK:
		print("LANGUAGE_PROBE_ERROR JSON.parse")
		quit(2)
		return
	for key in parsed.result:
		merged_defaults[key] = parsed.result[key]
	var comparisons = []
	for key in SOURCE_CONFIG:
		comparisons.append({"key": key, "actual": typed(merged_defaults[key]), "constant": typed(SOURCE_CONFIG[key]), "native_equal": merged_defaults[key] == SOURCE_CONFIG[key], "original_helper": source_same_slot_value(merged_defaults[key], SOURCE_CONFIG[key])})
	var dict_a = {"value": 1}
	var dict_alias = dict_a
	var dict_b = {"value": 1}
	var array_a = [1, 2]
	var array_alias = array_a
	var array_b = [1, 2]
	var numeric = JSON.parse("[1,1.0,-0.0,true,false,null]")
	var numeric_rows = []
	for v in numeric.result:
		numeric_rows.append(typed(v))
	var actual_autoloads = []
	for property in ProjectSettings.get_property_list():
		if str(property.name).begins_with("autoload/"):
			actual_autoloads.append(property.name)
	var report = {"schema": "phase364-godot-language-observations/1", "engine": Engine.get_version_info(), "actual_Game": false, "autoload_list": actual_autoloads, "game_node_present": get_root().has_node("Game"), "source_config": SOURCE_CONFIG, "merged_config": merged_defaults, "original_helper_whole_result": source_same_slot_value(merged_defaults, SOURCE_CONFIG), "config_fields": comparisons, "numeric_rows": numeric_rows, "scalar_equal": {"REAL1_vs_INT1": numeric.result[0] == 1, "BOOLtrue_vs_BOOLtrue": numeric.result[3] == true}, "original_helper_scalars": {"true_true": source_same_slot_value(true, true), "false_false": source_same_slot_value(false, false), "REAL1_INT1": source_same_slot_value(numeric.result[0], 1)}, "container_operators": {"dict_alias_equal": dict_a == dict_alias, "dict_distinct_equal_content": dict_a == dict_b, "array_alias_equal": array_a == array_alias, "array_distinct_equal_content": array_a == array_b, "dict_original_recursive_helper": source_same_slot_value(dict_a, dict_b), "array_original_recursive_helper": source_same_slot_value(array_a, array_b)}}
	if f.file_exists("res://language-report.json") or f.open("res://language-report.json", File.WRITE) != OK:
		print("LANGUAGE_PROBE_ERROR report conflict/open")
		quit(2)
		return
	f.store_string(JSON.print(report) + "\n")
	f.flush()
	f.close()
	print("LANGUAGE_PROBE_REPORT_WRITTEN")
	quit(0)
