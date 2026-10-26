"""New terminal helpers appended to the frozen typed schema; expected/control only."""

TERMINAL_POLICY = 'first-actual-idle-after-at-least-two-future-physics/1'
TERMINAL_ENDPOINT_SCHEMA = 'phase390-first-eligible-idle-endpoint/1'
TERMINAL_CONTROL_SCHEMA = 'phase390-terminal-cut-control/1'
TERMINAL_CUT_KEYS = ('schema', 'terminal_policy', 'cleanup_anchor_pass', 'first_eligible_idle_pass',
                     'minimum_future_physics_signals', 'observed_future_physics_signals')
TERMINAL_ENDPOINT_KEYS = ('schema', 'terminal_policy', 'phase', 'physics_frame', 'idle_frame', 'passes',
                         'minimum_future_physics_signals', 'observed_future_physics_signals',
                         'cleanup_anchor_pass', 'first_eligible_idle_pass', 'fx_exact_comparison')
TERMINAL_RECEIPT_KEYS = ('source_window_complete', 'failed', 'clock_closed', 'ui_closed', 'cleanup',
                        'clock_passes', 'native_capture_accepted', 'collector_archive_pending', 'terminal_cut')
TERMINAL_DISPATCH_KEYS = ('phase', 'dispatching', 'emit_count', 'receiver_available', 'receiver_id',
                        'physics', 'idle', 'ack', 'script_emit_return', 'script_emit_return_observed',
                        'native_emit_error_available', 'native_emit_error', 'finish_return', 'failed',
                        'closed', 'complete', 'clock_closed', 'ui_closed', 'first_error', 'ready_connect',
                        'diagnostic_error', 'terminal_cut')


def _terminal_clock_rows(clock):
    # The public helper also rejects a manually built, type-contaminated ClockSchedule.
    if type(clock) is not ClockSchedule or type(clock.passes) is not tuple or not 1 <= len(clock.passes) <= MAX_PASSES:
        raise ValueError('actual bounded decoded clock required')
    p, i = _counter(clock.physics_frame), _counter(clock.idle_frame) + 1
    for row in clock.passes:
        if type(row) is not FramePass or type(row.kind) is not str or row.kind not in ('physics', 'idle'):
            raise ValueError('terminal actual frame row kind')
        if type(row.delta) is not float or not math.isfinite(row.delta) or row.delta <= 0 or f32(row.delta) != row.delta:
            raise ValueError('terminal actual frame delta')
        if row.kind == 'physics':
            if row.delta != PHYSICS_DELTA:
                raise ValueError('terminal actual fixed60 delta')
            p += 1
        if (_counter(row.physics_frame), _counter(row.idle_frame)) != (p, i):
            raise ValueError('terminal missing/duplicate/reordered actual clock')
        if row.kind == 'idle':
            i += 1
    return clock.passes


def validate_terminal_evidence(endpoint, clock, cleanup):
    """Expected/control proof only; never a model cleanup or stop command."""
    exact(endpoint, TERMINAL_ENDPOINT_KEYS)
    if (endpoint['schema'] != TERMINAL_ENDPOINT_SCHEMA or endpoint['terminal_policy'] != TERMINAL_POLICY
            or endpoint['phase'] != 'idle_pre_internal_flush'
            or endpoint['fx_exact_comparison'] != 'NOT_EVALUATED_REQUIRES_MODEL'):
        raise ValueError('new exact terminal policy/endpoint required')
    for key in ('physics_frame', 'idle_frame', 'passes', 'cleanup_anchor_pass', 'first_eligible_idle_pass',
                'minimum_future_physics_signals', 'observed_future_physics_signals'):
        _counter(endpoint[key])
    if endpoint['minimum_future_physics_signals'] != 2 or endpoint['observed_future_physics_signals'] < 2:
        raise ValueError('minimum2 and actual future count required')
    rows = _terminal_clock_rows(clock)
    exact(cleanup, ('physics_frame', 'idle_frame', 'is_in_physics_frame'))
    cp, ci = _counter(cleanup['physics_frame']), _counter(cleanup['idle_frame'])
    if type(cleanup['is_in_physics_frame']) is not bool:
        raise ValueError('actual cleanup phase BOOL')
    kind = 'physics' if cleanup['is_in_physics_frame'] else 'idle'
    anchors = [index + 1 for index, row in enumerate(rows)
               if (row.kind, row.physics_frame, row.idle_frame) == (kind, cp, ci)]
    if len(anchors) == 1:
        anchor = anchors[0]
    elif not anchors and kind == 'idle' and (cp, ci) == (clock.physics_frame, clock.idle_frame):
        anchor = 0
    else:
        raise ValueError('unique actual cleanup row/checkpoint association')
    count = 0
    candidate = None
    for index in range(anchor, len(rows)):
        row = rows[index]
        if row.kind == 'physics':
            if row.physics_frame <= cp:
                raise ValueError('only strictly future physics signals count')
            count += 1
        if row.physics_frame - cp != count:
            raise ValueError('cleanup/future clock continuity')
        if row.kind == 'idle' and count >= 2:
            candidate = index + 1
            break
    if candidate is None:
        raise ValueError('EOF before first actual eligible idle')
    if candidate != len(rows):
        raise ValueError('missed first eligible idle or trailing clock records')
    last = rows[-1]
    if (endpoint['physics_frame'], endpoint['idle_frame'], endpoint['passes'], endpoint['cleanup_anchor_pass'],
            endpoint['first_eligible_idle_pass'], endpoint['observed_future_physics_signals']) != (
            last.physics_frame, last.idle_frame, len(rows), anchor, candidate, count):
        raise ValueError('actual first-idle frames/ordinals/count mismatch')
    return dict(schema='phase391-expected-terminal-proof/1', status='EXPECTED_ONLY_FIRST_ACTUAL_ELIGIBLE_IDLE',
                terminal_policy=TERMINAL_POLICY, cleanup_anchor_pass=anchor, first_eligible_idle_pass=candidate,
                minimum_future_physics_signals=2, observed_future_physics_signals=count,
                physics_frame=last.physics_frame, idle_frame=last.idle_frame, passes=len(rows),
                cleanup=dict(cleanup), no_model_stop_command=True)


def _terminal_cut_matches(value, proof):
    exact(value, TERMINAL_CUT_KEYS)
    if value['schema'] != TERMINAL_CONTROL_SCHEMA or value['terminal_policy'] != TERMINAL_POLICY:
        raise ValueError('terminal receipt/control policy version')
    for key in TERMINAL_CUT_KEYS[2:]:
        if _counter(value[key]) != proof[key]:
            raise ValueError('terminal receipt/control count/ordinal mismatch')


def validate_terminal_receipt(endpoint, clock, receipt, control, validation):
    """Public expected/control join used directly by the actual new host."""
    exact(receipt, TERMINAL_RECEIPT_KEYS)
    for key in ('source_window_complete', 'clock_closed', 'ui_closed', 'collector_archive_pending'):
        if receipt[key] is not True:
            raise ValueError('complete actual source receipt required')
    if receipt['failed'] is not False or receipt['native_capture_accepted'] is not False:
        raise ValueError('receipt failure or self native acceptance')
    proof = validate_terminal_evidence(endpoint, clock, receipt['cleanup'])
    if _counter(receipt['clock_passes']) != proof['passes']:
        raise ValueError('receipt actual clock pass count')
    _terminal_cut_matches(receipt['terminal_cut'], proof)
    exact(control, TERMINAL_DISPATCH_KEYS)
    if control['phase'] != 'FINALIZED' or _counter(control['emit_count']) != 1:
        raise ValueError('actual once FINALIZED dispatch required')
    for key in ('receiver_available', 'script_emit_return_observed', 'finish_return', 'closed', 'complete', 'clock_closed', 'ui_closed'):
        if control[key] is not True:
            raise ValueError('actual terminal BOOL evidence required')
    for key in ('dispatching', 'native_emit_error_available', 'failed'):
        if control[key] is not False:
            raise ValueError('dispatch/native Error/failure evidence')
    for key in ('script_emit_return', 'native_emit_error', 'first_error', 'diagnostic_error'):
        if control[key] is not None:
            raise ValueError('actual NIL/unavailable/no-error evidence')
    native = control['receiver_id']
    if type(native) is not str or re.fullmatch('[1-9][0-9]*', native) is None or int(native) > MAX_COUNTER:
        raise ValueError('actual receiver decimal native identity')
    if (_counter(control['physics']), _counter(control['idle'])) != (proof['physics_frame'], proof['idle_frame']):
        raise ValueError('same actual terminal dispatch frames')
    exact(control['ready_connect'], ('physics', 'idle'))
    if any(type(control['ready_connect'][key]) is not int or control['ready_connect'][key] != 0 for key in ('physics', 'idle')):
        raise ValueError('actual SceneTree connection Error values')
    exact(control['ack'], ('receiver_id', 'physics', 'idle', 'serial'))
    ack = control['ack']
    if (ack['receiver_id'] != native or (_counter(ack['physics']), _counter(ack['idle']), _counter(ack['serial']))
            != (proof['physics_frame'], proof['idle_frame'], 1)):
        raise ValueError('exact actual acknowledgement identity')
    _terminal_cut_matches(control['terminal_cut'], proof)
    # Other collector business fields remain opaque here and are not promoted to input.
    if type(validation) is not dict or not {'cut', 'full_snapshot_reads', 'terminal_cut', 'native_checks_pass', 'end_barrier'} <= set(validation):
        raise ValueError('actual collector terminal control subset')
    exact(validation['cut'], ('physics', 'idle', 'preinternal'))
    cut = validation['cut']
    if ((_counter(cut['physics']), _counter(cut['idle'])) != (proof['physics_frame'], proof['idle_frame'])
            or cut['preinternal'] is not True or type(validation['full_snapshot_reads']) is not int
            or validation['full_snapshot_reads'] != 1 or validation['native_checks_pass'] is not True
            or validation['end_barrier'] is not True):
        raise ValueError('one same-frame preinternal readonly collector cut')
    _terminal_cut_matches(validation['terminal_cut'], proof)
    return proof


def validate_terminal_diagnostics(rows):
    """Validate control headers/milestones only; other payloads are opaque."""
    if type(rows) is not list or not 1 <= len(rows) <= 64:
        raise ValueError('bounded actual source-control rows')
    keys = ('schema', 'control_sequence', 'site', 'reason', 'physics', 'idle', 'in_physics',
            'observer_sequence', 'ui_sequence', 'clock_passes', 'payload')
    milestones = []
    for index, row in enumerate(rows):
        exact(row, keys)
        if row['schema'] != 'phase391-source-control/1' or _counter(row['control_sequence']) != index:
            raise ValueError('actual diagnostic version/physical sequence')
        for key in ('physics', 'idle', 'observer_sequence', 'ui_sequence', 'clock_passes'):
            _counter(row[key])
        if type(row['in_physics']) is not bool or type(row['site']) is not str or type(row['reason']) is not str:
            raise ValueError('diagnostic primitive control header')
        if row['site'] == 'emit_source_idle_cut_once' and row['reason'] in ('EMITTING', 'RETURNED_ACK_CHECKED', 'FINALIZED'):
            milestones.append(row)
    if [row['reason'] for row in milestones] != ['EMITTING', 'RETURNED_ACK_CHECKED', 'FINALIZED'] or milestones[-1] is not rows[-1]:
        raise ValueError('unique ordered terminal milestones and final EOF required')
    final = rows[-1]
    exact(final['payload'], ('control',))
    control = final['payload']['control']
    exact(control, TERMINAL_DISPATCH_KEYS)
    if final['in_physics'] is not False or (final['physics'], final['idle']) != (control['physics'], control['idle']):
        raise ValueError('actual idle FINALIZED control frame')
    # Intermediate milestone contexts are SOURCE-control evidence, not business state.
    for row, phase in zip(milestones[:2], ('EMITTING', 'RETURNED')):
        payload = row['payload']
        exact(payload, ('control', 'private_connections', 'tree_connections') if phase == 'EMITTING' else ('control',))
        value = payload['control']
        exact(value, TERMINAL_DISPATCH_KEYS)
        if value['phase'] != phase or value['emit_count'] != 1 or type(value['emit_count']) is not int:
            raise ValueError('actual synchronous emission phase')
        if (row['physics'], row['idle'], value['physics'], value['idle'], value['receiver_id'], value['terminal_cut']) != (
                final['physics'], final['idle'], control['physics'], control['idle'], control['receiver_id'], control['terminal_cut']):
            raise ValueError('same-stack milestone identities')
        if value['native_emit_error_available'] is not False or value['native_emit_error'] is not None or value['script_emit_return'] is not None:
            raise ValueError('actual script NIL, native Error unavailable')
        if phase == 'EMITTING':
            if value['dispatching'] is not True or value['script_emit_return_observed'] is not False or value['ack'] is not None:
                raise ValueError('precall synchronous bracket')
        elif value['dispatching'] is not False or value['script_emit_return_observed'] is not True or value['ack'] != control['ack']:
            raise ValueError('returned actual NIL/ack bracket')
    return control
