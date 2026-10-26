"""Seal saved first execution evidence; no imports or reruns of SUT."""
import hashlib
import json
from pathlib import Path
import stat

ROOT=Path('/workspace/python-original-engine/repo')
OUT=ROOT/'data/phase402-independent-final'

def identity(path):
    s=path.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1,str(path)
    b=path.read_bytes();assert s==path.lstat()
    return dict(size=len(b),sha256=hashlib.sha256(b).hexdigest())

def read(path): return json.loads((ROOT/path).read_bytes())
def ref(path): return dict(path=path,**identity(ROOT/path))

def main():
    assert not OUT.exists();OUT.mkdir()
    base='data/phase402-completed-control-execution-binding-final/'
    execution='data/phase402-terminal-controls-first-001/'
    launch='data/phase402-terminal-controls-launch-first-001/'
    binding=read(base+'pre-helper-evidence.json');expected=read(base+'expected.json');contract=read('data/phase402-independent-attempt06-preparation/contract.json')
    result=read(execution+'execution-result.json');proof=read(execution+'terminal-helper-return.json');calls=read(execution+'call-observation.json');io=read(execution+'io-read-observation.json');outer=read(launch+'result.json')
    assert result['status']=='PASS' and result['top_level_helper_calls']==1 and outer['returncode']==0 and outer['runner_invocations']==1
    assert len(result['helper_capture_reads'])==6 and not io['violations']
    assert (ROOT/launch/'stderr.txt').read_bytes()==b''
    assert len(calls['local_module_instances'])==5
    count=calls['actual_function_call_counts']
    for module,method in [('phase391_oracle_host.py','read_terminal_expected_controls'),('phase391_oracle_host.py','load_terminal_schema'),('phase391_king_observer_schema.py','<module>'),('phase391_king_observer_schema.py','decode_clock'),('phase391_king_observer_schema.py','validate_terminal_diagnostics'),('phase391_king_observer_schema.py','validate_terminal_receipt'),('phase391_king_observer_schema.py','validate_terminal_evidence')]:
        assert count[str(ROOT/'tests'/module)+'::'+method]==1
    evidence={
        'A01':dict(result='PASS',host_invocations=1,host_exit=0,host_status=binding['host_result']['status'],run=binding['run'],config=read('data/phase401-root-native-attempt06/independent402-completed-control-read-release.json')['config']),
        'A02':dict(result='PASS',source_count=binding['source_count'],archived_driver_count=196,driver_bytes=binding['driver_bytes'],old363_storage_and_owner_present=True,
            source_map_write_line=binding['source_map_write_line'],first_process_line=binding['first_process_line'],ordering_scope=binding['ordering_scope']),
        'A03':dict(result='PASS',actual_top_level_calls=1,actual_capture_control_opens=6,proof=proof['proof'],same_as_saved_host_proof=True,tail_length_expected_constant=None),
        'A04':dict(result='PASS_BYTES_ONLY',lawful12=binding['lawful12_bytes_only'],full12_business_semantics_accepted=False,King_production_admitted=False),
        'A05':dict(result='PASS_RECORDED_ASSOCIATION_WITH_NONCLEAN_LIMITS',processes=binding['processes'],
            limitations=['Native exit0 does not mean process_clean_exit; native ERROR presence is true and wrapper clean is false.',
                'Parse clean flag true coexists with recorded zombie27712. Native zombie27771 is also not claimed reaped; both records sent TERM.',
                'Recorded live_remaining empty is scoped historical cleanup metadata, not current process absence or PID identity.',
                'Polling has observed time gaps; not a kernel aggregate quota or exhaustive continuous observation. No new /proc scan.',
                'The prior recovery400 visibility gaps are not remeasured or promoted to a new402 process proof.']),
        'A06':dict(result='PASS_SAVED_CONTROL_ONLY',capture_complete=True,primary_failure=None,secondary_errors=[],source_changes_after_run=[],
            stored_compaction=binding['stored_compaction'],ready_basis=binding['ready_basis'],current_pool_verified=False,
            physical_reconstruction=False,bundle_payloads_restreamed=False,unreleased_bundle_members='Only manifest-referenced identities; no new overlay/inputs read or reconstruction.'),
        'A07':dict(result='PASS_BOUNDED_LOG_AND_FAILURE_HANDLING',capture_file_count=len(binding['capture_bytes_only']),capture_total_bytes=sum(x['size'] for x in binding['capture_bytes_only'].values()),
            logs=binding['logs_bytes_only'],log_semantics='Only authorized stderr ERROR presence and three parse stdout marker booleans; no line/business extraction.',
            native_failure_branch_executed=False,SUT_failure_branch_executed=False,checker_failures_preserved=True),
        'A08':dict(result='PASS',input_post_pin_count=result['post_pin_count'],source_and_binding_unchanged=True,audit_violations=[],owner_rule='All listed leaves ordinary nlink1 with byte count and SHA readback; owner does not self-own.')}
    report=dict(schema='independent402-attempt06-control-review/1',status='INDEPENDENT402_ATTEMPT06_TERMINAL_CONTROLS_ACCEPTED_ROOT_PENDING',
        source_freeze=binding['source_freeze'],execution_source_owner=binding['source_owner'],Root_release=binding['release'],
        Root_scope_supplement=ref('data/phase401-root-native-attempt06/independent402-process-association-scope-supplement.json'),
        root_source_diagnosis=ref('data/phase404-root-monitor-wrapper-association/finding.json'),
        preparation_contract=ref('data/phase402-independent-attempt06-preparation/contract.json'),execution_preparation=ref(base+'execution-preparation-owner.json'),
        run=binding['run'],capture=binding['capture'],logical_cases=8,cases=[dict(c,evidence=evidence[c['id']]) for c in contract['cases']],
        classification=dict(real_terminal_dynamic_cases=1,saved_metadata_byte_and_static_cases=7,top_level_SUT_calls=1,host_main_calls=0,
            local_import_module_instances=5,pinned_dynamic_schema_exec_instances=1,supporting_call_counts={k:v for k,v in count.items() if any(k.endswith('::'+n) for n in ('load_terminal_schema','decode_clock','validate_terminal_diagnostics','validate_terminal_receipt','validate_terminal_evidence'))}),
        execution=dict(outer=outer,inner=result,actual_args=read(launch+'invocation.json'),result=ref(execution+'execution-result.json'),terminal_return=ref(execution+'terminal-helper-return.json'),
            io_observation=ref(execution+'io-read-observation.json'),call_observation=ref(execution+'call-observation.json'),stdout=ref(launch+'stdout.txt'),stderr=ref(launch+'stderr.txt')),
        first_errors=[dict(path='data/phase402-preparation-first-failure',kind='Historical preparation parse-only SyntaxError; body did not execute.'),
            dict(owner=ref('data/phase402-binding-inspection-first-failure/owned-files.json'),kind='Independent summary empty dict slicing; Root authorized narrow fix.'),
            dict(owner=ref('data/phase402-binding-association-first-failure/owned-files.json'),kind='Independent whole monitor/process equality contradicted actual frozen writer; Root404 established exact transformations.'),
            dict(owner=ref('data/phase402-corrected-binding-type-first-failure/owned-files.json'),kind='Independent Markdown SPEC JSON decode; byte-only format correction explicitly authorized.')],
        repeated_reads=binding['repeated_metadata_reads'],
        boundaries=dict(models=0,inputbuild=0,projection=0,new_native=0,FrameDriver=0,RNG=0,current_pool_reads=0,new_proc_scans=0,restore=0,READY=0,
            expected_business_semantics=False,King_production_admitted=False,full12_business_admission=False,engine_completion=False,
            runtime_error_diagnosis='Not performed beyond released presence booleans.',automatic_SUT_retry=False,original_game_count='Root historical cumulative5; this reviewer launches0.'),
        native=0,models=0,inputbuild=0,no_more_writes_after_owner=True)
    (OUT/'review.json').open('x').write(json.dumps(report,indent=2,sort_keys=True)+'\n')
    paths=set(ROOT.glob('docs/phase402*.md'))|set(ROOT.glob('tests/phase402*.py'))
    for d in (ROOT/'data').glob('phase402*'):
        if d.is_dir(): paths.update(p for p in d.rglob('*') if p.is_file())
    files={str(p.relative_to(ROOT)):identity(p) for p in sorted(paths)}
    owner=dict(schema='independent402-final-owned-files/1',files=files,leaf_count=len(files),total_bytes=sum(v['size'] for v in files.values()),
        native=0,models=0,inputbuild=0,terminal_helper_calls=1,all_regular_single_link=True)
    p=OUT/'owned-files.json';p.open('x').write(json.dumps(owner,indent=2,sort_keys=True)+'\n')
    for n,v in files.items(): assert identity(ROOT/n)==v,n
    print(json.dumps(dict(review=ref('data/phase402-independent-final/review.json'),owner=ref('data/phase402-independent-final/owned-files.json'),leaves=len(files),bytes=owner['total_bytes']),sort_keys=True))

if __name__=='__main__': main()
