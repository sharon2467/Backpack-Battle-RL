"""Bounded synthetic/shared-helper v8 candidate, importing accepted v7 Timer.

Genuine observation/native45/seed equivalence/full engine/RL are not admitted.
"""
from .engine import CombatEngine, RuntimeDTO, validate_fixture, validate_runtime_inputs, synthetic_runtime_inputs, synthetic_king_runtime_inputs, starter_fixture
from .randomness import SeededRandom, TapeRandom
from .state import strict_json_loads
__all__=['CombatEngine','RuntimeDTO','validate_fixture','validate_runtime_inputs','synthetic_runtime_inputs','synthetic_king_runtime_inputs','starter_fixture','SeededRandom','TapeRandom','strict_json_loads']
