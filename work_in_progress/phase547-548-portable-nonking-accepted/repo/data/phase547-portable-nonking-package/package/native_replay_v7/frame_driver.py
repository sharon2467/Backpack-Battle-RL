"""Finite synthetic frame-pass driver; no native collector or genuine admission.

Clock input carries exogenous pass deltas/counters only. End and cleanup come from
executing host rules. The collector barrier ends before the last internal idle.
"""
from dataclasses import dataclass
import json
import math
import re
import struct
from .timer_runtime import TimerRecord, TimerRuntime, UnsupportedTransition, f32, typed

SCHEMA = 'phase105-exogenous-frame-clock/1'
MAX_PASSES = 200000
MAX_JSON_BYTES = 64 * 1024 * 1024
MAX_COUNTER = (1 << 63) - 1
PHYSICS_DELTA = f32(1 / 60)


class IncompleteFrameStream(ValueError):
    """Exogenous data ended before a rule-derived terminal barrier completed."""


def _keys(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError('closed ' + label + ' keys required')


def _counter(value):
    if type(value) is not int or not 0 <= value <= MAX_COUNTER:
        raise ValueError('nonnegative bounded integer counter required')
    return value


def _real(bits):
    if type(bits) is not str or re.fullmatch('[0-9a-f]{16}', bits) is None:
        raise ValueError('BE64 lowercase hex required')
    value = struct.unpack('>d', bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError('finite BE64 required')
    return value


def _nonnegative_real(bits):
    value = _real(bits)
    if value < 0 or (value == 0 and math.copysign(1.0, value) < 0):
        raise ValueError('nonnegative clock with positive zero required')
    return value


@dataclass(frozen=True)
class FramePass:
    kind: str
    delta: float
    physics_frame: int
    idle_frame: int


@dataclass(frozen=True)
class ClockSchedule:
    physics_frame: int
    idle_frame: int
    util_frame_counter: int
    util_time: float
    util_clock_time: float
    passes: tuple


def decode_clock(carrier):
    """Validate every record before exposing immutable scalar inputs."""
    if type(carrier) is str:
        if len(carrier.encode('utf-8')) > MAX_JSON_BYTES:
            raise ValueError('clock JSON exceeds cap')
        def pairs(rows):
            result = {}
            for key, value in rows:
                if key in result:
                    raise ValueError('duplicate JSON clock key')
                result[key] = value
            return result
        def invalid(value):
            raise ValueError('nonfinite JSON number: ' + value)
        carrier = json.loads(carrier, object_pairs_hook=pairs, parse_constant=invalid)
    _keys(carrier, ('schema', 'lineage', 'environment', 'checkpoint', 'passes'), 'clock')
    if carrier['schema'] != SCHEMA or carrier['lineage'] != 'fresh_activate_idle_tail':
        raise ValueError('unsupported clock schema/lineage')
    env = carrier['environment']
    _keys(env, ('physics_fps', 'scale_bits', 'paused'), 'environment')
    if type(env['physics_fps']) is not int or env['physics_fps'] != 60:
        raise ValueError('fixed60 physics required')
    if env['scale_bits'] != '3ff0000000000000' or env['paused'] is not False:
        raise ValueError('only exact scale1/unpaused admitted')
    checkpoint = carrier['checkpoint']
    _keys(checkpoint, ('phase', 'physics_frame', 'idle_frame', 'util_frame_counter',
                       'util_time_bits', 'util_clock_time_bits'), 'checkpoint')
    if checkpoint['phase'] != 'activate_items_idle_tail':
        raise ValueError('only source activateItems idle-tail checkpoint admitted')
    physics = _counter(checkpoint['physics_frame'])
    idle = _counter(checkpoint['idle_frame'])
    util_frames = _counter(checkpoint['util_frame_counter'])
    util_time = _nonnegative_real(checkpoint['util_time_bits'])
    clock_time = _nonnegative_real(checkpoint['util_clock_time_bits'])
    rows = carrier['passes']
    if type(rows) is not list or not 1 <= len(rows) <= MAX_PASSES:
        raise ValueError('bounded nonempty pass list required')
    next_physics, next_idle = physics, idle + 1
    decoded = []
    for row in rows:
        _keys(row, ('kind', 'delta_bits', 'physics_frame', 'idle_frame'), 'frame pass')
        kind = row['kind']
        if type(kind) is not str or kind not in ('physics', 'idle'):
            raise ValueError('only physics/idle frame pass kinds')
        delta = _real(row['delta_bits'])
        if delta <= 0 or f32(delta) != delta:
            raise ValueError('positive source-promoted float32 delta required')
        if kind == 'physics':
            if delta != PHYSICS_DELTA:
                raise ValueError('non-source fixed60 physics delta')
            next_physics += 1
        p = _counter(row['physics_frame'])
        i = _counter(row['idle_frame'])
        if p != next_physics or i != next_idle:
            raise ValueError('missing/duplicate/reordered source frame counters')
        decoded.append(FramePass(kind, delta, p, i))
        if kind == 'idle':
            next_idle += 1
    return ClockSchedule(physics, idle, util_frames, util_time, clock_time, tuple(decoded))


class FrameDriver:
    """One activation checkpoint, source passes and one fixed cleanup barrier."""
    def __init__(self, runtime, carrier, util_node):
        clock = decode_clock(carrier)  # Full carrier validation before runtime mutation.
        if not isinstance(runtime, TimerRuntime) or runtime.active_copy is not None:
            raise ValueError('known non-dispatching staged runtime required')
        runtime._known(util_node)
        if (isinstance(util_node, TimerRecord) or util_node is runtime.root or not util_node.inside_tree
                or util_node.ordinary_physics or util_node.ordinary_idle
                or any((util_node, mode) in runtime.ordinary_callbacks for mode in (0, 1))):
            raise ValueError('fresh ordinary Util node required')
        for node in runtime.nodes.values():
            if isinstance(node, TimerRecord):
                runtime._mode(node.process_mode)
                if (node in runtime.started_timers or node.private_left != -1.0 or node.processing
                        or node.paused or node.autostart or node.internal_physics or node.internal_idle
                        or node.ordinary_physics or node.ordinary_idle
                        or type(node.one_shot) is not bool
                        or type(node.wait_time) is not float or not math.isfinite(node.wait_time)
                        or node.wait_time <= 0 or f32(node.wait_time) != node.wait_time):
                    raise ValueError('unknown/active/nonfresh Timer lineage')
        self.runtime = runtime
        self.clock = clock
        self.util_time = clock.util_time
        self.util_clock_time = clock.util_clock_time
        self.util_frame_counter = clock.util_frame_counter
        self.physics_frame = clock.physics_frame
        self.idle_frame = clock.idle_frame
        self.pass_index = 0
        self.phase = 'before_activation_idle_tail'
        self.activated = False
        self.ending = False
        self.cleaned = False
        self.finalized = False
        self.pending_cleanup = None
        self.physics_signals_remaining = None
        self.post_cleanup_snapshot = None
        self.final_snapshot = None
        self.pass_trace = []
        self._stepping = False
        runtime.connect_ordinary(util_node, self._util_physics, 0)
        runtime.connect_ordinary(util_node, self._util_idle, 1)
        runtime.set_ordinary_processing(util_node, True, 0)
        runtime.set_ordinary_processing(util_node, True, 1)

    def _util_physics(self, node, delta):
        self.util_time += delta
        self.util_frame_counter += 1
        if not math.isfinite(self.util_time) or self.util_frame_counter > MAX_COUNTER:
            raise ValueError('Util physics clock overflow')

    def _util_idle(self, node, delta):
        self.util_clock_time += delta
        if not math.isfinite(self.util_clock_time):
            raise ValueError('Util idle clock overflow')

    def activate(self, callback):
        if self.activated or self._stepping or not callable(callback):
            raise ValueError('one callable activation required')
        self.activated = True
        self.phase = 'activate_items_idle_tail'
        try:
            callback(self)
        finally:
            self.phase = 'idle_tail'

    def request_end(self, cleanup):
        if self.ending:
            return False
        if (not self._stepping or self.phase not in ('internal_physics', 'ordinary_physics',
                                                    'internal_idle', 'ordinary_idle')):
            raise UnsupportedTransition('end request requires an executing supported rule phase')
        if not callable(cleanup):
            raise ValueError('cleanup must be callable')
        self.ending = True
        self.pending_cleanup = cleanup
        return True

    def _flush_cleanup(self):
        if self.pending_cleanup is None:
            return
        cleanup = self.pending_cleanup
        self.pending_cleanup = None
        cleanup(self)
        self.cleaned = True
        self.physics_signals_remaining = 2
        self.post_cleanup_snapshot = self.snapshot()

    def step(self):
        if not self.activated or self.finalized or self._stepping or self.phase == 'activate_items_idle_tail':
            raise UnsupportedTransition('step requires activated unfinished non-nested driver')
        if self.pass_index == len(self.clock.passes):
            raise IncompleteFrameStream('EOF is not a rule-derived terminal barrier')
        row = self.clock.passes[self.pass_index]
        self.pass_index += 1
        self.physics_frame, self.idle_frame = row.physics_frame, row.idle_frame
        self._stepping = True
        try:
            self.phase = row.kind + '_frame_signal'
            if row.kind == 'physics':
                if self.cleaned and self.physics_signals_remaining > 0:
                    self.physics_signals_remaining -= 1
                mode = 0
            else:
                mode = 1
                self.phase = 'idle_pre_internal_flush'
                if self.cleaned and self.physics_signals_remaining == 0:
                    self.finalized = True
                    self.final_snapshot = self.snapshot()
                    self.pass_trace.append({'index': self.pass_index - 1, 'kind': row.kind,
                                            'end_phase': self.phase, 'completed': False})
                    return False
            self.phase = 'internal_' + row.kind
            self.runtime.dispatch_internal(row.delta, mode)
            self.phase = 'ordinary_' + row.kind
            self.runtime.dispatch_ordinary(row.delta, mode)
            self.phase = row.kind + '_post_ordinary_flush'
            self._flush_cleanup()
            self.phase = row.kind + '_tail'
            self.pass_trace.append({'index': self.pass_index - 1, 'kind': row.kind,
                                    'end_phase': self.phase, 'completed': True})
            return True
        finally:
            self._stepping = False

    def snapshot(self):
        timers = {}
        for role, node in self.runtime.nodes.items():
            if isinstance(node, TimerRecord):
                timers[role] = {'public': self.runtime.timer_state(node),
                                'private_left': typed(node.private_left), 'processing': typed(node.processing)}
        return {'phase': self.phase, 'passes_consumed': self.pass_index,
                'physics_frame': self.physics_frame, 'idle_frame': self.idle_frame,
                'util_time': typed(self.util_time), 'util_clock_time': typed(self.util_clock_time),
                'util_frame_counter': self.util_frame_counter, 'ending': self.ending,
                'cleaned': self.cleaned, 'finalized': self.finalized,
                'physics_signals_remaining': self.physics_signals_remaining, 'timers': timers}

    def run(self):
        while not self.finalized:
            self.step()
        if self.pass_index != len(self.clock.passes):
            raise ValueError('trailing frame records after computed terminal cutoff')
        return {'status': 'SYNTHETIC_COMPONENT_RESULT_NOT_INDEPENDENTLY_ACCEPTED',
                'post_cleanup': self.post_cleanup_snapshot, 'final': self.final_snapshot,
                'passes': self.pass_trace.copy()}
