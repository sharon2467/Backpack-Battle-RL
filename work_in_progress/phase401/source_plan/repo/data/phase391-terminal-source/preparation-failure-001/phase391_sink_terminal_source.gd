# SOURCE template: appended primitive-only terminal tracker, not an executable project.
const TERMINAL_POLICY = "first-actual-idle-after-at-least-two-future-physics/1"
const TERMINAL_CONTROL_SCHEMA = "phase390-terminal-cut-control/1"
var source_tail_checkpoint_p = -1
var source_tail_checkpoint_i = -1
var source_tail_last = null
var source_tail_anchor = -1
var source_tail_count = 0
var source_tail_first_idle = null

func source_tail_begin():
	source_tail_checkpoint_p = Engine.get_physics_frames()
	source_tail_checkpoint_i = Engine.get_idle_frames()
	source_tail_last = null
	source_tail_anchor = -1
	source_tail_count = 0
	source_tail_first_idle = null

func source_tail_mark_cleanup():
	if source_cleanup == null or source_tail_anchor != -1 or source_tail_first_idle != null:
		return fail("SOURCE_CLEANUP_CLOCK_ASSOCIATION", "source_tail_mark_cleanup")
	if king_clock_count == 0:
		if source_tail_last != null or source_cleanup.is_in_physics_frame or source_cleanup.physics_frame != source_tail_checkpoint_p or source_cleanup.idle_frame != source_tail_checkpoint_i:
			return fail("SOURCE_CLEANUP_CHECKPOINT_ASSOCIATION", "source_tail_mark_cleanup")
		source_tail_anchor = 0
	else:
		var kind = "physics" if source_cleanup.is_in_physics_frame else "idle"
		if source_tail_last == null or source_tail_last.ordinal != king_clock_count or source_tail_last.kind != kind or source_tail_last.physics != source_cleanup.physics_frame or source_tail_last.idle != source_cleanup.idle_frame:
			return fail("SOURCE_CLEANUP_PASS_ASSOCIATION", "source_tail_mark_cleanup")
		source_tail_anchor = king_clock_count
	return true

func source_tail_note_pass(kind, physics_frame, idle_frame, ordinal):
	if source_tail_first_idle != null:
		return fail("SOURCE_MISSED_FIRST_ELIGIBLE_IDLE", "source_tail_note_pass")
	source_tail_last = {"kind": kind, "physics": physics_frame, "idle": idle_frame, "ordinal": ordinal}
	if source_cleanup == null:
		return true
	if source_tail_anchor < 0 or ordinal <= source_tail_anchor:
		return fail("SOURCE_FUTURE_PASS_ASSOCIATION", "source_tail_note_pass")
	if kind == "physics":
		if physics_frame <= source_cleanup.physics_frame:
			return fail("SOURCE_NOT_STRICTLY_FUTURE_PHYSICS", "source_tail_note_pass")
		source_tail_count += 1
	elif kind != "idle":
		return fail("SOURCE_FUTURE_PASS_KIND", "source_tail_note_pass")
	if physics_frame - source_cleanup.physics_frame != source_tail_count:
		return fail("SOURCE_FUTURE_PHYSICS_CONTINUITY", "source_tail_note_pass")
	if kind == "idle" and source_tail_count >= 2:
		source_tail_first_idle = {"ordinal": ordinal, "physics": physics_frame, "idle": idle_frame, "count": source_tail_count}
	return true

func source_terminal_cut():
	if source_tail_first_idle == null:
		return null
	return {"schema": TERMINAL_CONTROL_SCHEMA, "terminal_policy": TERMINAL_POLICY, "cleanup_anchor_pass": source_tail_anchor, "first_eligible_idle_pass": source_tail_first_idle.ordinal, "minimum_future_physics_signals": 2, "observed_future_physics_signals": source_tail_first_idle.count}

func source_terminal_current():
	if source_cleanup == null or source_tail_anchor < 0 or source_tail_first_idle == null or source_tail_last == null or Engine.is_in_physics_frame():
		return false
	if source_tail_first_idle.count < 2 or source_tail_count != source_tail_first_idle.count or source_tail_first_idle.ordinal != king_clock_count or source_tail_last.ordinal != king_clock_count or source_tail_last.kind != "idle":
		return false
	if source_tail_first_idle.physics != Engine.get_physics_frames() or source_tail_first_idle.idle != Engine.get_idle_frames() or source_tail_last.physics != source_tail_first_idle.physics or source_tail_last.idle != source_tail_first_idle.idle:
		return false
	return Engine.get_physics_frames() - source_cleanup.physics_frame == source_tail_count
