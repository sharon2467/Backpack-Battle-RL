"""Expected/control SOURCE helpers; loaded by the actual391 host after descriptor checks."""

TERMINAL_POLICY = 'first-actual-idle-after-at-least-two-future-physics/1'
OBSERVER_VERSION = '7-king-single-A-390'
OBSERVER_PROFILE = 'observer7-390-native-single-king-A/1'


def validate_active_source_tuple(root, freeze):
    row = freeze['active_source_tuple']
    value = read(check_source_descriptor(root, row))
    keys = {'schema', 'profile', 'observer_version', 'terminal_policy', 'fixed_fixture',
            'native_patch', 'producer', 'sink', 'collector', 'schema_module', 'projector_source_origin'}
    if type(value) is not dict or set(value) != keys or value['schema'] != 'phase391-terminal-source-tuple/1':
        raise ValueError('closed actual391 source tuple')
    if (value['profile'], value['observer_version'], value['terminal_policy']) != (OBSERVER_PROFILE, OBSERVER_VERSION, TERMINAL_POLICY):
        raise ValueError('mixed terminal source policy/version')
    if (freeze['profile'], freeze['observer_version'], freeze['terminal_policy'], freeze['run_name']) != (OBSERVER_PROFILE, OBSERVER_VERSION, TERMINAL_POLICY, RUN_NAME):
        raise ValueError('host/freeze terminal policy/version/attempt mismatch')
    declared = _payload_rows(freeze['files'])
    for key in keys - {'schema', 'profile', 'observer_version', 'terminal_policy'}:
        source = value[key]
        if declared.get(source['path']) != source:
            raise ValueError('tuple source outside frozen descriptor graph')
        check_source_descriptor(root, source)
    if value['collector'] != freeze['collector'] or value['schema_module'] != freeze['schema_module']:
        raise ValueError('actual collector/schema tuple binding')
    sink = freeze['paths']['native_random_observer_sink_v7.gd']
    if value['sink'] != dict(path=sink['after_path'], **sink['after']):
        raise ValueError('actual terminal sink tuple binding')
    patch = read(check_source_descriptor(root, value['native_patch']))
    if type(patch) is not dict or set(patch) != {'schema', 'paths', 'producer', 'sink', 'profile', 'observer_version', 'terminal_policy'}:
        raise ValueError('closed actual patch declaration')
    if patch != dict(schema='phase391-native-patch-source/1', paths=freeze['paths'], producer=value['producer'],
                     sink=value['sink'], profile=OBSERVER_PROFILE, observer_version=OBSERVER_VERSION, terminal_policy=TERMINAL_POLICY):
        raise ValueError('actual75 patch tuple disagreement')
    return value


def load_terminal_schema(source_root, freeze):
    """Verify actual regular source bytes before executing this exact schema module."""
    import sys
    from types import ModuleType
    root = directory(source_root)
    validate_active_source_tuple(root, freeze)
    row = freeze['schema_module']
    path = check_source_descriptor(root, row)
    raw = path.read_bytes()
    if len(raw) != row['size'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError('schema changed between descriptor and read')
    name = '_phase391_terminal_schema_' + row['sha256']
    if name in sys.modules:
        raise ValueError('terminal schema already loaded; no cached foreign module')
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    try:
        exec(compile(raw, str(path), 'exec'), module.__dict__)
        if (module.VERSION, module.PROFILE, module.TERMINAL_POLICY) != (OBSERVER_VERSION, OBSERVER_PROFILE, TERMINAL_POLICY):
            raise ValueError('actual executed terminal module version')
        for api in ('validate_terminal_evidence', 'validate_terminal_receipt', 'validate_terminal_diagnostics'):
            if getattr(module.schema, api) is not getattr(module, api):
                raise ValueError('actual module export/delegate identity')
        return module
    finally:
        del sys.modules[name]


def read_terminal_expected_controls(source_root, freeze, capture):
    """Direct actual schema join; twelve lawful names remain unchanged, no model output."""
    module = load_terminal_schema(source_root, freeze)
    identities = {}
    def bounded(name, limit):
        path = member(capture, name)
        info = path.lstat()
        import stat
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError('bounded ordinary expected/control leaf required: ' + name)
        raw = path.read_bytes()
        if len(raw) != info.st_size or len(raw) > limit:
            raise ValueError('control read size drift')
        identities[name] = dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        return raw.decode('utf-8')
    def obj(name, limit=1048576):
        value = module.strict_json_loads(bounded(name, limit))
        if type(value) is not dict:
            raise ValueError('actual expected/control object')
        return value
    def rows(name, limit, row_cap, row_bytes):
        text = bounded(name, limit)
        if not text.endswith('\n'):
            raise ValueError('complete physical JSONL newline required')
        lines = text.splitlines()
        if not 1 <= len(lines) <= row_cap or any(not line or len(line.encode('utf-8')) + 1 > row_bytes for line in lines):
            raise ValueError('bounded nonblank physical JSONL rows')
        return [module.strict_json_loads(line) for line in lines]
    endpoint = obj('king-capture-endpoint.json')
    receipt = obj('observer7-status.json')
    validation = obj('validation.json')
    header = obj('king-clock-checkpoint.json')
    module.exact(header, ('schema', 'lineage', 'environment', 'checkpoint'))
    passes = rows('king-clock-passes.jsonl', 67108864, module.MAX_PASSES, 1048576)
    clock = module.decode_clock(dict(header, passes=passes))
    diagnostics = rows('source-window-diagnostic.jsonl', 1048576, 64, 262144)
    control = module.schema.validate_terminal_diagnostics(diagnostics)
    proof = module.schema.validate_terminal_receipt(endpoint, clock, receipt, control, validation)
    if diagnostics[-1]['clock_passes'] != proof['passes']:
        raise ValueError('FINALIZED header/full actual clock mismatch')
    return dict(schema='phase391-host-terminal-control-proof/1', proof=proof, source_schema=freeze['schema_module'],
                source_tuple=freeze['active_source_tuple'], files=identities, expected_control_only=True,
                model_calls=0, input_bundle_created=False)
