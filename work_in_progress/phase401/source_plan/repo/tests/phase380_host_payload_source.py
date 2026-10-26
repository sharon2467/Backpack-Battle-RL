"""Descriptor graph SOURCE merged into the new oracle host. No entrypoint."""


def _payload_rows(rows):
    if type(rows) not in (list,tuple): raise ValueError('descriptor row list required')
    result={}
    for row in rows:
        if type(row) is not dict or set(row)!={'path','size','sha256'}: raise ValueError('closed descriptor row')
        if row['path'] in result and result[row['path']]!=row: raise ValueError('same source path has conflicting identities')
        result[row['path']]=dict(row)
    return result


def resolve_execute_payloads(source_root,freeze,driver_descriptors=()):
    """Public real resolver, independent of pool/lease/ROOT execution permission."""
    root=directory(source_root); declared=_payload_rows(freeze['files'])
    if type(freeze.get('paths')) is not dict or len(freeze['paths'])!=75: raise ValueError('exact75 SOURCE patches')
    patches=[]
    for name,row in freeze['paths'].items():
        c.safe_path(name)
        source=dict(path=row['after_path'],**row['after'])
        if declared.get(source['path'])!=source: raise ValueError('patch source not in frozen descriptor closure')
        patches.append(dict(target=name,source=source,before=row['before']))
    def frozen(name):
        if name not in declared: raise ValueError('required fixedDATA descriptor absent')
        return dict(declared[name])
    cases={name:frozen(DATA+'/case-A/'+name) for name in NAMES}
    artifacts={'native_combat_capture.gd':dict(freeze['collector']),
        'native_capture_config.json':dict(cases['native_capture_config.json']),
        '.native-random-observer-disposable':frozen(DATA+'/disposable-marker.txt')}
    if artifacts!=freeze.get('artifacts'): raise ValueError('explicit frozen artifact descriptors differ from fixed authority')
    for row in artifacts.values():
        if declared.get(row['path'])!=row: raise ValueError('artifact not in actual frozen descriptor closure')
    bindings={name:dict(freeze[name]) for name in ('collector','schema_module','active_source_tuple','native_source_origin')}
    drivers=_payload_rows(list(declared.values())+list(driver_descriptors)+list(bindings.values()))
    graph=dict(schema='phase380-execute-payloads/1',patches=patches,artifacts=artifacts,case_inputs=cases,
        source_bindings=bindings,driver_sources=[drivers[k] for k in sorted(drivers)],
        labels=dict(profile=freeze['profile'],schema_case=freeze['schema_case']),
        install_limits=dict(files=MAX_INSTALL_PAYLOADS,bytes=MAX_INSTALL_BYTES))
    verify_execute_payloads(root,graph)
    return graph


def verify_execute_payloads(source_root,graph):
    """Read every true execute SOURCE descriptor; no ready/preflight bool input."""
    root=directory(source_root)
    if type(graph) is not dict or set(graph)!={'schema','patches','artifacts','case_inputs','source_bindings','driver_sources','labels','install_limits'} or graph['schema']!='phase380-execute-payloads/1':
        raise ValueError('closed real execute payload graph')
    if graph['install_limits']!=dict(files=MAX_INSTALL_PAYLOADS,bytes=MAX_INSTALL_BYTES): raise ValueError('exact frozen install limits')
    if type(graph['patches']) is not list or len(graph['patches'])!=75: raise ValueError('exact75 execute patch descriptors')
    if set(graph['artifacts'])!={'native_combat_capture.gd','native_capture_config.json','.native-random-observer-disposable'} or set(graph['case_inputs'])!=set(NAMES):
        raise ValueError('complete fixed artifact and case-input destinations')
    targets=set(); install=[]
    for row in graph['patches']:
        if type(row) is not dict or set(row)!={'target','source','before'}: raise ValueError('closed patch payload row')
        c.safe_path(row['target'])
        if row['target'] in targets: raise ValueError('duplicate mutable patch destination')
        targets.add(row['target']); install.append(row['source'])
    for name,row in graph['artifacts'].items():
        c.safe_path(name)
        if name in targets: raise ValueError('overlapping mutable artifact destination')
        targets.add(name);install.append(row)
    if len(install)!=MAX_INSTALL_PAYLOADS or sum(row['size'] for row in install)!=MAX_INSTALL_BYTES:
        raise ValueError('actual complete frozen install corpus count/size differs')
    if graph['artifacts']['native_combat_capture.gd']!=graph['source_bindings'].get('collector') or graph['artifacts']['native_capture_config.json']!=graph['case_inputs']['native_capture_config.json']:
        raise ValueError('reused artifact authority mismatch')
    if set(graph['source_bindings'])!={'collector','schema_module','active_source_tuple','native_source_origin'}: raise ValueError('required explicit source origins')
    drivers=_payload_rows(graph['driver_sources'])
    all_rows=install+list(graph['case_inputs'].values())+list(graph['source_bindings'].values())+list(drivers.values())
    unique=_payload_rows(all_rows)
    if any(drivers.get(row['path'])!=row for row in all_rows): raise ValueError('driver archive missing execute source binding')
    for row in unique.values(): check_source_descriptor(root,row)
    return dict(status='SOURCE_PAYLOAD_IDENTITIES_CHECKED_NOT_EXECUTED',sources=len(unique),install_files=len(install),install_bytes=sum(row['size'] for row in install))


def execute_driver_descriptors(root,config_descriptor,config,freeze):
    rows=list(freeze['files'])+read(descriptor(root,config['source_owner']))['files']
    rows += [config_descriptor,config['source_owner'],config['source_freeze']]
    for review in config['reviews']: rows += [review['receipt'],review['owner']]
    return list(_payload_rows(rows).values())
