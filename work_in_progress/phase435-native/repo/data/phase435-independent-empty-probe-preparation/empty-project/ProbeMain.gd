extends Node
# EMPTY fixture harness; never loads original Game/assets/collector.
const MEMORY = preload("res://MemoryObserver.gd")
const INTERVAL = preload("res://IntervalChild.gd")
const WRONG = preload("res://WrongTimer.gd")
var source_entries = 0
var results = []
var bad = false
func invoke(memory, method, args):
	source_entries += 1
	return memory.callv(method, args)
func check(ok, label):
	if not ok and not bad:
		bad = true
		print(JSON.print({"status":"FIRST_FAILURE", "label":label, "external_calls":source_entries, "results":results}))
	return ok
func primitive(value, depth = 0):
	if depth > 24:
		return false
	var kind = typeof(value)
	if kind in [TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_REAL, TYPE_STRING]:
		return true
	if kind == TYPE_ARRAY:
		for item in value:
			if not primitive(item, depth + 1): return false
		return true
	if kind == TYPE_DICTIONARY:
		for key in value:
			if not primitive(key, depth + 1) or not primitive(value[key], depth + 1): return false
		return true
	return false
func make_case(mode = "normal", interval = false):
	var memory = MEMORY.new()
	var path = "res://Core/Character.tscn" if mode == "wrong_scene" else "res://Core/Player.tscn"
	var owner = load(path).instance()
	owner.probe_memory = memory
	owner.probe_monitor = self
	var timer = owner.get_node("InvulnerabilityTimer")
	var extra = null
	var holder = null
	if interval:
		var child = Node.new()
		child.set_script(INTERVAL)
		owner.add_child(child)
	if mode == "wrong_class":
		owner.remove_child(timer)
		timer.free()
		timer = Node.new()
		timer.name = "InvulnerabilityTimer"
		owner.add_child(timer)
		owner.probe_target = timer
	elif mode == "wrong_name":
		timer.name = "DifferentTimer"
		owner.probe_target = timer
	elif mode == "target_script":
		timer.set_script(WRONG)
	elif mode == "wrong_parent":
		owner.remove_child(timer)
		var box = Node2D.new()
		owner.add_child(box)
		box.add_child(timer)
		owner.probe_target = timer
	elif mode == "already_inside":
		extra = Timer.new()
		extra.name = "InvulnerabilityTimer"
		add_child(extra)
		owner.probe_target = extra
	elif mode == "skip_entry":
		owner.skip_entry = true
	if mode == "deep":
		holder = Node2D.new()
		add_child(holder)
		var cursor = holder
		for index in range(16):
			var part = Node2D.new()
			cursor.add_child(part)
			cursor = part
		cursor.add_child(owner)
	else:
		add_child(owner)
	return {"memory":memory,"owner":owner,"timer":timer,"extra":extra,"holder":holder}
func clean(c):
	if c.holder != null: c.holder.free()
	else: c.owner.free()
	if c.extra != null: c.extra.free()
	c.memory.free()
func mark(label, before, expected, ok):
	var calls = source_entries - before
	var passed = check(ok and calls == expected, label)
	results.append({"id":label,"pass":passed,"external_calls":calls,"expected_calls":expected})
	return passed
func run_controls():
	var start = source_entries
	var c = make_case()
	var memory = c.memory
	var born = memory.invu_early_timers.get(c.timer.get_instance_id(), null)
	var ok = born != null and memory.invu_early_error == null
	if ok:
		ok = typeof(c.owner.first_return) == TYPE_NIL and typeof(c.owner.ready_return) == TYPE_NIL and not born.birth_raw.node.inside_tree and born.entry.owner_inside_tree and not born.entry.observer_ready_at_entry and born.parent_ready != null and primitive(memory.invu_early_timers)
	if not mark("G01",start,2,ok): return
	clean(c)
	start = source_entries
	c = make_case("normal",true)
	born = c.memory.invu_early_timers.get(c.timer.get_instance_id(),null)
	ok = born != null and born.starts == 1 and born.stops == 1 and born.parent_ready.starts == 1 and born.parent_ready.stops == 1 and typeof(born.parent_ready.state.wait_time) == TYPE_REAL
	if not mark("G02",start,4,ok): return
	clean(c)
	for mode in ["wrong_class","wrong_name","target_script","wrong_parent","already_inside","wrong_scene"]:
		start = source_entries
		c = make_case(mode)
		var codes = {"wrong_class":"INVU_NATIVE_TIMER","wrong_name":"INVU_NATIVE_TIMER_DOMAIN","target_script":"INVU_NATIVE_TIMER_DOMAIN","wrong_parent":"INVU_FIRST_ENTRY_DOMAIN","already_inside":"INVU_FIRST_ENTRY_DOMAIN","wrong_scene":"INVU_FIRST_ENTRY_DOMAIN"}
		ok = c.memory.invu_early_error != null and c.memory.invu_early_error.code == codes[mode] and c.memory.invu_early_timers.empty() and c.memory.fail_invocations == 0 and typeof(c.owner.first_return) == TYPE_NIL and primitive(c.memory.invu_early_error)
		if not mark("G03-"+mode,start,2,ok): return
		clean(c)
	start = source_entries
	c = make_case("normal",true)
	var frozen = JSON.print(c.memory.invu_early_timers)
	remove_child(c.owner)
	add_child(c.owner)
	ok = c.memory.invu_early_error != null and c.memory.invu_early_error.code == "INVU_FIRST_ENTRY_REUSED" and JSON.print(c.memory.invu_early_timers) == frozen
	if not mark("G04",start,5,ok): return
	clean(c)
	start = source_entries
	c = make_case("skip_entry")
	if not mark("G05-before",start,1,c.memory.invu_early_error != null and c.memory.invu_early_error.code == "INVU_READY_WITHOUT_ENTRY" and c.memory.invu_early_timers.empty()): return
	clean(c)
	start = source_entries
	c = make_case()
	frozen = JSON.print(c.memory.invu_early_timers)
	invoke(c.memory,"invu_parent_ready_memory",[c.timer,c.owner])
	if not mark("G05-duplicate",start,3,c.memory.invu_early_error != null and c.memory.invu_early_error.code == "INVU_READY_IDENTITY_OR_REUSED" and JSON.print(c.memory.invu_early_timers) == frozen): return
	clean(c)
	for mode in ["unknown","overflow"]:
		start = source_entries
		c = make_case()
		born = c.memory.invu_early_timers[c.timer.get_instance_id()]
		if mode == "overflow": born.starts = 9007199254740991
		var before_count = born.starts
		invoke(c.memory,"track_king_timer_api",[c.timer,"unknown" if mode == "unknown" else "start"])
		if not mark("G06-"+mode,start,3,c.memory.invu_early_error != null and c.memory.invu_early_error.code == ("INVU_TIMER_API_DOMAIN" if mode == "unknown" else "INVU_TIMER_API_COUNTER") and born.starts == before_count and born.stops == 0 and c.memory.fail_invocations == 0): return
		clean(c)
	start = source_entries
	memory = MEMORY.new()
	invoke(memory,"_invu_memory_error",["PRE_READY",1,2])
	invoke(memory,"probe_successful_bootstrap_tail",[])
	invoke(memory,"probe_successful_bootstrap_tail",[])
	if not mark("G07",start,3,memory.invu_observer_ready and memory.fail_invocations == 1 and memory.fail_effects == 1): return
	memory.free()
	start = source_entries
	c = make_case()
	c.memory.invu_observer_ready = true
	invoke(c.memory,"track_king_timer_api",[c.timer,"unknown"])
	invoke(c.memory,"track_king_timer_api",[c.timer,"unknown"])
	if not mark("G08",start,4,c.memory.fail_invocations == 2 and c.memory.fail_effects == 1): return
	clean(c)
	start = source_entries
	c = make_case()
	var result = invoke(c.memory,"_invu_memory_error",["NIL",1,2])
	var raw_error = invoke(c.memory,"_invu_raw_snapshot",[null])
	ok = typeof(result) == TYPE_NIL and typeof(raw_error) == TYPE_NIL and typeof(c.owner.first_return) == TYPE_NIL and typeof(c.owner.ready_return) == TYPE_NIL
	if not mark("G09",start,4,ok): return
	clean(c)
	start = source_entries
	c = make_case("deep")
	if not mark("G10",start,2,c.memory.invu_early_error != null and c.memory.invu_early_error.code == "INVU_ANCESTOR_DEPTH" and c.memory.invu_early_timers.empty()): return
	clean(c)
	start = source_entries
	c = make_case("normal",true)
	born = c.memory.invu_early_timers[c.timer.get_instance_id()]
	var copied = born.parent_ready.state.duplicate(true)
	var original = JSON.print(copied)
	var raw = invoke(c.memory,"_invu_raw_snapshot",[c.timer])
	var wait_bits = invoke(c.memory,"float_bits",[copied.wait_time])
	var left_bits = invoke(c.memory,"float_bits",[copied.time_left])
	ok = typeof(raw) == TYPE_DICTIONARY and primitive(raw) and typeof(copied.wait_time) == TYPE_REAL and wait_bits == "3ff4000000000000" and left_bits == "0000000000000000" and JSON.print(raw) == original
	if not mark("G11",start,7,ok): return
	clean(c)
	start = source_entries
	c = make_case()
	seed(43501)
	var expected = randi()
	seed(43501)
	invoke(c.memory,"_invu_raw_snapshot",[c.timer])
	var observed = randi()
	if not mark("G12",start,3,observed == expected): return
	clean(c)
	print(JSON.print({"status":"PASS","subcases":results.size(),"external_calls":source_entries,"results":results,"original_Game":0,"capture":0}))
func _ready():
	run_controls()
	get_tree().quit(1 if bad else 0)
