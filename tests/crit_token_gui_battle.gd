extends Node
var stage = 0
var started_at = OS.get_ticks_msec()
var combat_at = 0
var paused_at = 0
var advanced = false
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
		print("CRIT_GUI_START user_data=" + OS.get_user_data_dir())
		stage = 1
	elif stage == 1:
		if not advanced and Game.sceneAnimation.current_animation == "TitleToShop":
			advanced = true
			Game.sceneAnimation.advance(1000)
		if Game.state == Game.State.Shop and Game.canSwitchToCombat:
			Game.PLAYER.setMaxHealth(200)
			Game.switchToCombat()
			stage = 2
	elif stage == 2:
		if Game.state != Game.State.Combat: return
		if Game.curOpponentData.get("name", "") != "Custom Opponent":
			fail("wrong opponent")
			return
		for item in Game.OPPONENT.INVENTORY.getItems():
			print("CRIT_GUI_ITEM name=", item.getName(), " cells=", item.occupiedCells)
		capture("loaded")
		combat_at = OS.get_ticks_msec()
		stage = 3
	elif stage == 3 and OS.get_ticks_msec() - combat_at > 10000:
		capture("combat")
		print("CRIT_GUI_OBSERVED heat=", Game.OPPONENT.getHeat(), " mana=", Game.OPPONENT.getMana(), " char_tokens=", Game.OPPONENT.getCritTokens())
		Engine.time_scale = 0.001
		paused_at = OS.get_ticks_msec()
		stage = 4
	elif stage == 4 and OS.get_ticks_msec() - paused_at > 25000:
		print("CRIT_GUI_PASS")
		get_tree().quit(0)
func capture(label: String):
	var path = ProjectSettings.globalize_path("res://project.godot").get_base_dir().get_base_dir().plus_file("data/crit_token_gui_" + label + ".png")
	var img = get_viewport().get_texture().get_data()
	img.flip_y()
	if img.save_png(path) != OK: fail("capture failed")
func fail(message: String):
	push_error("CRIT_GUI_FAIL " + message)
	get_tree().quit(1)
