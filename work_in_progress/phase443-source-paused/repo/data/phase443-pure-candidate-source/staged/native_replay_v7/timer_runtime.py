"""Phase105 source-bound dual-process Timer subset; frozen Phase026 physics programs.

Only stdlib; no Godot, game assets, raw observations, RNG or expected schedules.
See docs/phase028_timer_kernel_implementation_spec.md for the admitted boundary.
"""
from dataclasses import dataclass, field
import hashlib
import json
import math
import re
import struct
from typing import Callable


class UnsupportedTransition(ValueError):
    """Operation outside the bounded fresh mode0/1 domain."""


@dataclass(frozen=True)
class ApiResult:
    ok: bool
    error: str | None = None


def f32(value):
    if type(value) not in (int, float):
        raise ValueError('expected finite numeric value, excluding bool')
    try:
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('nonfinite number')
        result = struct.unpack('<f', struct.pack('<f', number))[0]
    except (OverflowError, struct.error) as exc:
        raise ValueError('outside finite float32 domain') from exc
    if not math.isfinite(result):
        raise ValueError('outside finite float32 domain')
    return result


def decode_f64_le(bits):
    if type(bits) is not str or re.fullmatch('[0-9a-f]{16}', bits) is None:
        raise ValueError('expected16 lowercase binary64 LE hex digits')
    value = struct.unpack('<d', bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError('nonfinite binary64')
    return value


def typed(value):
    if value is None:
        return {'type': 'null'}
    if type(value) is bool:
        return {'type': 'bool', 'value': value}
    if type(value) is int:
        return {'type': 'int', 'decimal': str(value)}
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError('nonfinite projection')
        return {'type': 'float', 'binary64_le': struct.pack('<d', value).hex(), 'display': str(value)}
    if type(value) is str:
        return {'type': 'string', 'value': value}
    raise ValueError('unsupported primitive projection')


def _integer(value):
    if type(value) is not int or not -(1 << 31) <= value < (1 << 31):
        raise ValueError('expected signed32 integer, excluding bool')
    return value


@dataclass(eq=False)
class NodeRecord:
    role: str
    name: str
    class_name: str = 'Node'
    parent: 'NodeRecord | None' = None
    children: list = field(default_factory=list)
    inside_tree: bool = False
    process_priority: int = 0
    internal_physics: bool = False
    ordinary_physics: bool = False
    internal_idle: bool = False
    ordinary_idle: bool = False
    ready_first: bool = True
    alive: bool = True


@dataclass(eq=False)
class TimerRecord(NodeRecord):
    class_name: str = 'Timer'
    wait_time: float = 1.0
    private_left: float = -1.0
    one_shot: bool = False
    paused: bool = False
    autostart: bool = False
    process_mode: int = 1
    processing: bool = False
    timeout_handlers: list[Callable] = field(default_factory=list)


class TimerRuntime:
    """Fresh mode0/1 subset; root idle membership is explicit, synthetic by default."""
    def __init__(self, root_internal_idle=False):
        if type(root_internal_idle) is not bool:
            raise ValueError('root idle flag must be an explicit bool')
        self.root = NodeRecord('known_root', 'root', 'Viewport', inside_tree=True,
                               internal_physics=True, internal_idle=root_internal_idle, ready_first=False)
        self.nodes = {self.root.role: self.root}
        self.groups = {(mode, ordinary): {'members': [], 'changed': True}
                       for mode in (0, 1) for ordinary in (False, True)}
        self.groups[(0, False)]['members'].append(self.root)
        if root_internal_idle:
            self.groups[(1, False)]['members'].append(self.root)
        self.active_copy = None
        self.call_skip = set()
        self.ordinary_callbacks = {}
        self.started_timers = set()

    @property
    def internal_members(self):
        return self.groups[(0, False)]['members']

    @property
    def changed(self):
        return self.groups[(0, False)]['changed']

    @changed.setter
    def changed(self, value):
        self.groups[(0, False)]['changed'] = value

    @staticmethod
    def _mode(mode):
        if type(mode) is not int or mode not in (0, 1):
            raise UnsupportedTransition('only mode0 physics and mode1 idle admitted')
        return mode

    def _group(self, mode, ordinary=False):
        self._mode(mode)
        if type(ordinary) is not bool:
            raise ValueError('group kind must be bool')
        return self.groups[(mode, ordinary)]

    @staticmethod
    def _flag(mode, ordinary=False):
        return ('ordinary_' if ordinary else 'internal_') + ('physics' if mode == 0 else 'idle')

    def _known(self, node, timer=False):
        if not isinstance(node, NodeRecord) or not node.alive or self.nodes.get(node.role) is not node:
            raise ValueError('unknown or freed node identity')
        if timer and not isinstance(node, TimerRecord):
            raise ValueError('expected known Timer')
        return node

    def new_node(self, role, name, class_name='Node'):
        if type(role) is not str or not role or role in self.nodes:
            raise ValueError('duplicate or malformed stable role')
        if type(name) is not str or not name or '/' in name or ':' in name or name in ('.', '..'):
            raise ValueError('invalid bounded node name')
        if class_name != 'Node':
            raise UnsupportedTransition('only ordinary Node construction is admitted')
        node = NodeRecord(role, name)
        self.nodes[role] = node
        return node

    def new_timer(self, role, name):
        node = self.new_node(role, name)
        timer = TimerRecord(role, node.name)
        self.nodes[role] = timer
        return timer

    @staticmethod
    def _subtree(node):
        yield node
        for child in node.children:
            yield from TimerRuntime._subtree(child)

    def _register(self, node, mode=0, ordinary=False):
        group = self._group(mode, ordinary)
        if node not in group['members']:
            group['members'].append(node)
            group['changed'] = True

    def _erase(self, node, mode=0, ordinary=False):
        members = self._group(mode, ordinary)['members']
        if node in members:
            members.remove(node)

    def add_child(self, parent, node):
        self._known(parent)
        self._known(node)
        if node is self.root or node.parent is not None:
            raise ValueError('child already parented or is root')
        if parent in list(self._subtree(node)):
            raise ValueError('tree cycle')
        if any(c.name == node.name for c in parent.children):
            raise ValueError('duplicate sibling name outside bounded domain')
        if any(isinstance(n, TimerRecord) and n.autostart for n in self._subtree(node)):
            raise UnsupportedTransition('autostart lifecycle not admitted')
        parent.children.append(node)
        node.parent = parent
        if parent.inside_tree:
            for member in self._subtree(node):
                member.inside_tree = True
                for (mode, ordinary) in self.groups:
                    if getattr(member, self._flag(mode, ordinary)):
                        self._register(member, mode, ordinary)
                member.ready_first = False

    def remove_child(self, parent, node):
        self._known(parent)
        self._known(node)
        if node.parent is not parent:
            raise ValueError('not a direct child')
        for member in self._subtree(node):
            if member.inside_tree:
                if self.active_copy is not None:
                    self.call_skip.add(member)
                for mode, ordinary in self.groups:
                    self._erase(member, mode, ordinary)
            member.inside_tree = False
        parent.children.remove(node)
        node.parent = None

    def move_child(self, parent, node, index):
        self._known(parent)
        self._known(node)
        index = _integer(index)
        if node.parent is not parent or not 0 <= index <= len(parent.children):
            raise ValueError('invalid child/index')
        if index == len(parent.children):
            index -= 1
        if parent.children.index(node) == index:
            return
        parent.children.remove(node)
        parent.children.insert(index, node)
        if parent.inside_tree:
            for mode, ordinary in self.groups:
                if any(getattr(n, self._flag(mode, ordinary)) for n in self._subtree(node)):
                    self._group(mode, ordinary)['changed'] = True

    def free_node(self, node):
        self._known(node)
        if node is self.root or node.parent is not None or node.children or self.active_copy is not None:
            raise UnsupportedTransition('free requires detached childless node outside dispatch')
        if node.inside_tree or any(node in g['members'] for g in self.groups.values()):
            raise ValueError('inconsistent live membership')
        for mode in (0, 1):
            self.ordinary_callbacks.pop((node, mode), None)
        self.started_timers.discard(node)
        node.alive = False
        del self.nodes[node.role]

    def set_priority(self, node, priority):
        self._known(node)
        node.process_priority = _integer(priority)
        # Source intentionally has no same-value early return.
        if node.inside_tree:
            for mode, ordinary in self.groups:
                if getattr(node, self._flag(mode, ordinary)):
                    self._group(mode, ordinary)['changed'] = True

    def configure_timer(self, timer, one_shot, process_mode=0):
        self._known(timer, True)
        if type(one_shot) is not bool:
            raise ValueError('invalid configuration type')
        self._mode(process_mode)
        if timer.processing or timer.paused or timer.autostart:
            raise UnsupportedTransition('only inactive unpaused/autostartfalse configuration')
        if timer in self.started_timers and process_mode != timer.process_mode:
            raise UnsupportedTransition('mode changes require fresh never-started Timer')
        timer.process_mode = process_mode
        timer.one_shot = one_shot

    def connect_timeout(self, timer, callback):
        self._known(timer, True)
        if not callable(callback):
            raise ValueError('callback must be callable')
        if self.active_copy is not None:
            raise UnsupportedTransition('connection mutation during dispatch')
        timer.timeout_handlers.append(callback)

    def connect_ordinary(self, node, callback, mode):
        self._known(node)
        self._mode(mode)
        if isinstance(node, TimerRecord) or node is self.root:
            raise UnsupportedTransition('ordinary callbacks require ordinary Node')
        if not callable(callback) or (node, mode) in self.ordinary_callbacks:
            raise ValueError('one callable per ordinary node/mode required')
        if self.active_copy is not None:
            raise UnsupportedTransition('connection mutation during dispatch')
        self.ordinary_callbacks[(node, mode)] = callback

    def set_ordinary_processing(self, node, enabled, mode):
        self._known(node)
        self._mode(mode)
        if type(enabled) is not bool:
            raise ValueError('ordinary enabled must be bool')
        if isinstance(node, TimerRecord) or node is self.root:
            raise UnsupportedTransition('ordinary processing requires ordinary Node')
        if enabled and (node, mode) not in self.ordinary_callbacks:
            raise UnsupportedTransition('unknown ordinary callback')
        flag = self._flag(mode, True)
        if getattr(node, flag) == enabled:
            return
        setattr(node, flag, enabled)
        if node.inside_tree:
            if enabled:
                self._register(node, mode, True)
            else:
                self._erase(node, mode, True)

    def set_wait_time(self, timer, value):
        self._known(timer, True)
        value = f32(value)
        if value <= 0:
            return ApiResult(False, 'wait_time must be greater than zero')
        timer.wait_time = value
        return ApiResult(True)

    def start(self, timer, value=0.0):
        self._known(timer, True)
        value = f32(value)
        if not timer.inside_tree:
            return ApiResult(False, 'Timer was not added to the SceneTree')
        self._mode(timer.process_mode)
        if timer.paused or timer.autostart:
            raise UnsupportedTransition('only unpaused/autostartfalse Timer start')
        if value > 0:
            self.set_wait_time(timer, value)
        timer.private_left = timer.wait_time
        timer.processing = True
        self.started_timers.add(timer)
        setattr(timer, self._flag(timer.process_mode), True)
        self._register(timer, timer.process_mode)
        return ApiResult(True)

    def stop(self, timer):
        self._known(timer, True)
        self._mode(timer.process_mode)
        timer.private_left = -1.0
        timer.processing = False
        setattr(timer, self._flag(timer.process_mode), False)
        self._erase(timer, timer.process_mode)
        timer.autostart = False

    def time_left(self, timer):
        self._known(timer, True)
        return f32(max(timer.private_left, 0.0))

    def is_stopped(self, timer):
        return self.time_left(timer) <= 0

    @staticmethod
    def _positions(node):
        if node.parent is None:
            return (-1,)
        return TimerRuntime._positions(node.parent) + (node.parent.children.index(node),)

    @staticmethod
    def _path(node):
        if not node.inside_tree:
            return ''
        if node.parent is None:
            return '/' + node.name
        return TimerRuntime._path(node.parent) + '/' + node.name

    def node_state(self, node):
        self._known(node)
        positions = self._positions(node)
        return {'name': typed(node.name), 'class': typed(node.class_name),
                'path': typed(self._path(node)), 'index': typed(positions[-1]),
                'ancestor_positions': [typed(p) for p in positions],
                'process_priority': typed(node.process_priority), 'inside_tree': typed(node.inside_tree),
                'internal_physics': typed(node.internal_physics), 'ordinary_physics': typed(node.ordinary_physics),
                'internal_idle': typed(node.internal_idle), 'ordinary_idle': typed(node.ordinary_idle)}

    def timer_state(self, timer):
        self._known(timer, True)
        state = self.node_state(timer)
        del state['name']
        del state['class']
        return dict(state, wait_time=typed(timer.wait_time), time_left=typed(self.time_left(timer)),
                    stopped=typed(self.is_stopped(timer)), paused=typed(timer.paused),
                    one_shot=typed(timer.one_shot), autostart=typed(timer.autostart),
                    process_mode=typed(timer.process_mode))

    def get_internal_members_tree_order(self, mode=0):
        group = self._group(mode)
        if self.active_copy is not None:
            raise UnsupportedTransition('group getter during dispatch not admitted')
        if group['changed']:
            group['members'].sort(key=self._positions)
            group['changed'] = False
        return group['members'].copy()

    @staticmethod
    def _delta(delta):
        if type(delta) is not float or not math.isfinite(delta) or delta <= 0 or f32(delta) != delta:
            raise ValueError('delta must be positive promoted float32')

    def _dispatch(self, delta, mode, ordinary):
        group = self._group(mode, ordinary)
        self._delta(delta)
        if self.active_copy is not None:
            raise UnsupportedTransition('nested dispatch not admitted')
        flag = self._flag(mode, ordinary)
        # Reject malformed active configuration before sorting/countdown mutation.
        for node in group['members']:
            self._known(node)
            if node is self.root:
                continue
            if ordinary:
                if (node, mode) not in self.ordinary_callbacks:
                    raise UnsupportedTransition('unknown ordinary callback')
            elif (not isinstance(node, TimerRecord) or node.process_mode != mode
                  or node.paused or node.autostart or not node.processing):
                raise UnsupportedTransition('unsupported active Timer configuration')
        if group['changed']:
            group['members'].sort(key=lambda n: (n.process_priority, self._positions(n)))
            group['changed'] = False
        self.active_copy = group['members'].copy()
        self.call_skip.clear()
        try:
            for node in self.active_copy:
                if not node.alive or not node.inside_tree or not getattr(node, flag) or node in self.call_skip:
                    continue
                if node is self.root:
                    continue
                if ordinary:
                    self.ordinary_callbacks[(node, mode)](node, delta)
                else:
                    self._known(node, True)
                    if node.process_mode != mode or node.paused or not node.processing:
                        raise UnsupportedTransition('unsupported active Timer configuration')
                    node.private_left -= delta
                    if node.private_left < 0:
                        if node.one_shot:
                            self.stop(node)
                        else:
                            node.private_left += node.wait_time
                        for callback in tuple(node.timeout_handlers):
                            callback(node)
        finally:
            self.active_copy = None
            self.call_skip.clear()

    def dispatch_internal(self, delta, mode=0):
        self._dispatch(delta, mode, False)

    def dispatch_ordinary(self, delta, mode):
        self._dispatch(delta, mode, True)

D = f32(1 / 60)
D16 = f32(D * 16)


# These drivers transcribe the frozen GDScript fixed programs, not native rows.
class _FixedProgram:
    def __init__(self, config, schema):
        if type(config) is not dict or config.get('schema') != schema:
            raise ValueError('wrong fixed-program schema')
        # Reject bool/int aliases even inside nested fixed configuration records.
        self.config = json.loads(json.dumps(config, allow_nan=False))
        self.runtime = TimerRuntime()
        self.controller = self.runtime.new_node('controller', 'ProbeController')
        self.controller.process_priority = config.get('controller_priority', 0)
        self.controller.ordinary_physics = True
        self.runtime.add_child(self.runtime.root, self.controller)
        self.numbers = {k: decode_f64_le(v) for k, v in config['numbers'].items()}
        if self.numbers['clock_initial'] != 16.0 or self.numbers['D'] != D:
            raise ValueError('unexpected sealed clock/delta')
        self.clock = self.numbers['clock_initial']
        self.tick = -1
        self.rows = []
        self.timers = {}
        self.timer_order = []
        self.branch = None
        self.active = 'none'
        self.errors = []

    def states(self, numeric=False):
        key = 'case_id' if numeric else 'timer_id'
        return [{key: name, 'state': self.runtime.timer_state(self.timers[name])} for name in self.timer_order]

    def record(self, phase, label, who, payload, mode):
        row = {'sequence': typed(len(self.rows)), 'tick': typed(self.tick), 'phase': phase,
               'label': label, 'clock': typed(self.clock), 'payload': payload}
        if mode == 'numeric':
            row['case_id'] = who
        else:
            row['known_root'] = self.runtime.node_state(self.runtime.root)
            row['controller'] = self.runtime.node_state(self.controller)
            row['phase_id' if mode == 'purity' else 'case_id'] = self.active
            row['case_id' if mode == 'purity' else 'timer_id'] = who
        self.rows.append(row)

    def clear(self, mode):
        rt = self.runtime
        for name in self.timer_order:
            timer = self.timers[name]
            self.record('ordinary_action', 'stop_before' if mode == 'purity' else 'cleanup_stop_before', name,
                        {'state': rt.timer_state(timer)}, mode)
            rt.stop(timer)
            self.record('ordinary_action', 'stop_after' if mode == 'purity' else 'cleanup_stop_after', name,
                        {'state': rt.timer_state(timer)}, mode)
            rt.remove_child(self.branch, timer)
            self.record('ordinary_action', 'timer_removed' if mode == 'purity' else 'cleanup_timer_removed', name,
                        {'state': rt.timer_state(timer)}, mode)
            rt.free_node(timer)
        self.timers.clear()
        self.timer_order.clear()
        rt.remove_child(self.controller, self.branch)
        self.record('ordinary_action', 'branch_removed' if mode == 'purity' else 'cleanup_branch_removed', 'branch',
                    {'branch': rt.node_state(self.branch)}, mode)
        rt.free_node(self.branch)
        self.branch = None
        self.record('ordinary_action', 'phase_cleared' if mode == 'purity' else 'case_cleared', 'branch', {'timers': self.states()}, mode)
        self.active = 'none'

    def action_start(self, name, label, phase, mode, argument=D):
        rt = self.runtime
        payload = lambda: {'argument': typed(argument), 'state': rt.timer_state(self.timers[name])}
        self.record(phase, label + '_before', name, payload(), mode)
        result = rt.start(self.timers[name], argument)
        if not result.ok:
            raise ValueError(result.error)
        self.record(phase, label + '_after', name, payload(), mode)

    def action_stop(self, name, label, phase, mode):
        rt = self.runtime
        self.record(phase, label + '_before', name, {'state': rt.timer_state(self.timers[name])}, mode)
        rt.stop(self.timers[name])
        self.record(phase, label + '_after', name, {'state': rt.timer_state(self.timers[name])}, mode)


def _exact_shape(actual, expected):
    """Strict schema/type check against a source-written fixed configuration."""
    if type(actual) is not type(expected):
        raise ValueError('fixed input type mismatch')
    if isinstance(expected, dict):
        if actual.keys() != expected.keys():
            raise ValueError('fixed input keys differ')
        for key in expected:
            _exact_shape(actual[key], expected[key])
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise ValueError('fixed input list length differs')
        for a, e in zip(actual, expected):
            _exact_shape(a, e)
    elif actual != expected:
        raise ValueError('fixed input value differs')

_FIXED_INPUT_SHA = {
    'fresh-timer-numeric-input/1': '00e0769b1457a226d9dbf904808ab139c927ae836820a5fc0426b940771683ef',
    'timer-observer-purity-input/1': '956f2fcd81be0103dc9281122c72672afb17afe15c7a2ddc58121795fcba587d',
    'timer-snapshot-mutation-input/1': 'edca65ef7ff9ae9470f6ebda535a95fe388e0c2d8e792ff70eb7c397f8ea17ef',
}


def _fixed_config(config, schema):
    if type(config) is not dict or config.get('schema') != schema:
        raise ValueError('wrong fixed input schema')
    encoded = json.dumps(config, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    if hashlib.sha256(encoded).hexdigest() != _FIXED_INPUT_SHA[schema]:
        raise ValueError('fixed source input content/type differs')
    return config


def _result(program, schema, **fields):
    # Host engine/version/raw-byte input SHA are genuine native provenance, not
    # synthetic fields. The caller validates them separately against old pins.
    return dict(schema=schema, status='SYNTHETIC_KERNEL_PREDICTION_NOT_ACCEPTED',
                physics_fps=typed(program.config['physics_fps']), logical_tick=typed(program.tick),
                synthetic_clock=typed(program.clock), rows=program.rows, errors=program.errors, **fields)


def run_numeric_program(config, transition_old_d_prefix):
    _fixed_config(config, 'fresh-timer-numeric-input/1')
    if type(transition_old_d_prefix) is not int or not 0 <= transition_old_d_prefix <= 7:
        raise ValueError('source-fixed prefix must be integer0..7')
    p = _FixedProgram(config, 'fresh-timer-numeric-input/1')
    rt = p.runtime
    cases = {r['case_id']: r for r in config['cases']}
    timeouts = {name: 0 for name in cases}
    restarts = {name: 0 for name in cases}
    delta = D

    def record(phase, label, name, payload):
        p.record(phase, label, name, payload, 'numeric')

    def start(name, argument_name, label):
        argument = p.numbers[argument_name]
        p.action_start(name, label, 'internal_signal' if label == 'timeout_restart' else 'ordinary_action', 'numeric', argument)

    def stop(name, label):
        p.action_stop(name, label, 'ordinary_action', 'numeric')

    def on_timeout(timer):
        name = timer.name
        timeouts[name] += 1
        record('internal_signal', 'timeout_before_response', name,
               {'delta': typed(delta), 'timeout_count': typed(timeouts[name]), 'state': rt.timer_state(timer)})
        if restarts[name] < cases[name]['restartCount']:
            restarts[name] += 1
            start(name, cases[name]['start_argument'], 'timeout_restart')
        record('internal_signal', 'timeout_after_response', name,
               {'restart_count': typed(restarts[name]), 'state': rt.timer_state(timer)})

    def make(name):
        timer = rt.new_timer(name, name)
        record('bootstrap', 'constructor_default', name, {'state': rt.timer_state(timer)})
        rt.add_child(p.controller, timer)
        record('bootstrap', 'in_tree_default', name, {'state': rt.timer_state(timer)})
        rt.configure_timer(timer, not cases[name]['repeat'])
        rt.connect_timeout(timer, on_timeout)
        p.timers[name] = timer
        p.timer_order.append(name)
        record('bootstrap', 'configured', name, {'state': rt.timer_state(timer)})

    def clear(label):
        for name in p.timer_order:
            stop(name, label)
            timer = p.timers[name]
            rt.remove_child(p.controller, timer)
            record('ordinary_action', label + '_removed', name, {'state': rt.timer_state(timer)})
            rt.free_node(timer)
        p.timers.clear()
        p.timer_order.clear()

    for tick in range(50):
        p.tick = tick
        delta = D if tick <= 24 or 25 <= tick < 25 + transition_old_d_prefix else D16
        record('pre_internal', 'physics_frame', 'controller', {'timers': p.states(True)})
        rt.dispatch_internal(delta)
        record('ordinary', 'ordinary_enter', 'controller', {'delta': typed(delta), 'timers': p.states(True)})
        if tick == 0:
            outside = rt.new_timer('outside_start_rejection', 'outside_start_rejection')
            record('bootstrap', 'constructor_default', outside.name, {'state': rt.timer_state(outside)})
            record('bootstrap', 'outside_start_before', outside.name, {'argument': typed(p.numbers['two']), 'state': rt.timer_state(outside)})
            result = rt.start(outside, p.numbers['two'])
            if result.ok:
                raise AssertionError('outside-tree guard failed')
            record('bootstrap', 'outside_start_caller_continued', outside.name, {'state': rt.timer_state(outside)})
            rt.free_node(outside)
            for name in config['conventional_order']:
                make(name)
            start('wait_reuse', 'eighth', 'reuse_positive')
            stop('wait_reuse', 'reuse_stop_positive')
            start('wait_reuse', 'zero', 'reuse_zero')
            stop('wait_reuse', 'reuse_stop_zero')
            start('wait_reuse', 'negative_one', 'reuse_negative')
            stop('wait_reuse', 'reuse_stop_negative')
            for name in config['conventional_order']:
                if name != 'wait_reuse':
                    start(name, cases[name]['start_argument'], 'initial_start')
        if tick == 24:
            clear('conventional_cleanup')
            record('ordinary_action', 'scale_changed', 'controller', {'time_scale': typed(p.numbers['scale_sixteen'])})
        if tick == 40:
            make('repeat_large_125')
            start('repeat_large_125', 'eighth', 'scaled_start')
        if tick == 48:
            clear('scaled_cleanup')
        p.clock += delta
        record('ordinary', 'ordinary_exit', 'controller', {'delta': typed(delta), 'timers': p.states(True)})
    return _result(p, 'fresh-timer-numeric-observation/1', case_ids=list(cases), timeout_counts=timeouts,
                   restart_counts=restarts, limitations=['public states only; private countdown not observed',
                   'synthetic clock is not game Util.time', 'no Timer scheduling, Buff, item45, full engine or RL admission'])


def run_numeric_alternatives(config):
    return {'numeric_prefix_' + str(prefix): run_numeric_program(config, prefix) for prefix in range(8)}


def run_purity_program(config):
    _fixed_config(config, 'timer-observer-purity-input/1')
    p = _FixedProgram(config, 'timer-observer-purity-input/1')
    rt = p.runtime
    orders = {name: [] for name in config['phases']}
    query_count = 0

    def record(phase, label, name, payload):
        p.record(phase, label, name, payload, 'purity')

    def on_timeout(timer):
        orders[p.active].append(timer.name)
        record('internal_signal', 'timeout', timer.name,
               {'delta': typed(D), 'state': rt.timer_state(timer), 'timeout_ordinal': typed(len(orders[p.active]))})

    def make(phase):
        p.active = phase
        p.branch = rt.new_node('branch/' + phase, config['branch_name'])
        rt.add_child(p.controller, p.branch)
        record('ordinary_action', 'branch_created', 'branch', {'branch': rt.node_state(p.branch)})
        for row in config['timers']:
            name = row['name']
            timer = rt.new_timer(phase + '/' + name, name)
            record('ordinary_action', 'constructor_default', name, {'state': rt.timer_state(timer)})
            rt.set_priority(timer, row['priority'])
            rt.add_child(p.branch, timer)
            rt.configure_timer(timer, True)
            rt.connect_timeout(timer, on_timeout)
            p.timers[name] = timer
            p.timer_order.append(name)
            record('ordinary_action', 'configured', name, {'state': rt.timer_state(timer)})
        for name in p.timer_order:
            p.action_start(name, 'start', 'ordinary_action', 'purity')
        record('ordinary_action', 'phase_armed', 'branch', {'branch': rt.node_state(p.branch), 'timers': p.states()})

    def identity(node):
        fixture_id = 'known_root' if node is rt.root else next((name for name in p.timer_order if p.timers[name] is node), 'unknown')
        return {'fixture_id': fixture_id, 'node': rt.node_state(node)}

    for tick in range(8):
        p.tick = tick
        record('pre_internal', 'physics_frame', 'controller', {'timers': p.states()})
        if tick == 3:
            record('pre_internal', 'group_getter_before', 'controller', {'timers': p.states()})
            members = rt.get_internal_members_tree_order()
            query_count += 1
            projections = [identity(n) for n in members]
            if any(row['fixture_id'] == 'unknown' for row in projections) or len(members) != 4:
                raise ValueError('unknown or missing group member')
            record('pre_internal', 'group_getter_after', 'controller',
                   {'group_name': typed(config['group_name']), 'members': projections, 'query_count': typed(query_count), 'timers': p.states()})
        if tick == 5:
            projections = [identity(n) for n in p.branch.children]
            record('pre_internal', 'pure_tree_traversal', 'branch', {'branch': rt.node_state(p.branch), 'children': projections, 'timers': p.states()})
        rt.dispatch_internal(D)
        record('ordinary', 'ordinary_enter', 'controller', {'delta': typed(D), 'timers': p.states()})
        if tick in (0, 2, 4):
            if tick:
                p.clear('purity')
            make(config['phases'][tick // 2])
        if tick == 6:
            p.clear('purity')
        p.clock += D
        record('ordinary', 'ordinary_exit', 'controller', {'delta': typed(D), 'timers': p.states()})
    return _result(p, 'timer-observer-purity-observation/1', phase_ids=config['phases'].copy(),
                   timeout_orders=orders, group_query_count=typed(query_count), limitations=[
                   'public states only; private countdown not observed', 'synthetic clock is not game Util.time',
                   'only the fixed bare/getter/pure observer matrix; no broader scheduler, Buff, item45 or RL admission'])


def run_snapshot_program(config):
    _fixed_config(config, 'timer-snapshot-mutation-input/1')
    p = _FixedProgram(config, 'timer-snapshot-mutation-input/1')
    rt = p.runtime
    cases = {row['case_id']: row for row in config['cases']}
    responses = {name: 0 for name in cases}
    timeouts = {name: [] for name in cases}
    budget = 0
    current = None

    def record(phase, label, name, payload):
        p.record(phase, label, name, payload, 'snapshot')

    def start(name, label, phase='internal_signal'):
        p.action_start(name, label, phase, 'snapshot')

    def stop(name, label, phase='internal_signal'):
        p.action_stop(name, label, phase, 'snapshot')

    def apply_response():
        response = current['response']
        if response == 'start_absent_restart_copied':
            start('C', 'response_start_C')
            start('B', 'response_restart_B')
        elif response == 'stop_copied':
            stop('B', 'response_stop_B')
        elif response == 'stop_start_copied':
            stop('B', 'response_stop_B')
            start('B', 'response_start_B')
        elif response == 'remove_readd_same':
            b = p.timers['B']
            def bstate():
                return {'state': rt.timer_state(b), 'same_known_B': typed(b is p.timers['B'])}
            record('internal_signal', 'response_remove_B_before', 'B', bstate())
            rt.remove_child(p.branch, b)
            record('internal_signal', 'response_remove_B_after', 'B', bstate())
            record('internal_signal', 'response_readd_B_before', 'B', bstate())
            rt.add_child(p.branch, b)
            record('internal_signal', 'response_readd_B_after', 'B', bstate())
            start('B', 'response_start_B')
        elif response == 'change_priority':
            for change in current['priority_changes']:
                payload = lambda: {'new_priority': typed(change['priority']), 'timers': p.states()}
                record('internal_signal', 'response_priority_before', change['name'], payload())
                rt.set_priority(p.timers[change['name']], change['priority'])
                record('internal_signal', 'response_priority_after', change['name'], payload())
        elif response == 'move_sibling':
            payload = lambda: {'new_index': typed(current['move_index']), 'timers': p.states()}
            record('internal_signal', 'response_move_before', 'C', payload())
            rt.move_child(p.branch, p.timers['C'], current['move_index'])
            record('internal_signal', 'response_move_after', 'C', payload())
        else:
            raise ValueError('unknown response')

    def on_timeout(timer):
        nonlocal budget
        name = timer.name
        timeouts[p.active].append({'name': name, 'tick': typed(p.tick)})
        record('internal_signal', 'timeout_enter', name,
               {'delta': typed(D), 'state': rt.timer_state(timer), 'response_budget': typed(budget)})
        if name == 'A' and budget > 0:
            record('internal_signal', 'response_before', name, {'timers': p.states(), 'response_budget': typed(budget)})
            budget -= 1
            responses[p.active] += 1
            apply_response()
            record('internal_signal', 'response_after', name, {'timers': p.states(), 'response_budget': typed(budget)})
        record('internal_signal', 'timeout_exit', name, {'state': rt.timer_state(timer), 'response_budget': typed(budget)})

    def make(name):
        nonlocal budget, current
        p.active = name
        current = cases[name]
        budget = current['response_budget']
        p.branch = rt.new_node('branch/' + name, config['branch_name'])
        rt.add_child(p.controller, p.branch)
        record('ordinary_action', 'branch_created', 'branch', {'branch': rt.node_state(p.branch)})
        for row in current['timers']:
            timer = rt.new_timer(name + '/' + row['name'], row['name'])
            record('ordinary_action', 'constructor_default', row['name'], {'state': rt.timer_state(timer)})
            rt.set_priority(timer, row['priority'])
            rt.add_child(p.branch, timer)
            rt.configure_timer(timer, not current['repeat'])
            rt.connect_timeout(timer, on_timeout)
            p.timers[timer.name] = timer
            p.timer_order.append(timer.name)
            record('ordinary_action', 'configured', timer.name, {'state': rt.timer_state(timer)})
        for row in current['timers']:
            if row['start_at_arm']:
                start(row['name'], 'initial_start', 'ordinary_action')
        record('ordinary_action', 'case_armed', 'branch', {'branch': rt.node_state(p.branch), 'timers': p.states()})

    for tick in range(37):
        p.tick = tick
        record('pre_internal', 'physics_frame', 'controller', {'timers': p.states()})
        rt.dispatch_internal(D)
        record('ordinary', 'ordinary_enter', 'controller', {'delta': typed(D), 'timers': p.states()})
        for row in config['cases']:
            if tick == row['arm_tick']:
                make(row['case_id'])
            if tick == row['cleanup_tick']:
                p.clear('snapshot')
                current = None
        p.clock += D
        record('ordinary', 'ordinary_exit', 'controller', {'delta': typed(D), 'timers': p.states()})
    return _result(p, 'timer-snapshot-mutation-observation/1', case_ids=list(cases), timeout_records=timeouts,
                   response_counts=responses, limitations=['public states only; private countdown not observed',
                   'synthetic clock is not game Util.time',
                   'only the fixed six-case snapshot/mutation matrix; no pause, deferred, Buff, item45 or RL admission'])
