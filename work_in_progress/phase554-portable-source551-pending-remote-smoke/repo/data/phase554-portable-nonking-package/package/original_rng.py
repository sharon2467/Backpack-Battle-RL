"""Standalone deterministic source RNG; staged finite numeric ABI, not Game admission."""
import math
import struct
from godot_pcg_integer import GodotPCGInteger, MASK64, DEFAULT_SEQUENCE

SCHEMA = 'original-source-rng-snapshot/1'
INCREMENT = ((DEFAULT_SEQUENCE << 1) | 1) & MASK64


def _narrow(value):
    if type(value) not in (int, float) or (type(value) is int and abs(value) > 1 << 53):
        raise ValueError('finite float or exactly binary64-representable integer required')
    if not math.isfinite(value):
        raise ValueError('finite numeric domain required')
    try:
        result = struct.unpack('>f', struct.pack('>f', value))[0]
    except OverflowError as exc:
        raise ValueError('float32 binder overflow outside supported domain') from exc
    if not math.isfinite(result):
        raise ValueError('finite float32 domain required')
    return result


class OriginalRNG(GodotPCGInteger):
    __slots__ = ()

    def randf(self):
        proto = self.randi()
        if proto == 0:
            return 0.0
        significand = _narrow(self.randi() | 0x80000001)
        return _narrow(math.ldexp(significand, -32 - (32 - proto.bit_length())))

    def randf_range(self, lower, upper):
        lower, upper = _narrow(lower), _narrow(upper)
        difference = _narrow(upper - lower)
        # Check finite extrema before the first RNG draw, retaining atomic rejects.
        _narrow(_narrow(0.0 * difference) + lower)
        _narrow(_narrow(1.0 * difference) + lower)
        return _narrow(_narrow(self.randf() * difference) + lower)

    def snapshot(self):
        return dict(schema=SCHEMA, state=self._state, current_seed=self._current_seed,
                    increment=self._increment)

    @classmethod
    def from_snapshot(cls, value):
        if type(value) is not dict or set(value) != {'schema', 'state', 'current_seed', 'increment'} or value['schema'] != SCHEMA:
            raise ValueError('closed source RNG snapshot')
        if any(type(value[key]) is not int or not 0 <= value[key] <= MASK64
               for key in ('state', 'current_seed', 'increment')) or value['increment'] != INCREMENT:
            raise ValueError('snapshot integer or fixed sequence mismatch')
        result = cls(0)
        result._state = value['state']
        result._current_seed = value['current_seed']
        return result

    def copy(self):
        return type(self).from_snapshot(self.snapshot())
