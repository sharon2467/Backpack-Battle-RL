# SOURCE template: control-only checks; SceneTree owner, no Node-only get_tree API.
func source_terminal_receipt_matches(receipt, control):
	if typeof(receipt) != TYPE_DICTIONARY or typeof(control) != TYPE_DICTIONARY or not receipt.has("terminal_cut") or not control.has("terminal_cut") or not receipt.has("cleanup") or receipt.cleanup == null:
		return false
	var keys = ["schema", "terminal_policy", "cleanup_anchor_pass", "first_eligible_idle_pass", "minimum_future_physics_signals", "observed_future_physics_signals"]
	for value in [receipt.terminal_cut, control.terminal_cut]:
		if typeof(value) != TYPE_DICTIONARY or value.size() != keys.size():
			return false
		for key in keys:
			if not value.has(key):
				return false
		if typeof(value.schema) != TYPE_STRING or value.schema != "phase390-terminal-cut-control/1" or typeof(value.terminal_policy) != TYPE_STRING or value.terminal_policy != "first-actual-idle-after-at-least-two-future-physics/1":
			return false
		for key in ["cleanup_anchor_pass", "first_eligible_idle_pass", "minimum_future_physics_signals", "observed_future_physics_signals"]:
			if typeof(value[key]) != TYPE_INT or value[key] < 0:
				return false
		if value.minimum_future_physics_signals != 2 or value.observed_future_physics_signals < 2 or value.cleanup_anchor_pass >= value.first_eligible_idle_pass:
			return false
	for key in keys:
		if typeof(receipt.terminal_cut[key]) != typeof(control.terminal_cut[key]) or receipt.terminal_cut[key] != control.terminal_cut[key]:
			return false
	var cleanup = receipt.cleanup
	if typeof(cleanup) != TYPE_DICTIONARY or cleanup.size() != 3 or not cleanup.has("physics_frame") or not cleanup.has("idle_frame") or not cleanup.has("is_in_physics_frame"):
		return false
	if typeof(cleanup.physics_frame) != TYPE_INT or typeof(cleanup.idle_frame) != TYPE_INT or typeof(cleanup.is_in_physics_frame) != TYPE_BOOL or typeof(receipt.clock_passes) != TYPE_INT:
		return false
	if receipt.terminal_cut.first_eligible_idle_pass != receipt.clock_passes or receipt.terminal_cut.observed_future_physics_signals != Engine.get_physics_frames() - cleanup.physics_frame or Engine.is_in_physics_frame():
		return false
	return control.physics == Engine.get_physics_frames() and control.idle == Engine.get_idle_frames()
