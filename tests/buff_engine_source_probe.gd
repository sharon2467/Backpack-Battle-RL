extends MainLoop

func _initialize() -> void:
	var expected_sha = OS.get_environment("BB_BUFF_EDGE_EXPECTED_SHA").to_lower()
	var loaded_sha = File.new().get_sha256("res://Core/Buff.gd").to_lower()
	var source_version = ""
	var game_source = File.new()
	if game_source.open("res://Core/Game.gd", File.READ) == OK:
		for line in game_source.get_as_text().split("\n"):
			if line.begins_with("var VERSION = "):
				source_version = line.get_slice('"', 1)
		game_source.close()
	var row = {
		"probe_kind":"pre_autoload_metadata",
		"exe":OS.get_executable_path(),
		"engine":Engine.get_version_info(),
		"project":ProjectSettings.globalize_path("res://project.godot"),
		"resource_root":ProjectSettings.globalize_path("res://"),
		"user_data":OS.get_user_data_dir(),
		"editor_feature":OS.has_feature("editor"),
		"full_feature":OS.has_feature("full_version"),
		"disable_steam_feature":OS.has_feature("disable_steam_integration"),
		"custom_features_setting":ProjectSettings.get_setting("custom_features") if ProjectSettings.has_setting("custom_features") else null,
		"underscore_custom_features_setting":ProjectSettings.get_setting("_custom_features") if ProjectSettings.has_setting("_custom_features") else null,
		"game_version_source_text":source_version,
		"game_instance_started":false,
		"loaded_buff_sha256":loaded_sha,
		"expected_buff_sha256":expected_sha,
		"source_matches":loaded_sha != "" and loaded_sha == expected_sha
	}
	print("BUFF_EDGE_SOURCE ", JSON.print(row))
	var evidence = File.new()
	var evidence_path = OS.get_environment("BB_BUFF_EDGE_RUN_DATA").plus_file("source_probe.json")
	if evidence.open(evidence_path, File.WRITE) == OK:
		evidence.store_string(JSON.print(row))
		evidence.close()
	if source_version != "1.1.8" or not row.source_matches:
		print("BUFF_EDGE_SOURCE_MISMATCH")
		OS.set_exit_code(2)
	else:
		print("BUFF_EDGE_SOURCE_PASS")
		OS.set_exit_code(0)

func _idle(_delta: float) -> bool:
	return true
