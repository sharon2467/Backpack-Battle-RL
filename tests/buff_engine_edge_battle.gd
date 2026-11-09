extends Node

var case_data = {}
var run_data_dir = ""
var stage = 0
var started_at = OS.get_ticks_msec()
var combat_at = 0
var advanced = false
var next_id = 0
var active_calls = []
var call_data = {}
var done = false
var expected_events = {}
var partial_before_cap = false
var partial_at_cap = false
var full_at_cap = false
var last_report_time = -30.0

func _ready() -> void:
	var project_dir = ProjectSettings.globalize_path("res://project.godot").get_base_dir()
	run_data_dir = OS.get_environment("BB_BUFF_EDGE_RUN_DATA")
	var source = File.new()
	if source.open(run_data_dir.plus_file("case.json"), File.READ) != OK:
		fail("cannot read isolated case.json")
		return
	var parsed = JSON.parse(source.get_as_text())
	source.close()
	if parsed.error != OK or typeof(parsed.result) != TYPE_DICTIONARY:
		fail("invalid isolated case.json")
		return
	case_data = parsed.result
	var loaded_buff_sha = File.new().get_sha256("res://Core/Buff.gd").to_lower()
	var environment_row = {"case":case_data.get("name", "unknown"), "exe":OS.get_executable_path(), "engine":Engine.get_version_info(), "project":project_dir, "user_data":OS.get_user_data_dir(), "editor_feature":OS.has_feature("editor"), "full_feature":OS.has_feature("full_version"), "disable_steam_feature":OS.has_feature("disable_steam_integration"), "custom_features_setting":ProjectSettings.get_setting("custom_features") if ProjectSettings.has_setting("custom_features") else null, "EDITOR":Game.EDITOR, "FULLVERSION":Game.FULLVERSION, "game_version":Game.VERSION, "loaded_buff_sha256":loaded_buff_sha,"loaded_game_sha256":File.new().get_sha256("res://Core/Game.gd"),"time_scale":Engine.time_scale}
	environment_row["underscore_custom_features_setting"] = ProjectSettings.get_setting("_custom_features") if ProjectSettings.has_setting("_custom_features") else null
	environment_row["has_custom_feature_callable"] = ProjectSettings.has_method("has_custom_feature")
	if ProjectSettings.has_method("has_custom_feature"):
		environment_row["custom_editor_feature"] = ProjectSettings.call("has_custom_feature", "editor")
		environment_row["custom_full_feature"] = ProjectSettings.call("has_custom_feature", "full_version")
	var project_source = File.new()
	if project_source.open("res://project.godot", File.READ) == OK:
		for line in project_source.get_as_text().split("\n"):
			if line.begins_with("custom_features=") or line.begins_with("_custom_features="):
				environment_row["configured_feature_line"] = line
		project_source.close()
	var environment_file = File.new()
	if environment_file.open(run_data_dir.plus_file(String(case_data.get("name", "unknown")) + "_environment.json"), File.WRITE) == OK:
		environment_file.store_string(JSON.print(environment_row))
		environment_file.close()
	print("BUFF_EDGE_ENV ", JSON.print(environment_row))
	if loaded_buff_sha != OS.get_environment("BB_BUFF_EDGE_EXPECTED_SHA").to_lower():
		fail("unexpected observed Buff source hash")
		return
	print("BUFF_EDGE_DATA_SOURCE ", JSON.print({"file":"res://Sheets/CSV/ItemData.csv" if Game.EDITOR else "res://Sheets/CSV/ItemData_e.csv","plain_md5":File.new().get_md5("res://Sheets/CSV/ItemData.csv"),"encrypted_md5":File.new().get_md5("res://Sheets/CSV/ItemData_e.csv")}))
	if Game.VERSION != "1.1.8" or not Game.EDITOR:
		fail("unexpected game version or missing declared startup compatibility flag")
		return
	if not Game.FULLVERSION:
		fail("original engine did not expose full_version; report before changing startup flags")
		return
	if not OS.get_user_data_dir().replace("\\", "/").begins_with(project_dir.get_base_dir().replace("\\", "/") + "/"):
		fail("user data directory is not isolated under this run")

func _process(_delta: float) -> void:
	if done:
		return
	var timeout = 400000 if case_data.get("mode", "") == "full_cap" else 150000
	if OS.get_ticks_msec() - started_at > timeout:
		fail("timeout stage=" + String(stage))
		return
	if stage == 0:
		if Game.state != Game.State.Title or Game.PLAYER == null or Game.itemLibrary == null:
			return
		if not Game.sceneAnimation.is_connected("animation_finished", Game, "onSceneAnimationFinished"):
			return
		for name in ["Leather Bag", "Holy Armor", "Elephant Rune", "Magic Mirror", "Pocket Sand", "Deer Totem", "Hawk Rune", "Chili Pepper", "Gigawatz"]:
			var descriptor = ItemBook.getDescriptor(name)
			if descriptor == null or descriptor.scene == null:
				fail("required descriptor unavailable: " + name)
				return
		print("BUFF_EDGE_READY ", JSON.print({"case":case_data.name, "game_version":Game.VERSION, "user_data":OS.get_user_data_dir()}))
		if case_data.mode == "smoke":
			finish()
			return
		Game.instanceCharacter(0)
		Game.initStartInventory()
		Game.startFreshRun(Game.Mode.Unranked)
		stage = 1
	elif stage == 1:
		if not advanced and Game.sceneAnimation.current_animation == "TitleToShop":
			advanced = true
			Game.sceneAnimation.advance(1000)
		if Game.state == Game.State.Shop and Game.canSwitchToCombat:
			setup_case()
			if done:
				return
			Game.switchToCombat()
			stage = 2
	elif stage == 2:
		if Game.state != Game.State.Combat or Game.OPPONENT == null:
			return
		if Game.curOpponentData.get("name", "") != "Custom Opponent":
			fail("different opponent source used")
			return
		combat_at = OS.get_ticks_msec()
		print("BUFF_EDGE_COMBAT ", JSON.print({"case":case_data.name, "opponent_items":Game.OPPONENT.INVENTORY.getItems().size(), "time_scale":Engine.time_scale}))
		capture("combat")
		stage = 3
	elif stage == 3:
		if case_data.mode == "full_cap":
			var combat_time = Game.combatTimer.combatTime
			if combat_time - last_report_time >= 30:
				last_report_time = combat_time
				print("BUFF_EDGE_PROGRESS ", JSON.print({"case":case_data.name,"time":combat_time,"blind":Game.OPPONENT.getBlind(),"heat":Game.PLAYER.getHeat(),"player_resistance":Game.PLAYER.damageResistance,"opponent_resistance":Game.OPPONENT.damageResistance,"precap_partial":partial_before_cap,"cap_partial":partial_at_cap,"cap_full":full_at_cap}))
			if partial_before_cap and partial_at_cap and full_at_cap:
				capture("observed")
				finish()
			elif combat_time >= 240:
				capture("timeout")
				fail("natural full-cap target observations not complete by combat time 240")
		elif OS.get_ticks_msec() - combat_at >= 7000:
			capture("observed")
			finish()

func setup_case() -> void:
	Game.PLAYER.INVENTORY.reset()
	if case_data.mode == "full_cap":
		for y in [0, 2, 4]:
			for x in [0, 2, 4, 6]:
				add_item("Leather Bag", x, y)
		for x in range(7):
			add_item("Deer Totem", x, 0)
		for x in range(8):
			add_item("Chili Pepper", x, 2)
		add_item("Hawk Rune", 7, 0)
		add_item("Gigawatz", 7, 1)
		for y in [4, 5]:
			for x in range(8):
				add_item("Hawk Rune", x, y)
	else:
		for cell in [[0, 0], [2, 0], [0, 2], [2, 2]]:
			add_item("Leather Bag", cell[0], cell[1])
		var armor = add_item("Holy Armor", 0, 0)
		if done:
			return
		if case_data.get("elephants", false):
			socket_gems(armor, ["Elephant Rune", "Elephant Rune", "Elephant Rune"])
		if case_data.get("mirrors", false):
			for cell in [[2, 0], [3, 0], [2, 2], [3, 2]]:
				add_item("Magic Mirror", cell[0], cell[1])
			add_item("Magic Mirror", 0, 3, 1)
	var layout = []
	for item in Game.PLAYER.INVENTORY.getItems():
		var cells = []
		for cell in item.occupiedCells:
			cells.push_back([cell.x, cell.y])
		var gems = []
		for gem in item.getGems():
			gems.push_back(gem.descriptor.identifier if gem != null else null)
		layout.push_back({"name":item.descriptor.identifier, "index":item.descriptor.itemIndex, "face":item.faceDirection, "cells":cells, "gems":gems})
	print("BUFF_EDGE_LAYOUT ", JSON.print({"case":case_data.name, "player":0, "items":layout, "health":Game.PLAYER.getMaxHealth()}))

func add_item(name: String, x: int, y: int, f: int = 0) -> Item:
	var item = ItemBook.instantiateItem(name)
	if item == null:
		fail("cannot instantiate " + name)
		return null
	item.ownerType = Item.Owner.PlayerInventory
	Game.playerNode.add_child(item)
	item.setFaceDirectionInstant(f)
	var current_position = item.getTopLeftGlobal()
	var target_position = Game.PLAYER.INVENTORY.tilemap.to_global(Game.PLAYER.INVENTORY.tilemap.map_to_world(Vector2(x, y)))
	item.global_translate(target_position - current_position)
	if not Game.PLAYER.INVENTORY.canAddItemOrBag(item):
		fail("illegal player placement: " + name + " at " + String(Vector2(x, y)))
		return item
	Game.PLAYER.INVENTORY.addItemByTopLeft(item, Vector2(x, y))
	return item

func socket_gems(host: Item, names: Array) -> void:
	if host.getNumSockets() != names.size():
		fail("unexpected socket count")
		return
	for index in names.size():
		var gem = ItemBook.instantiateItem(names[index])
		Game.playerNode.add_child(gem)
		gem.addToSocket(host.sockets[index])
		print("BUFF_EDGE_SOCKET ", JSON.print({"host":host.descriptor.identifier, "slot":index, "gem":gem.descriptor.identifier, "power":gem.gemPower}))

func new_call_id() -> int:
	next_id += 1
	return next_id

func observe(label: String, call_id: int, buff: Reference, payload: Dictionary = {}) -> void:
	if label == "enter":
		var parent_call = active_calls.back() if not active_calls.empty() else -1
		call_data[call_id] = payload.duplicate()
		call_data[call_id]["parent_call"] = parent_call
		call_data[call_id]["initial_current"] = buff.current
		active_calls.push_back(call_id)
		if case_data.get("mode", "") == "full_cap" and payload.get("incoming_reflected", false) and parent_call >= 0:
			var parent_call_data = call_data[parent_call]
			if parent_call_data.get("source", "") == "Gigawatz" and parent_call_data.initial_current < 10000 and parent_call_data.get("last_reflected_count", 0) in [1, 2]:
				partial_before_cap = true
			if parent_call_data.get("source", "") == "Hawk Rune" and parent_call_data.initial_current == 10000 and parent_call_data.get("last_reflected_count", 0) == 1:
				full_at_cap = true
	if payload.has("reflected_count"):
		call_data[call_id]["last_reflected_count"] = payload.reflected_count
	var row = call_data.get(call_id, {}).duplicate()
	row["case"] = case_data.get("name", "startup")
	row["stage"] = label
	row["call_id"] = call_id
	row["time"] = Util.time
	row["frame"] = Util.frameCounter
	row["target"] = buff.character.playerId
	row["type"] = buff.type
	row["current"] = buff.current
	row["permanent"] = buff.permanentStacks
	row["resist_chance"] = buff.resistChancePercent
	row["reflect_chance"] = buff.reflectChancePercent
	row["resist_stacks"] = buff.resistStacks
	row["global_resist"] = buff.character.debuffResistStacks
	row["global_reflect"] = buff.character.debuffReflectStacks
	for key in payload:
		row[key] = payload[key]
	var keep = true
	if case_data.get("mode", "") == "full_cap":
		keep = row.type == 109 and (row.source == "Gigawatz" or (row.target == 1 and row.initial_current >= 9990))
		if row.get("incoming_reflected", false) and row.parent_call >= 0:
			var parent_row_data = call_data.get(row.parent_call, {})
			keep = keep or parent_row_data.get("source", "") == "Gigawatz" or parent_row_data.get("initial_current", 0) >= 9990
		if label == "cap_zero_return" and row.type == 109 and row.target == 1 and row.source == "Gigawatz" and row.initial_current == 10000 and row.get("reflected_count", 0) in [1, 2]:
			partial_at_cap = true
	if keep:
		print("BUFF_EDGE_TRACE ", JSON.print(row))
		if row.get("event_id", -1) >= 0:
			expected_events[row.event_id] = true
	if label == "exit" or label == "cap_zero_return":
		if not active_calls.empty() and active_calls.back() == call_id:
			active_calls.pop_back()
		call_data.erase(call_id)

func capture(label: String) -> void:
	var image = get_viewport().get_texture().get_data()
	image.flip_y()
	var result = image.save_png(run_data_dir.plus_file(String(case_data.name) + "_" + label + ".png"))
	if result != OK:
		fail("viewport capture failed: " + String(result))

func fail(message: String) -> void:
	if done:
		return
	done = true
	print("BUFF_EDGE_FAIL ", JSON.print({"case":case_data.get("name", "startup"), "message":message, "stage":stage}))
	get_tree().quit(1)

func finish() -> void:
	if done:
		return
	done = true
	if case_data.mode != "smoke":
		for event in Game.combatLog.events:
			if event.type == Game.EventType.Blind and (case_data.mode != "full_cap" or expected_events.has(event.id) or (event.origin is Item and event.origin.descriptor.identifier == "Gigawatz")):
				print("BUFF_EDGE_EVENT ", JSON.print({"case":case_data.name, "id":event.id, "time":event.timestamp, "type":event.type, "target":event.target, "origin":event.origin.descriptor.identifier if event.origin is Item else null, "parent":event.parentEvent.id if event.parentEvent != null else -1, "params":event.params}))
		print("BUFF_EDGE_FINAL ", JSON.print({"case":case_data.name, "fight_ended":Game.fightEnded, "player_blind":Game.PLAYER.getBlind(), "opponent_blind":Game.OPPONENT.getBlind(), "player_blind_resist_stacks":Game.PLAYER.buffs[Game.EventType.Blind].resistStacks, "player_resist_chance":Game.PLAYER.buffs[Game.EventType.Blind].resistChancePercent, "player_reflect_chance":Game.PLAYER.buffs[Game.EventType.Blind].reflectChancePercent, "player_damage_resistance":Game.PLAYER.damageResistance,"opponent_damage_resistance":Game.OPPONENT.damageResistance,"precap_partial":partial_before_cap,"cap_partial":partial_at_cap,"cap_full":full_at_cap}))
	print("BUFF_EDGE_PASS ", JSON.print({"case":case_data.name, "mode":case_data.mode, "game_version":Game.VERSION}))
	get_tree().quit(0)
