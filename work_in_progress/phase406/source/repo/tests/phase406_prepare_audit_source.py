"""Author SOURCE generator. Never imports/calls audit, schema, engine or actual inputs."""
from pathlib import Path
import ast
import hashlib
import json
import pprint
import stat
import traceback

R=Path(__file__).resolve().parents[1]
D=R/'data/phase406-initial-audit-source'
T=R/'tests/phase406_initial_audit_template.py'
M=R/'tests/phase406_initial_source_audit.py'
S=R/'docs/phase406_readonly_initial_audit_implementation_spec.md'


def pin(p):
    i=p.lstat();assert stat.S_ISREG(i.st_mode)and i.st_nlink==1 and not any(x.is_symlink()for x in (p,*p.parents))
    b=p.read_bytes();return dict(path=str(p.relative_to(R))if p.is_relative_to(R)else str(p),size=len(b),sha256=hashlib.sha256(b).hexdigest())


def read(p):return json.loads(p.read_text())


def save(p,v):
    with p.open('x')as f:json.dump(v,f,indent=2,sort_keys=True,ensure_ascii=False);f.write('\n')


def main():
    D.mkdir(exist_ok=False)
    allow=read(R/'data/phase405-initial-source-feasibility-design/finite-source-allowset.json')
    static={r['path']:r for r in allow['files']}
    design_owner=R/'data/phase405-initial-source-feasibility-design/owned-files.json'
    for row in read(design_owner)['files']:
        static[row['path']]=row
    for p in [design_owner,R/'data/phase405-independent-design-review/review.json',R/'data/phase405-independent-design-review/owned-files.json']:
        static[pin(p)['path']]=pin(p)
    for row in static.values():
        p=Path(row['path']);p=p if p.is_absolute()else R/p;assert pin(p)==row
    source=R/'tests/phase391_king_observer_schema.py'
    literals={}
    for n in ast.parse(source.read_text()).body:
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ('FIXED_FIXTURE','BINDING_FIXED_PLAN','INPUT_FILES','CHANNEL_FILES','TOTAL_BYTES'):
            literals[n.targets[0].id]=ast.literal_eval(n.value)
    fields=read(R/'data/phase405-initial-source-feasibility-design/field-obligation-manifest.json')
    artifacts=[str(p.relative_to(R))for p in [S,T,Path(__file__),M,D/'api-contract.json',D/'static-author-checks.json',D/'source-constraints.json']]
    constants=dict(SOURCE=str(D.relative_to(R)),MODULE=str(M.relative_to(R)),SOURCE_ARTIFACTS=artifacts,
        REVIEW_STATUS='INDEPENDENT407_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING',
        ROOT402='data/phase401-root-native-attempt06/independent402-accepted.json',
        REVIEW402='data/phase402-independent-final/review.json',OWNER402='data/phase402-independent-final/owned-files.json',
        REVIEW405='data/phase405-independent-design-review/review.json',OWNER405='data/phase405-independent-design-review/owned-files.json',
        FIXED_RUN='/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06',
        PERMISSION_KEYS=['models','inputbuild','projection','expected_reads','new_native','SUT_calls','schema_calls','restore','READY'],
        TOTAL_BYTES=literals['TOTAL_BYTES'],INPUT_NAMES=list(literals['INPUT_FILES'])+['king-slot-bindings.json'],
        CHANNELS=literals['CHANNEL_FILES'],PHASES=[['pre_prepare','Core/Game.gd::prepareItems'],['pre_activate','Core/Game.gd::activateItems']],
        TIMER_ROLES=fields['Timer_public_roles'],FIVE_TIMER_ROLES=fields['Timer_selected_five_private_chain'],
        SLOT_PLAN=literals['BINDING_FIXED_PLAN'],FIXED_FIXTURE=literals['FIXED_FIXTURE'],STATIC_PINS=static)
    header='"""406 readonly presence/source-route audit. Fullschema and all engine execution remain closed."""\n'
    header+='\n'.join(name+' = '+pprint.pformat(value,width=110,sort_dicts=True)for name,value in constants.items())+'\n\n'
    text=header+T.read_text();compile(text,str(M),'exec')
    with M.open('x')as f:f.write(text)
    tree=ast.parse(text);imports=[];functions=[];lines=text.splitlines(True)
    for n in tree.body:
        if isinstance(n,ast.Import):imports.extend(a.name for a in n.names)
        if isinstance(n,ast.ImportFrom):imports.append(n.module)
        if isinstance(n,ast.FunctionDef):
            raw=''.join(lines[n.lineno-1:n.end_lineno]).encode()
            functions.append(dict(name=n.name,signature='('+ast.unparse(n.args)+')',line=n.lineno,size=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
    assert set(imports)=={'argparse','hashlib','json','math','os','pathlib','re','stat','struct','sys','traceback'}
    assert not any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id in ('exec','eval','compile','__import__')for n in ast.walk(tree))
    assert len(constants['INPUT_NAMES'])==12 and len(set(constants['TIMER_ROLES']))==35 and len(set(constants['FIVE_TIMER_ROLES']))==5
    assert set(constants['FIVE_TIMER_ROLES'])<set(constants['TIMER_ROLES'])
    nodes={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    callnames=lambda n:[x.func.id for x in ast.walk(n)if isinstance(x,ast.Call)and isinstance(x.func,ast.Name)]
    assert 'validate_sources_with_binding'not in callnames(tree) and 'run_input_bundle'not in callnames(tree)
    route=ast.get_source_segment(text,nodes['audit_source_chain'])
    assert "classification='MISSING'"in route and "validation_result='UNPROVEN'"in route and "proof_complete=False"in route
    assert "classification='SOURCE_DERIVED'"not in text
    run=ast.get_source_segment(text,nodes['run_audit'])
    assert run.index('verify_audit_release(')<run.index('install_io_guard(')<run.index("authority['output'].mkdir()")<run.index('read_lawful12_once(')
    physical=ast.get_source_segment(text,nodes['read_regular'])
    assert physical.index('stat.S_ISREG(before.st_mode)')<physical.index('os.open(')<physical.index('os.fstat(')<physical.index('stream.read(')
    assert text.endswith(T.read_text()) and text[:-len(T.read_text())]==header
    for p in [S,T,M,Path(__file__)]:
        if p.suffix=='.py':compile(p.read_text(),str(p),'exec')
    api=dict(schema='phase406-actual-audit-source-api/1',module=pin(M),functions=functions,
        authority_schema='root406-lawful12-initial-audit/1',required_review_status=constants['REVIEW_STATUS'],
        source_freeze_path=str((D/'source-freeze.json').relative_to(R)),source_owner_path=str((D/'source-owner.json').relative_to(R)),
        future_release=None,future_review=None,fullgate_positive_executed=False,
        source_review_required_fields=['status','source_freeze','source_owner','models:strictINT0','native:strictINT0','inputbuild:strictINT0','old_SUT_calls:strictINT0','schema_calls:strictINT0'],
        input_files=constants['INPUT_NAMES'],permissions_zero=constants['PERMISSION_KEYS'],
        output_statuses=['FEASIBLE_PENDING_FULL_STRUCTURAL_VALIDATION','BLOCKED_INITIAL_SOURCE_GAPS','REJECTED_INITIAL_DOMAIN','FAILED_SOURCE_INTEGRITY'],
        field_classifications=['DIRECT_OBSERVATION','SOURCE_DERIVED','MISSING'],fullschema='NOT_VALIDATED',source_derived_recipes_implemented=0,
        counters=dict(author_audit_import=0,author_audit_calls=0,old_SUT_import=0,old_SUT_calls=0,models=0,inputbuild=0,capture_reads=0,expected_reads=0),
        optional391_job_implemented=False)
    save(D/'api-contract.json',api)
    save(D/'static-author-checks.json',dict(schema='phase406-static-author-checks/1',module=pin(M),template=pin(T),stdlib_imports=imports,
        template_embedding='EXACT_BYTES_HEADER_PLUS_TEMPLATE',compile_text_only=True,ast_no_eval_exec_dynamic_import=True,
        release_before_input_source_order=True,regular_nlink1_fstat_before_content=True,
        fixed12_names=True,fixed35_roles=True,five_plus_thirty_disjoint=True,no_accepted_SOURCE_DERIVED_construction=True,
        SUT_modules_imported=0,audit_module_imported=0,audit_functions_called=0,synthetic_or_actual_input_tested=0,
        limitation='Static checks only;407 independently tests new audit API. No dynamic positive/negative claim.'))
    save(D/'source-constraints.json',dict(schema='phase406-source-constraints/1',source_allowset_origin=pin(R/'data/phase405-initial-source-feasibility-design/finite-source-allowset.json'),
        added_original_source_dependencies=[],source_control_metadata_additions=[k for k in static if k not in {x['path']for x in allow['files']}],
        interpretation='MISSING/UNPROVEN may mean no full audit recipe, not proven absent original data; no mandatory recapture conclusion',
        no_optional8=True,no_micro_simulator=True,no_recipe_framework=True,no_model_runtime_or_bundle=True,
        source_only_author_calls=0,lawful12_reads=0,expected_reads=0,field_actual_status='NOT_ESTABLISHED_BEFORE_AUTHORIZED_AUDIT',
        new_audit_runtime_must_be_counted_separately_from_old_engine_SUT=True))
    files=dict(static)
    for name in artifacts:files[name]=pin(R/name)
    freeze=dict(schema='phase406-readonly-initial-audit-SOURCE/1',module=pin(M),files=list(files.values()),static_pins=static,
                fullschema='NOT_VALIDATED',derived_recipes=[],old_SUT_calls=0)
    save(D/'source-freeze.json',freeze)
    save(D/'summary.json',dict(schema='phase406-author-source-summary/1',status='SOURCE_FROZEN_INDEPENDENT407_PENDING',
        source_freeze=pin(D/'source-freeze.json'),api=pin(D/'api-contract.json'),spec=pin(S),
        operations=dict(audit_imports=0,audit_calls=0,old_SUT_imports=0,old_SUT_calls=0,schema_calls=0,models=0,inputbuild=0,projection=0,actual12_reads=0,expected_reads=0,native=0,Godot=0,livepool=0,restore=0,READY=0),
        optional391_implemented=False,no_more_writes_after_owner=True))
    files[str((D/'source-freeze.json').relative_to(R))]=pin(D/'source-freeze.json')
    files[str((D/'summary.json').relative_to(R))]=pin(D/'summary.json')
    save(D/'source-owner.json',dict(schema='phase406-audit-source-owner/1',files=list(files.values()),no_more_writes=True,scope='stdlib SOURCE only; no audit or old SUT executed'))
    for row in files.values():
        p=Path(row['path']);p=p if p.is_absolute()else R/p;assert pin(p)==row
    print(json.dumps(dict(owner=pin(D/'source-owner.json'),freeze=pin(D/'source-freeze.json'),api=pin(D/'api-contract.json'),module=pin(M),spec=pin(S),leaves=len(files),bytes=sum(r['size']for r in files.values()))))


if __name__=='__main__':
    try:main()
    except BaseException:
        f=D/'author-first-preparation-failure'
        f.mkdir(parents=True,exist_ok=False)
        for p in [T,M,Path(__file__),S]:
            if p.is_file():(f/p.name).write_bytes(p.read_bytes())
        (f/'traceback.txt').write_text(traceback.format_exc())
        raise
