"""Explicit synthetic v8 CLI; genuine runtime profiles remain disabled."""
import argparse
import json
from pathlib import Path
from .engine import CombatEngine, starter_fixture, validate_runtime_inputs
from .randomness import SeededRandom, TapeRandom
from .state import strict_json_loads


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture',type=Path)
    parser.add_argument('--runtime-input',type=Path,required=True)
    parser.add_argument('--random-tape',type=Path)
    parser.add_argument('--seed',type=int)
    parser.add_argument('--max-seconds',type=float,default=120.0)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    fixture=strict_json_loads(args.fixture.read_text())if args.fixture else starter_fixture()
    runtime=validate_runtime_inputs(strict_json_loads(args.runtime_input.read_text()),fixture)
    if (args.seed is None)==(args.random_tape is None):parser.error('explicitly select seed or direct primitive tape')
    rng=TapeRandom(strict_json_loads(args.random_tape.read_text()))if args.random_tape else SeededRandom(args.seed)
    result=CombatEngine(fixture,rng,runtime).run(args.max_seconds)
    if isinstance(rng,TapeRandom):rng.assert_consumed()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
