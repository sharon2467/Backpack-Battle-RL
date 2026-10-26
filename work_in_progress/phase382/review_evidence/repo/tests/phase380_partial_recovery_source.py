"""SOURCE replacement for saved partial-install evidence verification."""


def verify_evidence(roots,mapping,input_pins):
    for row in input_pins['files']: evidence_path(roots,row)
    analyzed=analyze_saved_partial(roots['source_root'],roots['failed_run'],roots['previous_run'])
    core=analyzed['core']
    require(set(mapping)==set(core)|{'roots','roots_are'} and all(mapping[k]==v for k,v in core.items()),'exact saved partial map, no synthetic journal or unknown fields')
    require(input_pins==analyzed['input_pins'],'complete exact saved evidence pins')
    require(mapping['known_absent_creates']==sorted(KNOWN_MISSING),'only two proven absent-target creates')
    aliases=mapping['roots'];relocation={aliases[k]:str(roots[k]) for k in roots if k in aliases and aliases[k]!=str(roots[k])}
    failed,failed_data,target,target_data=[analyzed[k] for k in ('failed','failed_data','target','target_data')]
    require(c.inventory(roots['baseline'])==analyzed['base'],'actual baseline full bytes/mode/mtime drift')
    bundle=roots['previous_run']/'output/compaction';proof=read(bundle/'pool-roundtrip.json')
    require(proof.get('status')=='PASS' and map_recorded(proof['run'],relocation)==roots['previous_run'] and map_recorded(proof['pool'],relocation)==roots['pool'] and
        proof['bundle_sha256']==c.digest(bundle/'bundle-manifest.json') and proof['provenance_sha256']==c.digest(roots['previous_run']/'output/pool-provenance.json'),'old READY proof/run/root identities')
    require(c.retained(roots['previous_run'])==read(bundle/'retained-evidence.json') and c.inventory(roots['previous_run']/'output/driver')==read(bundle/'driver-files.json'),'old retained/driver evidence')
    payloads=[]
    for row in mapping['file_differences']:
        payload=evidence_path(roots,row['payload']);payloads.append(('project',row['path'],payload,row['target']))
    before_data=c.index(failed_data)
    for row in mapping['staged_files']:
        payload=evidence_path(roots,row['payload'])
        if before_data[row['target']['path']]!=row['target']:payloads.append(('data',row['target']['path'],payload,row['target']))
    saved=roots['failed_run']/'output/failed-pool-preservation';state=pin(saved/'failed-pool-state.json')
    require(map_recorded(read(saved/'failed-pool-state.json')['run'],relocation)==roots['failed_run'],'exact failed state/run binding')
    return dict(failed=failed,failed_data=failed_data,target=target,target_data=target_data,failed_state=state,payloads=payloads,bundle=bundle,
        relocations=relocation,known_absent_creates=sorted(KNOWN_MISSING))
