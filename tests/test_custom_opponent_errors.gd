extends Node

var frames = 0

func _process(_delta):
	frames += 1
	if frames > 600:
		fail("main scene did not become ready")
		return
	if Game.state != Game.State.Title or Game.PLAYER == null or Game.itemLibrary == null or not Game.sceneAnimation.is_connected("animation_finished", Game, "onSceneAnimationFinished"):
		return
	set_process(false)
	run_checks()

func run_checks():
	var data_dir = ProjectSettings.globalize_path("res://project.godot").get_base_dir().get_base_dir().plus_file("data")
	var sample_path = data_dir.plus_file("custom_opponent.json")
	var invalid_path = data_dir.plus_file("custom_opponent_test_invalid.json")
	var sample_file = File.new()
	if sample_file.open(sample_path, File.READ) != OK:
		fail("cannot read sample JSON")
		return
	var source = JSON.parse(sample_file.get_as_text()).result
	sample_file.close()
	if not expect_rejected(invalid_path, "{", "malformed JSON"):
		return
	var wrong_version = source.duplicate(true)
	wrong_version["game_version"] = "0.0.0"
	if not expect_rejected(invalid_path, JSON.print(wrong_version), "game version"):
		return
	var unknown_field = source.duplicate(true)
	unknown_field["typo"] = true
	if not expect_rejected(invalid_path, JSON.print(unknown_field), "unknown field"):
		return
	var bad_item = source.duplicate(true)
	bad_item["items"][0]["item_index"] = ItemBook.getNumItems()
	if not expect_rejected(invalid_path, JSON.print(bad_item), "item index"):
		return
	var bad_gems = source.duplicate(true)
	var gems = []
	for i in ItemBook.getNumSockets(67) + 1:
		gems.push_back(null)
	bad_gems["items"][0]["gems"] = gems
	if not expect_rejected(invalid_path, JSON.print(bad_gems), "gem socket count"):
		return
	var bad_persistent_data = source.duplicate(true)
	bad_persistent_data["items"][0]["persistent_data"] = "abc"
	if not expect_rejected(invalid_path, JSON.print(bad_persistent_data), "unexpected persistent data"):
		return
	var bad_encoding = source.duplicate(true)
	bad_encoding["items"][0]["item_index"] = 505
	bad_encoding["items"][0]["persistent_data"] = "!!"
	if not expect_rejected(invalid_path, JSON.print(bad_encoding), "invalid native persistent encoding"):
		return
	var invalid_layout = source.duplicate(true)
	invalid_layout["items"][0]["x"] = 8
	invalid_layout["items"][0]["y"] = 6
	if not write_json(invalid_path, JSON.print(invalid_layout)):
		return
	var round_data = Game.loadCustomOpponentRound(invalid_path)
	if round_data == null:
		fail("invalid layout was rejected before placement")
		return
	Game.OPPONENT = Game.opponentScene.instance()
	Game.OPPONENT.playerId = Game.OPPONENT.ID.OPPONENT
	Game.PLAYER.setOpponent(Game.OPPONENT)
	Game.OPPONENT.setOpponent(Game.PLAYER)
	Game.opponentNode.add_child(Game.OPPONENT)
	var recent_marker = RunData.new()
	RunDatabase.recentOpponentRuns.push_back(recent_marker)
	if Game.initOpponent(0, 0, round_data) != -1:
		fail("invalid layout was accepted")
		return
	if RunDatabase.recentOpponentRuns.empty() or RunDatabase.recentOpponentRuns.back() != recent_marker:
		fail("invalid custom layout changed the recent opponent cache")
		return
	RunDatabase.recentOpponentRuns.pop_back()
	Directory.new().remove(invalid_path)
	print("CUSTOM_OPPONENT_ERRORS_PASS: malformed JSON, version, fields, index, gems, persistent encoding, layout")
	get_tree().quit(0)

func expect_rejected(path: String, body: String, label: String) -> bool:
	if not write_json(path, body):
		return false
	if Game.loadCustomOpponentRound(path) != null:
		fail(label + " was accepted")
		return false
	return true

func write_json(path: String, body: String) -> bool:
	var file = File.new()
	if file.open(path, File.WRITE) != OK:
		fail("cannot write test fixture")
		return false
	file.store_string(body)
	file.close()
	return true

func fail(message: String):
	push_error("CUSTOM_OPPONENT_ERRORS_FAIL: " + message)
	get_tree().quit(1)
