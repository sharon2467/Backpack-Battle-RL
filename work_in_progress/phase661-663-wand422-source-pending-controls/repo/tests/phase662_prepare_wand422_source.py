"""Single Source-only assembly. Never import or execute the staged candidate."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import traceback

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/workspace/backpack-python-publish-20261025/python_engine/experimental_nonking')
OUT = ROOT / 'data/phase662-wand422-source'
STAGED = OUT / 'staged'
FILES = (
    'godot_pcg_integer.py', 'headless.py', 'native_replay_v7/__init__.py',
    'native_replay_v7/frame_driver.py', 'native_replay_v7/timer_runtime.py',
    'native_replay_v8/__init__.py', 'native_replay_v8/__main__.py',
    'native_replay_v8/compare.py', 'native_replay_v8/engine.py',
    'native_replay_v8/genuine.py', 'native_replay_v8/histories.py',
    'native_replay_v8/observed.py', 'native_replay_v8/randomness.py',
    'native_replay_v8/state.py', 'original_rng.py',
)
CHANGED = {'native_replay_v8/engine.py', 'headless.py'}
EXPECTED = {
    'native_replay_v8/engine.py': (259634, '2a29367a60d55937bfd139ad16cc4b228c3616acf28f6d37f826c15284f9feff'),
    'headless.py': (35808, '767c9236eb930870c66b221c871a9c530b0af408bb9d6ac740a77a5149e1ebee'),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pin(path):
    data = path.read_bytes()
    return dict(path=str(path), size=len(data), sha256=sha(data))


def save(name, value):
    path = OUT / name
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def functions(text):
    tree = ast.parse(text)
    found = {}
    def walk(body, prefix=''):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found[prefix + node.name] = ast.get_source_segment(text, node)
            elif isinstance(node, ast.ClassDef):
                walk(node.body, prefix + node.name + '.')
    walk(tree.body)
    return found


def assemble():
    if STAGED.exists():
        raise ValueError('one assembly only: staged already exists')
    original = {name: (BASE / name).read_bytes() for name in FILES}
    for name, expected in EXPECTED.items():
        assert (len(original[name]), sha(original[name])) == expected, name
    selection = ROOT / 'data/phase661-next-business-block-selection/public-review.json'
    assert pin(selection)['sha256'] == '9b532554660af871ceef52ddd6d85156e5ff5bd99715e08ae6c652c404d11483'
    job_before = pin(OUT / 'source-job.json')
    assert job_before['sha256'] == 'b5597c364a595e8a786fd141c6a664f79e59851e3a528fbdb03a22da39e51480'
    updated = {name: data.decode('utf-8') for name, data in original.items()}
    patches = []

    def replace(name, before, after):
        assert before != after and updated[name].count(before) == 1, (name, before[:90])
        updated[name] = updated[name].replace(before, after, 1)
        patches.append(dict(file=name, before=before, after=after))

    engine = 'native_replay_v8/engine.py'
    replace(engine, 'CATALOG = {\n', '''CATALOG = {
    422: dict(name="Wand",shape=((0,0),(0,1)),bag=False,magic=True,accessory=True,wood=True,
              cooldown=3.3,mana_threshold=10,lucky_threshold=10,regeneration_threshold=10,
              empower=1,buffs_to_use=1,buff_subset=(105,101,102),socket_count=0,default_gem=None),
''')
    anchor = 'MIXED_BOWL_ENCHANTED_FIXTURE_IDS = frozenset({1,5,11,14,22,32,162,164,231,233,234,385})\n'
    replace(engine, anchor, anchor + 'WAND_FIXTURE_IDS = frozenset({1,11,22,231,422})\n')
    replace(engine, '\ndef validate_fixture(fixture):\n', '''
def validate_wand_fixture(fixture):
    if not any(entry["item_index"] == 422 for side in fixture["sides"] for entry in side["items"]):
        return True
    if (any(side["character_class"] != 0 for side in fixture["sides"])
            or any(entry["item_index"] not in WAND_FIXTURE_IDS
                   for side in fixture["sides"] for entry in side["items"])
            or any(sum(entry["item_index"] == 422 for entry in side["items"]) > 1
                   for side in fixture["sides"])):
        raise ValueError("Wand Source requires class0, finite five-ID fixture and at most one422 per side")
    return True


def validate_fixture(fixture):
''')
    replace(engine, '    validate_enchanted_fixture(fixture)\n    return True\n',
            '    validate_enchanted_fixture(fixture)\n    validate_wand_fixture(fixture)\n    return True\n')
    replace(engine, '\n    def give_most_buffs(self, item, num_buffs, parent=None, available_buffs=range(101, 108)):\n', '''
    def remove_most_buffs(self, item, num_buffs, parent=None, use=False, available_buffs=range(101, 108)):
        if self.items.get(getattr(item, "instance_id", None)) is not item:
            raise ValueError("most-buff removal requires an owned item")
        if (type(use) is not bool or type(num_buffs) not in (int, float)
                or not math.isfinite(num_buffs) or num_buffs < 0):
            raise ValueError("most-buff removal requires strict BOOL use and finite nonnegative source amount")
        target = item.side if use else ("O" if item.side == "P" else "P")
        picked = self.get_most_stacks(target, available_buffs)
        if not picked:
            raise ValueError("empty most-buff candidate selection has no admitted source index")
        index = self.random.randi_range(f"most_buff:{item.instance_id}:{target}", 0, len(picked) - 1)
        stack_type = self._stack_name(picked[index])
        to_remove = min(num_buffs, getattr(self.characters[target], stack_type.lower()))
        if to_remove == 0:
            return None
        if use:
            return self.use_stack(item, target, stack_type, to_remove, parent)
        return self.remove_stack(item, target, stack_type, to_remove, parent)

    def give_most_buffs(self, item, num_buffs, parent=None, available_buffs=range(101, 108)):
''')
    before = '''        char = self.characters[item.side]
        if item.item_index == 385:
'''
    after = '''        char = self.characters[item.side]
        if item.item_index == 422:
            definition = item.definition
            self.give_least_buffs(item, 1, None, definition["buff_subset"])
            # Read live stacks after the complete synchronous least-buff grant.
            if (char.mana >= definition["mana_threshold"]
                    or char.lucky >= definition["lucky_threshold"]
                    or char.regeneration >= definition["regeneration_threshold"]):
                used = self.remove_most_buffs(item, definition["buffs_to_use"], None, True,
                                              definition["buff_subset"])
                self.give_stack(item, item.side, "Empower", definition["empower"],
                                None if used is None else used["id"])
            self.activate(item)
            return
        if item.item_index == 385:
'''
    replace(engine, before, after)
    replace('headless.py',
            'EXPERIMENTAL_NONKING_ITEMS = frozenset({64,162,164,197,199,201,231,385})\n',
            'EXPERIMENTAL_NONKING_ITEMS = frozenset({64,162,164,197,199,201,231,385,422})\n')
    # Parse all text before producing a staged tree; no candidate code is evaluated.
    for text in updated.values():
        ast.parse(text)
    STAGED.mkdir()
    for name in FILES:
        path = STAGED / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(updated[name].encode('utf-8'))
    inverse = dict(updated)
    for change in reversed(patches):
        name, before, after = change['file'], change['before'], change['after']
        assert inverse[name].count(after) == 1, ('inverse', name)
        inverse[name] = inverse[name].replace(after, before, 1)
    assert all(inverse[name].encode('utf-8') == original[name] for name in FILES)
    census = {}
    for name in CHANGED:
        old, new = functions(original[name].decode('utf-8')), functions(updated[name])
        changed = sorted(key for key in old if key in new and old[key] != new[key])
        added, removed = sorted(new.keys() - old.keys()), sorted(old.keys() - new.keys())
        assert removed == []
        if name == engine:
            assert changed == ['CombatEngine.trigger', 'validate_fixture'], changed
            assert added == ['CombatEngine.remove_most_buffs', 'validate_wand_fixture'], added
        else:
            assert changed == [] and added == []
        census[name] = dict(changed=changed, added=added, removed=removed,
                            exact_functions={key: dict(size=len(old[key].encode()), sha256=sha(old[key].encode()))
                                             for key in old if key in new and old[key] == new[key]})
    old_tree, new_tree = ast.parse(original[engine]), ast.parse(updated[engine])
    def catalog(tree):
        assignment = [n for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'CATALOG' for t in n.targets)]
        assert len(assignment) == 1 and isinstance(assignment[0].value, ast.Dict)
        value = assignment[0].value
        return {k.value: ast.dump(v, include_attributes=False) for k, v in zip(value.keys, value.values)}
    old_catalog, new_catalog = catalog(old_tree), catalog(new_tree)
    assert len(old_catalog) == 84 and len(new_catalog) == 85
    assert set(new_catalog) - set(old_catalog) == {422}
    assert all(new_catalog[key] == value for key, value in old_catalog.items())
    unchanged = [name for name in FILES if (STAGED / name).read_bytes() == original[name]]
    assert len(unchanged) == 13 and set(FILES) - set(unchanged) == CHANGED
    compiled = []
    for name in sorted(CHANGED):
        compile((STAGED / name).read_bytes(), str(STAGED / name), 'exec')
        compiled.append(name)
    assert pin(OUT / 'source-job.json') == job_before
    source_refs = [pin(BASE / name) for name in FILES]
    output_refs = [dict(relative_path=name, **pin(STAGED / name)) for name in FILES]
    save('inverse.json', dict(schema='phase662-full-inverse/1', operations=patches,
                             inverse_all15_exact=True,
                             before_files={name: dict(size=len(data),sha256=sha(data)) for name,data in original.items()}))
    with (OUT / 'source.patch').open('x', encoding='utf-8') as stream:
        for name in sorted(CHANGED):
            stream.writelines(difflib.unified_diff(original[name].decode().splitlines(True),
                                                 updated[name].splitlines(True),
                                                 fromfile='public564/' + name, tofile='phase662/' + name))
    save('conservation.json', dict(schema='phase662-source-conservation/1', unchanged_modules=unchanged,
                                  function_census=census, all84_catalog_definitions_exact=True,
                                  new_catalog_count=85, full_inverse_exact=True,
                                  old_trigger_text_restored_by_exact_inverse=True))
    save('candidate-source-freeze.json', dict(schema='phase662-candidate-source-freeze/1',
                                            status='SOURCE_ONLY_NOT_RUNTIME_VALIDATED', files=output_refs))
    save('source-context.json', dict(schema='phase662-source-context/1', base_source=source_refs,
                                    public_selection=pin(selection),
                                    spec=pin(ROOT / 'docs/phase662_wand422_shared_buff_conversion_spec.md'),
                                    implementation_spec=pin(ROOT / 'docs/phase662_wand422_implementation_addendum.md'),
                                    original_pins=pin(OUT / 'original-source-pins.json'),
                                    source_job=job_before, defaults=pin(OUT / 'default-definition.json'),
                                    producer=pin(Path(__file__)),
                                    scope='experimental Source Wand422; formal75 and Native admission unchanged'))
    save('api.json', dict(schema='phase662-production-api/1',
                         public_entry='headless.initialize_experimental_nonking(layout, seed)',
                         public_validation='headless.validate_experimental_nonking_layout(layout)',
                         new_helper='CombatEngine.remove_most_buffs(item,num_buffs,parent=None,use=False,available_buffs=range(101,108))',
                         result='actual event dict with id, or None after a real chooser draw',
                         test_seam='existing CombatEngine.random provider and existing production trigger; no new injection API',
                         finite_ids=[1,11,22,231,422], max_wand_per_side=1,
                         source_job=job_before, independent_acceptance='PENDING'))
    save('generation-result.json', dict(schema='phase662-source-generation-result/1', status='SOURCE_FROZEN_NOT_INDEPENDENTLY_ACCEPTED',
                                       source_generation_attempts=1, compile_objects=compiled, compile_count=2,
                                       candidate_imports=0, helper_calls=0, constructors=0, battles=0,
                                       expected_reads=0, native_calls=0, catalog_registered=85, formal_support=75))


def freeze_owner():
    paths = sorted(path for path in OUT.rglob('*') if path.is_file() and path.name != 'owned-files.json')
    paths += [Path(__file__), ROOT / 'docs/phase662_wand422_implementation_addendum.md']
    save('owned-files.json', dict(schema='phase662-source-owner/1', files=[pin(path) for path in paths]))


if __name__ == '__main__':
    try:
        assemble()
    except Exception as error:
        save('first-error.json', dict(schema='phase662-source-first-error/1', error_type=type(error).__name__,
                                      error=str(error), traceback=traceback.format_exc(), candidate_imports=0,
                                      helper_calls=0, battles=0, native_calls=0))
        freeze_owner()
        raise
    freeze_owner()
    print(json.dumps(dict(status='SOURCE_FROZEN_NOT_INDEPENDENTLY_ACCEPTED', owner=pin(OUT / 'owned-files.json'))))
