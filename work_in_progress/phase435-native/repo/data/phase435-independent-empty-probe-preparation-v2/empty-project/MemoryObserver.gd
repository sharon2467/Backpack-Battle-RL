extends Node
const CAPS = {"array": 8192, "depth": 16, "descriptors": 6, "dictionary": 512, "failure_file_bytes": 4096, "file_bytes": 268435456, "first_error_bytes": 1024, "flush_bytes": 4194304, "host_capture_files": 64, "native_ids": 8192, "observer_files": 8, "pending_rows": 64, "record_bytes": 2097152, "records": 300000, "roles": 1024, "sparse_nodes": 16384, "string_utf8": 4096, "total_bytes": 268435456}
var ids = {} # integer native IDs -> immutable role strings only
var king_timer_births = {}
var invu_early_timers = {}
var invu_early_owners = {}
var invu_early_ordinal = 0
var invu_early_error = null
var invu_observer_ready = false

func _invu_memory_error(code, owner_id, timer_id):
	if invu_early_error == null:
		var safe_code = code if typeof(code) == TYPE_STRING and code.length() <= 64 else "INVU_MEMORY_ERROR"
		var safe_owner = owner_id if typeof(owner_id) == TYPE_INT and owner_id > 0 else 0
		var safe_timer = timer_id if typeof(timer_id) == TYPE_INT and timer_id > 0 else 0
		invu_early_error = {"code": safe_code, "owner_id": safe_owner, "timer_id": safe_timer}

func _invu_raw_snapshot(timer):
	if timer == null or not is_instance_valid(timer) or not timer is Timer:
		_invu_memory_error("INVU_NATIVE_TIMER", 0, 0)
		return null
	if timer.get_class() != "Timer" or timer.get_script() != null or str(timer.get_name()) != "InvulnerabilityTimer":
		_invu_memory_error("INVU_NATIVE_TIMER_DOMAIN", 0, timer.get_instance_id())
		return null
	var positions = []
	var cursor = timer
	while cursor != null:
		if positions.size() >= CAPS.depth:
			_invu_memory_error("INVU_ANCESTOR_DEPTH", 0, timer.get_instance_id())
			return null
		positions.push_front(cursor.get_index())
		cursor = cursor.get_parent()
	var inside = timer.is_inside_tree()
	var path = str(timer.get_path()) if inside else null
	var key = timer.get_instance_id()
	var role = ids.get(key, null)
	if typeof(key) != TYPE_INT or key <= 0 or (path != null and path.to_utf8().size() > CAPS.string_utf8) or (role != null and (typeof(role) != TYPE_STRING or role.to_utf8().size() > CAPS.string_utf8)):
		_invu_memory_error("INVU_NATIVE_ID_OR_TEXT", 0, 0)
		return null
	var wait = timer.wait_time
	var left = timer.time_left
	if typeof(wait) != TYPE_REAL or typeof(left) != TYPE_REAL or is_nan(wait) or is_inf(wait) or is_nan(left) or is_inf(left) or wait <= 0.0 or left < 0.0:
		_invu_memory_error("INVU_NATIVE_REAL", 0, key)
		return null
	var node = {"native_id": str(key), "role": role, "path": path, "name": str(timer.get_name()), "class": timer.get_class(), "positions": positions, "priority": timer.get_process_priority(), "inside_tree": inside, "ordinary_physics": timer.is_physics_processing(), "internal_physics": timer.is_physics_processing_internal(), "ordinary_idle": timer.is_processing(), "internal_idle": timer.is_processing_internal()}
	return {"node": node, "process_mode": timer.process_mode, "wait_time": wait, "time_left": left, "one_shot": timer.one_shot, "autostart": timer.autostart, "paused": timer.paused, "stopped": timer.is_stopped()}

func invu_first_enter_memory(timer, owner):
	if invu_early_error != null:
		return
	if owner == null or not is_instance_valid(owner) or not owner is Node2D:
		_invu_memory_error("INVU_OWNER", 0, 0)
		return
	var raw = _invu_raw_snapshot(timer)
	if raw == null:
		return
	var key = timer.get_instance_id()
	var owner_key = owner.get_instance_id()
	var script = owner.get_script()
	var scene = owner.get_filename()
	if script == null or script.resource_path != "res://Core/Character.gd" or not scene in ["res://Core/Player.tscn", "res://Core/Opponent.tscn"] or not owner.is_inside_tree() or raw.node.inside_tree or timer.get_parent() != owner:
		_invu_memory_error("INVU_FIRST_ENTRY_DOMAIN", owner_key, key)
		return
	if typeof(owner_key) != TYPE_INT or owner_key <= 0 or owner_key == key or invu_early_timers.has(key) or invu_early_owners.has(owner_key) or king_timer_births.has(key):
		_invu_memory_error("INVU_FIRST_ENTRY_REUSED", owner_key, key)
		return
	if invu_early_timers.size() >= CAPS.native_ids or invu_early_owners.size() >= CAPS.native_ids or invu_early_ordinal >= CAPS.native_ids * 2:
		_invu_memory_error("INVU_FIRST_ENTRY_CAP", owner_key, key)
		return
	invu_early_ordinal += 1
	invu_early_owners[owner_key] = key
	invu_early_timers[key] = {"timer_id": str(key), "owner_id": str(owner_key), "kind": "Character.first_enter_tree/434", "starts": 0, "stops": 0, "birth_raw": raw, "entry": {"schema": "phase434-invu-first-enter/1", "ordinal": invu_early_ordinal, "owner_inside_tree": owner.is_inside_tree(), "owner_script": script.resource_path, "owner_scene": scene, "observer_ready_at_entry": invu_observer_ready}, "parent_ready": null}

func invu_parent_ready_memory(timer, owner):
	if invu_early_error != null:
		return
	if owner == null or not is_instance_valid(owner) or not owner is Node2D:
		_invu_memory_error("INVU_READY_OWNER", 0, 0)
		return
	var raw = _invu_raw_snapshot(timer)
	if raw == null:
		return
	var key = timer.get_instance_id()
	var owner_key = owner.get_instance_id()
	if not invu_early_timers.has(key) or invu_early_owners.get(owner_key, 0) != key or king_timer_births.has(key):
		_invu_memory_error("INVU_READY_WITHOUT_ENTRY", owner_key, key)
		return
	var born = invu_early_timers[key]
	var script = owner.get_script()
	if born.owner_id != str(owner_key) or born.parent_ready != null or timer.get_parent() != owner or not owner.is_inside_tree() or not raw.node.inside_tree or script == null or script.resource_path != born.entry.owner_script or owner.get_filename() != born.entry.owner_scene:
		_invu_memory_error("INVU_READY_IDENTITY_OR_REUSED", owner_key, key)
		return
	if typeof(born.starts) != TYPE_INT or typeof(born.stops) != TYPE_INT or born.starts < 0 or born.stops < 0 or born.starts > 9007199254740991 or born.stops > 9007199254740991 or invu_early_ordinal >= CAPS.native_ids * 2:
		_invu_memory_error("INVU_READY_COUNTER_OR_CAP", owner_key, key)
		return
	invu_early_ordinal += 1
	born.parent_ready = {"schema": "phase434-invu-parent-ready/1", "ordinal": invu_early_ordinal, "starts": born.starts, "stops": born.stops, "state": raw}

func track_king_timer_api(timer, operation):
	var key = timer.get_instance_id()
	if invu_early_timers.has(key):
		var born = invu_early_timers[key]
		if king_timer_births.has(key) or typeof(operation) != TYPE_STRING or not operation in ["start", "stop"]:
			_invu_memory_error("INVU_TIMER_API_DOMAIN", 0, key)
		elif invu_early_error == null:
			var field = "starts" if operation == "start" else "stops"
			if typeof(born[field]) != TYPE_INT or born[field] < 0 or born[field] >= 9007199254740991:
				_invu_memory_error("INVU_TIMER_API_COUNTER", 0, key)
			else:
				born[field] += 1
		if invu_early_error != null and invu_observer_ready:
			fail(invu_early_error.code, "invu_early_memory")
		return
	if king_timer_births.has(key):
		king_timer_births[key]["starts" if operation == "start" else "stops"] += 1

func float_bits(value):
	var buffer = StreamPeerBuffer.new()
	buffer.big_endian = true
	buffer.put_double(value)
	return buffer.data_array.hex_encode()


# FIXTURE ONLY: normal-failure routing, no production file writer/bootstrap.
var failed = false
var fail_invocations = 0
var fail_effects = 0
func fail(code, site, detail = null):
	fail_invocations += 1
	if failed:
		return false
	failed = true
	fail_effects += 1
	return false
func probe_successful_bootstrap_tail():
	if failed:
		return
	invu_observer_ready = true
	if invu_early_error != null:
		fail(invu_early_error.code, "invu_early_memory")
