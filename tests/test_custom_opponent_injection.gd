extends Node

var frames = 0
var done = false

func _process(_delta):
	if done:
		return
	frames += 1
	if frames > 600:
		fail("main scene did not become ready")
		return
	if Game.mainNode == null or Game.PLAYER == null or Game.itemLibrary == null or not Game.sceneAnimation.is_connected("animation_finished", Game, "onSceneAnimationFinished"):
		return
	if Game.state != Game.State.Title:
		return
	done = true
	run_checks()

func run_checks():
	var path = ProjectSettings.globalize_path("res://project.godot").get_base_dir().get_base_dir().plus_file("data/custom_opponent.json")
	var round_data = Game.loadCustomOpponentRound(path)
	if round_data == null:
		fail("sample JSON did not load")
		return
	if round_data["class"] != 0 or round_data["health"] != 25 or round_data["stamina"] != 5 or round_data["items"].size() != 5:
		fail("sample attributes were not preserved")
		return
	var expected_ids = [67, 11, 11, 24, 1]
	for i in expected_ids.size():
		if round_data["items"][i]["d"].itemIndex != expected_ids[i]:
			fail("sample item index mismatch at " + String(i))
			return
	var socket_item_index = -1
	var gem_item_index = -1
	for i in ItemBook.getNumItems():
		var descriptor = ItemBook.getDescriptorFromIndex(i)
		if descriptor == null or descriptor.scene == null:
			continue
		if socket_item_index == -1 and ItemBook.getNumSockets(i) > 0 and not descriptor.isGem():
			socket_item_index = i
		if gem_item_index == -1 and descriptor.isGem() and ItemBook.gemIndex.has(descriptor.identifier):
			gem_item_index = i
	if socket_item_index == -1 or gem_item_index == -1:
		fail("socket item or gem descriptor was not found")
		return
	var sockets = []
	for i in ItemBook.getNumSockets(socket_item_index):
		sockets.push_back(null)
	sockets[0] = gem_item_index
	var ring_descriptor = ItemBook.getDescriptorFromIndex(505)
	var ring_instance = Game.itemLibrary.getInstance(ring_descriptor)
	if ring_instance == null or not ring_instance.has_method("getDataPersistentBits"):
		fail("Magic Ring persistent instance was not found")
		return
	var persistent_data = ""
	for i in int(ceil(ring_instance.getDataPersistentBits() / 6.0)):
		persistent_data += ">"
	if persistent_data.empty():
		fail("Magic Ring persistent encoding has zero length")
		return
	var optional_source = {
		"schema_version": 1, "game_version": Game.VERSION, "class": 0,
		"health": 25, "stamina": 5,
		"items": [
			{"item_index": socket_item_index, "x": 0, "y": 0, "f": 0, "gems": sockets},
			{"item_index": 505, "x": 3, "y": 3, "f": 0, "persistent_data": persistent_data}
		]
	}
	var optional_path = path.get_base_dir().plus_file("custom_opponent_test_invalid.json")
	var optional_file = File.new()
	if optional_file.open(optional_path, File.WRITE) != OK:
		fail("could not write optional-fields fixture")
		return
	optional_file.store_string(JSON.print(optional_source))
	optional_file.close()
	var optional_round = Game.loadCustomOpponentRound(optional_path)
	Directory.new().remove(optional_path)
	if optional_round == null or optional_round["items"][0]["g"][0] != ItemBook.gemIndex[ItemBook.getDescriptorFromIndex(gem_item_index).identifier] or optional_round["items"][1]["pd"] != persistent_data:
		fail("gem or persistent data was not converted")
		return
	Game.OPPONENT = Game.opponentScene.instance()
	Game.OPPONENT.playerId = Game.OPPONENT.ID.OPPONENT
	Game.PLAYER.setOpponent(Game.OPPONENT)
	Game.OPPONENT.setOpponent(Game.PLAYER)
	Game.opponentNode.add_child(Game.OPPONENT)
	if Game.initOpponent(0, 0, round_data) != 0:
		fail("sample placement failed")
		return
	if Game.OPPONENT.INVENTORY.getItems().size() != 5:
		fail("opponent inventory does not contain five items")
		return
	if Game.OPPONENT.getClass() != 0 or Game.OPPONENT.getMaxHealth() != 25 or Game.OPPONENT.getMaxStamina() != 5:
		fail("opponent attributes were not applied")
		return
	print("CUSTOM_OPPONENT_TEST_PASS: JSON load, native item conversion, gems, persistent data, placement, attributes")
	get_tree().quit(0)

func fail(message: String):
	push_error("CUSTOM_OPPONENT_TEST_FAIL: " + message)
	get_tree().quit(1)
