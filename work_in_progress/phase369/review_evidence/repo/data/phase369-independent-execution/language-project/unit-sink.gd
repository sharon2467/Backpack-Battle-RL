extends Node
const CAPS = {"array": 8192, "depth": 16, "descriptors": 6, "dictionary": 512, "failure_file_bytes": 4096, "file_bytes": 268435456, "first_error_bytes": 1024, "flush_bytes": 4194304, "host_capture_files": 64, "native_ids": 8192, "observer_files": 8, "pending_rows": 64, "record_bytes": 2097152, "records": 300000, "roles": 1024, "sparse_nodes": 16384, "string_utf8": 4096, "total_bytes": 268435456}
var OUT = "user://unused-unit"
var sequence = 23
var ui_sequence = 17
var king_clock_count = 9
var failed = false
var closed = true
var source_window_complete = true
var king_clock_closed = true
var ui_closed = true
var first_error = null
var source_cleanup = null
signal source_idle_cut_ready
var source_cut_phase = "IDLE"
var source_cut_emit_count = 0
var source_cut_dispatching = false
var source_cut_receiver_id = -1
var source_cut_physics = -1
var source_cut_idle = -1
var source_cut_ack = null
var source_cut_emit_error = null
var source_cut_finish_return = null
var source_cut_ready_connect = {"physics": null, "idle": null}
var source_diag_records = 0
var source_diag_bytes = 0
var source_diag_error = null



func source_diag_valid(value, depth = 0):
	if depth > 8:
		return false
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT:
			return true
		TYPE_STRING:
			return value.to_utf8().size() <= 512
		TYPE_ARRAY:
			if value.size() > 1024:
				return false
			for member in value:
				if not source_diag_valid(member, depth + 1):
					return false
			return true
		TYPE_DICTIONARY:
			if value.size() > 64:
				return false
			for key in value:
				if typeof(key) != TYPE_STRING or key.to_utf8().size() > 128 or not source_diag_valid(value[key], depth + 1):
					return false
			return true
	return false



func source_diag_secondary(code):
	if source_diag_error == null:
		source_diag_error = code
	print("SOURCE_DIAGNOSTIC_SECONDARY " + code)
	return false



func source_diagnostic(site, reason, payload):
	# No calls to fail/UI/clock/record/EventBus. This writer cannot recurse into primary failure.
	if typeof(site) != TYPE_STRING or typeof(reason) != TYPE_STRING or not source_diag_valid(payload):
		return source_diag_secondary("UNSUPPORTED_PRIMITIVE_DIAGNOSTIC")
	if source_diag_records >= 64:
		return source_diag_secondary("DIAGNOSTIC_RECORD_CAP")
	var row = {"schema": "phase368-source-control/1", "control_sequence": source_diag_records, "site": site, "reason": reason, "physics": Engine.get_physics_frames(), "idle": Engine.get_idle_frames(), "in_physics": Engine.is_in_physics_frame(), "observer_sequence": sequence, "ui_sequence": ui_sequence, "clock_passes": king_clock_count, "payload": payload}
	var bytes = (JSON.print(row) + "\n").to_utf8()
	if bytes.size() > 262144 or source_diag_bytes + bytes.size() > 1048576:
		return source_diag_secondary("DIAGNOSTIC_BYTE_CAP")
	var file = File.new()
	var path = OUT.plus_file("source-window-diagnostic.jsonl")
	if source_diag_records == 0 and file.file_exists(path):
		return source_diag_secondary("DIAGNOSTIC_PREEXISTING")
	if file.open(path, File.READ_WRITE if source_diag_records > 0 else File.WRITE) != OK:
		return source_diag_secondary("DIAGNOSTIC_OPEN")
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		return source_diag_secondary("DIAGNOSTIC_WRITE")
	source_diag_records += 1
	source_diag_bytes += bytes.size()
	return true



func source_control_target(value):
	if typeof(value) == TYPE_OBJECT and is_instance_valid(value):
		return value.get_instance_id()
	if typeof(value) == TYPE_INT and value > 0:
		return value
	return null



func source_control_bound_value(value):
	match typeof(value):
		TYPE_NIL:
			return {"type": "NULL"}
		TYPE_BOOL:
			return {"type": "BOOL", "value": value}
		TYPE_INT:
			return {"type": "INT", "value": str(value)}
		TYPE_REAL:
			return {"type": "REAL", "bits": float_bits(value)}
		TYPE_STRING:
			if value.to_utf8().size() <= 256:
				return {"type": "STRING", "value": value}
		TYPE_OBJECT:
			if is_instance_valid(value):
				return {"type": "OBJECT_ID", "value": str(value.get_instance_id())}
	return {"type": "UNSUPPORTED", "variant_type": typeof(value)}



func source_control_rows(emitter, signal_name):
	var result = {"complete_seen": false, "row_count": 0, "rows": [], "reason": null}
	if emitter == null or not is_instance_valid(emitter) or not emitter.has_signal(signal_name):
		result.reason = "NO_EMITTER_OR_SIGNAL"
		return result
	var rows = emitter.get_signal_connection_list(signal_name)
	result.row_count = rows.size()
	if rows.size() > 1024:
		result.reason = "CONNECTION_ROW_CAP"
		return result
	var supported = true
	for index in range(rows.size()):
		var row = rows[index]
		var binds = row.get("binds", null)
		var encoded = []
		if typeof(binds) != TYPE_ARRAY or binds.size() > 64:
			supported = false
		else:
			for bound in binds:
				var data = source_control_bound_value(bound)
				if data.type == "UNSUPPORTED":
					supported = false
				encoded.append(data)
		var method = row.get("method", null)
		var flags = row.get("flags", null)
		var source_id = source_control_target(row.get("source", null))
		var target_id = source_control_target(row.get("target", null))
		if typeof(method) != TYPE_STRING or method.to_utf8().size() > 256 or typeof(flags) != TYPE_INT:
			supported = false
		if source_id == null or target_id == null:
			supported = false
		result.rows.append({"ordinal": index, "source_has_key": row.has("source"), "source_variant_type": typeof(row.get("source", null)), "source_available": source_id != null, "source_native_id": str(source_id) if source_id != null else null, "target_has_key": row.has("target"), "target_variant_type": typeof(row.get("target", null)), "target_available": target_id != null, "target_native_id": str(target_id) if target_id != null else null, "method": method if typeof(method) == TYPE_STRING and method.to_utf8().size() <= 256 else null, "flags": flags if typeof(flags) == TYPE_INT else null, "binds_count": binds.size() if typeof(binds) == TYPE_ARRAY else null, "binds": encoded})
	result.complete_seen = supported
	result.reason = null if supported else "UNSUPPORTED_CONNECTION_FIELD"
	return result



func source_cut_control():
	return {"phase": source_cut_phase, "dispatching": source_cut_dispatching, "emit_count": source_cut_emit_count, "receiver_available": source_cut_receiver_id > 0, "receiver_id": str(source_cut_receiver_id) if source_cut_receiver_id > 0 else null, "physics": source_cut_physics if source_cut_physics >= 0 else null, "idle": source_cut_idle if source_cut_idle >= 0 else null, "ack": source_cut_ack, "emit_error": source_cut_emit_error, "finish_return": source_cut_finish_return, "failed": failed, "closed": closed, "complete": source_window_complete, "clock_closed": king_clock_closed, "ui_closed": ui_closed, "first_error": first_error, "ready_connect": source_cut_ready_connect, "diagnostic_error": source_diag_error}



func source_cut_reject(code, site, detail = null):
	source_diagnostic(site, code, {"control": source_cut_control(), "detail": detail, "private_connections": source_control_rows(self, "source_idle_cut_ready"), "tree_connections": source_control_rows(get_tree(), "idle_frame")})
	fail(code, site)
	get_tree().quit(2)
	return false



func source_cut_receiver():
	var rows = source_control_rows(self, "source_idle_cut_ready")
	if not rows.complete_seen or rows.row_count != 1:
		return null
	var row = rows.rows[0]
	if row.target_native_id != str(get_tree().get_instance_id()) or row.method != "on_idle_source_cut" or row.flags != 0 or row.binds_count != 0:
		return null
	return get_tree()



func ack_source_idle_cut(receiver_id, physics_frame, idle_frame):
	if typeof(receiver_id) != TYPE_INT or typeof(physics_frame) != TYPE_INT or typeof(idle_frame) != TYPE_INT:
		return source_cut_reject("CUT_ACK_TYPES", "ack_source_idle_cut")
	if source_cut_phase != "EMITTING" or not source_cut_dispatching or source_cut_emit_count != 1 or source_cut_ack != null or receiver_id != source_cut_receiver_id or physics_frame != source_cut_physics or idle_frame != source_cut_idle or Engine.get_physics_frames() != physics_frame or Engine.get_idle_frames() != idle_frame or failed:
		return source_cut_reject("CUT_ACK_CONTEXT", "ack_source_idle_cut")
	source_cut_ack = {"receiver_id": str(receiver_id), "physics": physics_frame, "idle": idle_frame, "serial": 1}
	return true



func emit_source_idle_cut_once():
	if failed or not closed or not source_window_complete or not king_clock_closed or not ui_closed or source_cut_phase != "IDLE" or source_cut_emit_count != 0 or source_cut_dispatching or source_cleanup == null or Engine.is_in_physics_frame() or Engine.get_physics_frames() != source_cleanup.physics_frame + 2:
		return source_cut_reject("CUT_DISPATCH_CONTEXT", "emit_source_idle_cut_once")
	var receiver = source_cut_receiver()
	if receiver == null or not receiver.has_method("finish_source_cut"):
		return source_cut_reject("CUT_PRIVATE_RECEIVER", "emit_source_idle_cut_once")
	source_cut_receiver_id = receiver.get_instance_id()
	source_cut_physics = Engine.get_physics_frames()
	source_cut_idle = Engine.get_idle_frames()
	source_cut_emit_count = 1
	source_cut_phase = "EMITTING"
	source_cut_dispatching = true
	if not source_diagnostic("emit_source_idle_cut_once", "EMITTING", {"control": source_cut_control(), "private_connections": source_control_rows(self, "source_idle_cut_ready"), "tree_connections": source_control_rows(get_tree(), "idle_frame")}):
		return source_cut_reject("CUT_DIAGNOSTIC_BEFORE_EMIT", "emit_source_idle_cut_once")
	source_cut_emit_error = emit_signal("source_idle_cut_ready")
	source_cut_dispatching = false
	source_cut_phase = "RETURNED"
	# An OK Error return is not a callback acknowledgement.
	if typeof(source_cut_emit_error) != TYPE_INT or source_cut_emit_error != OK or source_cut_ack == null or failed:
		return source_cut_reject("CUT_EMIT_OR_ACK", "emit_source_idle_cut_once")
	if source_cut_ack.receiver_id != str(source_cut_receiver_id) or source_cut_ack.physics != source_cut_physics or source_cut_ack.idle != source_cut_idle or source_cut_ack.serial != 1 or Engine.get_physics_frames() != source_cut_physics or Engine.get_idle_frames() != source_cut_idle or source_cut_receiver() != receiver:
		return source_cut_reject("CUT_RETURN_IDENTITY", "emit_source_idle_cut_once")
	if not source_diagnostic("emit_source_idle_cut_once", "RETURNED_ACK_CHECKED", {"control": source_cut_control()}):
		return source_cut_reject("CUT_DIAGNOSTIC_AFTER_RETURN", "emit_source_idle_cut_once")
	source_cut_phase = "FINALIZING"
	source_cut_finish_return = receiver.finish_source_cut()
	if typeof(source_cut_finish_return) != TYPE_BOOL or not source_cut_finish_return or failed or Engine.get_physics_frames() != source_cut_physics or Engine.get_idle_frames() != source_cut_idle:
		return source_cut_reject("CUT_FINALIZER_RETURN", "emit_source_idle_cut_once")
	source_cut_phase = "FINALIZED"
	if not source_diagnostic("emit_source_idle_cut_once", "FINALIZED", {"control": source_cut_control()}):
		return source_cut_reject("CUT_DIAGNOSTIC_FINALIZED", "emit_source_idle_cut_once")
	return true


# Replacement of existing functions: all normal clock operations remain in original order.

func float_bits(value):
	var buffer = StreamPeerBuffer.new()
	buffer.big_endian = true
	buffer.put_double(value)
	return buffer.data_array.hex_encode()


func fail(code, site, detail = null):
	if failed:
		return false
	failed = true
	# Fixed-size fields only; never stringifies an unknown Object or unbounded detail.
	var safe_detail = detail if typeof(detail) in [TYPE_NIL, TYPE_INT, TYPE_BOOL] else null
	first_error = {"schema": "observer7-failure/1", "code": code, "site": site.substr(0, 256), "sequence": sequence, "detail": safe_detail, "capture_complete": false}
	var message = JSON.print(first_error)
	if message.to_utf8().size() > CAPS.first_error_bytes:
		message = '{"schema":"observer7-failure/1","code":"FAILURE_ENCODING","capture_complete":false}'
	var file = File.new()
	if not file.file_exists(OUT.plus_file("observer7_failure.json")) and file.open(OUT.plus_file("observer7_failure.json"), File.WRITE) == OK:
		file.store_string(message + "\n")
		file.flush()
		file.close()
	return false


