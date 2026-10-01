extends Node

var stage = 0
var started_at = OS.get_ticks_msec()
var shop_animation_advanced = false

func _process(_delta):
	if OS.get_ticks_msec() - started_at > 90000:
		fail("battle did not finish within 90 seconds; stage=" + String(stage) + " state=" + String(Game.state) + " animation=" + String(Game.sceneAnimation.current_animation) + " position=" + String(Game.sceneAnimation.current_animation_position))
		return
	if stage == 0:
		if Game.state != Game.State.Title or Game.PLAYER == null or Game.itemLibrary == null or not Game.sceneAnimation.is_connected("animation_finished", Game, "onSceneAnimationFinished"):
			return
		if not Game.EDITOR:
			fail("expected editor feature")
			return
		Game.instanceCharacter(0)
		Game.initStartInventory()
		Game.startFreshRun(Game.Mode.Unranked)
		print("CUSTOM_OPPONENT_BATTLE_STARTED: user_data=" + OS.get_user_data_dir())
		stage = 1
	elif stage == 1:
		if not shop_animation_advanced and Game.sceneAnimation.current_animation == "TitleToShop":
			shop_animation_advanced = true
			Game.sceneAnimation.advance(1000)
		if Game.state == Game.State.Shop and Game.canSwitchToCombat:
			Game.switchToCombat()
			stage = 2
	elif stage == 2:
		if Game.state != Game.State.Combat:
			return
		if Game.OPPONENT == null or Game.curOpponentData.get("name", "") != "Custom Opponent":
			fail("combat used a different opponent source")
			return
		if Game.OPPONENT.INVENTORY.getItems().size() != 5:
			fail("combat opponent does not have five injected items")
			return
		if Game.OPPONENT.getMaxHealth() != 25 or Game.OPPONENT.getMaxStamina() != 5:
			fail("combat opponent attributes differ from JSON")
			return
		var capture_path = ProjectSettings.globalize_path("res://project.godot").get_base_dir().get_base_dir().plus_file("data/custom_opponent_battle_capture.png")
		var capture = get_viewport().get_texture().get_data()
		capture.flip_y()
		if capture.save_png(capture_path) != OK:
			fail("could not save combat screenshot")
			return
		print("CUSTOM_OPPONENT_BATTLE_LOADED: unranked injection reached combat")
		Engine.time_scale = 6
		stage = 3
	elif stage == 3 and Game.fightEnded:
		print("CUSTOM_OPPONENT_BATTLE_PASS: game engine finished the battle")
		get_tree().quit(0)

func fail(message: String):
	push_error("CUSTOM_OPPONENT_BATTLE_FAIL: " + message)
	get_tree().quit(1)
