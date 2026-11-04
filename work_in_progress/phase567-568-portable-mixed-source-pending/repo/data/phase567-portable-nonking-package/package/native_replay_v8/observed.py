"""Input-only runner with one source-approved finite observer7 genuine domain."""
from pathlib import Path
import json
from .engine import CombatEngine, validate_fixture, validate_runtime_inputs, GENUINE_PROFILES
from .randomness import TapeRandom, SeededRandom
from .state import strict_json_loads

MODEL_PACKAGE='native_replay_v8'
OBSERVER_VERSION='observer7-048-finite-input-domain'


def run_input_bundle(bundle):
    if type(bundle)is not dict or set(bundle)!={'schema','fixture','runtime','draws','synthetic_seed'}:
        raise ValueError('unknown/missing input-only bundle fields')
    if bundle['schema']!='native-v8-input-only/1':raise ValueError('unknown input bundle schema')
    validate_fixture(bundle['fixture'])
    runtime=validate_runtime_inputs(bundle['runtime'],bundle['fixture'])
    if bundle['draws']is None:
        if runtime.data['mode']=='genuine':raise ValueError('genuine requires actual direct primitive tape')
        if type(bundle['synthetic_seed'])is not int:raise ValueError('explicit synthetic integer seed required')
        rng=SeededRandom(bundle['synthetic_seed'])
    else:
        if bundle['synthetic_seed']is not None:raise ValueError('select either tape or synthetic seed')
        rng=TapeRandom(bundle['draws'])
    engine=CombatEngine(bundle['fixture'],rng,runtime)
    result=engine.run()
    if isinstance(rng,TapeRandom):rng.assert_consumed()
    return result


def load_input_bundle(path):
    return strict_json_loads(Path(path).read_text())


def run_observed(capture_dir):
    # Reject before opening legacy battle outputs or guessing missing runtime.
    raise ValueError('BLOCKED_INHERITED_INPUT: genuine observer7/runtime/terminal profile not enabled')


def compare_expected(capture_dir,result):
    from .compare import compare_capture
    return compare_capture(capture_dir,result)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-bundle',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=run_input_bundle(load_input_bundle(args.input_bundle))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
