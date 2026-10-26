"""New recovery gate only; complete-install mutator stays the frozen375 algorithm."""


def recovery_source_leaf(root, row):
    path = descriptor(root, row)
    regular_target(path)
    return path


def recovery_source_owner(root, row):
    path = recovery_source_leaf(root, row)
    value = read(path)
    rows = value['files']
    require(type(rows) is list and bool(rows), 'nonempty actual owner')
    result = {}
    for leaf in rows:
        require(leaf['path'] not in result, 'unique owned source leaves')
        result[leaf['path']] = pin(recovery_source_leaf(root, leaf))
    return result


def validate_terminal_component_context(root, context_descriptor):
    context = read(recovery_source_leaf(root, context_descriptor))
    require(context.get('schema') == 'root391-bounded-component-context/1' and
            context.get('status') == 'ROOT_391_BOUNDED_COMPONENT_ACCEPTED_LANGUAGE_AND_NATIVE_PENDING', 'real bounded component Root context')
    for key in ('READY_allowed','inputbuilds_allowed','models','native','restore_allowed'):
        require(type(context.get(key)) is int and context[key] == 0, 'component context grants no operations')
    sf = recovery_source_leaf(root, context['source_freeze'])
    so = recovery_source_owner(root, context['source_owner'])
    require(so.get(context['source_freeze']['path']) == pin(sf), 'owned actual391 freeze')
    freeze = read(sf)
    require(freeze['active_source_tuple'] == context['source_tuple'], 'actual391 terminal tuple context')
    recovery_source_leaf(root, context['source_tuple'])
    review_path = recovery_source_leaf(root, context['independent_review'])
    owned = recovery_source_owner(root, context['independent_owner'])
    review = read(review_path)
    require(owned.get(context['independent_review']['path']) == pin(review_path) and
            review.get('status') == 'INDEPENDENT392_FIRST_ELIGIBLE_IDLE_SOURCE_ACCEPTED_ROOT_PENDING' and
            review.get('source_freeze') == context['source_freeze'], 'owned real392 reviewed391 component')
    require(all(type(review.get(key)) is int and review[key] == 0 for key in ('native','models')), 'bounded component zero native/model')
    return context


def source_gate(source_root, config_descriptor, action):
    root = directory(source_root)
    config = read(recovery_source_leaf(root, config_descriptor))
    require(config.get('schema') == 'phase395-root-pool-recovery/1' and config.get('action') == action and action in ('restore','commit_ready'), 'separate exact395 recovery action')
    require(config.get('root_'+action+'_authorized') is True, 'explicit Root action required')
    require(all(type(config.get(k)) is int and config[k] == 0 for k in ('native_allowed','models_allowed','projection_allowed')), 'strictINT0 non-recovery permissions')
    freeze_path = recovery_source_leaf(root, config['source_freeze'])
    require(config['source_freeze']['path'] == SOURCE+'/combined-source-freeze.json', 'separate395 recovery freeze')
    freeze = read(freeze_path)
    require(freeze.get('schema') == 'phase395-complete-install-recovery-SOURCE/1', 'closed complete-install SOURCE family')
    declared = {}
    for row in freeze['files']:
        require(row['path'] not in declared, 'unique recovery freeze leaves')
        recovery_source_leaf(root, row); declared[row['path']] = row
    leaves = recovery_source_owner(root, config['source_owner'])
    require(leaves.get(str(Path(__file__).absolute().relative_to(root))) == pin(Path(__file__)) and leaves.get(config['source_freeze']['path']) == pin(freeze_path), 'owner covers executing recovery and its freeze')
    for row in freeze['import_closure']:
        require(declared.get(row['path']) == row and leaves.get(row['path']) == {k:row[k] for k in ('size','sha256')}, 'all actual import sources owned/frozen')
    reviews = config.get('reviews')
    require(type(reviews) is list and bool(reviews), 'independent396 recovery SOURCE review required')
    for review in reviews:
        path = recovery_source_leaf(root, review['receipt']); owned = recovery_source_owner(root, review['owner']); value = read(path)
        require(owned.get(review['receipt']['path']) == pin(path) and value.get('status') == REVIEW_STATUS and value.get('source_freeze') == config['source_freeze'], 'actual owned396 recovery SOURCE closure')
        require(all(type(value.get(k)) is int and value[k] == 0 for k in ('native','models')), 'recovery SOURCE review grants no native/model')
    for key,name in (('restore_map',MAP),('input_pins',INPUT_PINS)):
        require(config.get(key) == declared.get(name) and config[key]['path'] == name, 'exact actual map/input binding')
    context = freeze['terminal_component_context']
    require(config.get('terminal_component_context') == context and declared.get(context['path']) == context, 'Root/freeze actual component context descriptor')
    validate_terminal_component_context(root, context)
    if action == 'commit_ready':
        recovery_source_leaf(root, config['restore_receipt'])
        recovery_source_leaf(root, config['independent_readback']['receipt'])
        recovery_source_owner(root, config['independent_readback']['owner'])
    return root,config
