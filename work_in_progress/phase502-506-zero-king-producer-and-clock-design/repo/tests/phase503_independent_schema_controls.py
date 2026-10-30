"""Frozen finite503 pure schema batch; no producer/model/native calls."""
import sys
sys.dont_write_bytecode=True
import argparse,hashlib,importlib.util,json,time,traceback
from pathlib import Path
from collections import Counter
ROOT=Path('/workspace/python-original-engine/repo')
SOURCE=ROOT/'data/phase503-independent-controls-source'
def descriptor(path):
    raw=path.read_bytes()
    return dict(path=str(path.relative_to(ROOT)),size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
def write(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output-new',required=True);a=ap.parse_args()
    out=Path(a.output_new).resolve()
    if out.parent!=ROOT/'data' or out.name!='phase503-independent-controls-first-001':raise ValueError('fixed new output')
    out.mkdir(exist_ok=False)
    result=dict(schema='phase503-actual-synthetic-controls/1',status='STARTED',schema_imports=0,top_level_calls=0,cases=[],native=0,Godot=0,models=0,host=0,Expected_decode=0,pool=0,producer=0)
    started=time.monotonic();pins=json.loads((SOURCE/'pins.json').read_text());counts=Counter();schema_path=ROOT/pins['schema']['path']
    def profile(frame,event,arg):
        if event=='call' and frame.f_code.co_filename==str(schema_path):counts[frame.f_code.co_name]+=1
    try:
        for x in pins['files']:assert descriptor(ROOT/x['path'])==x, x['path']
        write(out/'before.json',pins)
        vectors=json.loads((SOURCE/'vectors.json').read_text())
        assert len(vectors['cases'])==12
        spec=importlib.util.spec_from_file_location('phase503_frozen_schema',schema_path)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module
        result['schema_imports']+=1;spec.loader.exec_module(module)
        assert Path(module.__file__).resolve()==schema_path
        result['loaded_schema']=descriptor(Path(module.__file__))
        for case in vectors['cases']:
            row=dict(id=case['id'],api=case['api'],expected=case['expected'],status='STARTED');result['cases'].append(row)
            result['top_level_calls']+=1
            error=None;returned=None
            try:
                sys.setprofile(profile)
                returned=getattr(module,case['api'])(*case['args'])
            except ValueError as exc:error=str(exc)
            finally:sys.setprofile(None)
            if case['expected']=='ACCEPT':
                assert error is None, 'unexpected rejection: '+str(error)
                assert returned==case['args'][0], 'positive projection altered value'
            else:
                assert error is not None, 'contamination accepted'
                assert case['error_contains'] in error, 'rejected for unexpected predicate: '+error
            row.update(status='PASS',error=error)
            write(out/'progress.json',result)
        result['status']='PASS_12_SYNTHETIC_SCHEMA_CASES_NOT_NATIVE_EXECUTION'
    except BaseException as exc:
        sys.setprofile(None);result['status']='FIRST_ERROR_STOPPED';result['error']=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
    finally:
        result['wall_seconds']=time.monotonic()-started
        result['all_schema_function_entries_during_top_calls']=dict(sorted(counts.items()))
        result['nested_function_entries']=sum(counts.values())-result['top_level_calls']
        after=[descriptor(ROOT/x['path']) for x in pins['files']]
        result['source_and_vectors_after_unchanged']=after==pins['files']
        if not result['source_and_vectors_after_unchanged']:result['status']='SOURCE_DRIFT_STOPPED'
        write(out/'after.json',dict(files=after));write(out/'result.json',result)
        files=[descriptor(p) for p in sorted(out.iterdir()) if p.is_file()]
        write(out/'owned-files.json',dict(schema='phase503-controls-owner/1',files=files))
    print(json.dumps(dict(status=result['status'],top_level_calls=result['top_level_calls'],schema_imports=result['schema_imports'],wall_seconds=result['wall_seconds'])))
    return 0 if result['status'].startswith('PASS_12') else 1
if __name__=='__main__':raise SystemExit(main())
