"""Godot3.6.2 source PCG integer component; custom-binary parity still pending.

PCG XSH-RR follows M. E. O'Neill's original PCG32 (Apache2.0).
Exact upstream source/license bytes are retained alongside this stage.
No float primitives, global Math RNG, binder conversion or combat admission.
"""

MASK64 = (1 << 64) - 1
MASK32 = (1 << 32) - 1
DEFAULT_SEED = 12047754176567800795
DEFAULT_SEQUENCE = 1442695040888963407
MULTIPLIER = 6364136223846793005
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1


def _u64(value):
    if type(value) is not int or not 0 <= value <= MASK64:
        raise ValueError('expected uint64 semantic integer')
    return value


class GodotPCGInteger:
    __slots__ = ('_state', '_current_seed', '_increment')

    def __init__(self, seed=DEFAULT_SEED):
        self._increment = ((DEFAULT_SEQUENCE << 1) | 1) & MASK64
        self.set_seed(seed)

    def _step(self):
        old = self._state
        self._state = (old * MULTIPLIER + self._increment) & MASK64
        shifted = (((old >> 18) ^ old) >> 27) & MASK32
        rotation = old >> 59
        return ((shifted >> rotation) | (shifted << ((-rotation) & 31))) & MASK32

    def set_seed(self, seed):
        seed = _u64(seed)
        self._current_seed = seed
        self._state = 0
        self._step()
        self._state = (self._state + seed) & MASK64
        self._step()

    def get_seed(self):
        return self._current_seed

    def set_state(self, state):
        self._state = _u64(state)

    def get_state(self):
        return self._state

    def randi(self):
        self._current_seed = self._state
        return self._step()

    def randi_range(self, from_value, to_value):
        if (type(from_value) is not int or type(to_value) is not int or
                not INT32_MIN <= from_value <= INT32_MAX or
                not INT32_MIN <= to_value <= INT32_MAX):
            raise ValueError('expected int32 endpoints')
        lower, upper = min(from_value, to_value), max(from_value, to_value)
        width = upper - lower + 1
        if width > INT32_MAX:
            raise ValueError('source signed interval arithmetic would overflow')
        return lower + self.randi() % width
