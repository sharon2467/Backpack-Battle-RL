# SOURCE template merged into the frozen298 collector. No business methods here.
var source_cut_frozen = false
var source_listener_attached = false
var source_write_bytes = 0
var source_file_bytes = {}
var source_connection_order = []

func slot_spec(side, slot):
	var observer = get_root().get_node("NativeRandomObserver")
	for spec in observer.SOURCE_SLOT_TABLE:
		if spec.side == side and spec.input_slot == slot:
			return spec
	return null

func ensure_source_window():
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if observer == null or observer.failed or not observer.ui_opened:
		return false
	if not source_listener_attached and not attach_source_listener():
		return false
	if not observer.source_fixture_window:
		return observer.begin_fixture_window(observer.SOURCE_SLOT_TABLE.duplicate(true))
	return true

func source_connection_target(row):
	var target = row.get("target", null)
	if typeof(target) == TYPE_OBJECT and is_instance_valid(target):
		return target.get_instance_id()
	if typeof(target) == TYPE_INT:
		return target
	return -1

func check_source_listener_order():
	var observer = get_root().get_node("NativeRandomObserver")
	var rows = get_signal_connection_list("idle_frame")
	var seen = []
	var sink_index = -1
	var collector_index = -1
	for i in range(rows.size()):
		var target = source_connection_target(rows[i])
		var method = rows[i].get("method", "")
		seen.append({"target_native_id": str(target), "method": method, "flags": rows[i].get("flags", -1)})
		if target == observer.get_instance_id() and method == "clock_idle_signal":
			if sink_index != -1:
				return false
			sink_index = i
		if target == get_instance_id() and method == "on_idle_source_cut":
			if collector_index != -1:
				return false
			collector_index = i
	if sink_index < 0 or collector_index != sink_index + 1:
		return false # unknown intervening callbacks are not declared pure
	if seen[sink_index].flags != 0 or seen[collector_index].flags != 0:
		return false
	source_connection_order = seen
	return true

func attach_source_listener():
	if source_listener_attached:
		return false
	var observer = get_root().get_node("NativeRandomObserver")
	if not is_connected("idle_frame", observer, "clock_idle_signal"):
		return false
	if connect("idle_frame", self, "on_idle_source_cut") != OK:
		return false
	source_listener_attached = true
	return check_source_listener_order()

func player_spatial_evidence():
	var rows = []
	for item in game.PLAYER.INVENTORY.getItems():
		rows.append({"stable_id": registry[item.get_instance_id()], "node_order": item.get_position_in_parent(), "position": encode(item.getTopLeftCell()), "orientation": encode(item.faceDirection), "occupied_cells": encode(item.occupiedCells), "descriptor_index": encode(item.descriptor.itemIndex), "current_affected": encode(item.currentAffectedItems), "cached_affected": encode(item.cachedAffectedItems)})
	return {"frame": frames(), "items": rows, "source": "DIRECT_MEMBERS_NO_AFFECTED_GETTER_OR_CACHE_REFRESH"}

func observer7_precondition():
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if observer == null or not observer.metadata_ready or not check_source_listener_order():
		return false
	if not observer.bind_fixed_inventory(observer.SOURCE_SLOT_TABLE.duplicate(true)):
		return false
	for id in registry:
		if observer.ids.get(id, "") != registry[id]:
			return false
	return not observer.failed

func start_controlled_combat(player_registered = false):
	if not player_registered or not ensure_source_window():
		fail("single King requires controlled fresh player and actual SOURCE window")
		return
	phase("shop_ready")
	set_stage("combat_wait")
	game.switchToCombat()

func on_combat_end(result):
	if done or source_cut_frozen:
		return
	result_value = result
	set_stage("finalizing")
	# No snapshot/yield/deferred finish. Producer closes on actual first idle cut.

func on_idle_source_cut():
	if done or source_cut_frozen:
		return
	var observer = get_root().get_node_or_null("NativeRandomObserver")
	if observer == null or observer.failed:
		fail("SOURCE observer failure before same-idle cut")
		return
	var receipt = observer.source_completion_receipt()
	if not receipt.source_window_complete:
		return
	if not check_source_listener_order() or Engine.is_in_physics_frame() or not receipt.clock_closed or not receipt.ui_closed or result_value == null:
		fail("same idle preinternal completion identity/order")
		return
	if Engine.get_physics_frames() != receipt.cleanup.physics_frame + 2:
		fail("not exactly two future physics at collector cut")
		return
	source_cut_frozen = true
	barrier_ok = check_barrier()
	var snapshot = stable_snapshot() # Exactly one full terminal sampling.
	var king_final = observer.source_runtime_snapshot() # same idle, adjacent to sink
	var count = snapshot.events.size()
	var native_manifest = {"schema": "native-combat-capture/1", "case_id": config.case_id, "config": config, "version": game.VERSION, "engine": Engine.get_version_info(), "main_scene": ProjectSettings.get_setting("application/run/main_scene"), "physics_fps": Engine.iterations_per_second, "time_scale": Engine.time_scale, "collector_source": "phase362-single-King-oracle-only", "clean_exit": "HOST_RECORD_SEPARATELY", "native_model_admission": false}
	var validation = {"native_capture_written": true, "capture_complete": false, "host_validation_required": true, "native_checks_pass": errors.empty() and barrier_ok and not observer.failed, "end_barrier": barrier_ok, "layout": legal_checks, "errors": errors.duplicate(), "events": count, "result": result_value, "elapsed_ms": OS.get_ticks_msec() - started, "cut": {"physics": Engine.get_physics_frames(), "idle": Engine.get_idle_frames(), "preinternal": true}, "full_snapshot_reads": 1}
	# Everything below uses only the just-frozen primitive DTOs, never resamples.
	write_json("instances.json", instance_rows)
	write_json("phases.json", phases)
	write_json("event_references.json", event_references)
	write_json("histories.json", snapshot.histories)
	write_json("final_state.json", snapshot.state)
	write_jsonl("events.jsonl", snapshot.events)
	write_json("native_manifest.json", native_manifest)
	write_json("observer7-status.json", receipt)
	write_json("king-collector-cut.json", {"receipt": receipt, "connection_order": source_connection_order, "actual_final": king_final, "source": "SAME_IDLE_AFTER_SINK_BEFORE_NODE_INTERNAL"})
	write_json("validation.json", validation)
	done = true
	print("NATIVE_CAPTURE_WRITTEN " + JSON.print({"success": errors.empty() and barrier_ok and not observer.failed, "events": count, "path": ProjectSettings.globalize_path(OUT)}))
	event_objects.clear()
	quit(0 if errors.empty() and barrier_ok and not observer.failed else 2)

func phase(name):
	# Phase bookkeeping no longer repeatedly walks full live state.
	phases.append({"name": name, "frame": frames(), "event_count": game.combatLog.events.size(), "time_scale": Engine.time_scale})
	print("NATIVE_PHASE " + name)

func fields(obj, names):
	var values = {}
	for key in names:
		# SOURCE generator closes each script member read; no property-list hook.
		values[key] = obj.get(key)
	return encode(values)

func run_context():
	return {"scope": "FIXED_SINGLE_KING_ORACLE_ONLY_NO_SKIN_LEAGUE_OR_STEAM_GETTERS"}

func write_json(name, value):
	if source_cut_frozen and done:
		return
	write_source_bytes(name, (JSON.print(value) + "\n").to_utf8())

func write_jsonl(name, rows):
	var bytes = PoolByteArray()
	for row in rows:
		var line = (JSON.print(row) + "\n").to_utf8()
		if line.size() > 2097152 or bytes.size() + line.size() > 67108864:
			fail_write_cap(name)
			return
		bytes.append_array(line)
	write_source_bytes(name, bytes)

func write_source_bytes(name, bytes):
	if done:
		return
	var previous = source_file_bytes.get(name, 0)
	if bytes.size() > 67108864 or source_write_bytes - previous + bytes.size() > 209715200:
		fail_write_cap(name)
		return
	var f = File.new()
	var path = OUT.plus_file(name)
	if f.open(path + ".partial", File.WRITE) != OK:
		fail_write_cap(name)
		return
	f.store_buffer(bytes)
	f.flush()
	var error = f.get_error()
	f.close()
	if error != OK or Directory.new().rename(path + ".partial", path) != OK:
		fail_write_cap(name)
		return
	source_write_bytes += bytes.size() - previous
	source_file_bytes[name] = bytes.size()

func fail_write_cap(name):
	fail("WRITE_CAP_OR_IO:" + name)

func fail(message):
	if done:
		return
	errors.append(message.substr(0, 512))
	done = true
	var f = File.new()
	var path = OUT.plus_file("collector-first-failure.json")
	if not f.file_exists(path) and f.open(path, File.WRITE) == OK:
		f.store_string(JSON.print({"schema": "phase362-failure/1", "code": message.substr(0, 512), "stage": stage, "cut_frozen": source_cut_frozen, "capture_complete": false}) + "\n")
		f.flush()
		f.close()
	print("NATIVE_CAPTURE_FAILED " + message.substr(0, 512))
	quit(2)
