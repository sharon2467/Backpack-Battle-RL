extends SceneTree
# Prepared only: Root must authorize the sole future language process.
# Complete source scripts unchanged; no autoload/Game, no receiver stub.
const POLICY = "first-actual-idle-after-at-least-two-future-physics/1"
const CONTROL_SCHEMA = "phase390-terminal-cut-control/1"
const UNITS = [{"label":"T01","mode":"POSITIVE","base_reference":"T2","cleanup":{"idle_frame":11,"is_in_physics_frame":true,"physics_frame":101},"anchor_row":{"idle_frame":11,"kind":"physics","physics_frame":101},"future_rows":[{"idle_frame":11,"kind":"physics","physics_frame":102},{"idle_frame":11,"kind":"physics","physics_frame":103},{"idle_frame":11,"kind":"idle","physics_frame":103}],"expected":{"cleanup_anchor_pass":1,"first_eligible_idle_pass":4,"minimum_future_physics_signals":2,"observed_future_physics_signals":2},"synthetic_prestate":true},{"label":"T02","mode":"POSITIVE","base_reference":"E8","cleanup":{"idle_frame":341,"is_in_physics_frame":true,"physics_frame":2724},"anchor_row":{"idle_frame":341,"kind":"physics","physics_frame":2724},"future_rows":[{"idle_frame":341,"kind":"idle","physics_frame":2724},{"idle_frame":342,"kind":"physics","physics_frame":2725},{"idle_frame":342,"kind":"physics","physics_frame":2726},{"idle_frame":342,"kind":"physics","physics_frame":2727},{"idle_frame":342,"kind":"physics","physics_frame":2728},{"idle_frame":342,"kind":"physics","physics_frame":2729},{"idle_frame":342,"kind":"physics","physics_frame":2730},{"idle_frame":342,"kind":"physics","physics_frame":2731},{"idle_frame":342,"kind":"physics","physics_frame":2732},{"idle_frame":342,"kind":"idle","physics_frame":2732}],"expected":{"cleanup_anchor_pass":1,"first_eligible_idle_pass":11,"minimum_future_physics_signals":2,"observed_future_physics_signals":8},"synthetic_prestate":true},{"label":"T03","mode":"POSITIVE","base_reference":"G2","cleanup":{"idle_frame":11,"is_in_physics_frame":false,"physics_frame":100},"anchor_row":{"idle_frame":11,"kind":"idle","physics_frame":100},"future_rows":[{"idle_frame":12,"kind":"idle","physics_frame":100},{"idle_frame":13,"kind":"idle","physics_frame":100},{"idle_frame":14,"kind":"physics","physics_frame":101},{"idle_frame":14,"kind":"idle","physics_frame":101},{"idle_frame":15,"kind":"idle","physics_frame":101},{"idle_frame":16,"kind":"physics","physics_frame":102},{"idle_frame":16,"kind":"idle","physics_frame":102}],"expected":{"cleanup_anchor_pass":1,"first_eligible_idle_pass":8,"minimum_future_physics_signals":2,"observed_future_physics_signals":2},"synthetic_prestate":true},{"label":"T04","mode":"MISSED","base_reference":"T2","cleanup":{"idle_frame":11,"is_in_physics_frame":true,"physics_frame":101},"anchor_row":{"idle_frame":11,"kind":"physics","physics_frame":101},"future_rows":[{"idle_frame":11,"kind":"physics","physics_frame":102},{"idle_frame":11,"kind":"physics","physics_frame":103},{"idle_frame":11,"kind":"idle","physics_frame":103}],"expected":{"cleanup_anchor_pass":1,"first_eligible_idle_pass":4,"minimum_future_physics_signals":2,"observed_future_physics_signals":2},"synthetic_prestate":true},{"label":"T05","mode":"WRONG_PHASE","base_reference":"T2","cleanup":{"idle_frame":11,"is_in_physics_frame":false,"physics_frame":101},"anchor_row":{"idle_frame":11,"kind":"physics","physics_frame":101},"future_rows":[],"expected":{"cleanup_anchor_pass":1,"first_eligible_idle_pass":4,"minimum_future_physics_signals":2,"observed_future_physics_signals":2},"synthetic_prestate":true},{"label":"T06","mode":"CHECKPOINT","synthetic_prestate":true,"expected_anchor":0,"expected_terminal_cut":null}]
var report = {"schema": "phase394-tracker-language-report/1", "resource_loads": [], "cases": [], "failure": null, "completed": false, "actual_Game": false, "native_positive": false, "full12": false, "model": false, "collector_instances": 0, "detached_sink_instances": 0, "SUT_direct_method_calls": 0, "ready_or_initialize_lifecycle_calls": 0, "source_clock_writer_calls": 0, "RNG_calls_requested": 0}
var sink_script = null
var current_case = "RESOURCE_LOAD"

func persist():
 var file = File.new()
 if file.open("res://language-report.json", File.WRITE) == OK:
  file.store_string(JSON.print(report) + "\n")
  file.flush()
  file.close()

func primitive(value, depth = 0):
 if depth > 16:
  return {"type": "UNSUPPORTED_DEPTH"}
 match typeof(value):
  TYPE_NIL:
   return {"type": "null"}
  TYPE_BOOL:
   return {"type": "bool", "value": value}
  TYPE_INT:
   return {"type": "int", "decimal": str(value)}
  TYPE_REAL:
   return {"type": "real", "text": str(value)}
  TYPE_STRING:
   return {"type": "string", "value": value}
  TYPE_ARRAY:
   var values = []
   for child in value:
    values.append(primitive(child, depth + 1))
   return {"type": "array", "values": values}
  TYPE_DICTIONARY:
   var entries = []
   for key in value:
    entries.append({"key": primitive(key, depth + 1), "value": primitive(value[key], depth + 1)})
   return {"type": "dictionary", "entries": entries}
 return {"type": "UNSUPPORTED_VARIANT", "variant_type": typeof(value)}

func require(condition, reason):
 if condition:
  return true
 if report.failure == null:
  report.failure = {"case": current_case, "reason": reason}
 return false

func invoke(node, method, args = []):
 report.SUT_direct_method_calls += 1
 return node.callv(method, args)

func observe(node):
 return primitive({"failed": node.failed, "first_error": node.first_error, "count": node.source_tail_count, "anchor": node.source_tail_anchor, "last": node.source_tail_last, "latch": node.source_tail_first_idle})

func check_cut(cut, expected):
 var keys = ["schema", "terminal_policy", "cleanup_anchor_pass", "first_eligible_idle_pass", "minimum_future_physics_signals", "observed_future_physics_signals"]
 if not require(typeof(cut) == TYPE_DICTIONARY and cut.size() == keys.size(), "closed cut dictionary"):
  return false
 for key in keys:
  if not require(cut.has(key), "missing cut key:" + key):
   return false
 if not require(typeof(cut.schema) == TYPE_STRING and cut.schema == CONTROL_SCHEMA and typeof(cut.terminal_policy) == TYPE_STRING and cut.terminal_policy == POLICY, "exact cut version"):
  return false
 for key in expected:
  if not require(typeof(cut[key]) == TYPE_INT and typeof(expected[key]) == TYPE_INT and cut[key] == expected[key], "typed cut mismatch:" + key):
   return false
 return true

func one_unit(row):
 current_case = row.label
 var node = sink_script.new()
 report.detached_sink_instances += 1
 var result = {"label": row.label, "manual_SOURCE_prestate": true, "natural_HIT": false, "method_calls_before": report.SUT_direct_method_calls}
 if not require(node is Node and not node.is_inside_tree(), "detached actual sink Node required"):
  node.free()
  return false
 invoke(node, "source_tail_begin")
 if row.mode == "CHECKPOINT":
  node.source_cleanup = {"physics_frame": node.source_tail_checkpoint_p, "idle_frame": node.source_tail_checkpoint_i, "is_in_physics_frame": false}
  result.actual_sampled_checkpoint = primitive(node.source_cleanup)
  var marked = invoke(node, "source_tail_mark_cleanup")
  var cut = invoke(node, "source_terminal_cut")
  require(typeof(marked) == TYPE_BOOL and marked and typeof(node.source_tail_anchor) == TYPE_INT and node.source_tail_anchor == 0 and typeof(cut) == TYPE_NIL and not node.failed, "matching checkpoint0 SOURCE unit")
  result.mark_return = primitive(marked)
  result.cut = primitive(cut)
 else:
  # These fields are disclosed primitive unit prestate; not native clock observations.
  node.source_cleanup = row.cleanup.duplicate(true)
  node.king_clock_count = 1
  node.source_tail_last = {"kind": row.anchor_row.kind, "physics": row.anchor_row.physics_frame, "idle": row.anchor_row.idle_frame, "ordinal": 1}
  result.before_mark = observe(node)
  var marked = invoke(node, "source_tail_mark_cleanup")
  result.mark_return = primitive(marked)
  if row.mode == "WRONG_PHASE":
   var empty_cut = invoke(node, "source_terminal_cut")
   require(typeof(marked) == TYPE_BOOL and not marked and node.failed and node.first_error != null and node.first_error.code == "SOURCE_CLEANUP_PASS_ASSOCIATION" and node.source_tail_anchor == -1 and typeof(empty_cut) == TYPE_NIL, "wrong phase fails before anchor")
   result.cut = primitive(empty_cut)
  else:
   require(typeof(marked) == TYPE_BOOL and marked and node.source_tail_anchor == 1, "manual anchor accepted")
   var ordinal = 1
   result.rows = []
   for pass_row in row.future_rows:
    if report.failure != null:
     break
    ordinal += 1
    var value = invoke(node, "source_tail_note_pass", [pass_row.kind, pass_row.physics_frame, pass_row.idle_frame, ordinal])
    result.rows.append({"ordinal": ordinal, "return": primitive(value), "state": observe(node)})
    require(typeof(value) == TYPE_BOOL and value and not node.failed, "actual tracker pass accepted")
    if ordinal < row.expected.first_eligible_idle_pass:
     require(typeof(node.source_tail_first_idle) == TYPE_NIL, "no early eligible latch")
   var cut = invoke(node, "source_terminal_cut")
   result.cut = primitive(cut)
   check_cut(cut, row.expected)
   if row.mode == "MISSED" and report.failure == null:
    var before = JSON.print(observe(node))
    var old_latch = node.source_tail_first_idle.duplicate(true)
    var old_last = node.source_tail_last.duplicate(true)
    var old_count = node.source_tail_count
    var missed = invoke(node, "source_tail_note_pass", ["physics", row.cleanup.physics_frame + 3, row.cleanup.idle_frame + 1, row.expected.first_eligible_idle_pass + 1])
    result.missed_return = primitive(missed)
    result.before_missed = before
    require(typeof(missed) == TYPE_BOOL and not missed and node.failed and node.first_error != null and node.first_error.code == "SOURCE_MISSED_FIRST_ELIGIBLE_IDLE", "missed first latch rejected")
    require(JSON.print(node.source_tail_first_idle) == JSON.print(old_latch) and JSON.print(node.source_tail_last) == JSON.print(old_last) and node.source_tail_count == old_count, "rejected late pass preserves first latch/last/count")
 result.after = observe(node)
 result.method_calls_after = report.SUT_direct_method_calls
 result.pass = report.failure == null
 report.cases.append(result)
 node.free()
 persist()
 return report.failure == null

func _initialize():
 persist()
 for name in ["full-collector.gd", "full-sink.gd"]:
  var script = load("res://" + name)
  var ok = script != null and script.can_instance()
  var base = script.get_instance_base_type() if script != null else null
  report.resource_loads.append({"file": name, "loaded": script != null, "can_instance": ok, "base": base})
  persist()
  if not require(ok and base == ("SceneTree" if name == "full-collector.gd" else "Node"), "complete resource parse/load:" + name):
   persist()
   quit(2)
   return
  if name == "full-sink.gd":
   sink_script = script
 for row in UNITS:
  if not one_unit(row):
   quit(2)
   return
 if Directory.new().dir_exists("user://native-capture"):
  require(false, "unexpected production capture directory / lifecycle")
 report.completed = report.failure == null
 persist()
 print("LANGUAGE394_SOURCE_UNITS " + JSON.print({"completed": report.completed, "cases": report.cases.size(), "calls": report.SUT_direct_method_calls}))
 quit(0 if report.completed else 2)
