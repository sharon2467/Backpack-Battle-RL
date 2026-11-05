"""One explicitly released seven-call consumer-only carrier batch."""
import __future__, argparse, ast, copy, dataclasses, hashlib, json, math, os, pathlib, re, signal, stat, struct, sys, time, traceback, types, typing

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pins',required=True);parser.add_argument('--pins-sha256',required=True);parser.add_argument('--vectors',required=True);parser.add_argument('--output-new',required=True);args=parser.parse_args()
    repo=pathlib.Path('/workspace/python-original-engine/repo');output=pathlib.Path(args.output_new);assert not output.exists();output.mkdir(mode=0o700)
    pinraw=pathlib.Path(args.pins).read_bytes();assert hashlib.sha256(pinraw).hexdigest()==args.pins_sha256;pins=json.loads(pinraw)
    def resolve(s):
        p=pathlib.Path(s);return p if p.is_absolute() else repo/p
    allowed={str(resolve(p['path'])) for p in pins['files']}|{str(pathlib.Path(args.pins)),str(pathlib.Path(args.vectors))}
    reads=[];writes=[];stage='setup';counts={};result={'schema':'phase652-actual-controls/1','status':'RUNNING','pid':os.getpid(),'schema_eval_attempts':0,'schema_imports_completed':0,'top_calls_entered':0,'cases':[],'fullINPUT':0,'models':0,'Native':0,'Expected':0}
    def alarm(a,b):raise TimeoutError('inner15seconddeadline')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(15)
    def audit(event,a):
        if event!='open':return
        p=a[0]
        if isinstance(p,int):return
        path=str(pathlib.Path(os.fsdecode(p)).absolute());flags=a[2] if isinstance(a[2],int) else 0;write=bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if write:
            if pathlib.Path(path).parent!=output:raise PermissionError('WRITE_SCOPE:'+path)
            writes.append({'stage':stage,'path':path})
        else:
            if path not in allowed:raise PermissionError('READ_SCOPE:'+path)
            reads.append({'stage':stage,'path':path})
    sys.addaudithook(audit)
    schemafile=str(resolve(pins['schema_source']['path']))
    def profile(frame,event,arg):
        if event=='call' and frame.f_code.co_filename==schemafile:
            k=frame.f_code.co_name;counts[k]=counts.get(k,0)+1
    def hashes():
        rows=[]
        for p in pins['files']:
            path=resolve(p['path']);a=path.lstat();assert stat.S_ISREG(a.st_mode) and not path.is_symlink();raw=path.read_bytes();z=path.lstat();assert (a.st_size,a.st_mtime_ns,a.st_ino)==(z.st_size,z.st_mtime_ns,z.st_ino);d={'path':p['path'],'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()};assert all(d[k]==p[k] for k in ('size','sha256'));rows.append(d)
        return rows
    error=None;started=time.monotonic()
    try:
        result['before']=hashes();vectors=json.loads(pathlib.Path(args.vectors).read_bytes());assert len(vectors)==6
        actualraw=resolve(pins['lawful_input']['path']).read_bytes();actual=json.loads(actualraw);schema_raw=resolve(pins['schema_source']['path']).read_bytes()
        name='_phase652_exact649_consumer_schema';m=types.ModuleType(name);m.__file__=schemafile;sys.modules[name]=m
        stage='schema_load';result['schema_eval_attempts']=1;sys.setprofile(profile);exec(compile(schema_raw,schemafile,'exec'),m.__dict__);result['schema_imports_completed']=1
        result['loaded_schema']={'name':name,'file':m.__file__,'sha256':hashlib.sha256(schema_raw).hexdigest(),'VERSION':m.VERSION,'PROFILE':m.PROFILE}
        frozen_plan=copy.deepcopy(m.BINDING_FIXED_PLAN)
        for v in vectors:
            value=copy.deepcopy(actual);mutation=v['mutation']
            if mutation:
                role,field,new=mutation;row=next(r for r in value['actual_bindings'] if r['instance_id']==role)
                if isinstance(new,dict):new=next(r for r in value['actual_bindings'] if r['instance_id']==new['copy_from'])[field]
                row[field]=new
            raw=actualraw if mutation is None else json.dumps(value,separators=(',',':')).encode()+b'\n';raw_before=hashlib.sha256(raw).hexdigest();stage='control:'+v['name'];result['top_calls_entered']+=1;got=None
            try:ret=m.validate_binding_carrier(raw,m.BINDING_FIXED_PLAN)
            except ValueError as e:got=str(e)
            if v['expected'] is None:
                assert got is None,got;assert ret==actual;assert ret is not actual and ret['actual_bindings'] is not actual['actual_bindings']
            else:assert got==v['expected'],(v['name'],got,v['expected'])
            assert m.BINDING_FIXED_PLAN==frozen_plan and hashlib.sha256(raw).hexdigest()==raw_before
            result['cases'].append({'name':v['name'],'status':'PASS','first_reject':got,'input_sha256':raw_before,'input_unchanged':True,'fixed_plan_unchanged':True})
        result['status']='PASS';result['positive']=0;result['expected_rejects']=6
    except BaseException as e:
        error={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc(),'automatic_retry':False};result['status']='FAIL';result['first_error']=error
    finally:
        sys.setprofile(None);stage='after';result['profile']=counts;result['after']=hashes();result['pins_unchanged']=result['before']==result['after'];result['elapsed_seconds']=time.monotonic()-started;result['read_audit']=list(reads);result['write_audit_before_report']=list(writes);result['write_audit_limit']='Snapshot before report serialization; not a complete report-phase write log.';result['schema_control_IO']=[x for x in reads if x['stage'].startswith('control:')];result['forbidden_profile']={k:counts.get(k,0) for k in ('join_binding_provenance','validate_sources_with_binding','decode_sources','validate_source_carriers')};stage='report';signal.alarm(0)
        blobs={'result.json':json.dumps(result,indent=2,allow_nan=False)+'\n'}
        if error:blobs['first-error.json']=json.dumps(error,indent=2)+'\n'
        owned=[]
        for n,s in blobs.items():
            raw=s.encode();(output/n).write_bytes(raw);owned.append({'path':str(output/n),'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        (output/'owned-files.json').write_text(json.dumps({'schema':'phase652-actual-owner/1','files':owned},indent=2)+'\n')
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
