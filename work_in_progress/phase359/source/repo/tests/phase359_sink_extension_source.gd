# SOURCE-only extension template. The generator merges these actual methods into154.
var source_fixture_window = false
var source_fixture_bound = false
var source_buffer = [] # fully encoded primitive rows, never Node/Event objects
var source_buffer_bytes = 0
var source_cleanup = null
var source_window_complete = false
var source_crowns = {} # nativeID -> actual last onStateChanged INT argument
var source_binding_proof = null

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

func entry(site, object, arguments):
	if failed or closed:
		return
	# Native IDs and primitive constructor counters are captured even before the
	# selected inventory can be geometrically associated. No event object is kept.
	if site in ["Core/Buff.gd::init", "Core/Buff.gd::TemporaryStacks._init"]:
		var source_id = native_id(object)
		if source_id == null:
			return
		var source_type = "temporary" if site == "Core/Buff.gd::TemporaryStacks._init" else "buff"
		var key = object.get_instance_id()
		if source_types.has(key) and source_types[key] != source_type:
			fail("SOURCE_TYPE_ID_COLLISION", site)
			return
		source_types[key] = source_type
	if site in ["Items/Item.gd::_ready", "Items/Item.gd::prepare", "Core/Buff.gd::init"]:
		var id = object.get_instance_id()
		native_id(object)
		if not source_lifetimes.has(id):
			source_lifetimes[id] = {"scene": 0, "ready": 0, "prepare": 0, "buff_init": 0, "pooled": false}
		var counter = "ready" if site == "Items/Item.gd::_ready" else ("prepare" if site == "Items/Item.gd::prepare" else "buff_init")
		source_lifetimes[id][counter] += 1
	if site == "Core/Game.gd::prepareItems" and not source_fixture_bound:
		fail("SOURCE_PREPARE_WITHOUT_ACTUAL_SLOT_BINDING", site)
		return
	if not source_observable(site, object):
		return
	if not SITES.has(site):
		fail("SOURCE_UNDECLARED_SELECTED_SITE", site)
		return
	begin_encoding()
	source_phase = site + ":enter"
	if site == "Core/Game.gd::prepareItems":
		if not source_fixture_bound or not selected_lineage(arguments.items, [object.PLAYER, object.OPPONENT]) or not rng_initial_capture(object):
			fail("SOURCE_PREPARE_WITHOUT_BOUND_FRESH_PROOF", site)
			return
		enabled = true
	if site == "Core/Game.gd::activateItems":
		if not rng_initial_continuity() or not begin_king_clock(object, arguments.items):
			return
		activation_checkpoints += 1
		if activation_checkpoints != 1:
			fail("SOURCE_ACTIVATE_MULTIPLE", site)
	if site == "Items/Exclusive/KingGoobert.gd::onStateChanged":
		if typeof(arguments._crownState) != TYPE_INT:
			fail("SOURCE_CROWN_ARGUMENT_TYPE", site)
			return
		source_crowns[str(object.get_instance_id())] = arguments._crownState
	if site == "Core/Buff.gd::gainTemporary":
		if active_buff_calls.size() >= CAPS.depth:
			fail("SOURCE_BUFF_CONTEXT_DEPTH", site)
		else:
			active_buff_calls.append({"target": ids.get(object.character.get_instance_id(), null), "stack": buff_name(object.type), "reflect": arguments.reflect})
	if site in ["Core/Game.gd::prepareItems", "Core/Game.gd::activateItems"]:
		checkpoint(site, object, arguments.items)
	var spec = SITES[site]
	write_record(spec.channel, site, "enter", object, {"arguments": encode(arguments), "state": state(object, spec.state_schema)})

func leave(site, object, value, edge):
	if failed or closed:
		return
	if site == "Sheets/ItemBook.gd::detectMentionedStacks":
		metadata_ready = true
	if site in ["Items/ItemDescriptor.gd::instantiate", "Items/ItemDescriptor.gd::instantiate_pooled"]:
		scene_instance(object, value, site.ends_with("instantiate_pooled"))
	if not source_observable(site, object):
		return
	if not SITES.has(site):
		fail("SOURCE_UNDECLARED_SELECTED_RETURN", site)
		return
	begin_encoding()
	if site.begins_with("Core/CombatLog.gd::createEvent") and source_is(value, "res://Core/CombatEvent.gd"):
		write_record("allocation", site, "allocation_complete", object, {"event_data": event_data(value)})
	source_phase = site + ":" + edge
	var spec = SITES[site]
	write_record(spec.channel, site, edge, object, {"return_value": encode(value), "state": state(object, spec.state_schema)})
	if site == "Core/Buff.gd::gainTemporary":
		if active_buff_calls.empty():
			fail("SOURCE_BUFF_CONTEXT_UNBALANCED", site)
		else:
			active_buff_calls.pop_back()
	if site == "Core/Game.gd::combatEndDeferred":
		enabled = false
		source_mark_cleanup()

func scene_instance(descriptor, item, pooled):
	if failed or closed:
		return
	ui_bind_scene(descriptor, item, pooled)
	if descriptor.itemIndex == 262:
		timer_birth(item.get_node("BuffTimer"), item, "King.scene.instance")
	var id = native_id(item)
	var key = item.get_instance_id()
	if not source_lifetimes.has(key):
		source_lifetimes[key] = {"scene": 0, "ready": 0, "prepare": 0, "buff_init": 0, "pooled": false}
	source_lifetimes[key].scene += 1
	source_lifetimes[key].pooled = pooled
	if not source_fixture_window:
		return
	begin_encoding()
	var row = {"descriptor_id": native_id(descriptor), "item_id": id, "item_index": encode(descriptor.itemIndex), "pooled": pooled, "scene_path": descriptor.scene.resource_path, "particle": null}
	# This thin domain has no53/168 ParticleTimer; never invent a ready sample.
	if source_fixture_bound and not ids.has(key):
		var observation = {"schema": "observer7-record/1", "sequence": sequence, "channel": "lineage", "site": "Items/ItemDescriptor.gd::instantiate_pooled" if pooled else "Items/ItemDescriptor.gd::instantiate", "edge": "scene_instance", "subject": reference(item), "stamp": stamp(), "payload": row}
		sequence += 1
		source_write_diagnostic(observation)
	else:
		write_record("lineage", "Items/ItemDescriptor.gd::instantiate_pooled" if pooled else "Items/ItemDescriptor.gd::instantiate", "scene_instance", item, row)

func timer_before(timer, operation, args, site):
	track_king_timer_api(timer, operation)
	if failed or closed or not source_fixture_bound:
		return
	if not ids.has(timer.get_instance_id()):
		# Foreign visual AutoHide calls stay in the complete UI authority stream.
		if site.begins_with("Utility/AutoHideParticles.gd::"):
			return
		fail("SOURCE_UNKNOWN_TIMER_API_OWNER", site)
		return
	if not SITES.has(site):
		fail("SOURCE_UNKNOWN_TIMER_API_SITE", site)
		return
	begin_encoding()
	source_phase = site + ":timer_before"
	var raw_args = []
	for arg in args:
		raw_args.append(encode(arg))
	write_record("runtime", site, "timer_before", timer, {"role": ids[timer.get_instance_id()], "operation": operation, "argc": args.size(), "args": raw_args, "public_before": timer_state(timer), "public_after": null})

func timer_after(timer, operation, args, site):
	if failed or closed or not source_fixture_bound:
		return
	if not ids.has(timer.get_instance_id()):
		if site.begins_with("Utility/AutoHideParticles.gd::"):
			return
		fail("SOURCE_UNKNOWN_TIMER_API_OWNER_AFTER", site)
		return
	if not SITES.has(site):
		fail("SOURCE_UNKNOWN_TIMER_API_SITE_AFTER", site)
		return
	begin_encoding()
	source_phase = site + ":timer_after"
	var raw_args = []
	for arg in args:
		raw_args.append(encode(arg))
	write_record("runtime", site, "timer_after", timer, {"role": ids[timer.get_instance_id()], "operation": operation, "argc": args.size(), "args": raw_args, "public_before": null, "public_after": timer_state(timer)})

func begin_fixture_window(slot_table):
	if failed or closed or source_fixture_window or configured or not ui_opened:
		return fail("SOURCE_FIXTURE_WINDOW_ORDER", "begin_fixture_window")
	if not source_same_slot_value(slot_table, SOURCE_SLOT_TABLE):
		return fail("SOURCE_FIXED_SLOT_TABLE", "begin_fixture_window")
	source_fixture_window = true
	return true

func source_register(registry, object, role):
	if object == null or not is_instance_valid(object) or registry.has(object.get_instance_id()):
		return fail("SOURCE_ROLE_OBJECT_ALIAS", role)
	for old_role in registry.values():
		if old_role == role:
			return fail("SOURCE_ROLE_DUPLICATE", role)
	registry[object.get_instance_id()] = role
	return true

func bind_fixed_inventory(slot_table):
	if failed or closed or not source_fixture_window or source_fixture_bound or configured:
		return fail("SOURCE_BIND_ORDER", "bind_fixed_inventory")
	if not source_same_slot_value(slot_table, SOURCE_SLOT_TABLE):
		return fail("SOURCE_BIND_FIXED_TABLE", "bind_fixed_inventory")
	var game = get_node("/root/Game")
	var registry = {}
	var proof = []
	for side in ["P", "O"]:
		var character = game.PLAYER if side == "P" else game.OPPONENT
		if character.characterClass != 0 or not source_is(character, "res://Core/Character.gd"):
			return fail("SOURCE_CHARACTER_DOMAIN", side)
		if not source_register(registry, character, side):
			return false
		var inventory = character.INVENTORY
		var actual = inventory.getItems()
		var wanted = []
		for spec in SOURCE_SLOT_TABLE:
			if spec.side == side:
				wanted.append(spec)
		if actual.size() != wanted.size():
			return fail("SOURCE_INVENTORY_COUNT", side)
		var used = {}
		var encounter = []
		for item in actual:
			if not source_is(item, "res://Items/Item.gd") or item.inventory != inventory:
				return fail("SOURCE_FOREIGN_ITEM", side)
			var matches = []
			var top_left = item.getTopLeftCell()
			for spec in wanted:
				if item.descriptor.itemIndex == spec.item_index and top_left == Vector2(spec.x, spec.y) and item.faceDirection == spec.f:
					matches.append(spec)
			if matches.size() != 1:
				return fail("SOURCE_SLOT_GEOMETRY_AMBIGUOUS", side)
			var spec = matches[0]
			if used.has(spec.instance_id) or not item.placed or item.getGemsNoNull().size() != 0:
				return fail("SOURCE_SLOT_DUPLICATE_OR_GEMS", spec.instance_id)
			if item.occupiedCells.size() != spec.cells.size():
				return fail("SOURCE_OCCUPIED_SIZE", spec.instance_id)
			var cells = []
			for cell in item.occupiedCells:
				if cell.x != int(cell.x) or cell.y != int(cell.y) or not spec.cells.has([int(cell.x), int(cell.y)]) or cells.has([int(cell.x), int(cell.y)]):
					return fail("SOURCE_OCCUPIED_MEMBERS", spec.instance_id)
				cells.append([int(cell.x), int(cell.y)])
			if not source_register(registry, item, spec.instance_id):
				return false
			used[spec.instance_id] = true
			encounter.append(spec.instance_id)
			proof.append({"instance_id": spec.instance_id, "input_slot": spec.input_slot, "native_id": native_id(item), "descriptor_id": native_id(item.descriptor), "item_index": encode(item.descriptor.itemIndex), "top_left": {"x": encode(top_left.x), "y": encode(top_left.y)}, "orientation": encode(item.faceDirection), "occupiedCells": cells, "inventory_id": native_id(inventory), "character_id": native_id(character), "inventory_encounter_index": actual.find(item)})
		if used.size() != wanted.size():
			return fail("SOURCE_SLOT_MISSING", side)
		for name in ["tickTimer", "invulnerabilityTimer", "battleRageTimer", "autoRageTimer"]:
			var role = "tick:" + side if name == "tickTimer" else ("invu:" + side if name == "invulnerabilityTimer" else "aux:" + side + ":" + name)
			if not source_register(registry, character.get(name), role):
				return false
		for category in range(100, 111):
			if not source_register(registry, character.buffs[category].timer, "buff:" + side + ":" + str(category)):
				return false
	for pair in [[get_tree().get_root(), "root_viewport"], [game, "game"], [get_node("/root/Util"), "util"], [game.combatTimer, "combat_timer"], [game.combatTimer.fatigueStartTimer, "fatigue:start"], [game.combatTimer.fatigueTickTimer, "fatigue:tick"]]:
		if not source_register(registry, pair[0], pair[1]):
			return false
	for item in game.PLAYER.INVENTORY.getItems():
		if item.descriptor.itemIndex == 262:
			for pair in [[item.buffTimer, "king_buff:P:12"], [item.activationParticles.timer, "king_hide:P:12"], [item.get_node("Icon/SpecificDragParticles").timer, "king_drag:P:12"]]:
				if not source_register(registry, pair[0], pair[1]):
					return false
	if not configure(registry):
		return false
	source_fixture_bound = true
	source_binding_proof = {"schema": "phase359-source-slot-bindings/1", "source_slot_table": SOURCE_SLOT_TABLE, "actual_bindings": proof, "raw_early_rows_unchanged": true, "model_input_admitted": false, "remaining_interface": "NOT_IN_358_ELEVEN_CARRIER_SCHEMA"}
	if not write_king_json("king-slot-bindings.json", source_binding_proof):
		return false
	for row in source_buffer:
		var native = int(row.subject.native_id)
		if registry.has(native) and (registry[native].begins_with("P:") or registry[native].begins_with("O:")):
			if not source_write_row(row):
				return false
		else:
			# The early observation is retained as provenance, never silently dropped.
			if not source_write_diagnostic(row):
				return false
	source_buffer.clear()
	source_buffer_bytes = 0
	return metadata([1, 4, 11, 19, 22, 262])

func source_write_diagnostic(row):
	var bytes = (JSON.print(row) + "\n").to_utf8()
	var previous = file_sizes.get("unselected-source-lineage.jsonl", 0)
	if bytes.size() > CAPS.record_bytes or previous + bytes.size() > CAPS.file_bytes or total_bytes + king_input_bytes + bytes.size() > CAPS.total_bytes:
		return fail("SOURCE_DIAGNOSTIC_CAP", row.site)
	var file = File.new()
	var path = OUT.plus_file("unselected-source-lineage.jsonl")
	if file.open(path, File.READ_WRITE if file.file_exists(path) else File.WRITE) != OK:
		return fail("SOURCE_DIAGNOSTIC_OPEN", row.site)
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		return fail("SOURCE_DIAGNOSTIC_WRITE", row.site)
	file_sizes["unselected-source-lineage.jsonl"] = previous + bytes.size()
	total_bytes += bytes.size()
	return true

func source_write_row(row):
	if not CHANNEL_FILES.has(row.channel):
		return fail("SOURCE_UNKNOWN_CHANNEL", row.site)
	var bytes = (JSON.print(row) + "\n").to_utf8()
	var previous = file_sizes.get(CHANNEL_FILES[row.channel], 0)
	if bytes.size() > CAPS.record_bytes or previous + bytes.size() > CAPS.file_bytes or total_bytes + king_input_bytes + bytes.size() > CAPS.total_bytes:
		return fail("SOURCE_ROW_CAP", row.site)
	var file = File.new()
	var path = OUT.plus_file(CHANNEL_FILES[row.channel])
	if file.open(path, File.READ_WRITE if previous > 0 else File.WRITE) != OK:
		return fail("SOURCE_ROW_OPEN", row.site)
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		return fail("SOURCE_ROW_WRITE", row.site)
	file_sizes[CHANNEL_FILES[row.channel]] = previous + bytes.size()
	total_bytes += bytes.size()
	return true

func write_record(channel, site, edge, subject, payload):
	if failed or closed:
		return false
	if not CHANNEL_FILES.has(channel) or sequence >= CAPS.records:
		return fail("SOURCE_RECORD_CAP_OR_CHANNEL", site)
	var row = {"schema": "observer7-record/1", "sequence": sequence, "channel": channel, "site": site, "edge": edge, "subject": reference(subject), "stamp": stamp(), "payload": payload}
	sequence += 1
	if not source_fixture_bound:
		if not source_fixture_window or channel != "lineage":
			return true
		var bytes = (JSON.print(row) + "\n").to_utf8()
		if source_buffer.size() >= 384 or source_buffer_bytes + bytes.size() > 2097152:
			return fail("SOURCE_PREBIND_PRIMITIVE_BUFFER_CAP", site)
		source_buffer.append(row) # already primitive; stamp/seq/role remain original
		source_buffer_bytes += bytes.size()
		return true
	return source_write_row(row)

func source_observable(site, object):
	if site == "Items/Item.gd::_ready":
		return source_fixture_window and (not source_fixture_bound or ids.has(object.get_instance_id()))
	if not source_fixture_bound:
		return false
	if not SITES.has(site):
		if object != null and ids.has(object.get_instance_id()):
			fail("SOURCE_UNKNOWN_SELECTED_HOOK", site)
		return false
	if object != null and source_is(object, "res://Items/Item.gd"):
		return ids.has(object.get_instance_id())
	if source_is(object, "res://Utility/AutoHideParticles.gd"):
		return source_selected_auto(object)
	return true

func source_selected_auto(object):
	var id = str(object.get_instance_id())
	if not ui_particles.has(id):
		return false
	var owner = ui_particle_owners.get(id, "")
	return ui_kings.has(owner) and ui_kings[owner].pooled == false and ids.get(int(owner), "") == "P:12"

func state(object, schema):
	if schema in ["item", "goobert", "king", "potion"]:
		var index = object.descriptor.itemIndex
		if not index in [1, 4, 11, 19, 22, 262]:
			fail("SOURCE_ITEM_DOMAIN", source_phase)
			return {}
		schema = "king" if index == 262 else ("potion" if index == 19 else "item")
	if not STATE_SCHEMAS.has(schema):
		fail("SOURCE_STATE_SCHEMA", source_phase)
		return {}
	if schema == "node":
		return node_state(object)
	if schema == "timer":
		return timer_state(object)
	var result = {}
	for key in STATE_SCHEMAS[schema]:
		if key == "descriptorIndex":
			result[key] = encode(object.descriptor.itemIndex)
		elif key == "native_id":
			result[key] = native_id(object)
		elif key == "allocation_counter":
			result[key] = encode(object.combatLog.eventNum)
		elif key == "event_count":
			result[key] = encode(object.events.size())
		elif key == "connection_count":
			var count = 0
			for emission in object.connections:
				count += object.connections[emission].size()
			result[key] = encode(count)
		elif STATE_SCHEMAS[schema][key] in ["timer", "timer|null"]:
			result[key] = timer_state(object.get(key))
		elif STATE_SCHEMAS[schema][key] == "auto_hide":
			result[key] = state(object.get(key), "auto_hide")
		else:
			result[key] = encode(object.get(key))
	return result

func source_resources(game):
	var result = []
	for character in [game.PLAYER, game.OPPONENT]:
		var rows = []
		for category in range(100, 111):
			rows.append({"stack": encode(category), "state": state(character.buffs[category], "buff")})
		result.append({"side": side(character), "native_id": native_id(character), "buffProtectStacks": encode(character.buffProtectStacks), "debuffReflectStacks": encode(character.debuffReflectStacks), "buffs": rows})
	return result

func source_mark_cleanup():
	if source_cleanup != null or not king_clock_active or failed:
		return fail("SOURCE_CLEANUP_ORDER", "Core/Game.gd::combatEndDeferred")
	source_cleanup = {"physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames(), "is_in_physics_frame": Engine.is_in_physics_frame()}
	return write_king_json("king-post-cleanup-source.json", source_runtime_snapshot())

func source_runtime_snapshot():
	var value = king_runtime_snapshot()
	var game = get_node("/root/Game")
	var chars = {}
	for side in ["P", "O"]:
		var character = game.PLAYER if side == "P" else game.OPPONENT
		chars[side] = {"invulnerable": encode(character.invulnerable), "invulnerabilityItem": encode(character.invulnerabilityItem), "invulBubbleVisible": encode(character.invulBubbleVisible), "buffProtectStacks": encode(character.buffProtectStacks)}
	var kings = {}
	for item in game.PLAYER.INVENTORY.getItems():
		if item.descriptor.itemIndex == 262:
			var id = str(item.get_instance_id())
			if not source_crowns.has(id):
				fail("SOURCE_CROWN_NOT_OBSERVED", "source_runtime_snapshot")
				return {}
			kings[ids[item.get_instance_id()]] = {"fields": state(item, "king"), "crown_last_observed_argument": encode(source_crowns[id]), "crown_origin": "ACTUAL_ON_STATE_CHANGED_ARGUMENT_NOT_NATIVE_STORED_GETTER"}
	value["characters_invu"] = chars
	value["king_source_state"] = kings
	value["cleanup_clock"] = source_cleanup
	value["partition"] = "EXPECTED_ONLY_NOT_MODEL_INPUT"
	return value

func clock_idle_signal():
	ui_check_controls()
	if king_clock_active:
		clock_pass("idle", get_process_delta_time())
		if source_cleanup != null and Engine.get_physics_frames() >= source_cleanup.physics_frame + 2:
			if Engine.get_physics_frames() != source_cleanup.physics_frame + 2:
				fail("SOURCE_MISSED_FIRST_IDLE_CUT", "clock_idle_signal")
				return
			if not close_king_clock():
				return
			if not write_king_json("king-final-source.json", source_runtime_snapshot()):
				return
			if not ui_close():
				return
			source_window_complete = not failed
			closed = true

func source_completion_receipt():
	return {"source_window_complete": source_window_complete, "failed": failed, "clock_closed": king_clock_closed, "ui_closed": ui_closed, "cleanup": source_cleanup, "clock_passes": king_clock_count, "native_capture_accepted": false, "collector_archive_pending": true}
