extends Node
var stage = 0
var started_at = OS.get_ticks_msec()
var combat_at = 0
var shop_animation_advanced = false

func _process(_delta):
	if OS.get_ticks_msec() - started_at > 90000:
		fail("timeout stage=" + String(stage))
		return
	if stage == 0:
		if Game.state != Game.State.Title or Game.PLAYER == null or Game.itemLibrary == null or not Game.sceneAnimation.is_connected("animation_finished", Game, "onSceneAnimationFinished"):
			return
		Game.instanceCharacter(0)
		Game.initStartInventory()
		Game.startFreshRun(Game.Mode.Unranked)
		print("EFFECT_SPIKES_STARTED user_data=" + OS.get_user_data_dir())
		stage = 1
	elif stage == 1:
		if not shop_animation_advanced and Game.sceneAnimation.current_animation == "TitleToShop":
			shop_animation_advanced = true
			Game.sceneAnimation.advance(1000)
		if Game.state == Game.State.Shop and Game.canSwitchToCombat:
			setup_player()
			Game.switchToCombat()
			stage = 2
	elif stage == 2:
		if Game.state != Game.State.Combat:
			return
		if Game.curOpponentData.get("name", "") != "Custom Opponent":
			fail("wrong opponent")
			return
		print("EFFECT_SPIKES_COMBAT opponent_items=" + String(Game.OPPONENT.INVENTORY.getItems().size()))
		combat_at = OS.get_ticks_msec()
		capture("combat")
		stage = 3
	elif stage == 3:
		if OS.get_ticks_msec() - combat_at > 12000:
			capture("active")
			stage = 4
	elif stage == 4:
		if Game.fightEnded or OS.get_ticks_msec() - combat_at > 24000:
			capture("final")
			print("EFFECT_SPIKES_GUI_PASS original combat observed")
			get_tree().quit(0)

func setup_player():
	Game.PLAYER.INVENTORY.reset()
	for y in [0, 2, 4]:
		for x in [0, 2, 4, 6]:
			add_player_item("Leather Bag", x, y)
	for x in [0, 1, 2, 3]:
		add_player_item("Walrus Tusk", x, 0)
	Game.PLAYER.setMaxHealth(200)
	print("EFFECT_SPIKES_PLAYER four Walrus Tusk, base health 200")

func add_player_item(item_name: String, x: int, y: int):
	var item = ItemBook.instantiateItem(item_name)
	item.ownerType = Item.Owner.PlayerInventory
	Game.playerNode.add_child(item)
	item.setFaceDirectionInstant(0)
	var cur_pos = item.getTopLeftGlobal()
	var target_pos = Game.PLAYER.INVENTORY.tilemap.to_global(Game.PLAYER.INVENTORY.tilemap.map_to_world(Vector2(x, y)))
	item.global_translate(target_pos - cur_pos)
	if not item.isBag() and not Game.PLAYER.INVENTORY.canAddItem(item):
		fail("illegal player item " + item_name)
		return
	Game.PLAYER.INVENTORY.addItemByTopLeft(item, Vector2(x, y))

func capture(label: String):
	var path = ProjectSettings.globalize_path("res://project.godot").get_base_dir().get_base_dir().plus_file("data/effect_spikes_gui_" + label + ".png")
	var picture = get_viewport().get_texture().get_data()
	picture.flip_y()
	if picture.save_png(path) != OK:
		fail("capture failed")

func fail(message: String):
	push_error("EFFECT_SPIKES_GUI_FAIL " + message)
	get_tree().quit(1)
