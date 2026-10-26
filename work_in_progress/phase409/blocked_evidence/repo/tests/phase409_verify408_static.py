"""Independent SOURCE-only identity/delta check. Never imports audit code."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
import traceback

ROOT = Path('/workspace/python-original-engine/repo')
OUT = ROOT/'data/phase409-independent408-source-review'
SOURCE = 'data/phase408-initial-audit-source/'
PINS = {
 SOURCE+'source-owner.json': (16495,'c188422bd9dfe6d6365465204410f27f7c8ed9d8798afe21b8220ca09236dc88'),
 SOURCE+'source-freeze.json': (29684,'38f29ec7829b64805cd5c8cbe09caf59a32d11f75032d29948990878e10eeab8'),
 SOURCE+'api-contract.json': (8729,'898de46b9acfbed05dbc58dd33c61680c74684c534cbdbb937050bd523474dd3'),
 'tests/phase408_initial_source_audit.py': (74685,'c572cdbb35f44a3e696b0fa5ab3df539e9e985c5d88770d73e1f3bb9afe6977d'),
 'docs/phase408_owner_readback_assessment_repair_spec.md': (9363,'6b19f6f7ad028d7977db9cd72dfa9a2a9f7756eeeaffd84edc1182d6c662e41f'),
}
READS = {}
def ident(s):
    return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def read(name, size, sha):
    p=Path(name) if Path(name).is_absolute() else ROOT/name
    assert not any(x.is_symlink() for x in (p,*p.parents)), name
    pre=p.lstat(); assert stat.S_ISREG(pre.st_mode) and pre.st_nlink==1 and pre.st_size==size,name
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as f:
        assert ident(os.fstat(f.fileno()))==ident(pre),name
        raw=f.read(size+1)
        assert ident(os.fstat(f.fileno()))==ident(pre),name
    assert ident(p.lstat())==ident(pre) and len(raw)==size and hashlib.sha256(raw).hexdigest()==sha,name
    READS[name]=dict(path=name,size=size,sha256=sha,identity=ident(pre))
    return raw
def get(row): return read(row['path'],row['size'],row['sha256'])
def index(rows):
    assert isinstance(rows,list)
    d={r['path']:r for r in rows}; assert len(d)==len(rows)
    return d
def funcs(s): return {n.name:n for n in ast.parse(s).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
def segment(s,n): return (ast.get_source_segment(s,n)+'\n').encode()
def literals(s):
    out={}
    for n in ast.parse(s).body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try: out[n.targets[0].id]=ast.literal_eval(n.value)
            except (ValueError,TypeError): pass
    return out
class ProtocolNormalize(ast.NodeTransformer):
    def visit_Constant(self,node):
        if type(node.value) is str:
            node.value=node.value.replace('408','406').replace('409','407')
        return node
def dump(n): return ast.dump(ProtocolNormalize().visit(n),include_attributes=False)
def write(name,value):
    with (OUT/name).open('x') as f: json.dump(value,f,indent=2,sort_keys=True);f.write('\n')

def main():
    OUT.mkdir(exist_ok=False)
    evidence=dict(schema='independent409-source-static/1',new_audit_imports=0,new_audit_calls=0,actual12_reads=0,old_SUT_calls=0)
    try:
        for name,(size,sha) in PINS.items():read(name,size,sha)
        owner=json.loads(read(SOURCE+'source-owner.json',*PINS[SOURCE+'source-owner.json']))
        owned=index(owner['files']); cache={name:get(row) for name,row in owned.items()}
        assert len(owned)==83 and sum(x['size'] for x in owned.values())==2282824
        freeze=json.loads(cache[SOURCE+'source-freeze.json']); declared=index(freeze['files'])
        module=freeze['module']['path'];s=cache[module].decode();const=literals(s)
        assert set(owned)==set(declared)|{SOURCE+'source-freeze.json',SOURCE+'summary.json'}
        assert set(declared)==set(const['SOURCE_ARTIFACTS'])|set(const['STATIC_PINS'])
        assert all(owned[k]==v for k,v in declared.items())
        assert freeze['static_pins']==const['STATIC_PINS'] and len(const['STATIC_PINS'])==49
        assert all(declared[k]==v for k,v in const['STATIC_PINS'].items())
        old=cache['tests/phase406_initial_source_audit.py'].decode()
        assert literals(old)['STATIC_PINS']==const['STATIC_PINS']
        assert freeze['derived_recipes']==[] and freeze['fullschema']=='NOT_VALIDATED'
        assert const['REVIEW_STATUS']=='INDEPENDENT409_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING'
        api=json.loads(cache[SOURCE+'api-contract.json']); nodes=funcs(s)
        actual_api=[]
        assert {r['name'] for r in api['functions']}=={k for k,n in nodes.items() if isinstance(n,ast.FunctionDef)}
        for r in api['functions']:
            n=nodes[r['name']];raw=segment(s,n)
            assert r['line']==n.lineno and r['signature']=='('+ast.unparse(n.args)+')'
            assert len(raw)==r['size'] and hashlib.sha256(raw).hexdigest()==r['sha256'],r['name']
            actual_api.append(r)
        assert len(actual_api)==29
        inverses=[]
        for stem in ('phase408_initial_audit_template','phase408_initial_source_audit'):
            inv=json.loads(cache[SOURCE+stem+'-inverse.json']);current=cache[inv['after']['path']].decode()
            for edit in reversed(inv['edits']):
                for pos in reversed(edit['positions']):
                    assert current[pos:pos+len(edit['after'])]==edit['after'],(stem,pos)
                    current=current[:pos]+edit['before']+current[pos+len(edit['after']):]
            assert current.encode()==cache[inv['before']['path']],stem
            before=cache[inv['before']['path']].decode();after=cache[inv['after']['path']].decode()
            bn,an=funcs(before),funcs(after)
            assert set(an)-set(bn)=={'required_initial_targets'} and not set(bn)-set(an)
            assert set(inv['semantic_changed'])=={'owned_index','save_new','assess_initial_feasibility'}
            assert set(inv['conserved'])==set(bn)-set(inv['semantic_changed'])
            for name in inv['conserved']:assert dump(bn[name])==dump(an[name]),(stem,name)
            inverses.append(dict(before=inv['before'],after=inv['after'],full_byte_inverse='EXACT',conserved_after_protocol_normalization=inv['conserved'],edits=inv['edits']))
        imports=[]
        for n in ast.walk(ast.parse(s)):
            if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
            elif isinstance(n,ast.ImportFrom):imports.append(n.module)
        assert set(imports)=={'argparse','hashlib','json','math','os','pathlib','re','stat','struct','sys','traceback'}
        fields=json.loads(cache['data/phase405-initial-source-feasibility-design/field-obligation-manifest.json'])
        assert const['TIMER_ROLES']==fields['Timer_public_roles']
        assert const['FIVE_TIMER_ROLES']==fields['Timer_selected_five_private_chain']
        assert len(set(const['TIMER_ROLES']))==35 and len(set(const['FIVE_TIMER_ROLES']))==5
        assert set(fields['Timer_other_thirty_private_chain'])==set(const['TIMER_ROLES'])-set(const['FIVE_TIMER_ROLES'])
        assert [x[0] for x in const['PHASES']]==fields['phases']
        targets=[]
        def add(field,phase,role,route):targets.append(dict(field_id=field,phase=phase,side_or_role=role,route=route))
        # Independent finite expansion of the reviewed producer/405 obligations, not SUT execution.
        for phase in fields['phases']:
            for side in fields['character_sides']:
                for f in fields['character_direct_candidate']:add('Character.'+f,phase,side,'direct')
                for f in fields['character_source_derived_candidates']:add('Character.'+f,phase,side,'source')
            for f in fields['King_direct_candidates']:add('King.'+f,phase,'P:12','direct')
            for f in ('crown','light_visible','light_modulate'):add('King.'+f,phase,'P:12','source')
            for role in fields['Timer_public_roles']:
                for f in ('process_mode','wait_time','time_left','one_shot','autostart','paused','stopped'):add('Timer.'+f,phase,role,'direct')
                for f in ('native_id','role','path','name','class','positions','priority','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle'):add('Timer.node.'+f,phase,role,'direct')
                add('Timer.private_left',phase,role,'source')
        for part in fields['particle_groups']:
            for f in ('visible','emitting','one_shot','lifetime','explosiveness','speed_scale'):add('Particle.'+part+'.'+f,'pre_activate','P:12','direct')
        for role in fields['Timer_selected_five_private_chain']:
            for f in ('timer_id','owner_id','kind','starts','stops','birth'):add('Timer.lineage.'+f,'pre_activate',role,'direct')
            add('Timer.private_provenance_label','pre_activate',role,'direct')
        key=lambda r:(r['field_id'],r['phase'],r['side_or_role'])
        assert len(targets)==len({key(x) for x in targets})==1479
        author=json.loads(cache[SOURCE+'required-target-inventory.json'])
        assert sorted(targets,key=key)==sorted(author['targets'],key=key)
        assert sum(x['route']=='source' for x in targets)==88
        evidence.update(status='STATIC_PASS',owner_leaf_count=len(owned),owner_bytes=sum(r['size'] for r in owned.values()),source_owner=dict(path=SOURCE+'source-owner.json',size=PINS[SOURCE+'source-owner.json'][0],sha256=PINS[SOURCE+'source-owner.json'][1]),source_freeze=owned[SOURCE+'source-freeze.json'],APIs=actual_api,imports=imports,static_pins=49,inverses=inverses,required_targets=1479,direct_targets=1391,unproven_source_targets=88,Timer_roles=35,selected_Timer_roles=5,other_Timer_roles=30,physical_read_evidence=list(READS.values()))
        write('independently-derived-targets.json',targets)
        write('static-evidence.json',evidence)
        print(json.dumps({k:evidence[k] for k in ('status','owner_leaf_count','owner_bytes','required_targets','unproven_source_targets','new_audit_imports','new_audit_calls')}))
    except BaseException:
        evidence.update(status='STATIC_FIRST_FAILURE_STOP',traceback=traceback.format_exc(),physical_read_evidence=list(READS.values()))
        write('static-first-failure.json',evidence)
        raise

if __name__=='__main__':main()
