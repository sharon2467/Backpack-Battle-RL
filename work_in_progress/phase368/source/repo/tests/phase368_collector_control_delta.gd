# Observation-control delta only; merged into a new365-derived collector.
var source_cut_payload = null
var source_cut_finish_entered = false
var source_control_fallback_records = 0
var source_control_fallback_bytes = 0
var source_control_secondary = null
var source_control_connect_attempted = false
var source_control_connect_return = null
var source_book_reached = false
var source_instantiate_reached = false
var source_geometry_reached = false


func source_control_snapshot(site, reason, detail = null):
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	var available = observer != null and observer.has_method("source_cut_control")
	var table = observer.source_control_rows(get_tree(), "idle_frame") if available else collector_control_rows(get_tree(), "idle_frame")
	var private_rows = observer.source_control_rows(observer, "source_idle_cut_ready") if available else {"complete_seen": false, "row_count": 0, "rows": [], "reason": "OBSERVER_UNAVAILABLE"}
	var match_indices = {"sink": [], "collector_cut": [], "private_collector": []}
	for row in table.rows:
		if observer != null and row.target_native_id == str(observer.get_instance_id()) and row.method == "clock_idle_signal":
			match_indices.sink.append(row.ordinal)
		if row.target_native_id == str(get_instance_id()) and row.method == "on_idle_source_cut":
			match_indices.collector_cut.append(row.ordinal)
	for row in private_rows.rows:
		if row.target_native_id == str(get_instance_id()) and row.method == "on_idle_source_cut":
			match_indices.private_collector.append(row.ordinal)
	return {"site": site, "reason": reason, "stage": stage, "detail": detail, "collector_id": str(get_instance_id()), "tree_id": str(get_tree().get_instance_id()), "observer_present": observer != null, "observer_id": str(observer.get_instance_id()) if observer != null else null, "observer_api_available": available, "observer_failed": observer.failed if available else null, "first_error": observer.first_error.duplicate(true) if available and typeof(observer.first_error) == TYPE_DICTIONARY else null, "ui_opened": observer.ui_opened if available else null, "ui_closed": observer.ui_closed if available else null, "closed": observer.closed if available else null, "configured": observer.configured if available else null, "metadata_ready": observer.metadata_ready if available else null, "source_fixture_window": observer.source_fixture_window if available else null, "source_window_complete": observer.source_window_complete if available else null, "listener_attached": source_listener_attached, "connect_attempted": source_control_connect_attempted, "connect_return": source_control_connect_return, "clock_is_connected": is_connected("idle_frame", observer, "clock_idle_signal") if available else null, "private_is_connected": observer.is_connected("source_idle_cut_ready", self, "on_idle_source_cut") if available and observer.has_signal("source_idle_cut_ready") else null, "tree_connections": table, "private_connections": private_rows, "match_indices": match_indices, "cut": observer.source_cut_control() if available else null, "once_guard": source_cut_frozen, "finish_entered": source_cut_finish_entered, "book_reached": source_book_reached, "instantiate_reached": source_instantiate_reached, "geometry_reached": source_geometry_reached}


func source_control_record(site, reason, detail = null):
	var snapshot = source_control_snapshot(site, reason, detail)
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	var ok = false
	if observer != null and observer.has_method("source_diagnostic"):
		ok = observer.source_diagnostic(site, reason, snapshot)
	else:
		ok = collector_diagnostic_fallback(snapshot)
	if not ok and source_control_secondary == null:
		source_control_secondary = "DIAGNOSTIC_WRITE_FAILED_SECONDARY"
		print("SOURCE_COLLECTOR_DIAGNOSTIC_SECONDARY")
	return ok


func collector_diagnostic_fallback(snapshot):
	if not collector_diag_valid(snapshot) or source_control_fallback_records >= 64:
		return false
	var bytes = (JSON.print({"schema": "phase368-collector-source-control/1", "control_sequence": source_control_fallback_records, "physics": Engine.get_physics_frames(), "idle": Engine.get_idle_frames(), "in_physics": Engine.is_in_physics_frame(), "payload": snapshot}) + "\n").to_utf8()
	if bytes.size() > 262144 or source_control_fallback_bytes + bytes.size() > 1048576:
		return false
	var file = File.new()
	var path = OUT.plus_file("collector-source-window-diagnostic.jsonl")
	if source_control_fallback_records == 0 and file.file_exists(path):
		return false
	if file.open(path, File.READ_WRITE if source_control_fallback_records > 0 else File.WRITE) != OK:
		return false
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		return false
	source_control_fallback_records += 1
	source_control_fallback_bytes += bytes.size()
	return true


func source_window_reject(site, reason, detail = null):
	source_control_record(site, reason, detail)
	return false


func source_cut_reject_collector(reason):
	source_window_reject("on_idle_source_cut", reason)
	fail(reason)
	return false


func ensure_source_window():
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if observer == null:
		return source_window_reject("ensure_source_window", "OBSERVER_ABSENT")
	if not observer.has_signal("source_idle_cut_ready") or not observer.has_method("source_cut_control"):
		return source_window_reject("ensure_source_window", "OBSERVER_CONTROL_API_ABSENT")
	if observer.failed:
		return source_window_reject("ensure_source_window", "OBSERVER_FAILED")
	if not observer.ui_opened:
		return source_window_reject("ensure_source_window", "UI_NOT_OPEN")
	if not source_listener_attached and not attach_source_listener():
		return source_window_reject("ensure_source_window", "ATTACH_REJECTED")
	if not observer.source_fixture_window:
		var opened = observer.begin_fixture_window(observer.SOURCE_SLOT_TABLE.duplicate(true))
		if not opened:
			return source_window_reject("ensure_source_window", "BEGIN_FIXTURE_REJECTED", {"called": true, "return": opened})
		if not source_control_record("ensure_source_window", "BEGIN_FIXTURE_RETURNED", {"called": true, "return": opened}):
			return source_window_reject("ensure_source_window", "BEGIN_DIAGNOSTIC_FAILED")
	return true


func check_source_listener_order():
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	var seen = source_control_snapshot("check_source_listener_order", "CHECK")
	# Preserve all rows before any early return. Tree order is evidence, not sink+1 policy.
	source_connection_order = {"tree": seen.tree_connections, "private": seen.private_connections, "indices": seen.match_indices}
	if observer == null or not seen.observer_api_available:
		return source_window_reject("check_source_listener_order", "OBSERVER_API_ABSENT")
	if not seen.tree_connections.complete_seen or not seen.private_connections.complete_seen:
		return source_window_reject("check_source_listener_order", "CONNECTION_EVIDENCE_INCOMPLETE")
	if seen.match_indices.sink.size() != 1 or seen.match_indices.collector_cut.size() != 0:
		return source_window_reject("check_source_listener_order", "TREE_CLOCK_OR_OLD_CUT_SUBSCRIPTION")
	var sink_row = seen.tree_connections.rows[seen.match_indices.sink[0]]
	if sink_row.flags != 0 or sink_row.binds_count != 0:
		return source_window_reject("check_source_listener_order", "TREE_CLOCK_FLAGS_OR_BINDS")
	if seen.private_connections.row_count != 1 or seen.match_indices.private_collector.size() != 1:
		return source_window_reject("check_source_listener_order", "PRIVATE_RECEIVER_NOT_UNIQUE")
	var row = seen.private_connections.rows[0]
	if row.flags != 0 or row.binds_count != 0 or row.source_native_id != str(observer.get_instance_id()):
		return source_window_reject("check_source_listener_order", "PRIVATE_FLAGS_BINDS_OR_SOURCE")
	if not seen.clock_is_connected or not seen.private_is_connected:
		return source_window_reject("check_source_listener_order", "ACTUAL_CONNECTION_ABSENT")
	return true


func attach_source_listener():
	if source_listener_attached:
		return source_window_reject("attach_source_listener", "DUPLICATE_ATTACH")
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if observer == null or not observer.has_signal("source_idle_cut_ready") or not observer.has_method("source_cut_control"):
		return source_window_reject("attach_source_listener", "OBSERVER_SIGNAL_API_ABSENT")
	if not is_connected("idle_frame", observer, "clock_idle_signal"):
		return source_window_reject("attach_source_listener", "TREE_CLOCK_NOT_CONNECTED")
	if not observer.get_signal_connection_list("source_idle_cut_ready").empty():
		return source_window_reject("attach_source_listener", "PRIVATE_SIGNAL_PRECONNECTED")
	source_control_connect_attempted = true
	source_control_connect_return = observer.connect("source_idle_cut_ready", self, "on_idle_source_cut")
	if not source_control_record("attach_source_listener", "CONNECT_RETURNED"):
		return source_window_reject("attach_source_listener", "CONNECT_DIAGNOSTIC_FAILED")
	if source_control_connect_return != OK:
		return source_window_reject("attach_source_listener", "CONNECT_ERROR")
	if not check_source_listener_order():
		return source_window_reject("attach_source_listener", "SUBSCRIPTION_REJECTED")
	source_listener_attached = true
	return true


func observer7_precondition():
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if observer == null:
		return source_window_reject("observer7_precondition", "OBSERVER_ABSENT")
	if not observer.metadata_ready:
		return source_window_reject("observer7_precondition", "METADATA_NOT_READY")
	if not check_source_listener_order():
		return source_window_reject("observer7_precondition", "SUBSCRIPTION_REJECTED")
	var bound = observer.bind_fixed_inventory(observer.SOURCE_SLOT_TABLE.duplicate(true))
	if not bound:
		return source_window_reject("observer7_precondition", "BIND_FIXED_INVENTORY_REJECTED", {"called": true, "return": bound})
	for id in registry:
		if observer.ids.get(id, "") != registry[id]:
			return source_window_reject("observer7_precondition", "REGISTRY_JOIN_REJECTED", {"native_id": str(id), "collector_role": registry[id], "observer_role": observer.ids.get(id, "")})
	if observer.failed:
		return source_window_reject("observer7_precondition", "OBSERVER_FAILED_AFTER_BIND")
	return true


func on_idle_source_cut():
	if done or source_cut_frozen:
		return source_cut_reject_collector("CUT_DUPLICATE_OR_DONE")
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if observer == null or not observer.has_method("source_cut_control") or observer.failed:
		return source_cut_reject_collector("CUT_OBSERVER_FAILURE")
	var control = observer.source_cut_control()
	if control.phase != "EMITTING" or not control.dispatching or control.emit_count != 1 or control.receiver_id != str(get_instance_id()) or control.ack != null or control.emit_error != null:
		return source_cut_reject_collector("CUT_NOT_SYNCHRONOUS_DISPATCH")
	if control.physics != Engine.get_physics_frames() or control.idle != Engine.get_idle_frames():
		return source_cut_reject_collector("CUT_DISPATCH_FRAME_MISMATCH")
	var receipt = observer.source_completion_receipt()
	if not receipt.source_window_complete or not observer.closed or not check_source_listener_order() or Engine.is_in_physics_frame() or not receipt.clock_closed or not receipt.ui_closed or result_value == null:
		return source_cut_reject_collector("CUT_COMPLETION_GUARD")
	if receipt.cleanup == null or Engine.get_physics_frames() != receipt.cleanup.physics_frame + 2:
		return source_cut_reject_collector("CUT_TWO_FUTURE_PHYSICS")
	# Atomic synchronous once guard BEFORE any sampling or callback that can reenter.
	source_cut_frozen = true
	barrier_ok = check_barrier()
	var snapshot = stable_snapshot() # Exactly one full terminal sampling; original getter chain.
	var king_final = observer.source_runtime_snapshot() # Same existing readonly SOURCE sampling.
	if done or observer.failed:
		return source_cut_reject_collector("CUT_SAMPLING_FAILURE")
	var count = snapshot.events.size()
	var native_manifest = {"schema": "native-combat-capture/1", "case_id": config.case_id, "config": config, "version": game.VERSION, "engine": Engine.get_version_info(), "main_scene": ProjectSettings.get_setting("application/run/main_scene"), "physics_fps": Engine.iterations_per_second, "time_scale": Engine.time_scale, "collector_source": "phase362-single-King-oracle-only", "clean_exit": "HOST_RECORD_SEPARATELY", "native_model_admission": false}
	var validation = {"native_capture_written": true, "capture_complete": false, "host_validation_required": true, "native_checks_pass": errors.empty() and barrier_ok and not observer.failed, "end_barrier": barrier_ok, "layout": legal_checks, "errors": errors.duplicate(), "events": count, "result": result_value, "elapsed_ms": OS.get_ticks_msec() - started, "cut": {"physics": Engine.get_physics_frames(), "idle": Engine.get_idle_frames(), "preinternal": true}, "full_snapshot_reads": 1}
	source_cut_payload = {"instances": instance_rows.duplicate(true), "phases": phases.duplicate(true), "event_references": event_references.duplicate(true), "snapshot": snapshot, "native_manifest": native_manifest, "receipt": receipt, "king_cut": {"receipt": receipt, "connection_order": source_connection_order.duplicate(true), "actual_final": king_final, "source": "SAME_IDLE_INSIDE_SINK_AFTER_WRITE_BEFORE_NODE_INTERNAL"}, "validation": validation, "success": errors.empty() and barrier_ok and not observer.failed, "count": count}
	if not source_control_record("on_idle_source_cut", "FROZEN_BEFORE_ACK"):
		return source_cut_reject_collector("CUT_FROZEN_DIAGNOSTIC_FAILED")
	if not observer.ack_source_idle_cut(get_instance_id(), Engine.get_physics_frames(), Engine.get_idle_frames()):
		return source_cut_reject_collector("CUT_ACK_REJECTED")
	return true


func finish_source_cut():
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if done or source_cut_finish_entered or not source_cut_frozen or source_cut_payload == null or observer == null or not observer.has_method("source_cut_control"):
		return source_cut_reject_collector("CUT_FINALIZER_ENTRY")
	var control = observer.source_cut_control() # Observation-control primitives only, no business getter.
	if control.phase != "FINALIZING" or control.dispatching or control.emit_count != 1 or typeof(control.emit_error) != TYPE_INT or control.emit_error != OK or control.ack == null or control.receiver_id != str(get_instance_id()) or control.physics != source_cut_payload.validation.cut.physics or control.idle != source_cut_payload.validation.cut.idle or Engine.get_physics_frames() != control.physics or Engine.get_idle_frames() != control.idle or control.failed:
		return source_cut_reject_collector("CUT_FINALIZER_CONTEXT")
	source_cut_finish_entered = true
	# Serialization only below: frozen primitive DTOs, no getters/snapshots/getStats/advance.
	var jobs = [["instances.json", source_cut_payload.instances], ["phases.json", source_cut_payload.phases], ["event_references.json", source_cut_payload.event_references], ["histories.json", source_cut_payload.snapshot.histories], ["final_state.json", source_cut_payload.snapshot.state], ["native_manifest.json", source_cut_payload.native_manifest], ["observer7-status.json", source_cut_payload.receipt], ["king-collector-cut.json", source_cut_payload.king_cut]]
	for job in jobs:
		write_json(job[0], job[1])
		if done:
			source_control_record("finish_source_cut", "FROZEN_WRITE_FAILED", {"file": job[0]})
			return false # Existing writer already preserved primary and requested exit2.
	write_jsonl("events.jsonl", source_cut_payload.snapshot.events)
	if done:
		source_control_record("finish_source_cut", "FROZEN_WRITE_FAILED", {"file": "events.jsonl"})
		return false
	write_json("validation.json", source_cut_payload.validation)
	if done:
		source_control_record("finish_source_cut", "FROZEN_WRITE_FAILED", {"file": "validation.json"})
		return false
	if not source_control_record("finish_source_cut", "SERIALIZED_BEFORE_RETURN", {"events": source_cut_payload.count}):
		return source_cut_reject_collector("CUT_FINALIZER_DIAGNOSTIC_FAILED")
	done = true
	print("NATIVE_CAPTURE_WRITTEN " + JSON.print({"success": source_cut_payload.success, "events": source_cut_payload.count, "path": ProjectSettings.globalize_path(OUT)}))
	event_objects.clear()
	quit(0 if source_cut_payload.success else 2)
	return source_cut_payload.success
