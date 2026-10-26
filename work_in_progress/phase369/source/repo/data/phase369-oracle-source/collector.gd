extends SceneTree
# Phase045 lifecycle-corrected observer7 driver;040 original is preserved.
# External observer7 driver; inherited collector body attributed to immutable v6.
# Phase040 never executes this GDScript; genuine remains disabled in host.
# Source anchors: Game finishSwitchingToCombat/activateItems/combatEndDeferred,
# CombatLog createEvent/logEvent/onCombatEnd; Inventory canAddItemOrBag.

const SOURCE_P = {"schema_version": 1, "game_version": "1.1.8", "class": 0, "health": 360, "stamina": 5, "items": [{"f": 0, "item_index": 11, "x": 0, "y": 0}, {"f": 0, "item_index": 11, "x": 2, "y": 0}, {"f": 0, "item_index": 11, "x": 4, "y": 0}, {"f": 0, "item_index": 11, "x": 6, "y": 0}, {"f": 0, "item_index": 11, "x": 0, "y": 2}, {"f": 0, "item_index": 11, "x": 2, "y": 2}, {"f": 0, "item_index": 11, "x": 4, "y": 2}, {"f": 0, "item_index": 11, "x": 6, "y": 2}, {"f": 0, "item_index": 11, "x": 0, "y": 4}, {"f": 0, "item_index": 11, "x": 2, "y": 4}, {"f": 0, "item_index": 11, "x": 4, "y": 4}, {"f": 0, "item_index": 11, "x": 6, "y": 4}, {"f": 0, "item_index": 262, "x": 2, "y": 1}, {"f": 0, "item_index": 22, "x": 1, "y": 1}, {"f": 0, "item_index": 22, "x": 1, "y": 2}, {"f": 0, "item_index": 22, "x": 1, "y": 3}, {"f": 0, "item_index": 1, "x": 4, "y": 1}, {"f": 0, "item_index": 22, "x": 4, "y": 3}, {"f": 0, "item_index": 19, "x": 6, "y": 0}, {"f": 0, "item_index": 4, "x": 6, "y": 4}]}
const SOURCE_O = {"schema_version": 1, "game_version": "1.1.8", "class": 0, "health": 380, "stamina": 5, "items": [{"f": 0, "item_index": 11, "x": 0, "y": 0}, {"f": 0, "item_index": 11, "x": 2, "y": 0}, {"f": 0, "item_index": 11, "x": 4, "y": 0}, {"f": 0, "item_index": 11, "x": 6, "y": 0}, {"f": 0, "item_index": 11, "x": 0, "y": 2}, {"f": 0, "item_index": 11, "x": 2, "y": 2}, {"f": 0, "item_index": 11, "x": 4, "y": 2}, {"f": 0, "item_index": 11, "x": 6, "y": 2}, {"f": 0, "item_index": 11, "x": 0, "y": 4}, {"f": 0, "item_index": 11, "x": 2, "y": 4}, {"f": 0, "item_index": 11, "x": 4, "y": 4}, {"f": 0, "item_index": 11, "x": 6, "y": 4}, {"f": 0, "item_index": 22, "x": 1, "y": 1}, {"f": 0, "item_index": 22, "x": 1, "y": 2}, {"f": 0, "item_index": 22, "x": 1, "y": 3}, {"f": 0, "item_index": 1, "x": 4, "y": 1}, {"f": 0, "item_index": 22, "x": 4, "y": 3}, {"f": 0, "item_index": 19, "x": 6, "y": 0}, {"f": 0, "item_index": 4, "x": 6, "y": 4}]}
const SOURCE_CONFIG = {"schema": "native-combat-capture/1", "case_id": "NATIVE-027-KING-A", "global_seed": 35301, "util_seed": 35302, "player_fixture_enabled": true, "timeouts": {"battle_seconds": 120, "total_seconds": 295}}

const OUT = "user://native-capture"
const PLAYER_ITEM_WHITELIST = [1, 4, 11, 19, 22, 262]
const STARTERS = [[67, 3, 2], [11, 5, 3], [11, 1, 3], [24, 4, 4], [1, 3, 3]]
const CHAR_FIELDS = ["playerId", "characterClass", "characterName", "chibi", "isDead", "maxHealth", "curHealth", "temporaryMaxHealth", "temporaryMaxHealthGain", "baseMaxStamina", "maxStamina", "curStamina", "temporaryMaxStamina", "baseStaminaRegen", "staminaRegen", "allowStaminaOverflow", "stunnedDuration", "invulnerable", "unhealingAmount", "healingEfficiency", "damageResistance", "damageReduction", "dodgeStacks", "critResistance", "critResistStacks", "stunResistance", "debuffResistStacks", "debuffReflectStacks", "buffProtectStacks", "critTokens", "invulnerabilityItem", "invulBubbleVisible", "battleRageBonusDur", "bonusFatigueDamage", "meleeSpikesLimit", "rangedSpikesLimit", "effectSpikesLimit", "meleeVampirismLimit", "rangedVampirismLimit", "empowerDamage", "typedDamageFactors", "tickCounter"]
const ITEM_FIELDS = ["ownerType", "placed", "occupiedCells", "faceDirection", "consumed", "lastActivationTime", "activationsThisFrame", "lastTriggerTime", "triggersThisFrame", "triggerTime", "iterationCooldown", "baseCooldownOverride", "speedScale", "bonusMaxDam", "bonusMinDam", "removableDam", "bonusDamageFactor", "staminaFactor", "critChancePercent", "critTokens", "critSeverity", "bonusChancePercent_mult", "bonusChancePercent_additive1", "bonusChancePercent_additive2", "bonusAccuracy", "buffPowers", "buffAmplificationChances", "doubleActivationChance", "doubleAttackEffectChance", "paramMult", "paramAdd", "numCharges", "itemMetrics"]
const RNG_FIELDS = ["expectedWins", "wins", "balancedness", "lastResult", "extraLuck", "lastTarget", "accChance"]
const LOG_FIELDS = ["eventNum", "timestamps", "globalStatHistories", "activeItemState", "activeCharacterStats", "itemsWithCooldown", "electricalCharges", "emitterEventToChargeInstance", "numPlayerCharges"]
const HIST_FIELDS = ["playerId", "characterStatHistories", "stackHistories", "itemTooltipHistories", "itemMetricHistories", "itemStateHistories", "metricHistories"]

var game
var util
var steam
var bus
var rules
var settings
var stage = "startup"
var started = 0
var stage_started = 0
var done = false
var errors = []
var phases = []
var registry = {}
var instance_rows = []
var event_objects = {}
var event_references = {}
var event_visiting = {}
var config = {"global_seed": 10136021, "util_seed": 20261013, "case_id": "NATIVE-001", "player_fixture_enabled": false, "timeouts": {"battle_seconds": 120, "total_seconds": 295}}
var player_fixture = {}
var player_fixture_sha256 = ""
var player_setup_step = ""
var player_setup_idle = 0
var old_player_items = []
var player_setup_evidence = {"setup_complete": false, "errors": [], "budget_ms": 30000, "steps": [], "old_items": [], "new_items": []}
var legal_checks = []
var opponent_fixture = {}
var property_cache = {}
var result_value = null
var barrier_ok = false
var stable_ok = false

# SOURCE template merged into the frozen298 collector. No business methods here.
var source_cut_frozen = false
var source_listener_attached = false
var source_write_bytes = 0
var source_file_bytes = {}
var source_connection_order = []


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
	started = OS.get_ticks_msec()
	stage_started = started
	Directory.new().make_dir_recursive(OUT)
	var f = File.new()
	var source_config_input = {}
	if f.file_exists("res://native_capture_config.json"):
		f.open("res://native_capture_config.json", File.READ)
		var parsed = JSON.parse(f.get_as_text())
		f.close()
		if parsed.error != OK or typeof(parsed.result) != TYPE_DICTIONARY:
			fail("invalid native_capture_config.json")
			return
		source_config_input = parsed.result
		for key in parsed.result:
			config[key] = parsed.result[key]
	if not config_matches_source(source_config_input):
		fail("fixed config differs")
		return
	if not timeout_budget_selftest():
		fail("timeout budget validator selftest failed")
		return
	if not timeout_budget_valid(config.timeouts):
		fail("invalid timeouts: expected numeric integer pair 120/295,180/355 or300/475")
		return
	if typeof(config.player_fixture_enabled) != TYPE_BOOL:
		fail("player_fixture_enabled must be a boolean")
		return
	if config.player_fixture_enabled and not read_player_fixture():
		fail("invalid controlled player fixture")
		return
	var fixture_path = ProjectSettings.globalize_path("res://project.godot").get_base_dir().get_base_dir().plus_file("data/custom_opponent.json")
	if f.open(fixture_path, File.READ) != OK:
		fail("missing controlled opponent fixture")
		return
	var fixture_parsed = JSON.parse(f.get_as_text())
	f.close()
	if fixture_parsed.error != OK or typeof(fixture_parsed.result) != TYPE_DICTIONARY:
		fail("invalid controlled opponent fixture")
		return
	opponent_fixture = fixture_parsed.result
	if not get_root().get_node("NativeRandomObserver").source_same_slot_value(opponent_fixture, SOURCE_O):
		fail("fixed O SOURCE fixture differs")
		return
	write_json("fixture.json", opponent_fixture)
	if not serializer_selftest():
		fail("serializer selftest")
		return
	connect("idle_frame", self, "observe")

# Bounded, fixed presets; these functions do not touch gameplay or RNG.
func timeout_budget_valid(budget):
	if typeof(budget) != TYPE_DICTIONARY or budget.size() != 2:
		return false
	for key in ["battle_seconds", "total_seconds"]:
		if not budget.has(key):
			return false
		if typeof(budget[key]) != TYPE_INT and typeof(budget[key]) != TYPE_REAL:
			return false
	# Exact allowed values reject non-finite/fractional inputs before any int cast.
	return (budget.battle_seconds == 120 and budget.total_seconds == 295) or (budget.battle_seconds == 300 and budget.total_seconds == 475) or (budget.battle_seconds == 180 and budget.total_seconds == 355)

func timeout_budget_selftest():
	if not timeout_budget_valid({"battle_seconds": 180, "total_seconds": 355}):
		return false
	if not timeout_budget_valid({"battle_seconds": 120, "total_seconds": 295}):
		return false
	if not timeout_budget_valid({"battle_seconds": 300.0, "total_seconds": 475.0}):
		return false
	for invalid in [null, [], {}, {"battle_seconds": 300}, {"battle_seconds": 300, "total_seconds": 475, "other": 1}, {"battle_seconds": "300", "total_seconds": 475}, {"battle_seconds": true, "total_seconds": 475}, {"battle_seconds": 300.5, "total_seconds": 475}, {"battle_seconds": 300, "total_seconds": 295}, {"battle_seconds": 301, "total_seconds": 475}, {"battle_seconds": -1, "total_seconds": 475}, {"battle_seconds": INF, "total_seconds": 475}, {"battle_seconds": NAN, "total_seconds": 475}]:
		if timeout_budget_valid(invalid):
			return false
	return true

func set_stage(name):
	stage = name
	stage_started = OS.get_ticks_msec()
	print("NATIVE_PHASE " + name)

func observe():
	var observer7 = get_root().get_node_or_null("NativeRandomObserver")
	if observer7 != null and observer7.failed and not done:
		fail("observer7 durable failure; stopped by existing idle driver")
		return
	if done:
		return
	var limit = 10000 if stage == "finalizing" else 120000
	if stage == "player_setup":
		limit = 30000
	if stage in ["combat_wait", "combat_active"]:
		limit = int(config.timeouts.battle_seconds) * 1000
	if OS.get_ticks_msec() - stage_started > limit or OS.get_ticks_msec() - started > int(config.timeouts.total_seconds) * 1000:
		fail("phase timeout: " + stage)
		return
	if stage == "startup":
		game = get_root().get_node_or_null("Game")
		if game == null or game.PLAYER == null or game.itemLibrary == null or game.sceneAnimation == null:
			return
		if not game.sceneAnimation.is_connected("animation_finished", game, "onSceneAnimationFinished"):
			return
		if game.state != game.State.Title or get_root().get_node_or_null("Main") == null:
			return
		util = get_root().get_node("Util")
		steam = get_root().get_node("SteamHelper")
		bus = get_root().get_node("EventBus")
		rules = get_root().get_node("CustomRules")
		settings = get_root().get_node("Settings")
		if not preflight():
			fail("preflight failed")
			return
		game.connect("shop_closed", self, "on_shop_closed")
		game.connect("combat_start", self, "on_combat_start")
		game.connect("combat_end", self, "on_combat_end", [], CONNECT_DEFERRED)
		var before = encode(util.rng.state)
		seed(int(config.global_seed))
		util.rng.seed = int(config.util_seed)
		phases.append({"name": "seed_boundary", "frame": frames(), "util_state_before": before, "util_state_after": encode(util.rng.state), "global_seed": str(int(config.global_seed)), "util_seed": str(int(config.util_seed))})
		var selected_class = int(player_fixture["class"]) if config.player_fixture_enabled else 0
		game.instanceCharacter(selected_class)
		game.initStartInventory(0)
		game.startFreshRun(game.Mode.Unranked)
		set_stage("shop_wait")
	elif stage == "shop_wait":
		if game.isSwitchToCombatPossible() and not game.sceneAnimation.is_playing():
			if config.player_fixture_enabled:
				set_stage("player_setup")
				print("NATIVE_PLAYER_SETUP_BEGIN")
				player_setup_evidence["started_ms"] = OS.get_ticks_msec()
				player_setup_step = "settle_initial"
			else:
				start_controlled_combat()
	elif stage == "player_setup":
		observe_player_setup()
	if game != null and util != null:
		if Engine.time_scale != 1.0:
			fail("time scale changed")
		elif steam.IS_INIT or steam.IS_ONLINE or steam.STATS_RECEIVED:
			fail("unexpected online Steam state")

# External fixture setup uses ordinary native inventory notifications; never prepare/activate.
func integer_between(value, low, high):
	return (typeof(value) == TYPE_INT or typeof(value) == TYPE_REAL) and value >= low and value <= high and value == floor(value)

func exact_keys(value, keys):
	if typeof(value) != TYPE_DICTIONARY or value.size() != keys.size():
		return false
	for key in keys:
		if not value.has(key):
			return false
	return true

func player_input_valid(value):
	return get_root().get_node("NativeRandomObserver").source_same_slot_value(value, SOURCE_P)

func read_player_fixture():
	var input_path = ProjectSettings.globalize_path("res://project.godot").get_base_dir().get_base_dir().plus_file("data/custom_player.json")
	var input_file = File.new()
	if input_file.open(input_path, File.READ) != OK:
		return false
	var raw_text = input_file.get_as_text()
	input_file.close()
	var parsed = JSON.parse(raw_text)
	if parsed.error != OK or not player_input_valid(parsed.result):
		return false
	player_fixture = parsed.result
	player_fixture_sha256 = input_file.get_sha256(input_path)
	var output_path = OUT.plus_file("player_fixture.json")
	if input_file.open(output_path + ".partial", File.WRITE) != OK:
		return false
	input_file.store_string(raw_text)
	input_file.close()
	if Directory.new().rename(output_path + ".partial", output_path) != OK or input_file.get_sha256(output_path) != player_fixture_sha256:
		return false
	player_setup_evidence["player_fixture_sha256"] = player_fixture_sha256
	return true

func player_setup_settled():
	var crafting = get_root().get_node("CraftingManager")
	if game.draggedItem != null or game.inventoryEditMode != game.InventoryEditMode.Default or game.sceneAnimation.is_playing() or util.isTweenRunning(game.loadoutTween):
		return false
	if crafting.updatePending or not crafting.itemsAvailablePending.empty() or not crafting.itemsRemovedPending.empty() or game.PLAYER.INVENTORY.recalculateQueued:
		return false
	for item in game.PLAYER.INVENTORY.getItems():
		if item.fusing or item.willBeConsumed:
			return false
	return true

func setup_step(name):
	player_setup_step = name
	player_setup_idle = Engine.get_idle_frames()
	player_setup_evidence.steps.append({"name": name, "frame": frames(), "elapsed_ms": OS.get_ticks_msec() - stage_started, "util_rng_state": encode(util.rng.state)})
	write_json("player_setup_evidence.json", player_setup_evidence)

func observe_player_setup():
	var inventory = game.PLAYER.INVENTORY
	if not player_setup_settled():
		return
	if player_setup_step == "settle_initial":
		if not game.STORAGEBOX.getItems().empty():
			fail("unexpected storage items before player fixture")
			return
		for item in inventory.getItems():
			old_player_items.append({"object": item, "oid": item.get_instance_id(), "pooled": item.pooled, "scene": item.descriptor.scene})
			player_setup_evidence.old_items.append({"native_object_id": str(item.get_instance_id()), "item_index": item.descriptor.itemIndex, "position": encode(item.getTopLeftCell()), "pooled": item.pooled, "scene": item.descriptor.scene.resource_path})
		# Non-bags first; all objects stay alive until recipe notifications drain.
		for bag in [false, true]:
			for record in old_player_items:
				if record.object.isBag() == bag:
					inventory.removeItem(record.object)
		setup_step("removed_wait")
	elif player_setup_step == "removed_wait":
		for record in old_player_items:
			var item = record.object
			if item.placed or not item.bondedIngredients.empty() or item.bondedBaseItem != null or item.curRecipe != null:
				fail("old player recipe/placement remains after removal")
				return
			item.discard()
		setup_step("discarded_wait")
	elif player_setup_step == "discarded_wait":
		if Engine.get_idle_frames() < player_setup_idle + 2:
			return
		if not old_player_exit_valid():
			fail("old player objects did not exit native memberships")
			return
		old_player_items.clear()
		if not place_player_items():
			fail("native player placement rejected")
			return
		setup_step("placed_wait")
	elif player_setup_step == "placed_wait":
		if Engine.get_idle_frames() < player_setup_idle + 2:
			return
		game.PLAYER.setMaxHealth(float(player_fixture.health))
		if not register_inventory(game.PLAYER, "P"):
			fail("controlled player layout invalid")
			return
		player_setup_evidence["ready_spatial"] = player_spatial_evidence()
		if not errors.empty() or not game.STORAGEBOX.getItems().empty():
			fail("player setup spatial/storage checks failed")
			return
		player_setup_evidence.setup_complete = true
		setup_step("ready")
		print("NATIVE_PLAYER_SETUP_READY")
		phase("player_fixture_ready")
		start_controlled_combat(true)

func old_player_exit_valid():
	var inventory = game.PLAYER.INVENTORY
	var book = get_root().get_node("ItemBook")
	var pool = get_root().get_node("ObjectPool")
	if not inventory.getItems().empty() or not inventory.bagCells.empty() or not inventory.filledCells.empty():
		return false
	for i in range(old_player_items.size()):
		var record = old_player_items[i]
		var item = record.object
		var alive = is_instance_valid(item)
		var exited = not alive
		if record.pooled:
			exited = alive and item.get_parent() == null and not item.is_inside_tree() and not item.placed and item in pool.instances.get(record.scene, [])
		elif alive:
			exited = false
		for members in book.ownableItems.values():
			for member in members:
				if member.get_instance_id() == record.oid or (member.bondedBaseItem != null and member.bondedBaseItem.get_instance_id() == record.oid):
					exited = false
				for ingredient in member.bondedIngredients:
					if ingredient.get_instance_id() == record.oid:
						exited = false
		for members in [game.hoveredItems, game.itemsUnderMouse]:
			for member in members:
				if not is_instance_valid(member) or member.get_instance_id() == record.oid:
					exited = false
		player_setup_evidence.old_items[i]["exit_verified"] = exited
		player_setup_evidence.old_items[i]["alive_after_discard"] = alive
		player_setup_evidence.old_items[i]["exit_kind"] = "detached_in_pool" if record.pooled else "freed"
		if not exited:
			return false
	return true

func place_player_items():
	if not ensure_source_window():
		return source_window_reject("place_player_items", "SOURCE_WINDOW_REJECTED")
	source_book_reached = true
	var book = get_root().get_node("ItemBook")
	var inventory = game.PLAYER.INVENTORY
	for slot in range(player_fixture.items.size()):
		var spec = player_fixture.items[slot]
		if int(spec.item_index) >= book.getNumItems():
			return source_window_reject("place_player_items", "DESCRIPTOR_RANGE", {"slot": slot, "raw_descriptor": collector_control_bound_value(spec.item_index)})
		var descriptor = book.getDescriptorFromIndex(int(spec.item_index))
		source_instantiate_reached = true
		var item = book.instantiateItem(descriptor)
		item.ownerType = item.Owner.PlayerInventory
		game.playerNode.add_child(item)
		source_geometry_reached = true
		inventory.orientItem(item, Vector2(spec.x, spec.y), int(spec.f))
		if item.has_method("getDataPersistent") or not item.getGemsNoNull().empty() or not inventory.canAddItemOrBag(item):
			errors.append("player fixture illegal placement at input slot " + str(slot))
			return source_window_reject("place_player_items", "GEOMETRY_OR_MODIFIER_REJECTED", {"slot": slot, "descriptor": descriptor.itemIndex})
		inventory.addItemByTopLeft(item, Vector2(spec.x, spec.y))
		player_setup_evidence.new_items.append({"stable_id": slot_spec("P", slot).instance_id, "native_object_id": str(item.get_instance_id()), "input_slot": slot, "item_index": descriptor.itemIndex})
	return true

func native_ids(items):
	var result = []
	for item in items:
		if not is_instance_valid(item) or not registry.has(item.get_instance_id()):
			errors.append("unregistered player spatial member")
			continue
		result.append(registry[item.get_instance_id()])
	return result

func same_id_set(a, b):
	var left = a.duplicate()
	var right = b.duplicate()
	left.sort()
	right.sort()
	if left.size() != right.size():
		return false
	for i in range(left.size()):
		if left[i] != right[i]:
			return false
	return true

func player_spatial_evidence():
	var rows = []
	for item in game.PLAYER.INVENTORY.getItems():
		rows.append({"stable_id": registry[item.get_instance_id()], "node_order": item.get_position_in_parent(), "position": encode(item.getTopLeftCell()), "orientation": encode(item.faceDirection), "occupied_cells": encode(item.occupiedCells), "descriptor_index": encode(item.descriptor.itemIndex), "current_affected": encode(item.currentAffectedItems), "cached_affected": encode(item.cachedAffectedItems)})
	return {"frame": frames(), "items": rows, "source": "DIRECT_MEMBERS_NO_AFFECTED_GETTER_OR_CACHE_REFRESH"}


func player_membership_unchanged():
	var inventory = game.PLAYER.INVENTORY
	if inventory.getItems().size() != player_fixture.items.size():
		return false
	for item in inventory.getItems():
		var stable = registry.get(item.get_instance_id(), "")
		if not stable.begins_with("P:"):
			return false
		var slot = int(stable.substr(2))
		var spec = player_fixture.items[slot]
		if str(item.get_instance_id()) != player_setup_evidence.new_items[slot].native_object_id or item.descriptor.itemIndex != int(spec.item_index) or item.getTopLeftCell() != Vector2(spec.x, spec.y) or item.faceDirection != int(spec.f) or item.inventory != inventory or not item.placed or item.ownerType != item.Owner.PlayerInventory:
			return false
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


func start_controlled_combat(player_registered = false):
	if not player_registered or not ensure_source_window():
		source_control_record("start_controlled_combat", "FRESH_PLAYER_OR_WINDOW_REJECTED", {"player_registered": player_registered})
		fail("single King requires controlled fresh player and actual SOURCE window")
		return
	phase("shop_ready")
	set_stage("combat_wait")
	game.switchToCombat()


func preflight():
	var checks = {"editor": game.EDITOR, "offline": not steam.IS_INIT and not steam.IS_ONLINE and not steam.STATS_RECEIVED, "version": game.VERSION == "1.1.8", "rules_inactive": not rules.customRulesActive, "rules_default": rules_are_default(), "normal_time": Engine.time_scale == 1.0, "normal_speed": settings.settings[settings.Setting.combat_speed] == 1.0}
	for key in ["randomCharacter", "DEVCHEATS", "winNextRound", "winNextRun", "loseNextRound", "loseNextRun"]:
		checks[key + "_off"] = not game.get(key)
	write_json("preflight.json", checks)
	write_json("rules_preflight.json", {"actual": encode(rules.values), "defaults": encode(rules.DEFAULTS)})
	for key in checks:
		if not checks[key]:
			errors.append("preflight: " + key)
	return errors.empty()

func rules_are_default():
	if rules.values.size() != rules.DEFAULTS.size():
		return false
	for key in rules.DEFAULTS:
		if not rules.values.has(key) or typeof(rules.values[key]) != typeof(rules.DEFAULTS[key]) or rules.values[key] != rules.DEFAULTS[key]:
			return false
	return true

func register_inventory(character, side):
	registry[character.get_instance_id()] = side
	var inventory = character.INVENTORY
	var items = inventory.getItems()
	var expected = []
	if side == "P":
		if config.player_fixture_enabled:
			expected = player_fixture.items
		else:
			for entry in STARTERS:
				expected.append({"item_index": entry[0], "x": entry[1], "y": entry[2], "f": 0})
	else:
		expected = opponent_fixture.items
	var valid = items.size() == expected.size()
	var expected_class = int(player_fixture["class"]) if side == "P" and config.player_fixture_enabled else (0 if side == "P" else int(opponent_fixture["class"]))
	var expected_health = int(player_fixture.health) if side == "P" and config.player_fixture_enabled else (25 if side == "P" else int(opponent_fixture.health))
	var expected_stamina = 5 if side == "P" else int(opponent_fixture.stamina)
	valid = valid and character.characterClass == expected_class and character.maxHealth == expected_health and character.maxStamina == expected_stamina
	var matched = {}
	var occupied_bag = {}
	var occupied_item = {}
	for item in items:
		var slot = -1
		for i in range(expected.size()):
			var spec = expected[i]
			if item.descriptor.itemIndex == int(spec.item_index) and item.getTopLeftCell() == Vector2(spec.x, spec.y):
				slot = i
		if slot < 0 or matched.has(slot):
			errors.append("unmatched/duplicate fixture item: " + side)
			valid = false
			continue
		matched[slot] = true
		var stable = slot_spec(side, slot).instance_id
		registry[item.get_instance_id()] = stable
		if expected[slot].has("persistent_data") or item.has_method("getDataPersistent"):
			errors.append("persistent item not supported by this bounded capture: " + stable)
			valid = false
		valid = valid and item.faceDirection == int(expected[slot].f) and item.getGemsNoNull().empty() and item.inventory == inventory
		var occupied = occupied_bag if item.isBag() else occupied_item
		for cell in item.occupiedCells:
			if not inventory.isInventoryCell(cell) or occupied.has(cell):
				valid = false
			occupied[cell] = stable
			if item.isBag():
				valid = valid and inventory.bagCells.get(cell) == item
			else:
				valid = valid and inventory.bagCells.has(cell) and inventory.filledCells.get(cell) == item
		instance_rows.append({"stable_id": stable, "native_object_id": str(item.get_instance_id()), "inventory_order": items.find(item), "item_index": item.descriptor.itemIndex, "identifier": item.descriptor.identifier, "script": item.get_script().resource_path, "scene": item.filename, "position": encode(item.getTopLeftCell()), "orientation": encode(item.faceDirection), "occupied_cells": encode(item.occupiedCells), "owner": side})
	legal_checks.append({"side": side, "valid": valid, "count": items.size(), "matched_slots": matched.keys()})
	return valid

func on_shop_closed():
	if done:
		return
	if game.curOpponentData.get("name", "") != "Custom Opponent" or not register_inventory(game.OPPONENT, "O"):
		fail("custom opponent/layout not verified")
		return
	if config.player_fixture_enabled:
		if not player_membership_unchanged():
			fail("player fixture changed before native preparation")
			return
		player_setup_evidence["before_native_prepare"] = player_spatial_evidence()
		write_json("player_setup_evidence.json", player_setup_evidence)
		if not errors.empty():
			fail("player spatial associations invalid before preparation")
			return
	if not observer7_precondition():
		fail("observer7 post-opponent lineage PRECONDITION_UNSUPPORTED")
		return
	phase("shop_closed_sync")

func on_combat_start():
	if done:
		return
	phase("combat_start_sync")
	call_deferred("after_activate")

func after_activate():
	if not done:
		phase("activate_return_deferred")
		set_stage("combat_active")

func on_combat_end(result):
	if done or source_cut_frozen:
		return
	result_value = result
	set_stage("finalizing")
	# No snapshot/yield/deferred finish. Producer closes on actual first idle cut.


func check_barrier():
	var combat_log = game.combatLog
	var ok = game.fightEnded and combat_log.loggingFinished and game.curRound == 2 and not combat_log.events.empty()
	ok = ok and bus.connections.empty() and bus.signalQueue.empty()
	ok = ok and not game.combatTimer.is_physics_processing() and game.combatTimer.fatigueStartTimer.is_stopped() and game.combatTimer.fatigueTickTimer.is_stopped()
	ok = ok and game.ropeSpeedups.empty() and game.cubeAdvanced.empty() and not game.sandbagActive
	var expected_type = game.EventType.Win if result_value == game.RoundResult.Win else game.EventType.Loss
	ok = ok and combat_log.events[-1].type == expected_type
	for c in [game.PLAYER, game.OPPONENT]:
		ok = ok and not c.is_physics_processing()
		for timer_name in ["tickTimer", "battleRageTimer", "invulnerabilityTimer", "autoRageTimer"]:
			ok = ok and c.get(timer_name).is_stopped()
		for buff in c.buffs.values():
			ok = ok and buff.timer.is_stopped()
		for item in c.INVENTORY.getItems():
			ok = ok and not item.is_physics_processing()
	var winner = game.PLAYER if result_value == game.RoundResult.Win else game.OPPONENT
	var loser = game.OPPONENT if result_value == game.RoundResult.Win else game.PLAYER
	ok = ok and winner.curHealth >= 1 and loser.curHealth == 0
	return ok

func stable_snapshot():
	return {"events": freeze_events(), "histories": histories(), "state": state_snapshot()}

func frames():
	return {"idle": str(Engine.get_idle_frames()), "physics": str(Engine.get_physics_frames()), "elapsed_ms": OS.get_ticks_msec() - started}

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


func state_snapshot():
	var characters = []
	for c in [game.PLAYER, game.OPPONENT]:
		if c == null:
			continue
		var buffs = []
		for key in c.buffs:
			buffs.append({"stack_type": encode(key), "fields": fields(c.buffs[key], ["type", "current", "permanentStacks", "resistChancePercent", "resistStacks", "reflectChancePercent", "cleanseProtectionChancePercent", "temporaryStacks", "nextTemporaryTimeout"])})
		var items = []
		for item in c.INVENTORY.getItems():
			var observer7_fields = {}
			if item.descriptor.itemIndex == 62:
				observer7_fields = fields(item, ["reflects", "heat"])
			if item.descriptor.itemIndex == 179:
				observer7_fields = fields(item, ["manaNeeded", "cold", "spellSpeed"])
			if item.descriptor.itemIndex == 332:
				observer7_fields = fields(item, ["buffFactor", "buffLimit"])
			if item.descriptor.itemIndex == 374:
				observer7_fields = fields(item, ["cleanses", "potionSpeed"])
			if item.descriptor.itemIndex == 32:
				observer7_fields = fields(item,["manaCost","tempDamBonus","permDamBonus"])
			if item.descriptor.itemIndex == 209:
				observer7_fields = fields(item,["permDamBonus"])
			if item.descriptor.itemIndex == 39:
				observer7_fields = fields(item,["affectedItems"])
			if item.descriptor.itemIndex == 3:
				observer7_fields = fields(item,["broomBonusDam"])
			if item.descriptor.itemIndex in [19,35,36,37,46,172]:
				observer7_fields = fields(item,["isFull"])
			if item.descriptor.itemIndex == 172:
				observer7_fields = fields(item,["isFull","healthThreshold"])
			if item.descriptor.itemIndex == 129:
				observer7_fields = fields(item, ["activated"])
			if source_is(item, "res://Items/Goobert.gd"):
				observer7_fields = fields(item, ["activations", "activationsToTrigger"])
			if item.descriptor.itemIndex == 168:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "empower"])
			if item.descriptor.itemIndex == 53:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "blindAmount"])
			elif item.descriptor.itemIndex == 54:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "dam", "vampirism"])
			elif item.descriptor.itemIndex == 52:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "affectedWeapons"])
			elif item.descriptor.itemIndex == 340:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "numBuffs"])
			elif item.descriptor.itemIndex == 400:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "luck", "luckNeeded", "regen"])
			elif item.descriptor.itemIndex == 469:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "vampirism", "regen", "stamina", "blind", "dambonus"])
			elif item.descriptor.itemIndex == 468:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "staminaThreshold", "stamina", "regen"])
			if item.descriptor.itemIndex == 262:
				observer7_fields = fields(item, ["activations", "activationsToTrigger", "invuCharges", "protectedBuffs", "manaCost"])
			var observer7_timers = {}
			if item.descriptor.itemIndex in [53, 168]:
				var observer = get_root().get_node("NativeRandomObserver")
				observer.begin_encoding()
				observer7_timers = {"particleTimer": observer.timer_state(item.particleTimer)}
			items.append({"observer7_timers": observer7_timers, "observer7_fields": observer7_fields, "instance": encode(item), "fields": fields(item, ITEM_FIELDS), "physics_processing": item.is_physics_processing(), "chance_rng": fields(item.chanceRng, RNG_FIELDS), "damage_rng": fields(item.damageRangeRng, ["acc"])})
		var balanced = {}
		for key in ["accuracyRng", "critRng", "critResistanceRng", "stunResistanceRng"]:
			balanced[key] = fields(c.get(key), RNG_FIELDS)
		var stats = {}
		for stat_id in c.Stat.values():
			stats[stat_id] = c.getStat(stat_id)
		characters.append({"stats": encode(stats), "instance": encode(c), "fields": fields(c, CHAR_FIELDS), "buffs": buffs, "items": items, "balanced_rng": balanced, "physics_processing": c.is_physics_processing()})
	return {"event_bus": {"logging_mode": encode(bus.loggingMode), "pending_signal_count": bus.signalQueue.size(), "connection_count": bus.connections.size()}, "game": fields(game, ["curMode", "curClass", "curRound", "wins", "losses", "tries", "survivalMode", "fightEnded", "roundResults", "ropeSpeedups", "cubeAdvanced", "sandbagActive", "numTimesOutOfStamina"]), "characters": characters, "timer": fields(game.combatTimer, ["combatTime", "timeAdvance", "fatigueCounter"]), "rules": fields(rules, ["customRulesActive", "values"])}

func histories():
	var loggers = []
	for logger in game.combatLog.statLoggers:
		loggers.append(fields(logger, HIST_FIELDS))
	return {"stat_loggers": loggers, "global": fields(game.combatLog, LOG_FIELDS)}

func freeze_events():
	var rows = []
	for event in game.combatLog.events:
		var row = event_row(event)
		row["sequence"] = rows.size()
		rows.append(row)
	return rows

func event_row(event):
	var native_id = str(event.id)
	var oid = event.get_instance_id()
	if event_objects.has(native_id) and event_objects[native_id] != oid:
		errors.append("duplicate event ID: " + native_id)
	event_objects[native_id] = oid
	if event_visiting.has(oid):
		errors.append("cyclic event parent: " + native_id)
		return {"error": "cyclic_parent"}
	event_visiting[oid] = true
	var parent = null
	if event.parentEvent != null:
		parent = {"type": "event_reference", "id": str(event.parentEvent.id)}
		var parent_id = str(event.parentEvent.id)
		if not event_references.has(parent_id):
			event_references[parent_id] = event_row(event.parentEvent)
	var row = {"id": encode(event.id), "timestamp": encode(event.timestamp), "parent": parent, "origin": encode(event.origin), "target": encode(event.target), "type": encode(event.type), "type_name": game.eventTypeKeys[event.type], "params": encode(event.params), "snapshot": encode(event.snapshot)}
	event_visiting.erase(oid)
	return row

func encode(value, depth = 0):
	if depth > 64:
		errors.append("variant depth/cycle exceeds 64")
		return {"type": "unsupported", "reason": "depth"}
	var kind = typeof(value)
	match kind:
		TYPE_NIL:
			return {"type": "null"}
		TYPE_BOOL:
			return {"type": "bool", "value": value}
		TYPE_INT:
			return {"type": "int", "decimal": str(value)}
		TYPE_REAL:
			var buffer = StreamPeerBuffer.new()
			buffer.big_endian = true
			buffer.put_double(value)
			return {"type": "float", "display": str(value), "binary64_be": buffer.data_array.hex_encode()}
		TYPE_STRING:
			return {"type": "string", "value": value}
		TYPE_VECTOR2:
			return {"type": "Vector2", "x": encode(value.x, depth + 1), "y": encode(value.y, depth + 1)}
		TYPE_ARRAY, TYPE_INT_ARRAY, TYPE_REAL_ARRAY, TYPE_STRING_ARRAY, TYPE_VECTOR2_ARRAY, TYPE_RAW_ARRAY:
			var arr = []
			for v in value:
				arr.append(encode(v, depth + 1))
			return {"type": "array", "variant_type": kind, "values": arr}
		TYPE_DICTIONARY:
			var entries = []
			for key in value:
				entries.append({"key": encode(key, depth + 1), "value": encode(value[key], depth + 1)})
			return {"type": "dictionary", "entries": entries}
		TYPE_OBJECT:
			if get_root().get_node("NativeRandomObserver").is_temporary(value):
				# Snapshot fields now: duplicate(true) would keep the same Reference alive.
				return {"type": "TemporaryStacks", "native_id": str(value.get_instance_id()), "amount": encode(value.amount, depth + 1), "timeout": encode(value.timeout, depth + 1), "item": encode(value.item, depth + 1)}
			if not is_instance_valid(value):
				errors.append("freed object")
				return {"type": "unsupported", "reason": "freed"}
			var oid = value.get_instance_id()
			if registry.has(oid):
				return {"type": "instance_reference", "id": registry[oid]}
			var script = value.get_script()
			var path = script.resource_path if script != null else ""
			if path == "res://Core/StatHistory.gd":
				return {"type": "StatHistory", "event_numbers": encode(value.eventNumbers, depth + 1), "values": encode(value.values, depth + 1)}
			if path == "res://Core/CombatEvent.gd":
				var eid = str(value.id)
				if not event_references.has(eid):
					event_references[eid] = event_row(value)
				return {"type": "event_reference", "id": eid}
			errors.append("unsupported object: " + path)
			return {"type": "unsupported", "script": path}
	errors.append("unsupported Variant: " + str(kind))
	return {"type": "unsupported", "variant_type": kind}

func serializer_selftest():
	var zero = StreamPeerBuffer.new()
	zero.big_endian = true
	zero.put_double(-0.0)
	zero.seek(0)
	return encode(0).type == "int" and encode(null).type == "null" and encode(9223372036854775807).decimal == "9223372036854775807" and encode(-0.0).binary64_be == "8000000000000000" and encode(1.0).binary64_be == "3ff0000000000000" and zero.get_double() == 0.0

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

func source_is(value, expected_path):
	if value == null or not is_instance_valid(value):
		return false
	var script = value.get_script()
	for _depth in range(16):
		if script == null:
			return false
		if script.resource_path == expected_path:
			return true
		script = script.get_base_script()
	errors.append("script inheritance exceeds bounded16")
	return false

func slot_spec(side, slot):
	var observer = get_root().get_node("NativeRandomObserver")
	for spec in observer.SOURCE_SLOT_TABLE:
		if spec.side == side and spec.input_slot == slot:
			return spec
	return null


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


func source_connection_target(row):
	var target = row.get("target", null)
	if typeof(target) == TYPE_OBJECT and is_instance_valid(target):
		return target.get_instance_id()
	if typeof(target) == TYPE_INT:
		return target
	return -1


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



# PHASE368 OBSERVATION-CONTROL EXTENSION
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
	var table = observer.source_control_rows(self, "idle_frame") if available else collector_control_rows(self, "idle_frame")
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
	return {"site": site, "reason": reason, "stage": stage, "detail": detail, "collector_id": str(get_instance_id()), "tree_id": str(self.get_instance_id()), "observer_present": observer != null, "observer_id": str(observer.get_instance_id()) if observer != null else null, "observer_api_available": available, "observer_failed": observer.failed if available else null, "first_error": observer.first_error.duplicate(true) if available and typeof(observer.first_error) == TYPE_DICTIONARY else null, "ui_opened": observer.ui_opened if available else null, "ui_closed": observer.ui_closed if available else null, "closed": observer.closed if available else null, "configured": observer.configured if available else null, "metadata_ready": observer.metadata_ready if available else null, "source_fixture_window": observer.source_fixture_window if available else null, "source_window_complete": observer.source_window_complete if available else null, "listener_attached": source_listener_attached, "connect_attempted": source_control_connect_attempted, "connect_return": source_control_connect_return, "clock_is_connected": is_connected("idle_frame", observer, "clock_idle_signal") if available else null, "private_is_connected": observer.is_connected("source_idle_cut_ready", self, "on_idle_source_cut") if available and observer.has_signal("source_idle_cut_ready") else null, "tree_connections": table, "private_connections": private_rows, "match_indices": match_indices, "cut": observer.source_cut_control() if available else null, "once_guard": source_cut_frozen, "finish_entered": source_cut_finish_entered, "book_reached": source_book_reached, "instantiate_reached": source_instantiate_reached, "geometry_reached": source_geometry_reached}


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

func collector_diag_valid(value, depth = 0):
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
				if not collector_diag_valid(member, depth + 1):
					return false
			return true
		TYPE_DICTIONARY:
			if value.size() > 64:
				return false
			for key in value:
				if typeof(key) != TYPE_STRING or key.to_utf8().size() > 128 or not collector_diag_valid(value[key], depth + 1):
					return false
			return true
	return false



func collector_control_target(value):
	if typeof(value) == TYPE_OBJECT and is_instance_valid(value):
		return value.get_instance_id()
	if typeof(value) == TYPE_INT and value > 0:
		return value
	return null



func collector_control_bound_value(value):
	match typeof(value):
		TYPE_NIL:
			return {"type": "NULL"}
		TYPE_BOOL:
			return {"type": "BOOL", "value": value}
		TYPE_INT:
			return {"type": "INT", "value": str(value)}
		TYPE_REAL:
			return {"type": "REAL", "bits": collector_control_float_bits(value)}
		TYPE_STRING:
			if value.to_utf8().size() <= 256:
				return {"type": "STRING", "value": value}
		TYPE_OBJECT:
			if is_instance_valid(value):
				return {"type": "OBJECT_ID", "value": str(value.get_instance_id())}
	return {"type": "UNSUPPORTED", "variant_type": typeof(value)}



func collector_control_rows(emitter, signal_name):
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
				var data = collector_control_bound_value(bound)
				if data.type == "UNSUPPORTED":
					supported = false
				encoded.append(data)
		var method = row.get("method", null)
		var flags = row.get("flags", null)
		var source_id = collector_control_target(row.get("source", null))
		var target_id = collector_control_target(row.get("target", null))
		if typeof(method) != TYPE_STRING or method.to_utf8().size() > 256 or typeof(flags) != TYPE_INT:
			supported = false
		if source_id == null or target_id == null:
			supported = false
		result.rows.append({"ordinal": index, "source_has_key": row.has("source"), "source_variant_type": typeof(row.get("source", null)), "source_available": source_id != null, "source_native_id": str(source_id) if source_id != null else null, "target_has_key": row.has("target"), "target_variant_type": typeof(row.get("target", null)), "target_available": target_id != null, "target_native_id": str(target_id) if target_id != null else null, "method": method if typeof(method) == TYPE_STRING and method.to_utf8().size() <= 256 else null, "flags": flags if typeof(flags) == TYPE_INT else null, "binds_count": binds.size() if typeof(binds) == TYPE_ARRAY else null, "binds": encoded})
	result.complete_seen = supported
	result.reason = null if supported else "UNSUPPORTED_CONNECTION_FIELD"
	return result



func collector_control_float_bits(value):
	var buffer = StreamPeerBuffer.new()
	buffer.big_endian = true
	buffer.put_double(value)
	return buffer.data_array.hex_encode()

