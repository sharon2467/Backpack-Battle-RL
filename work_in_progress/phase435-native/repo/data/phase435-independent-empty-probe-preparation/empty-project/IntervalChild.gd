extends Node
# FIXTURE ONLY intentional native Timer activity before owner-ready checkpoint.
func _ready():
	var owner = get_parent()
	var timer = owner.get_node("InvulnerabilityTimer")
	owner.probe_monitor.invoke(owner.probe_memory, "track_king_timer_api", [timer, "start"])
	timer.start(1.25)
	owner.probe_monitor.invoke(owner.probe_memory, "track_king_timer_api", [timer, "stop"])
	timer.stop()
