extends SceneTree

var report = {"schema": "phase370-independent-language-controls/1", "resource_loads": [], "cases": [], "failure": null, "full_production_instances": 0, "full_lifecycle_calls": 0, "actual_Game": false, "native_positive": false, "unit_node_instances": 0, "exact_method_calls": 0}
var active = null
var mode = ""
var callbacks = 0
var finishes = 0
var trace = []
var frozen_unit = null
var unit_script = null

func persist():
	var file = File.new()
	if file.open("res://language-report.json", File.WRITE) == OK:
		file.store_string(JSON.print(report) + "\n")
		file.flush()
		file.close()

func on_idle_source_cut():
	callbacks += 1
	trace.append("callback:" + active.source_cut_phase)
	if mode == "NO_ACK":
		return
	if mode == "REENTRY":
		report.exact_method_calls += 1
		active.emit_source_idle_cut_once()
		return
	if mode == "BAD_ACK_TYPE":
		report.exact_method_calls += 1
		active.ack_source_idle_cut(true, Engine.get_physics_frames(), Engine.get_idle_frames())
		return
	frozen_unit = {"scope": "UNIT_ONLY_NOT_PRODUCTION_DTO", "physics": Engine.get_physics_frames(), "idle": Engine.get_idle_frames()}
	report.exact_method_calls += 1
	active.ack_source_idle_cut(get_instance_id(), Engine.get_physics_frames(), Engine.get_idle_frames())
	trace.append("ack-return")

func finish_source_cut():
	finishes += 1
	trace.append("finish:" + active.source_cut_phase)
	if mode == "FINISH_INT":
		return 1
	if mode == "FINISH_FALSE":
		return false
	return active.source_cut_phase == "FINALIZING" and active.source_cut_script_return_observed and typeof(active.source_cut_script_return) == TYPE_NIL and frozen_unit != null

func one_case(label, expected, expected_callbacks, expected_finishes):
	mode = label
	callbacks = 0
	finishes = 0
	trace = []
	frozen_unit = null
	active = unit_script.new()
	report.unit_node_instances += 1
	active.OUT = "user://units/" + label
	Directory.new().make_dir_recursive(active.OUT)
	get_root().add_child(active)
	active.source_cleanup = {"physics_frame": Engine.get_physics_frames() - 2}
	var extra = null
	var flags = CONNECT_DEFERRED if label == "DEFERRED" else 0
	var binds = ["UNIT_BIND"] if label == "BINDS" else []
	var connect_result = null
	if label != "MISSING":
		connect_result = active.connect("source_idle_cut_ready", self, "on_idle_source_cut", binds, flags)
	if label == "EXTRA":
		extra = load("res://extra.gd").new()
		report.unit_node_instances += 1
		active.connect("source_idle_cut_ready", extra, "noop")
	if label == "BLOCKED":
		active.set_block_signals(true)
	if label == "CLOSED_FALSE":
		active.closed = false
	if label == "ALREADY_FAILED":
		active.failed = true
		active.first_error = {"code": "UNIT_ORIGINAL_PRIMARY"}
	if label == "DIAG_CAP":
		active.source_diag_records = 64
	var before = active.source_cut_control()
	trace.append("before")
	report.exact_method_calls += 1
	var actual = active.emit_source_idle_cut_once()
	trace.append("after:" + active.source_cut_phase)
	var first_actual = actual
	if label == "DUPLICATE":
		report.exact_method_calls += 1
		actual = active.emit_source_idle_cut_once()
	var control = active.source_cut_control()
	var unchanged = active.sequence == 23 and active.ui_sequence == 17 and active.king_clock_count == 9
	var ok = actual == expected and callbacks == expected_callbacks and finishes == expected_finishes and unchanged
	if label == "GOOD":
		ok = ok and control.phase == "FINALIZED" and control.script_emit_return_observed and typeof(control.script_emit_return) == TYPE_NIL and typeof(control.finish_return) == TYPE_BOOL and control.finish_return and control.native_emit_error_available == false and control.native_emit_error == null and trace == ["before", "callback:EMITTING", "ack-return", "finish:FINALIZING", "after:FINALIZED"]
	if label == "DUPLICATE":
		ok = ok and first_actual and control.emit_count == 1
	if label == "ALREADY_FAILED":
		ok = ok and active.first_error.code == "UNIT_ORIGINAL_PRIMARY"
	var row = {"label": label, "expected": expected, "actual": actual, "pass": ok, "callbacks": callbacks, "finishes": finishes, "trace": trace.duplicate(), "before": before, "after": control, "connect_result": connect_result, "collector_id": str(get_instance_id()), "node_id": str(active.get_instance_id()), "counters_unchanged": unchanged}
	report.cases.append(row)
	if extra != null:
		extra.free()
	active.free()
	active = null
	return ok

func _initialize():
	for name in ["full-collector.gd", "full-sink.gd"]:
		var script = load("res://" + name)
		var ok = script != null and script.can_instance()
		report.resource_loads.append({"file": name, "loaded": script != null, "can_instance": ok, "base": script.get_instance_base_type() if script != null else null})
		persist()
		if not ok:
			report.failure = {"stage": "FULL_RESOURCE_LOAD", "file": name}
			persist()
			quit(2)
			return
	unit_script = load("res://unit-sink.gd")
	if unit_script == null or not unit_script.can_instance():
		report.failure = {"stage": "EXACT_CONTROL_UNIT_RESOURCE_LOAD"}
		persist()
		quit(2)
		return
	var cases = [["GOOD", true, 1, 1], ["MISSING", false, 0, 0], ["EXTRA", false, 0, 0], ["DEFERRED", false, 0, 0], ["BINDS", false, 0, 0], ["NO_ACK", false, 1, 0], ["BLOCKED", false, 0, 0], ["BAD_ACK_TYPE", false, 1, 0], ["REENTRY", false, 1, 0], ["FINISH_INT", false, 1, 1], ["FINISH_FALSE", false, 1, 1], ["DUPLICATE", false, 1, 1], ["CLOSED_FALSE", false, 0, 0], ["ALREADY_FAILED", false, 0, 0], ["DIAG_CAP", false, 0, 0]]
	for row in cases:
		if not one_case(row[0], row[1], row[2], row[3]):
			report.failure = {"stage": "CONTROL_CASE", "label": row[0]}
			persist()
			quit(2)
			return
		persist()
	report.completed = true
	report.autoloads = []
	for property in ProjectSettings.get_property_list():
		if str(property.name).begins_with("autoload/"):
			report.autoloads.append(property.name)
	report.Game_present = get_root().has_node("Game")
	persist()
	print("INDEPENDENT370_LANGUAGE_CONTROLS_COMPLETE")
	quit(0)
