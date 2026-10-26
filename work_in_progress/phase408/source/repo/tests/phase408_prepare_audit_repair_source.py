"""SOURCE-only408 repair generator. Compile/AST/byte inverse; no audit import or call."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import pprint
import re
import stat
import traceback

R=Path(__file__).resolve().parents[1]
D=R/'data/phase408-initial-audit-source'
OLD=R/'data/phase406-initial-audit-source'
SPEC=R/'docs/phase408_owner_readback_assessment_repair_spec.md'
T=R/'tests/phase408_initial_audit_template.py'
M=R/'tests/phase408_initial_source_audit.py'


def pin(p):
    s=p.lstat();assert stat.S_ISREG(s.st_mode)and s.st_nlink==1 and not any(x.is_symlink()for x in(p,*p.parents))
    b=p.read_bytes();return dict(path=str(p.relative_to(R))if p.is_relative_to(R)else str(p),size=len(b),sha256=hashlib.sha256(b).hexdigest())


def read(p):return json.loads(p.read_text())


def save(p,value):
    with p.open('x')as f:json.dump(value,f,indent=2,sort_keys=True);f.write('\n')


def write(p,value):
    with p.open('x')as f:f.write(value)


def nodes(text):return {n.name:n for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}


def span(text,name):
    n=nodes(text)[name];return ''.join(text.splitlines(True)[n.lineno-1:n.end_lineno])


class Delta:
    def __init__(self,p):self.p=p;self.before=p.read_text();self.text=self.before;self.edits=[]
    def replace(self,a,b,kind):
        assert a!=b and self.text.count(a)>0,(self.p,a[:100])
        positions=[m.start()for m in re.finditer(re.escape(a),self.text)]
        self.edits.append(dict(before=a,after=b,kind=kind,positions=[p+i*(len(b)-len(a))for i,p in enumerate(positions)]))
        self.text=self.text.replace(a,b)
    def finish(self,p):
        inverse=self.text
        for e in reversed(self.edits):
            for pos in reversed(e['positions']):
                assert inverse[pos:pos+len(e['after'])]==e['after']
                inverse=inverse[:pos]+e['before']+inverse[pos+len(e['after']):]
        assert inverse.encode()==self.p.read_bytes()
        normalized=self.text
        for e in reversed(self.edits):
            if e['kind']=='protocol':normalized=normalized.replace(e['after'],e['before'])
        a,b=nodes(self.before),nodes(normalized)
        assert set(b)-set(a)=={'required_initial_targets'} and not set(a)-set(b)
        changed=[name for name in a if ast.dump(a[name],include_attributes=False)!=ast.dump(b[name],include_attributes=False)]
        assert set(changed)=={'owned_index','save_new','assess_initial_feasibility'},changed
        compile(self.text,str(p),'exec');write(p,self.text)
        proof=dict(before=pin(self.p),after=pin(p),edits=self.edits,full_byte_inverse='EXACT',semantic_changed=changed,
                   new_pure_helper='required_initial_targets',conserved=[name for name in a if name not in changed],SUT_imports=0,SUT_calls=0)
        save(D/(p.stem+'-inverse.json'),proof)
        write(D/(p.stem+'-source.patch'),''.join(difflib.unified_diff(self.before.splitlines(True),self.text.splitlines(True),fromfile=str(self.p.relative_to(R)),tofile=str(p.relative_to(R)))))
        return proof


OWNED='''def owned_index(value):
    need(type(value) is dict and type(value.get('files')) in (list, dict), 'owner list or path-map files')
    files = value['files']
    rows = []
    if type(files) is dict:
        for name, content in files.items():
            exact(content, ('size', 'sha256'), 'path-map owner value; no path override')
            rows.append(dict(path=name, size=content['size'], sha256=content['sha256']))
    else:
        rows = files
    result = {}
    for row in rows:
        descriptor(row)
        name = row['path']
        need(bool(name) and '\\\\' not in name and '\\0' not in name, 'owner path string')
        if PurePosixPath(name).is_absolute():
            need(name in STATIC_PINS and name == PurePosixPath(name).as_posix() and
                 all(part not in ('', '.', '..') for part in name.split('/')[1:]), 'exact approved absolute SOURCE owner path')
            normalized = name
        else:
            normalized = canonical(Path('.'), name).as_posix()
            need(normalized == name, 'canonical relative owner path')
        need(normalized not in result, 'unique normalized owned source path')
        result[normalized] = dict(path=normalized, size=row['size'], sha256=row['sha256'])
    return result
'''

SAVE='''def save_new(path, value):
    raw=(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\\n').encode()
    need(len(raw)<=64*1024*1024,'bounded report artifact')
    unlinked(path)
    with path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    expected=dict(path=path.name,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())
    readback=read_regular(path,expected,64*1024*1024,[])
    need(readback==raw,'strict output physical/byte readback')
    return expected
'''

REQUIRED='''def required_initial_targets():
    required = {}
    for phase, unused_site in PHASES:
        for side in ('P', 'O'):
            required[('Character.buffProtectStacks', phase, side)] = 'direct'
            for field in ('invulnerable', 'invulnerabilityItem', 'invulBubbleVisible'):
                required[('Character.'+field, phase, side)] = 'source'
        for field in ('invuCharges', 'activations', 'activationsToTrigger', 'protectedBuffs', 'manaCost'):
            required[('King.'+field, phase, 'P:12')] = 'direct'
        for field in ('crown', 'light_visible', 'light_modulate'):
            required[('King.'+field, phase, 'P:12')] = 'source'
        for role in TIMER_ROLES:
            for field in ('process_mode', 'wait_time', 'time_left', 'one_shot', 'autostart', 'paused', 'stopped'):
                required[('Timer.'+field, phase, role)] = 'direct'
            for field in ('native_id', 'role', 'path', 'name', 'class', 'positions', 'priority', 'inside_tree',
                          'ordinary_physics', 'internal_physics', 'ordinary_idle', 'internal_idle'):
                required[('Timer.node.'+field, phase, role)] = 'direct'
            required[('Timer.private_left', phase, role)] = 'source'
    for part in ('activation', 'drag'):
        for field in ('visible', 'emitting', 'one_shot', 'lifetime', 'explosiveness', 'speed_scale'):
            required[('Particle.'+part+'.'+field, 'pre_activate', 'P:12')] = 'direct'
    for role in FIVE_TIMER_ROLES:
        for field in ('timer_id', 'owner_id', 'kind', 'starts', 'stops', 'birth'):
            required[('Timer.lineage.'+field, 'pre_activate', role)] = 'direct'
        required[('Timer.private_provenance_label', 'pre_activate', role)] = 'direct'
    return required
'''

ASSESS='''def assess_initial_feasibility(rows, findings):
    need(type(rows) is list and type(findings) is list, 'assessment row/finding arrays')
    required = required_initial_targets()
    seen = set()
    for row in rows:
        need(type(row) is dict, 'assessment row object')
        fields = ('field_id', 'phase', 'side_or_role', 'classification', 'validation_result')
        need(all(type(row.get(field)) is str for field in fields) and
             type(row.get('proof_complete')) is bool, 'assessment strict strings/BOOL proof')
        key = (row['field_id'], row['phase'], row['side_or_role'])
        need(key in required and key not in seen, 'known unique required assessment target')
        seen.add(key)
        classification, validation, complete = row['classification'], row['validation_result'], row['proof_complete']
        need(classification in ('DIRECT_OBSERVATION', 'SOURCE_DERIVED', 'MISSING') and
             validation in ('SUPPORTED', 'REJECTED', 'UNPROVEN'), 'allowed assessment states')
        need(classification != 'SOURCE_DERIVED', 'zero reviewed SOURCE derivation recipes; caller flags cannot prove a chain')
        need(required[key] == 'direct' or classification == 'MISSING', 'SOURCE-only target cannot be directly observed, including private Timer')
        if classification == 'MISSING':
            need(validation == 'UNPROVEN' and complete is False, 'missing target stays unproven/incomplete')
        need(complete is False or validation == 'SUPPORTED', 'complete proof requires supported validation')
    need(seen == set(required), 'complete exact required field/phase/role set')
    for finding in findings:
        exact(finding, ('kind', 'detail'), 'assessment finding')
        need(finding['kind'] == 'DOMAIN_REJECTED' and type(finding['detail']) is str, 'known domain rejection finding')
    if any(row['validation_result']=='REJECTED'for row in rows)or any(x['kind']=='DOMAIN_REJECTED'for x in findings):
        status='REJECTED_INITIAL_DOMAIN'
    elif any(row['classification']=='MISSING'or row['validation_result']!='SUPPORTED'or row['proof_complete']is not True for row in rows):
        status='BLOCKED_INITIAL_SOURCE_GAPS'
    else:
        status='FEASIBLE_PENDING_FULL_STRUCTURAL_VALIDATION'
    return dict(schema='phase406-initial-source-feasibility/1',status=status,fullschema='NOT_VALIDATED',
                source_derived_recipes_implemented=0,field_count=len(rows),classifications={k:sum(r['classification']==k for r in rows)for k in ('DIRECT_OBSERVATION','SOURCE_DERIVED','MISSING')},
                rejected_fields=sum(r['validation_result']=='REJECTED'for r in rows),models=0,inputbuild=0,projection=0,old_SUT_calls=0,schema_calls=0,
                genuine_input_accepted=False,King_admitted=False,reader361='CLOSED',model356='CLOSED')
'''

PROTOCOL=[('root406-lawful12-initial-audit/1','root408-lawful12-initial-audit/1'),
          ('data/phase406-initial-audit-[A-Za-z0-9_-]+','data/phase408-initial-audit-[A-Za-z0-9_-]+'),
          ('fixed406 authority paths','fixed408 authority paths'),
          ('phase406-readonly-initial-audit-SOURCE/1','phase408-readonly-initial-audit-SOURCE/1'),
          ('exact406 source scope','exact408 source scope'),('closed406 source owner set','closed408 source owner set'),
          ('actual owned407 review','actual owned409 review'),('407 binds actual406 freeze and owner','409 binds actual408 freeze and owner'),
          ('No complete reviewed derivation recipe in406.','No complete reviewed derivation recipe in408.'),
          ('phase406-initial-source-feasibility/1','phase408-initial-source-feasibility/1'),
          ('phase406-actual-initial-audit-owner/1','phase408-actual-initial-audit-owner/1')]


def main():
    D.mkdir(exist_ok=False)
    before={r['path']:r for r in read(OLD/'source-owner.json')['files']}
    before[pin(OLD/'source-owner.json')['path']]=pin(OLD/'source-owner.json')
    review=R/'data/phase407-frozen406-static-review/review.json'
    assert pin(review)==dict(path=str(review.relative_to(R)),size=9540,sha256='c311aaf0280e6a2ca89e565d4f4246d5abc39a0639bd9a9f2a35e03232c1dd1d')
    owner407=R/'data/phase407-frozen406-static-review/owned-files.json'
    entries=read(owner407)['files']
    if isinstance(entries,dict):entries=[dict(path=k,**v)for k,v in entries.items()]
    for row in entries:before[row['path']]=row
    before[pin(owner407)['path']]=pin(owner407)
    for row in before.values():
        p=Path(row['path']);p=p if p.is_absolute()else R/p;assert pin(p)==row
    old_freeze=read(OLD/'source-freeze.json');static=old_freeze['static_pins']
    new_artifacts=[str(p.relative_to(R))for p in [SPEC,T,M,Path(__file__),D/'api-contract.json',D/'static-author-checks.json',D/'source-constraints.json',D/'required-target-inventory.json',D/(T.stem+'-inverse.json'),D/(M.stem+'-inverse.json'),D/(T.stem+'-source.patch'),D/(M.stem+'-source.patch')]]
    artifacts=new_artifacts+[name for name in before if name not in static]
    results=[]
    for old,p in [(R/'tests/phase406_initial_audit_template.py',T),(R/'tests/phase406_initial_source_audit.py',M)]:
        delta=Delta(old)
        for name,value in [('owned_index',OWNED),('save_new',SAVE),('assess_initial_feasibility',ASSESS)]:
            delta.replace(span(delta.text,name),value,'semantic')
        delta.replace('def assess_initial_feasibility(rows, findings):',REQUIRED+'\n\ndef assess_initial_feasibility(rows, findings):','helper')
        for a,b in PROTOCOL:delta.replace(a,b,'protocol')
        if p==M:
            assignments={n.targets[0].id:n for n in ast.parse(delta.text).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
            replacements=dict(SOURCE=str(D.relative_to(R)),MODULE=str(M.relative_to(R)),SOURCE_ARTIFACTS=artifacts,
                              REVIEW_STATUS='INDEPENDENT409_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING')
            for name,value in replacements.items():
                n=assignments[name];old_expr=ast.get_source_segment(delta.text,n) if name==next(iter(replacements))else None
                # Positions change after each edit: reparse the current assignment.
                n=next(n for n in ast.parse(delta.text).body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id==name)
                delta.replace(ast.get_source_segment(delta.text,n),name+' = '+pprint.pformat(value,width=110,sort_dicts=True),'protocol')
            delta.replace('406 readonly presence/source-route audit.','408 readonly presence/source-route audit.','protocol')
        results.append(delta.finish(p))
    for name in ('owned_index','save_new','required_initial_targets','assess_initial_feasibility'):
        assert span(T.read_text(),name)==span(M.read_text(),name)
    module=M.read_text();tree=ast.parse(module);methods=nodes(module)
    values={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
    assert values['STATIC_PINS']==static
    assert values['TIMER_ROLES']==ast.literal_eval(next(n.value for n in ast.parse((R/'tests/phase406_initial_source_audit.py').read_text()).body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id=='TIMER_ROLES'))
    imports=[]
    for n in tree.body:
        if isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
        elif isinstance(n,ast.ImportFrom):imports.append(n.module)
    assert set(imports)=={'argparse','hashlib','json','math','os','pathlib','re','stat','struct','sys','traceback'}
    assert not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in ('exec','eval','__import__','compile')for n in ast.walk(tree))
    save_source=span(module,'save_new');assert 'path.read_bytes'not in save_source and 'read_regular(path,expected,64*1024*1024,[])'in save_source
    assert span(module,'read_regular')==span((R/'tests/phase406_initial_source_audit.py').read_text(),'read_regular')
    # Independent author metadata enumeration; never invokes the new pure helper.
    targets={}
    def add(field,phase,role,route):
        key=(field,phase,role);assert key not in targets;targets[key]=route
    for phase in ('pre_prepare','pre_activate'):
        for side in ('P','O'):
            add('Character.buffProtectStacks',phase,side,'direct')
            for f in ('invulnerable','invulnerabilityItem','invulBubbleVisible'):add('Character.'+f,phase,side,'source')
        for f in ('invuCharges','activations','activationsToTrigger','protectedBuffs','manaCost'):add('King.'+f,phase,'P:12','direct')
        for f in ('crown','light_visible','light_modulate'):add('King.'+f,phase,'P:12','source')
        for role in values['TIMER_ROLES']:
            for f in ('process_mode','wait_time','time_left','one_shot','autostart','paused','stopped'):add('Timer.'+f,phase,role,'direct')
            for f in ('native_id','role','path','name','class','positions','priority','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle'):add('Timer.node.'+f,phase,role,'direct')
            add('Timer.private_left',phase,role,'source')
    for part in ('activation','drag'):
        for f in ('visible','emitting','one_shot','lifetime','explosiveness','speed_scale'):add('Particle.'+part+'.'+f,'pre_activate','P:12','direct')
    for role in values['FIVE_TIMER_ROLES']:
        for f in ('timer_id','owner_id','kind','starts','stops','birth'):add('Timer.lineage.'+f,'pre_activate',role,'direct')
        add('Timer.private_provenance_label','pre_activate',role,'direct')
    assert len(targets)==1479 and sum(v=='source'for v in targets.values())==88
    save(D/'required-target-inventory.json',dict(schema='phase408-source-required-target-inventory/1',scope='author SOURCE metadata; not a SUT input/fixture/call',total=1479,direct_candidates=1391,source_only_unproven=88,targets=[dict(field_id=k[0],phase=k[1],side_or_role=k[2],route=v)for k,v in targets.items()]))
    functions=[]
    for name,n in methods.items():
        if not isinstance(n,ast.FunctionDef):continue
        raw=span(module,name).encode();functions.append(dict(name=name,signature='('+ast.unparse(n.args)+')',line=n.lineno,size=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    api=read(OLD/'api-contract.json')
    api.update(schema='phase408-actual-audit-source-api/1',module=pin(M),functions=functions,authority_schema='root408-lawful12-initial-audit/1',
               required_review_status=values['REVIEW_STATUS'],source_freeze_path=str((D/'source-freeze.json').relative_to(R)),source_owner_path=str((D/'source-owner.json').relative_to(R)),
               repair_origin=pin(OLD/'source-freeze.json'),repair_review=pin(review),required_target_count=1479,unproven_target_count=88,
               owned_index_formats=['list of exact path,size,sha256 rows','dict canonical path -> exact size,sha256'],
               assessment_behavior='Exact complete unique targets. StrictBOOL/state/route validation; no caller-derived success recipe.')
    save(D/'api-contract.json',api)
    save(D/'static-author-checks.json',dict(schema='phase408-static-author-repair-checks/1',module=pin(M),template=pin(T),compile_text_only=True,stdlib_imports=imports,
        complete_byte_inverse=True,semantic_changed=['owned_index','save_new','assess_initial_feasibility'],added_pure_helper='required_initial_targets',
        read_regular_complete_bytes_unchanged=True,template_actual_repaired_functions_identical=True,old49_static_controls_unchanged=True,
        required_set_source_enumeration=dict(total=1479,direct=1391,source_unproven=88),
        new_audit_imports=0,new_audit_calls=0,old_SUT_imports=0,old_SUT_calls=0,synthetic_or_actual_data_tests=0,
        limitations='SOURCE static checks only. Dynamic409 gates pending; no future authority or accepted proof recipe.'))
    constraints=read(OLD/'source-constraints.json');constraints.update(schema='phase408-source-constraints/1',repair_only=['F01','F02','F03'],extra_original_dependencies=[],
        author_baseline_writes=0,author_metadata_changes=0,packaging=0,new_audit_imports=0,new_audit_calls=0,repair_review=pin(review))
    save(D/'source-constraints.json',constraints)
    files=dict(static)
    for name in artifacts:files[name]=pin(R/name)
    freeze=dict(schema='phase408-readonly-initial-audit-SOURCE/1',module=pin(M),files=list(files.values()),static_pins=static,fullschema='NOT_VALIDATED',derived_recipes=[],old_SUT_calls=0)
    save(D/'source-freeze.json',freeze)
    save(D/'summary.json',dict(schema='phase408-author-source-summary/1',status='SOURCE_FROZEN_INDEPENDENT409_PENDING',source_freeze=pin(D/'source-freeze.json'),api=pin(D/'api-contract.json'),spec=pin(SPEC),
        operations=dict(new_audit_imports=0,new_audit_calls=0,old_SUT_calls=0,schema_calls=0,models=0,inputbuild=0,actual12_reads=0,expected_reads=0,run_reads=0,native=0,baseline_writes=0,metadata_changes=0,packaging=0),no_more_writes_after_owner=True))
    files[str((D/'source-freeze.json').relative_to(R))]=pin(D/'source-freeze.json');files[str((D/'summary.json').relative_to(R))]=pin(D/'summary.json')
    save(D/'source-owner.json',dict(schema='phase408-audit-source-owner/1',files=list(files.values()),no_more_writes=True,scope='three SOURCE repairs only; dynamic409 pending'))
    for row in [*before.values(),*files.values()]:
        p=Path(row['path']);p=p if p.is_absolute()else R/p;assert pin(p)==row
    print(json.dumps(dict(owner=pin(D/'source-owner.json'),freeze=pin(D/'source-freeze.json'),api=pin(D/'api-contract.json'),module=pin(M),spec=pin(SPEC),leaves=len(files),bytes=sum(r['size']for r in files.values()))))


if __name__=='__main__':
    try:main()
    except BaseException:
        fail=D/'author-first-preparation-failure';fail.mkdir(parents=True,exist_ok=False)
        for p in [Path(__file__),SPEC,T,M]:
            if p.is_file():(fail/p.name).write_bytes(p.read_bytes())
        (fail/'traceback.txt').write_text(traceback.format_exc());raise
