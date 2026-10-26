extends Node2D
# FIXTURE ONLY callback wrappers: exact selected memory function bodies reside in MemoryObserver.
var probe_memory = null
var probe_monitor = null
var probe_target = null
var skip_entry = false
var first_return = "UNSET"
var ready_return = "UNSET"
func target():
	return probe_target if probe_target != null else get_node("InvulnerabilityTimer")
func _enter_tree():
	if not skip_entry:
		first_return = probe_monitor.invoke(probe_memory, "invu_first_enter_memory", [target(), self])
func _ready():
	ready_return = probe_monitor.invoke(probe_memory, "invu_parent_ready_memory", [target(), self])
