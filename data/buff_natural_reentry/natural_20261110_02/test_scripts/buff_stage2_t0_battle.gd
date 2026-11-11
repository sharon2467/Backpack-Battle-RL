extends Node

var case_data = {}
var run_dir = ""
var stage = 0
var done = false
var advanced = false
var started_wall = OS.get_ticks_msec()
var round_count = 0
var start_frame = -1
var case_started = false
var action_done = false
var reaction_done = false
var deferred_queued = false
var next_id = 0
var observation_sequence = 0
var active_calls = []
var timeout_return_frames = {}
var source_a = null
var source_b = null
var source_c = null
var source_aliases = {}
var banana = null
var traces = []
var timeout_frames = {}
var tick_frames = []
var item_frames = []
var character_ended = false
var shop_requested = false
var shop_cleanse_seen = false
var second_requested = false
var finish_time = 0.8
var round_event_archive = []
var natural_items = {}
var call_metadata = {}
var natural_reentries = []
var natural_timeout_checks = []
var natural_crown_use = false
var natural_crown_use_actual = false

func _ready() -> void:
	run_dir = OS.get_environment("BB_BUFF_T0_RUN_DATA")
	var input = File.new()
	if input.open(run_dir.plus_file("case.json"), File.READ) != OK:
		finish("error", "case.json unavailable")
		return
	var parsed = JSON.parse(input.get_as_text())
	input.close()
	if parsed.error != OK or typeof(parsed.result) != TYPE_DICTIONARY:
		finish("error", "invalid case.json")
		return
	case_data = parsed.result
	if case_data.name.begins_with("natural_") and File.new().get_sha256(run_dir.plus_file("opponent_second.json")).to_lower() != String(case_data.opponent_second_sha256).to_lower():
		finish("error", "second opponent fixture unavailable or changed")
		return
	var fingerprints = {}
	var source_match = true
	for path in case_data.observed_hashes:
		fingerprints[path] = File.new().get_sha256(path).to_lower()
		source_match = source_match and fingerprints[path] == String(case_data.observed_hashes[path]).to_lower()
	var environment = {"exe":OS.get_executable_path(),"exe_sha256":File.new().get_sha256(OS.get_executable_path()),"engine":Engine.get_version_info(),"game_version":Game.VERSION,"project":ProjectSettings.globalize_path("res://"),"user_data":OS.get_user_data_dir(),"editor":OS.has_feature("editor"),"full_version_feature":OS.has_feature("full_version"),"Game_EDITOR":Game.EDITOR,"Game_FULLVERSION":Game.FULLVERSION,"time_scale":Engine.time_scale,"physics_steps_per_second":Engine.iterations_per_second,"loaded_sources":fingerprints,"original_sources":case_data.original_hashes,"source_match":source_match,"plain_csv_md5":File.new().get_md5("res://Sheets/CSV/ItemData.csv"),"encrypted_csv_md5":File.new().get_md5("res://Sheets/CSV/ItemData_e.csv")}
	var evidence = File.new()
	if evidence.open(run_dir.plus_file("environment.json"), File.WRITE) == OK:
		evidence.store_string(JSON.print(environment))
		evidence.close()
	print("BUFF_T0_ENV ",JSON.print(environment))
	if not source_match or environment.exe_sha256.to_lower() != String(case_data.expected_exe_sha).to_lower() or Engine.get_version_info().major != 3 or Engine.get_version_info().minor != 6 or Engine.get_version_info().patch != 2 or Game.VERSION != "1.1.8" or not Game.EDITOR or not Game.FULLVERSION or Engine.time_scale != 1:
		finish("error", "runtime/source fingerprint or feature gate failed")
		return
	if not OS.get_user_data_dir().replace("\\", "/").begins_with(run_dir.replace("\\", "/") + "/appdata/"):
		finish("error", "user data is not isolated in workspace data")
		return
	Game.connect("combat_start", self, "start_case")

func _process(_delta: float) -> void:
	if done:
		return
	if OS.get_ticks_msec() - started_wall > 105000:
		finish("incomplete", "wall deadline")
		return
	if stage == 0:
		if Game.state != Game.State.Title or Game.PLAYER == null or Game.itemLibrary == null:
			return
		if not Game.sceneAnimation.is_connected("animation_finished", Game, "onSceneAnimationFinished"):
			return
		var required_names = ["Leather Bag", "Banana"]
		if case_data.name.begins_with("natural_"):
			required_names += ["Fanny Pack","Leather Armor","Heart Container","Hungry Blade","Strong Stone Skin Potion","Toad","Crown","Healing Herbs","Blueberries","Mana Potion"]
		for name in required_names:
			if ItemBook.getDescriptor(name) == null:
				finish("error", "missing descriptor " + name)
				return
		if case_data.name == "smoke":
			finish("observed", "native title and descriptors ready")
			return
		Game.instanceCharacter(1 if case_data.name.begins_with("natural_") else 0)
		Game.initStartInventory()
		Game.startFreshRun(Game.Mode.Unranked)
		stage = 1
	elif stage == 1:
		if not advanced and Game.sceneAnimation.current_animation == "TitleToShop":
			advanced = true
			Game.sceneAnimation.advance(1000)
		if Game.state == Game.State.Shop and Game.canSwitchToCombat:
			setup_layout()
			if done:
				return
			Game.switchToCombat()
			stage = 2
	elif stage == 2:
		if case_started and Game.state == Game.State.Combat:
			if Game.curOpponentData.get("name", "") != "Custom Opponent":
				finish("error", "different opponent input used")
				return
			snapshot("combat_ready")
			stage = 3
	elif stage == 3:
		if case_data.name.begins_with("natural_"):
			if round_count >= 2:
				var preconditions_met = false
				var matching_reentry = false
				for check in natural_timeout_checks:
					preconditions_met = preconditions_met or check.met
					if check.met:
						for reentry in natural_reentries:
							if reentry.old_timeout_call == check.call_id and reentry.buff_id == check.buff_id and reentry.old_batch_id == check.batch_id and reentry.new_batch_id != check.batch_id and reentry.before_old_remove and reentry.gain_source == natural_items["Strong Stone Skin Potion"].get_instance_id() and reentry.request == 2 and reentry.duration == 4:
								matching_reentry = true
				var chain_met = natural_crown_use and natural_crown_use_actual and not natural_items["Mana Potion"].isFull
				var expected_batch = matching_reentry if case_data.name == "natural_linked" else natural_reentries.empty()
				var covered = preconditions_met and chain_met and expected_batch
				if (Game.combatTimer.combatTime >= 9.0 and covered) or Game.combatTimer.combatTime >= 12.0 or Game.fightEnded:
					finish("observed" if covered else "incomplete", "natural item chain measured" if covered else "natural prerequisites or expected batch were not covered")
		elif case_data.name == "lifecycle_natural":
			if round_count >= 2 and not Game.fightEnded and Game.combatTimer.combatTime >= 0.8:
				finish("observed", "natural end, shop cleanse, and second combat observed")
		elif Game.combatTimer.combatTime >= finish_time:
			finish("observed", "observation window completed; inspect raw events/errors")

func _physics_process(_delta: float) -> void:
	if done or not case_started:
		return
	if case_data.name == "phase_deferred":
		if not action_done and not deferred_queued:
			deferred_queued = true
			call_deferred("run_actions")
	else:
		run_actions()

func setup_layout() -> void:
	Game.PLAYER.INVENTORY.reset()
	natural_items.clear()
	var natural_second = case_data.name.begins_with("natural_") and round_count == 1
	for y in [0,2,4]:
		for x in [0,2,4,6]:
			if natural_second and x == 4 and y == 2:
				continue
			var bag = add_item("Leather Bag",x,y)
			if y == 0 and x == 0:
				source_a = bag
			elif y == 0 and x == 2:
				source_b = bag
			elif y == 0 and x == 4:
				source_c = bag
	if done:
		return
	source_aliases[source_a.get_instance_id()] = "A"
	source_aliases[source_b.get_instance_id()] = "B"
	source_aliases[source_c.get_instance_id()] = "C"
	if natural_second:
		var placements = [["Fanny Pack",4,2],["Fanny Pack",4,3],["Leather Armor",0,0],["Heart Container",4,0],["Hungry Blade",6,2],["Strong Stone Skin Potion",2,2],["Toad",4,3],["Crown",0,3],["Healing Herbs",0,4],["Healing Herbs",1,4],["Healing Herbs",0,5],["Healing Herbs",1,5],["Blueberries",2,0],["Blueberries",3,0],["Blueberries",2,1],["Blueberries",3,1],["Blueberries",3,2],["Blueberries",4,2],["Blueberries",5,2],["Blueberries",3,3]]
		placements.push_back(["Mana Potion",2,4] if case_data.name == "natural_linked" else ["Mana Potion",7,3])
		for placement in placements:
			var item = add_item(placement[0],placement[1],placement[2])
			if done:
				return
			natural_items[placement[0]] = item
			source_aliases[item.get_instance_id()] = placement[0] + ":" + String(item.get_instance_id())
	if case_data.name.begins_with("phase_"):
		banana = add_item("Banana",0,2)
	var layout = []
	for item in Game.PLAYER.INVENTORY.getItems():
		var cells = []
		for cell in item.occupiedCells:
			cells.push_back([cell.x,cell.y])
		var entry = {"instance":item.get_instance_id(),"source_alias":source_aliases.get(item.get_instance_id(),""),"name":item.descriptor.identifier,"cells":cells,"face":item.faceDirection}
		if natural_second:
			entry["params"] = item.descriptor.params
			entry["named_params"] = item.descriptor.namedParams
			entry["base_cooldown"] = item.getBaseCooldown()
			entry["affected_cells"] = []
			for cell in item.getAffectedCellsInInventory():
				entry.affected_cells.push_back([cell.x,cell.y])
			entry["affected_items"] = []
			for affected in item.getAffectedItems_nocache():
				entry.affected_items.push_back({"id":affected.get_instance_id(),"name":affected.descriptor.identifier})
			if item.isBag():
				entry["inside_items"] = []
				for inside in item.getItemsInside():
					entry.inside_items.push_back({"id":inside.get_instance_id(),"name":inside.descriptor.identifier})
		layout.push_back(entry)
	snapshot("layout", {"items":layout})

func add_item(name: String,x: int,y: int,f: int=0) -> Item:
	var item = ItemBook.instantiateItem(name)
	if item == null:
		finish("error", "cannot instantiate " + name)
		return null
	item.ownerType = Item.Owner.PlayerInventory
	Game.playerNode.add_child(item)
	item.setFaceDirectionInstant(f)
	var target = Game.PLAYER.INVENTORY.tilemap.to_global(Game.PLAYER.INVENTORY.tilemap.map_to_world(Vector2(x,y)))
	item.global_translate(target-item.getTopLeftGlobal())
	if not Game.PLAYER.INVENTORY.canAddItemOrBag(item):
		finish("error", "illegal placement " + name)
		return item
	Game.PLAYER.INVENTORY.addItemByTopLeft(item,Vector2(x,y))
	return item

func start_case() -> void:
	if done:
		return
	round_count += 1
	start_frame = Engine.get_physics_frames()
	case_started = true
	action_done = false
	reaction_done = false
	var player = Game.PLAYER
	for signal_name in ["character_lucky_changed","character_empower_changed","character_spikes_changed","character_mana_changed","character_blind_changed","character_regeneration_changed"]:
		EventBus.connectEvent(player,signal_name,self,"on_stack_changed")
	if case_data.name.begins_with("natural_"):
		snapshot("natural_round_start", {"evidence_kind":"only natural items; driver invokes no stack, counter, timer, HP, or RNG APIs","base_health":player.getCurrentHealth(),"character_id":player.get_instance_id(),"selected_class":Game.curClass})
		if round_count == 2 and player.getCurrentHealth() < 35:
			finish("incomplete", "natural second combat base health below 35")
		return
	snapshot("case_api_begin", {"case":case_data.name,"round":round_count,"evidence_kind":"controlled original API; natural timers and callbacks"})
	match case_data.name:
		"zero_fresh":
			player.gainStacksTemporary(Game.EventType.Lucky,1,0,source_a)
			finish_time = 1.5
		"zero_reused":
			player.gainStacksTemporary(Game.EventType.Empower,1,0.1,source_a)
			finish_time = 1.0
		"zero_running":
			player.gainStacksTemporary(Game.EventType.Spikes,1,0.3,source_a)
			player.gainStacksTemporary(Game.EventType.Spikes,1,0,source_b)
		"equal_forward":
			player.gainStacksTemporary(Game.EventType.Lucky,2,float(case_data.get("equal_duration",0.2)),source_a)
			player.gainStacksTemporary(Game.EventType.Lucky,3,float(case_data.get("equal_duration",0.2)),source_b)
		"equal_reverse":
			player.gainStacksTemporary(Game.EventType.Lucky,3,float(case_data.get("equal_duration",0.2)),source_b)
			player.gainStacksTemporary(Game.EventType.Lucky,2,float(case_data.get("equal_duration",0.2)),source_a)
		"tolerance_inside", "tolerance_outside":
			player.gainStacksTemporary(Game.EventType.Lucky,2,0.12,source_a)
			player.gainStacksTemporary(Game.EventType.Lucky,3,float(case_data.tolerance_b),source_b)
		"cross_start_forward", "cross_start_reverse":
			var targets = [[player,Game.EventType.Lucky],[player,Game.EventType.Empower],[Game.OPPONENT,Game.EventType.Lucky],[Game.OPPONENT,Game.EventType.Empower]]
			if case_data.name == "cross_start_reverse":
				targets.invert()
			for pair in targets:
				pair[0].gainStacksTemporary(pair[1],1,0.2,source_a)
		"phase_physics", "phase_deferred":
			finish_time = 7.0
		"reentry_use", "reentry_lose", "reentry_gain":
			player.gainStacks(Game.EventType.Mana,1,source_c)
			if case_data.name == "reentry_gain" and case_data.variant == "reverse":
				player.gainStacksTemporary(Game.EventType.Mana,3,0.3,source_b)
				player.gainStacksTemporary(Game.EventType.Mana,2,0.1,source_a)
			else:
				player.gainStacksTemporary(Game.EventType.Mana,2,0.1,source_a)
				player.gainStacksTemporary(Game.EventType.Mana,3,0.3,source_b)
			finish_time = 1.2
		"stale_far_first", "stale_early_first":
			if case_data.name == "stale_far_first":
				player.gainStacksTemporary(Game.EventType.Mana,3,10.0,source_b)
				player.gainStacksTemporary(Game.EventType.Mana,2,5.0,source_a)
			else:
				player.gainStacksTemporary(Game.EventType.Mana,2,5.0,source_a)
				player.gainStacksTemporary(Game.EventType.Mana,3,10.0,source_b)
			player.loseStacks(Game.EventType.Mana,3,source_c)
			finish_time = 7.0
		"cap_expiry":
			player.gainStacks(Game.EventType.Blind,9999,source_c)
			player.gainStacksTemporary(Game.EventType.Blind,1,0.2,source_a)
			snapshot("cap_before_packet", {"api":"changeDebuffReflectStacks(1); gainStacks(Blind,3,C)","expected_precondition":10000})
			if player.getBlind() != 10000:
				finish("incomplete", "controlled cap setup did not reach 10000")
				return
			player.changeDebuffReflectStacks(1)
			player.gainStacks(Game.EventType.Blind,3,source_c)
		"reset_controlled":
			player.gainStacks(Game.EventType.Mana,2,source_c)
			player.gainStacksTemporary(Game.EventType.Mana,3,0.3,source_a)
			snapshot("controlled_reset_before", {"api":"Buff.reset; loseStacks(Mana,1,C); gainStacks(Mana,1,C)"})
			player.buffs[Game.EventType.Mana].reset()
			player.loseStacks(Game.EventType.Mana,1,source_c)
			player.gainStacks(Game.EventType.Mana,1,source_c)
		"lifecycle_natural":
			finish_time = 90.0
			if round_count == 1:
				player.gainStacks(Game.EventType.Mana,2,source_c)
				player.gainStacksTemporary(Game.EventType.Mana,3,60.0,source_a)
			else:
				player.gainStacksTemporary(Game.EventType.Mana,3,0.3,source_a)
				player.loseStacks(Game.EventType.Mana,2,source_c)
				player.gainStacks(Game.EventType.Mana,1,source_c)
	snapshot("case_api_end", {"case":case_data.name,"round":round_count})

func run_actions() -> void:
	deferred_queued = false
	if done or not case_started:
		return
	var player = Game.PLAYER
	if case_data.name == "zero_reused" and not action_done:
		var buff = player.buffs[Game.EventType.Empower]
		var returned_frame = timeout_return_frames.get(buff.get_instance_id(),-1)
		if returned_frame >= 0 and Engine.get_physics_frames() > returned_frame and buff.temporaryStacks.empty() and buff.timer.is_stopped():
			action_done = true
			snapshot("zero_reused_api_before", {"api":"gainStacksTemporary(Empower,1,0,A)","original_timeout_return_frame":returned_frame})
			player.gainStacksTemporary(Game.EventType.Empower,1,0,source_a)
			snapshot("zero_reused_api_after")
	elif case_data.name.begins_with("phase_") and not action_done and Engine.get_physics_frames() > start_frame:
		if player.tickTimer.is_stopped() or banana == null or not banana.is_physics_processing() or banana.triggerTime <= 0:
			return
		action_done = true
		var tick_duration = player.tickTimer.get_time_left()
		var item_duration = banana.triggerTime / banana.getSpeed()
		if case_data.name == "phase_physics":
			item_duration = max(0.0001,item_duration - 1.0/Engine.iterations_per_second)
		item_duration += float(case_data.phase_offset)
		snapshot("phase_api_before", {"api":"gainStacksTemporary(Regeneration,1,tick_left,A); gainStacksTemporary(Lucky,1,CD_remaining,B)","phase":case_data.name,"tick_duration":tick_duration,"item_duration":item_duration,"item_remaining":banana.triggerTime,"item_speed":banana.getSpeed()})
		player.gainStacksTemporary(Game.EventType.Regeneration,1,tick_duration,source_a)
		player.gainStacksTemporary(Game.EventType.Lucky,1,item_duration,source_b)
		snapshot("phase_api_after")
	elif case_data.name == "lifecycle_natural" or case_data.name.begins_with("natural_"):
		if round_count == 1 and Game.fightEnded and character_ended and not shop_requested:
			shop_requested = true
			for event in Game.combatLog.events:
				round_event_archive.push_back({"round":round_count,"id":event.id,"time":event.timestamp,"type":event.type,"target":event.target,"source":event.origin.get_instance_id() if event.origin is Item else -1,"parent":event.parentEvent.id if event.parentEvent != null else -1,"params":event.params})
			snapshot("lifecycle_switch_shop_before", {"api":"Game.switchToShop()"})
			Game.switchToShop()
		elif shop_requested and shop_cleanse_seen and not second_requested and Game.state == Game.State.Shop and Game.canSwitchToCombat:
			second_requested = true
			if case_data.name.begins_with("natural_"):
				if player.getCurrentHealth() < 35:
					finish("incomplete", "natural shop health below 35")
					return
				var second_path = run_dir.plus_file("opponent_second.json")
				if File.new().get_sha256(second_path).to_lower() != String(case_data.opponent_second_sha256).to_lower():
					finish("error", "second opponent fixture fingerprint mismatch")
					return
				var input = File.new()
				if input.open(second_path,File.READ) != OK:
					finish("error", "second opponent fixture unavailable")
					return
				var fixture_bytes = input.get_buffer(input.get_len())
				input.close()
				if File.new().get_sha256(case_data.opponent_path).to_lower() != String(case_data.opponent_first_sha256).to_lower():
					finish("error", "opponent input changed concurrently before fixture switch")
					return
				if input.open(case_data.opponent_path,File.WRITE) != OK:
					finish("error", "cannot switch backed-up opponent input")
					return
				input.store_buffer(fixture_bytes)
				input.close()
				var written_sha = File.new().get_sha256(case_data.opponent_path)
				snapshot("fixture_input_switch", {"path":case_data.opponent_path,"expected_sha256":case_data.opponent_second_sha256,"actual_sha256":written_sha})
				if written_sha.to_lower() != String(case_data.opponent_second_sha256).to_lower():
					finish("error", "written second opponent fingerprint mismatch")
					return
				setup_layout()
				if done:
					return
			snapshot("lifecycle_second_combat_before", {"api":"Game.switchToCombat()"})
			Game.switchToCombat()

func on_stack_changed(amount: int,event: CombatEvent) -> void:
	snapshot("notification", {"amount":amount,"event_id":event.id,"type":event.type,"target":event.target,"source":event.origin.get_instance_id() if event.origin is Item else -1,"params":event.params})
	if case_data.name.begins_with("natural_"):
		return
	if done or reaction_done or amount >= 0 or not event.getParam("timeout",false) or event.origin != source_a:
		return
	var player = Game.PLAYER
	if case_data.name in ["reentry_use","reentry_lose","reentry_gain","cap_expiry"]:
		reaction_done = true
		snapshot("reentry_api_before", {"case":case_data.name,"trigger_event":event.id,"evidence_kind":"real EventBus timeout notification invokes original API"})
		match case_data.name:
			"reentry_use":
				player.useStacks(Game.EventType.Mana,1,source_c,event)
			"reentry_lose":
				player.loseStacks(Game.EventType.Mana,2,source_c,event)
			"reentry_gain":
				player.gainStacksTemporary(Game.EventType.Mana,1,0.5,source_c,event)
			"cap_expiry":
				player.changeDebuffReflectStacks(1)
				player.gainStacks(Game.EventType.Blind,3,source_c,event)
		snapshot("reentry_api_after", {"case":case_data.name,"trigger_event":event.id})

func new_call_id() -> int:
	next_id += 1
	return next_id

func observe(label: String,call_id: int,subject: Object,payload: Dictionary={}) -> void:
	var metadata = payload.duplicate()
	if payload.has("duration"):
		metadata["duration_exact"] = "%.17f" % payload.duration
	metadata["label"] = label
	metadata["call_id"] = call_id
	metadata["subject_id"] = subject.get_instance_id() if subject != null else -1
	if label.ends_with("_enter"):
		metadata["parent_call"] = active_calls.back() if not active_calls.empty() else -1
		active_calls.push_back(call_id)
	if subject is Buff:
		metadata["player"] = subject.character.playerId
		metadata["type"] = subject.type
		metadata["current"] = subject.current
		metadata["permanent"] = subject.permanentStacks
		metadata["next_index"] = subject.nextTemporaryTimeout
		if label.ends_with("_enter"):
			call_metadata[call_id] = {"label":label,"buff_id":subject.get_instance_id(),"player":subject.character.playerId,"type":subject.type}
		if label == "gain_request":
			call_metadata[call_id]["source"] = payload.source
			call_metadata[call_id]["duration"] = payload.duration
			call_metadata[call_id]["request"] = payload.request
		if label == "timeout_selected":
			call_metadata[call_id]["old_batch"] = payload.batch_id
		if label == "timeout_before_remove":
			call_metadata[call_id]["before_remove_observed"] = true
		if case_data.name.begins_with("natural_") and round_count == 2 and not natural_items.empty():
			if label == "lose_request" and subject.character == Game.PLAYER and subject.type == Game.EventType.Mana and payload.source == natural_items["Crown"].get_instance_id() and payload.used and payload.request == 10:
				natural_crown_use = true
			if label == "change_actual" and subject.character == Game.PLAYER and subject.type == Game.EventType.Mana and payload.source == natural_items["Crown"].get_instance_id() and payload.used and payload.actual == 10:
				natural_crown_use_actual = true
			if label == "timeout_selected" and subject.character == Game.PLAYER and subject.type == Game.EventType.Spikes and payload.source == natural_items["Strong Stone Skin Potion"].get_instance_id():
				var check = {"call_id":call_id,"buff_id":subject.get_instance_id(),"batch_id":payload.batch_id,"selected_amount":payload.selected_amount,"toad_used":natural_items["Toad"].usedBuffs,"mana":Game.PLAYER.getMana(),"crown_state":natural_items["Crown"].crownState,"mana_potion_full":natural_items["Mana Potion"].isFull,"strong_potion_full":natural_items["Strong Stone Skin Potion"].isFull,"engine_physics_frame":Engine.get_physics_frames(),"observation":observation_sequence+1}
				check["met"] = check.selected_amount == 2 and check.toad_used in [8,9] and check.mana == 9 and check.crown_state == 0 and check.mana_potion_full and not check.strong_potion_full
				natural_timeout_checks.push_back(check)
			if label == "gain_batch_added" and subject.character == Game.PLAYER and subject.type == Game.EventType.Spikes:
				for ancestor in active_calls:
					var ancestor_info = call_metadata.get(ancestor,{})
					if ancestor_info.get("label","") == "buff_onTimeout_enter" and ancestor_info.get("buff_id",-1) == subject.get_instance_id():
						var gain_info = call_metadata[call_id]
						var reentry = {"old_timeout_call":ancestor,"new_gain_call":call_id,"buff_id":subject.get_instance_id(),"old_batch_id":ancestor_info.get("old_batch",-1),"new_batch_id":payload.batch_id,"gain_source":gain_info.get("source",-1),"duration":gain_info.get("duration",null),"request":gain_info.get("request",null),"before_old_remove":not ancestor_info.get("before_remove_observed",false),"active_calls":active_calls.duplicate(),"engine_physics_frame":Engine.get_physics_frames(),"observation":observation_sequence+1}
						natural_reentries.push_back(reentry)
						metadata["natural_reentry"] = reentry
		if label == "buff_onTimeout_exit":
			timeout_return_frames[subject.get_instance_id()] = Engine.get_physics_frames()
		if label == "buff_onTimeout_enter":
			var key = String(subject.character.playerId) + ":" + String(subject.type)
			if not timeout_frames.has(key):
				timeout_frames[key] = []
			timeout_frames[key].push_back(Engine.get_physics_frames())
	elif subject is Character:
		metadata["player"] = subject.playerId
		metadata["tick_counter"] = subject.tickCounter
		if label == "character_onTick_enter" and subject == Game.PLAYER:
			tick_frames.push_back(Engine.get_physics_frames())
		if label == "character_combatEnd_exit" and subject == Game.PLAYER:
			character_ended = true
		if label == "character_cleanse_exit" and subject == Game.PLAYER and shop_requested:
			shop_cleanse_seen = true
	elif subject is Item:
		metadata["item"] = subject.descriptor.identifier
		metadata["player"] = subject.character().playerId if subject.character() != null else -1
		metadata["trigger_time"] = subject.triggerTime
		metadata["speed"] = subject.getSpeed()
		if label == "item_trigger_enter" and subject == banana:
			item_frames.push_back(Engine.get_physics_frames())
	snapshot("trace",metadata)
	if label.ends_with("_exit") and not active_calls.empty() and active_calls.back() == call_id:
		active_calls.pop_back()

func snapshot(label: String,payload: Dictionary={}) -> void:
	if run_dir == "":
		return
	observation_sequence += 1
	var row = payload.duplicate()
	row["observation"] = observation_sequence
	row["snapshot"] = label
	row["case"] = case_data.get("id", "startup")
	row["engine_physics_frame"] = Engine.get_physics_frames()
	row["engine_idle_frame"] = Engine.call("get_idle_frames") if Engine.has_method("get_idle_frames") else null
	row["relative_physics_frame"] = Engine.get_physics_frames()-start_frame if start_frame >= 0 else null
	row["util_frame"] = Util.frameCounter
	row["util_time"] = Util.time
	row["combat_time"] = Game.combatTimer.combatTime if Game.combatTimer != null else null
	row["physics_steps_per_second"] = Engine.iterations_per_second
	row["game_state"] = Game.state
	row["fight_ended"] = Game.fightEnded
	row["round"] = round_count
	var characters = []
	for character in [Game.PLAYER,Game.OPPONENT]:
		if character == null:
			continue
		var states = []
		for type in [Game.EventType.Lucky,Game.EventType.Empower,Game.EventType.Spikes,Game.EventType.Mana,Game.EventType.Blind,Game.EventType.Regeneration]:
			if not character.buffs.has(type):
				continue
			var buff = character.buffs[type]
			var batches = []
			for batch in buff.temporaryStacks:
				batches.push_back({"id":batch.get_instance_id(),"amount":batch.amount,"timeout":batch.timeout,"source":batch.item.get_instance_id() if batch.item != null else -1,"source_alias":source_aliases.get(batch.item.get_instance_id(),"") if batch.item != null else ""})
			var timer = buff.timer
			states.push_back({"type":type,"buff_id":buff.get_instance_id(),"current":buff.current,"permanent":buff.permanentStacks,"batches":batches,"next_index":buff.nextTemporaryTimeout,"timer":{"id":timer.get_instance_id(),"path":String(timer.get_path()),"index":timer.get_index(),"priority":timer.process_priority,"mode":timer.process_mode,"is_physics":timer.process_mode==Timer.TIMER_PROCESS_PHYSICS,"wait_time":timer.wait_time,"time_left":timer.get_time_left(),"stopped":timer.is_stopped()}})
			states.back().timer["wait_time_exact"] = "%.17f" % timer.wait_time
			states.back().timer["time_left_exact"] = "%.17f" % timer.get_time_left()
		var tick = character.tickTimer
		characters.push_back({"id":character.get_instance_id(),"player":character.playerId,"health":character.getCurrentHealth(),"tick_counter":character.tickCounter,"global_reflect":character.debuffReflectStacks,"states":states,"tick_timer":{"id":tick.get_instance_id(),"path":String(tick.get_path()),"index":tick.get_index(),"priority":tick.process_priority,"mode":tick.process_mode,"is_physics":tick.process_mode==Timer.TIMER_PROCESS_PHYSICS,"wait_time":tick.wait_time,"time_left":tick.get_time_left(),"stopped":tick.is_stopped()}})
	row["characters"] = characters
	if case_data.name.begins_with("natural_"):
		row["active_calls"] = active_calls.duplicate()
		row["natural_items"] = []
		if not natural_items.empty():
			for item in Game.PLAYER.INVENTORY.getItems():
				var name = item.descriptor.identifier
				if not name in ["Toad","Crown","Strong Stone Skin Potion","Mana Potion","Heart Container","Hungry Blade","Blueberries","Fanny Pack"]:
					continue
				var item_row = {"name":name,"id":item.get_instance_id(),"trigger_time":item.triggerTime,"speed":item.getSpeed(),"base_cooldown":item.getBaseCooldown(),"params":item.descriptor.params}
				if name == "Toad":
					item_row["used"] = item.usedBuffs
					item_row["gained"] = item.gainedBuffs
				elif name == "Crown":
					item_row["crown_state"] = item.crownState
				elif name in ["Strong Stone Skin Potion","Mana Potion"]:
					item_row["full"] = item.isFull
					item_row["affected"] = []
					for affected in item.getAffectedItems():
						item_row.affected.push_back({"id":affected.get_instance_id(),"name":affected.descriptor.identifier})
				elif name == "Heart Container":
					item_row["activated"] = item.activated
				row.natural_items.push_back(item_row)
	if banana != null and is_instance_valid(banana):
		row["banana"] = {"id":banana.get_instance_id(),"path":String(banana.get_path()),"index":banana.get_index(),"priority":banana.process_priority,"trigger_time":banana.triggerTime,"speed":banana.getSpeed(),"processing":banana.is_physics_processing()}
	traces.push_back(row)
	print("BUFF_T0_OBSERVATION ",JSON.print(row))

func capture(label: String) -> void:
	var image = get_viewport().get_texture().get_data()
	image.flip_y()
	image.save_png(run_dir.plus_file(label+".png"))

func finish(status: String,message: String="") -> void:
	if done:
		return
	done = true
	var events = []
	if Game.combatLog != null:
		for event in Game.combatLog.events:
			events.push_back({"id":event.id,"time":event.timestamp,"type":event.type,"target":event.target,"source":event.origin.get_instance_id() if event.origin is Item else -1,"source_name":event.origin.descriptor.identifier if event.origin is Item else null,"source_alias":source_aliases.get(event.origin.get_instance_id(),"") if event.origin is Item else "","parent":event.parentEvent.id if event.parentEvent != null else -1,"params":event.params})
	snapshot("final", {"status":status,"message":message})
	var tick_matches = []
	var item_matches = []
	for frame in timeout_frames.get("0:"+String(Game.EventType.Regeneration),[]):
		if frame in tick_frames:
			tick_matches.push_back(frame)
	for frame in timeout_frames.get("0:"+String(Game.EventType.Lucky),[]):
		if frame in item_frames:
			item_matches.push_back(frame)
	var result = {"status":status,"message":message,"case":case_data,"rounds":round_count,"reaction_executed":reaction_done,"action_executed":action_done,"timeout_frames":timeout_frames,"tick_frames":tick_frames,"item_frames":item_frames,"actual_tick_frame_matches":tick_matches,"actual_item_frame_matches":item_matches,"observations":traces,"events":events,"previous_round_events":round_event_archive,"elapsed_wall_ms":OS.get_ticks_msec()-started_wall}
	if case_data.name.begins_with("natural_"):
		result["natural_timeout_checks"] = natural_timeout_checks
		result["natural_reentries"] = natural_reentries
		result["natural_crown_use_request"] = natural_crown_use
		result["natural_crown_use_actual"] = natural_crown_use_actual
	var file = File.new()
	if file.open(run_dir.plus_file("result.json"),File.WRITE) == OK:
		file.store_string(JSON.print(result))
		file.close()
	print("BUFF_T0_FINAL ",JSON.print({"status":status,"message":message,"case":case_data.get("id","startup"),"events":events.size(),"observations":traces.size(),"tick_matches":tick_matches,"item_matches":item_matches}))
	if stage >= 2:
		capture("observed")
	get_tree().quit(1 if status == "error" else 0)
