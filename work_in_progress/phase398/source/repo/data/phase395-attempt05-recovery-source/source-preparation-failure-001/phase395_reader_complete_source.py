"""Independent saved/process/capsule checks for the395 readonly physical reader."""


def verify_complete_saved_contract(roots, contract, mapping):
    # Each consumed saved leaf is checked before metadata decoding. No recovery imports.
    for row in read(verify_descriptor(R, contract['input_pins']))['files']:
        verify_descriptor(roots[row['root']], row)
    failed = roots['failed_run']; previous = roots['previous_run']
    load = lambda name: read(canonical(failed, name))
    journal = load('output/source-preimages/preimages.json')
    prior = load('output/previous-source-preimages/inventory.json')
    reset = load('output/prior-observer-reset.json')
    before = load('output/pool-before.json')
    target = read(canonical(previous, 'output/compaction/project-files.json'))
    target_data = read(canonical(previous, 'output/compaction/staged-inputs.json'))
    saved = load('output/failed-pool-preservation/failed-project-files.json')
    staged = load('output/failed-pool-preservation/failed-staged-files.json')
    base = load('output/failed-pool-preservation/baseline-files.json')
    require(before == dict(baseline=base,project=saved,staged=staged), 'saved05 equals complete before-native manifests')
    require(target == prior['project'] == reset['before'], 'old026 authoritative target/reset')
    index = lambda value: {row['path']:row for row in value['entries']}
    for value in (target,target_data,saved,staged,base,reset['after']):
        require(len(index(value)) == len(value['entries']), 'unique saved manifest paths')
    actual,wanted,start = index(saved),index(target),index(reset['after'])
    data,wanted_data = index(staged),index(target_data)
    require(actual.keys() == wanted.keys() and data.keys() == wanted_data.keys(), 'complete existing target path sets')
    require(all(actual[k]['kind'] == wanted[k]['kind'] for k in actual) and all(data[k]['kind'] == wanted_data[k]['kind'] for k in data), 'complete target kinds')
    file_diff = {k for k in actual if actual[k]!=wanted[k] and actual[k]['kind']=='file'}
    dir_diff = {k for k in actual if actual[k]!=wanted[k] and actual[k]['kind']=='directory'}
    require(len(mapping['file_differences']) == len(file_diff) and {row['path'] for row in mapping['file_differences']} == file_diff, 'independent complete project difference set')
    require(len(mapping['directory_differences']) == len(dir_diff) and {row['path'] for row in mapping['directory_differences']} == dir_diff, 'independent complete directory difference set')
    require({row['target']['path'] for row in mapping['staged_files']} == {k for k in wanted_data if wanted_data[k]['kind']=='file'}, 'all staged target file writes')
    driver = load('output/driver/source-map.json')['files']
    declared = {row['source']['path']:row for row in driver}
    require(len(declared) == len(driver), 'unique actual archived SOURCE')
    frozen = contract['installed_source_freeze']
    require(declared[frozen['path']]['source'] == frozen, 'actual380 installed SOURCE freeze')
    archived_freeze = verify_descriptor(failed, dict(path='output/driver/'+declared[frozen['path']]['file'], **{k:frozen[k] for k in ('size','sha256')}))
    source = read(archived_freeze)
    payloads = {name:row['after'] for name,row in source['paths'].items()}
    require(len(payloads)==75 and len(source['artifacts'])==3 and not(set(payloads)&set(source['artifacts'])), 'complete installed75+3 declaration')
    payloads.update({name:{k:row[k] for k in ('size','sha256')} for name,row in source['artifacts'].items()})
    jm = {row['path']:row for row in journal}
    require(len(jm)==len(journal)==len(payloads) and jm.keys()==payloads.keys(), 'complete unique actual install journal')
    checked=0
    for name,row in jm.items():
        require(row['after']==payloads[name]=={k:actual[name][k] for k in ('size','sha256')}, 'installed source/journal/failed bytes')
        if row['before'] is None:
            require(name not in start and row['backup'] is None, 'exact before-install absence only')
        else:
            require(row['before']==dict(identity={k:start[name][k] for k in ('size','sha256')},mode=start[name]['mode'],mtime_ns=start[name]['mtime_ns']), 'before-image/reset metadata')
            verify_descriptor(failed,dict(path='output/source-preimages/'+row['backup'],**row['before']['identity']));checked+=1
    for i,row in enumerate(prior['patch']['patches']):
        verify_descriptor(failed,dict(path='output/previous-source-preimages/'+str(i),size=row['after_size'],sha256=row['after_sha256']))
    verify_descriptor(failed,dict(path='output/previous-source-preimages/marker',**{k:wanted['.native-random-observer-disposable'][k] for k in ('size','sha256')}))
    for row in mapping['file_differences']:
        require(row['before_preserved']==actual[row['path']] and row['target']==wanted[row['path']], 'exact mapped targets')
        payload=verify_descriptor(roots[row['payload']['root']],row['payload'])
        require(pin(payload)=={k:row['target'][k] for k in ('size','sha256')}, 'old026 target payload bytes')
    for row in mapping['staged_files']:
        require(row['target']==wanted_data[row['target']['path']], 'exact staged target')
        payload=verify_descriptor(roots[row['payload']['root']],row['payload'])
        require(pin(payload)=={k:row['target'][k] for k in ('size','sha256')}, 'old026 staged payload bytes')
    expected_writes=len(file_diff)+len(mapping['staged_files'])
    expected=contract['complete_install']
    require((len(file_diff),len(dir_diff),len(mapping['staged_files']),sum(data[k]!=wanted_data[k] for k in wanted_data if wanted_data[k]['kind']=='file'),expected_writes,checked,len(prior['patch']['patches'])) ==
            (expected['project_file_differences'],expected['directory_differences'],expected['staged_files'],expected['staged_file_differences'],expected['expected_writer_files'],expected['checked_install_backups'],expected['checked_previous_patch_backups']), 'independently derived complete writer counts')
    return expected_writes


def attempt05_process_controls(roots, contract):
    groups=set();pids=set();zombies=set();observed={}
    for name,row in contract['process_controls'].items():
        value=read(verify_descriptor(roots['failed_run'],row))
        parse=name=='parse-process-result.json'
        require(type(value['parse_only']) is bool and value['parse_only'] is parse and type(value['actual_oracle_processes']) is int and value['actual_oracle_processes']==(0 if parse else 1), 'actual05 parse/native process control identity')
        cleanup=value['cleanup'];group=cleanup['pgid']
        require(type(group) is int and group>0, 'actual positive recorded process group');groups.add(group)
        for key in ('before','after','live_remaining'):
            require(type(cleanup[key]) is list, 'recorded process member list')
            for item in cleanup[key]:
                require(type(item) is dict and type(item['pid']) is int and item['pid']>0 and type(item['live']) is bool and type(item['state']) is str, 'recorded process member primitives')
                pids.add(item['pid'])
        for pid in cleanup['zombies_not_claimed_reaped']:
            require(type(pid) is int and pid>0,'recorded zombie identity');pids.add(pid);zombies.add(pid)
        observed[name]=dict(identity=row,parse_only=value['parse_only'],actual_oracle_processes=value['actual_oracle_processes'],exit_code=value['exit_code'],
            process_clean_exit=value['process_clean_exit'],abort_reason=value['abort_reason'],timed_out=value['timed_out'],cleanup=cleanup)
    require(set(observed)=={'parse-process-result.json','native-process-result.json'},'both real05 process records required')
    return groups,pids,dict(records=observed,historical_zombies=sorted(zombies),pid_reuse='Historical records have no starttime; live matching PID/PGID conservatively blocks, no identity/reaping claim')


def verify_capsule385(contract, manifest):
    archive_row=contract['capsule_archive']
    root=Path(contract['capsule_root']);require(root.is_dir() and not any(p.is_symlink() for p in (root,*root.parents)), 'explicit unlinked readonly capsule root')
    path=verify_descriptor(root,archive_row)
    require(manifest['schema']=='standalone-native385-failure-capsule/1' and manifest['file_count']==len(manifest['files'])==contract['capsule_members'], 'real complete385 capsule manifest')
    require(archive_row['size']==manifest['archive_size'] and archive_row['sha256']==manifest['archive_sha256'], 'capsule archive/manifest binding')
    source_members=contract['capsule_non_run_members']
    require(set(source_members)=={name for name in manifest['files'] if not name.startswith('run/')}, 'exact non-run capsule source ledger')
    with zipfile.ZipFile(path) as archive:
        infos=archive.infolist()
        require(len(infos)==len(set(archive.namelist())) and set(archive.namelist())==set(manifest['files']), 'exact unique380 capsule members')
        for info in infos:
            canonical(D,info.filename)
            require(stat.S_IFMT(info.external_attr>>16)==stat.S_IFREG, 'ordinary archived capsule member')
            expected=manifest['files'][info.filename];h=hashlib.sha256();size=0
            with archive.open(info) as stream:
                for block in iter(lambda:stream.read(1048576),b''):h.update(block);size+=len(block)
            require(dict(size=size,sha256=h.hexdigest())==expected, 'capsule CRC/SHA/size')
            if info.filename in source_members:
                binding=source_members[info.filename]
                require(binding['identity']==expected, 'cross-root capsule member descriptor')
                require(binding['storage']=='source', 'all13 actual non-run source origins required')
                actual=verify_descriptor(Path(binding['root']),dict(path=binding['path'],**expected))
                require(pin(actual)==expected, 'actual non-run SOURCE member bytes')
    return dict(members=len(manifest['files']),bytes=sum(row['size'] for row in manifest['files'].values()),non_run_members=len(source_members),CRC_SHA_valid=True,extractions=0,business_semantics_read=False)
