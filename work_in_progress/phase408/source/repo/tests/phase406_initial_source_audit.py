"""406 readonly presence/source-route audit. Fullschema and all engine execution remain closed."""
SOURCE = 'data/phase406-initial-audit-source'
MODULE = 'tests/phase406_initial_source_audit.py'
SOURCE_ARTIFACTS = ['docs/phase406_readonly_initial_audit_implementation_spec.md',
 'tests/phase406_initial_audit_template.py',
 'tests/phase406_prepare_audit_source.py',
 'tests/phase406_initial_source_audit.py',
 'data/phase406-initial-audit-source/api-contract.json',
 'data/phase406-initial-audit-source/static-author-checks.json',
 'data/phase406-initial-audit-source/source-constraints.json']
REVIEW_STATUS = 'INDEPENDENT407_STDLIB_INITIAL_AUDIT_SOURCE_ACCEPTED_ROOT_PENDING'
ROOT402 = 'data/phase401-root-native-attempt06/independent402-accepted.json'
REVIEW402 = 'data/phase402-independent-final/review.json'
OWNER402 = 'data/phase402-independent-final/owned-files.json'
REVIEW405 = 'data/phase405-independent-design-review/review.json'
OWNER405 = 'data/phase405-independent-design-review/owned-files.json'
FIXED_RUN = '/workspace/native-combat-20261013/runs/original027-king-single-A-20261026-attempt06'
PERMISSION_KEYS = ['models',
 'inputbuild',
 'projection',
 'expected_reads',
 'new_native',
 'SUT_calls',
 'schema_calls',
 'restore',
 'READY']
TOTAL_BYTES = 268435456
INPUT_NAMES = ['fixture.json',
 'player_fixture.json',
 'observer7-input.jsonl',
 'observer7-lineage.jsonl',
 'observer7-metadata.jsonl',
 'observer7-primitives.jsonl',
 'king-clock-checkpoint.json',
 'king-clock-passes.jsonl',
 'king-input-facts.json',
 'king-ui-authority.jsonl',
 'king-rng-checkpoint.json',
 'king-slot-bindings.json']
CHANNELS = {'observer7-input.jsonl': 'input',
 'observer7-lineage.jsonl': 'lineage',
 'observer7-metadata.jsonl': 'metadata',
 'observer7-primitives.jsonl': 'primitive'}
PHASES = [['pre_prepare', 'Core/Game.gd::prepareItems'], ['pre_activate', 'Core/Game.gd::activateItems']]
TIMER_ROLES = ['tick:P',
 'tick:O',
 'buff:P:100',
 'buff:P:101',
 'buff:P:102',
 'buff:P:103',
 'buff:P:104',
 'buff:P:105',
 'buff:P:106',
 'buff:P:107',
 'buff:P:108',
 'buff:P:109',
 'buff:P:110',
 'buff:O:100',
 'buff:O:101',
 'buff:O:102',
 'buff:O:103',
 'buff:O:104',
 'buff:O:105',
 'buff:O:106',
 'buff:O:107',
 'buff:O:108',
 'buff:O:109',
 'buff:O:110',
 'fatigue:start',
 'fatigue:tick',
 'aux:P:battleRageTimer',
 'aux:P:autoRageTimer',
 'aux:O:battleRageTimer',
 'aux:O:autoRageTimer',
 'invu:P',
 'invu:O',
 'king_buff:P:12',
 'king_hide:P:12',
 'king_drag:P:12']
FIVE_TIMER_ROLES = ['invu:P', 'invu:O', 'king_buff:P:12', 'king_hide:P:12', 'king_drag:P:12']
SLOT_PLAN = [{'cells': [[0, 0], [1, 0], [0, 1], [1, 1]],
  'f': 0,
  'input_slot': 0,
  'instance_id': 'P:0',
  'item_index': 11,
  'side': 'P',
  'x': 0,
  'y': 0},
 {'cells': [[2, 0], [3, 0], [2, 1], [3, 1]],
  'f': 0,
  'input_slot': 1,
  'instance_id': 'P:1',
  'item_index': 11,
  'side': 'P',
  'x': 2,
  'y': 0},
 {'cells': [[4, 0], [5, 0], [4, 1], [5, 1]],
  'f': 0,
  'input_slot': 2,
  'instance_id': 'P:2',
  'item_index': 11,
  'side': 'P',
  'x': 4,
  'y': 0},
 {'cells': [[6, 0], [7, 0], [6, 1], [7, 1]],
  'f': 0,
  'input_slot': 3,
  'instance_id': 'P:3',
  'item_index': 11,
  'side': 'P',
  'x': 6,
  'y': 0},
 {'cells': [[0, 2], [1, 2], [0, 3], [1, 3]],
  'f': 0,
  'input_slot': 4,
  'instance_id': 'P:4',
  'item_index': 11,
  'side': 'P',
  'x': 0,
  'y': 2},
 {'cells': [[2, 2], [3, 2], [2, 3], [3, 3]],
  'f': 0,
  'input_slot': 5,
  'instance_id': 'P:5',
  'item_index': 11,
  'side': 'P',
  'x': 2,
  'y': 2},
 {'cells': [[4, 2], [5, 2], [4, 3], [5, 3]],
  'f': 0,
  'input_slot': 6,
  'instance_id': 'P:6',
  'item_index': 11,
  'side': 'P',
  'x': 4,
  'y': 2},
 {'cells': [[6, 2], [7, 2], [6, 3], [7, 3]],
  'f': 0,
  'input_slot': 7,
  'instance_id': 'P:7',
  'item_index': 11,
  'side': 'P',
  'x': 6,
  'y': 2},
 {'cells': [[0, 4], [1, 4], [0, 5], [1, 5]],
  'f': 0,
  'input_slot': 8,
  'instance_id': 'P:8',
  'item_index': 11,
  'side': 'P',
  'x': 0,
  'y': 4},
 {'cells': [[2, 4], [3, 4], [2, 5], [3, 5]],
  'f': 0,
  'input_slot': 9,
  'instance_id': 'P:9',
  'item_index': 11,
  'side': 'P',
  'x': 2,
  'y': 4},
 {'cells': [[4, 4], [5, 4], [4, 5], [5, 5]],
  'f': 0,
  'input_slot': 10,
  'instance_id': 'P:10',
  'item_index': 11,
  'side': 'P',
  'x': 4,
  'y': 4},
 {'cells': [[6, 4], [7, 4], [6, 5], [7, 5]],
  'f': 0,
  'input_slot': 11,
  'instance_id': 'P:11',
  'item_index': 11,
  'side': 'P',
  'x': 6,
  'y': 4},
 {'cells': [[2, 1], [3, 1], [2, 2], [3, 2], [2, 3], [3, 3]],
  'f': 0,
  'input_slot': 12,
  'instance_id': 'P:12',
  'item_index': 262,
  'side': 'P',
  'x': 2,
  'y': 1},
 {'cells': [[1, 1]],
  'f': 0,
  'input_slot': 13,
  'instance_id': 'P:13',
  'item_index': 22,
  'side': 'P',
  'x': 1,
  'y': 1},
 {'cells': [[1, 2]],
  'f': 0,
  'input_slot': 14,
  'instance_id': 'P:14',
  'item_index': 22,
  'side': 'P',
  'x': 1,
  'y': 2},
 {'cells': [[1, 3]],
  'f': 0,
  'input_slot': 15,
  'instance_id': 'P:15',
  'item_index': 22,
  'side': 'P',
  'x': 1,
  'y': 3},
 {'cells': [[4, 1], [4, 2]],
  'f': 0,
  'input_slot': 16,
  'instance_id': 'P:16',
  'item_index': 1,
  'side': 'P',
  'x': 4,
  'y': 1},
 {'cells': [[4, 3]],
  'f': 0,
  'input_slot': 17,
  'instance_id': 'P:17',
  'item_index': 22,
  'side': 'P',
  'x': 4,
  'y': 3},
 {'cells': [[6, 0], [6, 1]],
  'f': 0,
  'input_slot': 18,
  'instance_id': 'P:18',
  'item_index': 19,
  'side': 'P',
  'x': 6,
  'y': 0},
 {'cells': [[6, 4], [7, 4], [6, 5], [7, 5]],
  'f': 0,
  'input_slot': 19,
  'instance_id': 'P:19',
  'item_index': 4,
  'side': 'P',
  'x': 6,
  'y': 4},
 {'cells': [[0, 0], [1, 0], [0, 1], [1, 1]],
  'f': 0,
  'input_slot': 0,
  'instance_id': 'O:0',
  'item_index': 11,
  'side': 'O',
  'x': 0,
  'y': 0},
 {'cells': [[2, 0], [3, 0], [2, 1], [3, 1]],
  'f': 0,
  'input_slot': 1,
  'instance_id': 'O:1',
  'item_index': 11,
  'side': 'O',
  'x': 2,
  'y': 0},
 {'cells': [[4, 0], [5, 0], [4, 1], [5, 1]],
  'f': 0,
  'input_slot': 2,
  'instance_id': 'O:2',
  'item_index': 11,
  'side': 'O',
  'x': 4,
  'y': 0},
 {'cells': [[6, 0], [7, 0], [6, 1], [7, 1]],
  'f': 0,
  'input_slot': 3,
  'instance_id': 'O:3',
  'item_index': 11,
  'side': 'O',
  'x': 6,
  'y': 0},
 {'cells': [[0, 2], [1, 2], [0, 3], [1, 3]],
  'f': 0,
  'input_slot': 4,
  'instance_id': 'O:4',
  'item_index': 11,
  'side': 'O',
  'x': 0,
  'y': 2},
 {'cells': [[2, 2], [3, 2], [2, 3], [3, 3]],
  'f': 0,
  'input_slot': 5,
  'instance_id': 'O:5',
  'item_index': 11,
  'side': 'O',
  'x': 2,
  'y': 2},
 {'cells': [[4, 2], [5, 2], [4, 3], [5, 3]],
  'f': 0,
  'input_slot': 6,
  'instance_id': 'O:6',
  'item_index': 11,
  'side': 'O',
  'x': 4,
  'y': 2},
 {'cells': [[6, 2], [7, 2], [6, 3], [7, 3]],
  'f': 0,
  'input_slot': 7,
  'instance_id': 'O:7',
  'item_index': 11,
  'side': 'O',
  'x': 6,
  'y': 2},
 {'cells': [[0, 4], [1, 4], [0, 5], [1, 5]],
  'f': 0,
  'input_slot': 8,
  'instance_id': 'O:8',
  'item_index': 11,
  'side': 'O',
  'x': 0,
  'y': 4},
 {'cells': [[2, 4], [3, 4], [2, 5], [3, 5]],
  'f': 0,
  'input_slot': 9,
  'instance_id': 'O:9',
  'item_index': 11,
  'side': 'O',
  'x': 2,
  'y': 4},
 {'cells': [[4, 4], [5, 4], [4, 5], [5, 5]],
  'f': 0,
  'input_slot': 10,
  'instance_id': 'O:10',
  'item_index': 11,
  'side': 'O',
  'x': 4,
  'y': 4},
 {'cells': [[6, 4], [7, 4], [6, 5], [7, 5]],
  'f': 0,
  'input_slot': 11,
  'instance_id': 'O:11',
  'item_index': 11,
  'side': 'O',
  'x': 6,
  'y': 4},
 {'cells': [[1, 1]],
  'f': 0,
  'input_slot': 12,
  'instance_id': 'O:13',
  'item_index': 22,
  'side': 'O',
  'x': 1,
  'y': 1},
 {'cells': [[1, 2]],
  'f': 0,
  'input_slot': 13,
  'instance_id': 'O:14',
  'item_index': 22,
  'side': 'O',
  'x': 1,
  'y': 2},
 {'cells': [[1, 3]],
  'f': 0,
  'input_slot': 14,
  'instance_id': 'O:15',
  'item_index': 22,
  'side': 'O',
  'x': 1,
  'y': 3},
 {'cells': [[4, 1], [4, 2]],
  'f': 0,
  'input_slot': 15,
  'instance_id': 'O:16',
  'item_index': 1,
  'side': 'O',
  'x': 4,
  'y': 1},
 {'cells': [[4, 3]],
  'f': 0,
  'input_slot': 16,
  'instance_id': 'O:17',
  'item_index': 22,
  'side': 'O',
  'x': 4,
  'y': 3},
 {'cells': [[6, 0], [6, 1]],
  'f': 0,
  'input_slot': 17,
  'instance_id': 'O:18',
  'item_index': 19,
  'side': 'O',
  'x': 6,
  'y': 0},
 {'cells': [[6, 4], [7, 4], [6, 5], [7, 5]],
  'f': 0,
  'input_slot': 18,
  'instance_id': 'O:19',
  'item_index': 4,
  'side': 'O',
  'x': 6,
  'y': 4}]
FIXED_FIXTURE = {'below_master': True,
 'game_version': '1.1.8',
 'mode': 'Unranked',
 'round': 1,
 'rules': 'default',
 'schema': 1,
 'sides': [{'character_class': 0,
            'hp': 360.0,
            'items': [{'f': 0, 'instance_id': 'P:0', 'item_index': 11, 'x': 0, 'y': 0},
                      {'f': 0, 'instance_id': 'P:1', 'item_index': 11, 'x': 2, 'y': 0},
                      {'f': 0, 'instance_id': 'P:2', 'item_index': 11, 'x': 4, 'y': 0},
                      {'f': 0, 'instance_id': 'P:3', 'item_index': 11, 'x': 6, 'y': 0},
                      {'f': 0, 'instance_id': 'P:4', 'item_index': 11, 'x': 0, 'y': 2},
                      {'f': 0, 'instance_id': 'P:5', 'item_index': 11, 'x': 2, 'y': 2},
                      {'f': 0, 'instance_id': 'P:6', 'item_index': 11, 'x': 4, 'y': 2},
                      {'f': 0, 'instance_id': 'P:7', 'item_index': 11, 'x': 6, 'y': 2},
                      {'f': 0, 'instance_id': 'P:8', 'item_index': 11, 'x': 0, 'y': 4},
                      {'f': 0, 'instance_id': 'P:9', 'item_index': 11, 'x': 2, 'y': 4},
                      {'f': 0, 'instance_id': 'P:10', 'item_index': 11, 'x': 4, 'y': 4},
                      {'f': 0, 'instance_id': 'P:11', 'item_index': 11, 'x': 6, 'y': 4},
                      {'f': 0, 'instance_id': 'P:12', 'item_index': 262, 'x': 2, 'y': 1},
                      {'f': 0, 'instance_id': 'P:13', 'item_index': 22, 'x': 1, 'y': 1},
                      {'f': 0, 'instance_id': 'P:14', 'item_index': 22, 'x': 1, 'y': 2},
                      {'f': 0, 'instance_id': 'P:15', 'item_index': 22, 'x': 1, 'y': 3},
                      {'f': 0, 'instance_id': 'P:16', 'item_index': 1, 'x': 4, 'y': 1},
                      {'f': 0, 'instance_id': 'P:17', 'item_index': 22, 'x': 4, 'y': 3},
                      {'f': 0, 'instance_id': 'P:18', 'item_index': 19, 'x': 6, 'y': 0},
                      {'f': 0, 'instance_id': 'P:19', 'item_index': 4, 'x': 6, 'y': 4}],
            'side': 'P',
            'stamina': 5.0},
           {'character_class': 0,
            'hp': 380.0,
            'items': [{'f': 0, 'instance_id': 'O:0', 'item_index': 11, 'x': 0, 'y': 0},
                      {'f': 0, 'instance_id': 'O:1', 'item_index': 11, 'x': 2, 'y': 0},
                      {'f': 0, 'instance_id': 'O:2', 'item_index': 11, 'x': 4, 'y': 0},
                      {'f': 0, 'instance_id': 'O:3', 'item_index': 11, 'x': 6, 'y': 0},
                      {'f': 0, 'instance_id': 'O:4', 'item_index': 11, 'x': 0, 'y': 2},
                      {'f': 0, 'instance_id': 'O:5', 'item_index': 11, 'x': 2, 'y': 2},
                      {'f': 0, 'instance_id': 'O:6', 'item_index': 11, 'x': 4, 'y': 2},
                      {'f': 0, 'instance_id': 'O:7', 'item_index': 11, 'x': 6, 'y': 2},
                      {'f': 0, 'instance_id': 'O:8', 'item_index': 11, 'x': 0, 'y': 4},
                      {'f': 0, 'instance_id': 'O:9', 'item_index': 11, 'x': 2, 'y': 4},
                      {'f': 0, 'instance_id': 'O:10', 'item_index': 11, 'x': 4, 'y': 4},
                      {'f': 0, 'instance_id': 'O:11', 'item_index': 11, 'x': 6, 'y': 4},
                      {'f': 0, 'instance_id': 'O:13', 'item_index': 22, 'x': 1, 'y': 1},
                      {'f': 0, 'instance_id': 'O:14', 'item_index': 22, 'x': 1, 'y': 2},
                      {'f': 0, 'instance_id': 'O:15', 'item_index': 22, 'x': 1, 'y': 3},
                      {'f': 0, 'instance_id': 'O:16', 'item_index': 1, 'x': 4, 'y': 1},
                      {'f': 0, 'instance_id': 'O:17', 'item_index': 22, 'x': 4, 'y': 3},
                      {'f': 0, 'instance_id': 'O:18', 'item_index': 19, 'x': 6, 'y': 0},
                      {'f': 0, 'instance_id': 'O:19', 'item_index': 4, 'x': 6, 'y': 4}],
            'side': 'O',
            'stamina': 5.0}]}
STATIC_PINS = {'/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Core/Buff.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                           'Battles/Core/Buff.gd',
                                                                                   'sha256': '3efabb72eb0b337e30ebc924347aba40bd1039a3c5f718b761b0ee78b48ab8bb',
                                                                                   'size': 8827},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Core/Character.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                                'Battles/Core/Character.gd',
                                                                                        'sha256': 'dc372965eaa048657caa1646d70aba85ff9b4b9677565eaa480bc195de027496',
                                                                                        'size': 48033},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Core/Character.tscn': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                                  'Battles/Core/Character.tscn',
                                                                                          'sha256': '5a6e1a99539975a7664e651fa32ed078f1017ba157ce1247a75fecd8266c97e9',
                                                                                          'size': 49260},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Core/Game.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                           'Battles/Core/Game.gd',
                                                                                   'sha256': 'f3688bfdf39b95a8ed6a77d9a7ad058a95a0aaa4bcb6d297bc953425add4b9c9',
                                                                                   'size': 145148},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Interface/CombatTimer/CombatTimer.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                                                   'Battles/Interface/CombatTimer/CombatTimer.gd',
                                                                                                           'sha256': '3e1bb3ac33ae78b399d98cfd7bdd6ddb35a337d3afa9f3347af660757cd3b7fd',
                                                                                                           'size': 5769},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/KingGoobert.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                                             'Battles/Items/Exclusive/KingGoobert.gd',
                                                                                                     'sha256': '2f852255072386a57757bceea38a9f5825e0d1299b6fa8ce2c55b14827385d0f',
                                                                                                     'size': 1581},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Exclusive/KingGoobert.tscn': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                                               'Battles/Items/Exclusive/KingGoobert.tscn',
                                                                                                       'sha256': '853c83082edf0086f21c518075cf5701d93d88669e712df9094856cee6d89c8c',
                                                                                                       'size': 4541},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Food.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                            'Battles/Items/Food.gd',
                                                                                    'sha256': 'e0ff858b55f1f5a2d8e1b06ee155a4f7444ba7f4cd903bbee2b09780bfb20a23',
                                                                                    'size': 187},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Goobert.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                               'Battles/Items/Goobert.gd',
                                                                                       'sha256': '8fda35f3740fe787231d4c69c38eaab1938127c1a01e076df70252cc4212e723',
                                                                                       'size': 1076},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/Item.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                            'Battles/Items/Item.gd',
                                                                                    'sha256': '7d2bf930d1a0d2ccdf57ccbbc4bbd4c9a3b985a210c42ec8cfa6291e8aae780f',
                                                                                    'size': 170717},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Items/ItemDescriptor.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                                      'Battles/Items/ItemDescriptor.gd',
                                                                                              'sha256': '5c4959baed459c1981bf0fb9c2d39ace7f99f916925b03b05e3359cd55694794',
                                                                                              'size': 8254},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Utility/AutoHideParticles.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                                           'Battles/Utility/AutoHideParticles.gd',
                                                                                                   'sha256': 'c18ceb3f6a489fd1fc69329155a182e1a658804c36e14651ecc546b450c53503',
                                                                                                   'size': 531},
 '/workspace/godotsteam-startup-20261013/baseline/Backpack Battles/Utility/Util.gd': {'path': '/workspace/godotsteam-startup-20261013/baseline/Backpack '
                                                                                              'Battles/Utility/Util.gd',
                                                                                      'sha256': '596e7f7a9308ea03957e5c9f6e5cb43aa1591e1e0fd13217e2f2c70368970a36',
                                                                                      'size': 44381},
 'data/phase332-king-fresh-source-interface/source-excerpts.json': {'path': 'data/phase332-king-fresh-source-interface/source-excerpts.json',
                                                                    'sha256': '868df5608dd48fc0e29c820952fa7eda1c9c6c074a54a2ad70d9a0399e8a5e31',
                                                                    'size': 17330},
 'data/phase349-king-fresh-source/source-defaults-and-topology-contract.json': {'path': 'data/phase349-king-fresh-source/source-defaults-and-topology-contract.json',
                                                                                'sha256': 'd0fe25ca7998463a75b324882fe0b6b50019b661ec13c4afb9340b2b9088954b',
                                                                                'size': 4363},
 'data/phase359-king-producer-source/after-source/Core/Buff.gd': {'path': 'data/phase359-king-producer-source/after-source/Core/Buff.gd',
                                                                  'sha256': 'a1bfe97c556bfa3b3110988ec7d4f78cbefb7a1ddc2e2d80f31fcb968e817916',
                                                                  'size': 13374},
 'data/phase359-king-producer-source/after-source/Core/Character.gd': {'path': 'data/phase359-king-producer-source/after-source/Core/Character.gd',
                                                                       'sha256': '4e37b2f5d044e015be5dd75fca37577bdb9fc870dd2e32cad5198c36649df984',
                                                                       'size': 55679},
 'data/phase359-king-producer-source/after-source/Core/Game.gd': {'path': 'data/phase359-king-producer-source/after-source/Core/Game.gd',
                                                                  'sha256': 'fafe9612858a25b95d8d6149531b50869dbd9709719bd5d2ab6b070b6b8283b1',
                                                                  'size': 145943},
 'data/phase359-king-producer-source/after-source/Interface/CombatTimer/CombatTimer.gd': {'path': 'data/phase359-king-producer-source/after-source/Interface/CombatTimer/CombatTimer.gd',
                                                                                          'sha256': '70d396e088ac50aac7bd16165cc264ad8917a633fec9fa00d383f911f9936dd0',
                                                                                          'size': 8469},
 'data/phase359-king-producer-source/after-source/Items/Exclusive/KingGoobert.gd': {'path': 'data/phase359-king-producer-source/after-source/Items/Exclusive/KingGoobert.gd',
                                                                                    'sha256': 'd40b72f75f8455c407fb0425520396139f6e8f9213449c9a86368ad21eb4fcf5',
                                                                                    'size': 3101},
 'data/phase359-king-producer-source/after-source/Items/Food.gd': {'path': 'data/phase359-king-producer-source/after-source/Items/Food.gd',
                                                                   'sha256': '07a477dc16365fa0d5e8cfaca3cf9aacaca76eaef4b9d3d05740b5f874340d37',
                                                                   'size': 337},
 'data/phase359-king-producer-source/after-source/Items/Goobert.gd': {'path': 'data/phase359-king-producer-source/after-source/Items/Goobert.gd',
                                                                      'sha256': '7a7b70e9a230b551feca7e00df2fe5e241b97c7aeb15f060e792c15ff4015ebb',
                                                                      'size': 1579},
 'data/phase359-king-producer-source/after-source/Items/Item.gd': {'path': 'data/phase359-king-producer-source/after-source/Items/Item.gd',
                                                                   'sha256': '2fc1d658db352a7ecae8c2bfb60640a019284992a9c5f9a14c87baea50721631',
                                                                   'size': 178363},
 'data/phase359-king-producer-source/after-source/Items/ItemDescriptor.gd': {'path': 'data/phase359-king-producer-source/after-source/Items/ItemDescriptor.gd',
                                                                             'sha256': '710a3dd4cf4d172d46771ed04b743fa9e0d8ab266715443e2c4907b459b7f032',
                                                                             'size': 8740},
 'data/phase359-king-producer-source/after-source/Utility/AutoHideParticles.gd': {'path': 'data/phase359-king-producer-source/after-source/Utility/AutoHideParticles.gd',
                                                                                  'sha256': 'be98d47071983af16d9cb044ab54834336025522298e07dba65eadcf1d63771b',
                                                                                  'size': 3282},
 'data/phase359-king-producer-source/after-source/Utility/Util.gd': {'path': 'data/phase359-king-producer-source/after-source/Utility/Util.gd',
                                                                     'sha256': 'd437e9338c8c4587c0cddd29e848bef54e8b621169dd364ceaa341fbc7a1e507',
                                                                     'size': 46276},
 'data/phase391-terminal-source/after-source/native_random_observer_sink_v7.gd': {'path': 'data/phase391-terminal-source/after-source/native_random_observer_sink_v7.gd',
                                                                                  'sha256': '999e0043a653067a962819cf81340b0dad745fa2148bbfab7724d7948a6a21ea',
                                                                                  'size': 104333},
 'data/phase391-terminal-source/api-contract.json': {'path': 'data/phase391-terminal-source/api-contract.json',
                                                     'sha256': 'c8ef98ca7a39a0d97d85e5744da96d5730867b13ddfe8a40ac08452b61197ef5',
                                                     'size': 2471},
 'data/phase391-terminal-source/collector.gd': {'path': 'data/phase391-terminal-source/collector.gd',
                                                'sha256': 'f05bbf6b0e7277b5a342553d3a8d3c842f3efa6526f0b85948bd003837ac74ce',
                                                'size': 64928},
 'data/phase391-terminal-source/native-patch-source.json': {'path': 'data/phase391-terminal-source/native-patch-source.json',
                                                            'sha256': 'e889a9faf1669706732ceb72937011d5867f3094ca503b7997ff311b7c1002de',
                                                            'size': 30584},
 'data/phase391-terminal-source/source-tuple.json': {'path': 'data/phase391-terminal-source/source-tuple.json',
                                                     'sha256': '883e9b20dfb4c268cd265910ad7adedc403aac785287f2f39f859cdcdac8f8e6',
                                                     'size': 1551},
 'data/phase401-root-native-attempt06/independent402-accepted.json': {'path': 'data/phase401-root-native-attempt06/independent402-accepted.json',
                                                                      'sha256': 'cabf6a704ec10e4fa1322ed3051e280ade500186b938de33bb6ddf4704812021',
                                                                      'size': 993},
 'data/phase402-independent-final/owned-files.json': {'path': 'data/phase402-independent-final/owned-files.json',
                                                      'sha256': 'ec599ca3a5cd803ef918d62007f877f41e121ab276993d123017f5a9abd33456',
                                                      'size': 7529},
 'data/phase402-independent-final/review.json': {'path': 'data/phase402-independent-final/review.json',
                                                 'sha256': '278776b72d664d2925988e09807fb9842af6cdb93df9950e786ff4b59cc838fd',
                                                 'size': 23995},
 'data/phase403-genuine-input-model-design/owned-files.json': {'path': 'data/phase403-genuine-input-model-design/owned-files.json',
                                                               'sha256': '9c1a6efafb7204440f80b3868ba719f986b880cf95b7639f68fee93a21a409d4',
                                                               'size': 1157},
 'data/phase403-independent-design-review/owned-files.json': {'path': 'data/phase403-independent-design-review/owned-files.json',
                                                              'sha256': '887761ee0c4e01109702a692042746daab7c8b1fef8dd4fa45c05cda2911233c',
                                                              'size': 1819},
 'data/phase403-independent-design-review/review.json': {'path': 'data/phase403-independent-design-review/review.json',
                                                         'sha256': '854e23cf12a63a2f7a8dbecc85730dbd99dae7f58a20afef405c7e7b30e44108',
                                                         'size': 8295},
 'data/phase405-independent-design-review/owned-files.json': {'path': 'data/phase405-independent-design-review/owned-files.json',
                                                              'sha256': 'd7dddd89516c7c33ce62c1664a0b6ea48070a3834304c28a6ba7ef2be26aa1cc',
                                                              'size': 900},
 'data/phase405-independent-design-review/review.json': {'path': 'data/phase405-independent-design-review/review.json',
                                                         'sha256': 'd22e84ad17eec0b0aca96910548e6a25da18b709149d51574eb4f944a8a86310',
                                                         'size': 6644},
 'data/phase405-initial-source-feasibility-design/field-obligation-manifest.json': {'path': 'data/phase405-initial-source-feasibility-design/field-obligation-manifest.json',
                                                                                    'sha256': '7a78fdcb5125eecf5fd16f542ad35a947978959f5b00aa7fa87ea01ae22466a9',
                                                                                    'size': 2751},
 'data/phase405-initial-source-feasibility-design/finite-source-allowset.json': {'path': 'data/phase405-initial-source-feasibility-design/finite-source-allowset.json',
                                                                                 'sha256': '8bf88370cc938cb27e395e3f2f4db04b2deb439561ccbb897a01ffde662661e6',
                                                                                 'size': 16142},
 'data/phase405-initial-source-feasibility-design/owned-files.json': {'path': 'data/phase405-initial-source-feasibility-design/owned-files.json',
                                                                      'sha256': '323b672eb761f85dbce98d243a2e48e36912f3e7a76a49c93857e49c4cb6dc1f',
                                                                      'size': 1181},
 'data/phase405-initial-source-feasibility-design/source-api-pins.json': {'path': 'data/phase405-initial-source-feasibility-design/source-api-pins.json',
                                                                          'sha256': '61e671aec5fd86f19fb78238274a728fafb6aeaf575d2abf34b5e8c9705c3f5f',
                                                                          'size': 10791},
 'data/phase405-initial-source-feasibility-design/summary.json': {'path': 'data/phase405-initial-source-feasibility-design/summary.json',
                                                                  'sha256': '7c917dab2e72b458c3e1d99d9aabf23ddc91db14a28eee2ccf09dd3c41ff09b5',
                                                                  'size': 1627},
 'docs/phase403_genuine_input_and_independent_model_design_spec.md': {'path': 'docs/phase403_genuine_input_and_independent_model_design_spec.md',
                                                                      'sha256': 'e5a76bf8157cfc8d4754d65724247ca7a8045c48816617ab9ad69c22c77219d1',
                                                                      'size': 23085},
 'docs/phase403_independent_design_review_findings.md': {'path': 'docs/phase403_independent_design_review_findings.md',
                                                         'sha256': '65c95c9d2f0f9c056deb1e79e5bf21a0ce484dc3dfaa0a494f47c452b3e82e20',
                                                         'size': 14628},
 'docs/phase405_lawful12_initial_presence_source_chain_audit_spec.md': {'path': 'docs/phase405_lawful12_initial_presence_source_chain_audit_spec.md',
                                                                        'sha256': '94848841d9760ed674c3cf9580dd890792fd2ba9a4d530ddf35ec7fe57956a84',
                                                                        'size': 20124},
 'tests/phase361_king_projection_sealer.py': {'path': 'tests/phase361_king_projection_sealer.py',
                                              'sha256': '4f840a2f3a9e04d4d6f646e8490b0e60545a79bf0f0e8b091dee4b6147bc5bb3',
                                              'size': 26582},
 'tests/phase391_king_observer_schema.py': {'path': 'tests/phase391_king_observer_schema.py',
                                            'sha256': 'ffcddfd2cbe58307f7258c1aefad5586a9179c6c452dc59c3342f9047f31457c',
                                            'size': 208243}}

# Appended after literal constants; no imports of schema/candidate/model.
import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import sys
import traceback


class SourceIntegrityError(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise SourceIntegrityError(message)


def exact(value, keys, label):
    need(type(value) is dict and set(value) == set(keys), 'closed '+label)


def same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(same(a, b) for a, b in zip(left, right))
    if type(left) is float:
        return struct.pack('>d', left) == struct.pack('>d', right)
    return left == right


def strict_json(raw):
    def pairs(values):
        result = {}
        for key, value in values:
            need(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def bad(value):
        raise SourceIntegrityError('nonfinite JSON number '+value)
    def real(value):
        number = float(value)
        need(math.isfinite(number), 'finite JSON real')
        return number
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                      parse_constant=bad, parse_float=real)


def descriptor(row):
    exact(row, ('path', 'size', 'sha256'), 'descriptor')
    need(type(row['path']) is str and type(row['size']) is int and 0 <= row['size'] <= TOTAL_BYTES,
         'descriptor primitive fields')
    need(type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']) is not None,
         'descriptor SHA')
    return row


def canonical(root, name):
    need(type(name) is str and bool(name) and '\\' not in name and '\0' not in name,
         'relative path string')
    rel = PurePosixPath(name)
    need(not rel.is_absolute() and rel.as_posix() == name and
         all(x not in ('', '.', '..') for x in name.split('/')), 'canonical relative member')
    return root.joinpath(*rel.parts)


def unlinked(path):
    need(not any(p.is_symlink() for p in (path, *path.parents)), 'no symlink ancestry')


def identity(info):
    return [info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns]


def read_regular(path, row, cap, io):
    descriptor(row)
    need(row['size'] <= cap, 'file cap')
    unlinked(path)
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'ordinary single-link before read')
    need(before.st_size == row['size'], 'physical size')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        opened = os.fstat(stream.fileno())
        need(identity(opened) == identity(before) and stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1,
             'opened identity before read')
        raw = stream.read(row['size'] + 1)
        closed = os.fstat(stream.fileno())
    unlinked(path)
    need(identity(before) == identity(closed) == identity(path.lstat()), 'read identity stable')
    need(len(raw) == row['size'] and hashlib.sha256(raw).hexdigest() == row['sha256'], 'content identity')
    io.append(dict(path=str(path), size=len(raw), sha256=row['sha256'], identity=identity(before)))
    return raw


def source_path(root, name):
    if name in STATIC_PINS and Path(name).is_absolute():
        return Path(name)
    return canonical(root, name)


def metadata(root, row, io):
    path = canonical(root, descriptor(row)['path'])
    need(row['path'].startswith('data/') and row['size'] <= 8 * 1024 * 1024, 'bounded repo authority leaf')
    return strict_json(read_regular(path, row, 8 * 1024 * 1024, io))


def owned_index(value):
    need(type(value) is dict and type(value.get('files')) is list, 'owner files')
    result = {}
    for row in value['files']:
        descriptor(row)
        need(row['path'] not in result, 'unique owned source path')
        result[row['path']] = row
    return result


def verify_audit_release(root, release_descriptor, io):
    root = Path(root).absolute()
    unlinked(root)
    need(root.is_dir(), 'source root')
    release = metadata(root, release_descriptor, io)
    exact(release, ('schema','action','authorized','run','input_directory','output_directory',
                   'permissions','source_freeze','source_owner','source_review','source_review_owner',
                   'root402','design405_review','input_files'), 'Root audit release')
    need(release['schema'] == 'root406-lawful12-initial-audit/1' and
         release['action'] == 'initial_presence_source_chain_audit' and release['authorized'] is True,
         'explicit Root initial-audit authority')
    exact(release['permissions'], PERMISSION_KEYS, 'permissions')
    need(all(type(v) is int and v == 0 for v in release['permissions'].values()), 'strict zero non-audit permissions')
    need(release['run'] == FIXED_RUN and release['input_directory'] == FIXED_RUN+'/output/capture',
         'exact fixed06 capture root')
    out_name = release['output_directory']
    need(type(out_name) is str and re.fullmatch(r'data/phase406-initial-audit-[A-Za-z0-9_-]+', out_name) is not None,
         'new bounded audit output root')
    output = canonical(root, out_name)
    unlinked(output)
    need(output.parent.is_dir() and not output.exists(), 'exclusive new output directory')
    need(release['root402'] == STATIC_PINS[ROOT402] and release['design405_review'] == STATIC_PINS[REVIEW405],
         'actual402Root/405review descriptors')
    controls = {}
    for name, row in STATIC_PINS.items():
        controls[name] = read_regular(source_path(root, name), row, TOTAL_BYTES, io)
    accepted = strict_json(controls[ROOT402])
    need(accepted['status'] == 'ROOT_ACCEPTS_FIXED06_BOUNDED_TERMINAL_SOURCE_PROCESS_CONTROLS' and
         accepted['full12_business_or_input_admitted'] is False and accepted['King_admitted'] is False,
         'bounded actual402 receipt only')
    need(accepted['review'] == STATIC_PINS[REVIEW402] and accepted['owner'] == STATIC_PINS[OWNER402],
         'actual402 review owner relation')
    need(owned_index(strict_json(controls[OWNER402])).get(REVIEW402) == STATIC_PINS[REVIEW402], 'owned402 review')
    review405 = strict_json(controls[REVIEW405])
    need(review405['status'] == 'INDEPENDENT405_DESIGN_ACCEPTED_FOR_SMALL_STDLIB_AUDIT_SOURCE_IMPLEMENTATION_ROOT_PENDING' and
         review405['models'] == 0 and type(review405['models']) is int and review405['writer_closure_proven'] is False,
         'actual405 limited design review')
    need(owned_index(strict_json(controls[OWNER405])).get(REVIEW405) == STATIC_PINS[REVIEW405], 'owned405 review')
    need(release['source_freeze']['path'] == SOURCE+'/source-freeze.json' and
         release['source_owner']['path'] == SOURCE+'/source-owner.json', 'fixed406 authority paths')
    freeze = metadata(root, release['source_freeze'], io)
    owner = owned_index(metadata(root, release['source_owner'], io))
    exact(freeze, ('schema','module','files','static_pins','fullschema','derived_recipes','old_SUT_calls'), 'SOURCE freeze')
    need(freeze['schema'] == 'phase406-readonly-initial-audit-SOURCE/1' and
         freeze['static_pins'] == STATIC_PINS and freeze['derived_recipes'] == [] and
         freeze['fullschema'] == 'NOT_VALIDATED' and type(freeze['old_SUT_calls']) is int and freeze['old_SUT_calls'] == 0,
         'exact406 source scope')
    need(freeze['module']['path'] == MODULE and Path(__file__).absolute() == canonical(root, MODULE),
         'executing exact SOURCE path')
    declared = owned_index({'files': freeze['files']})
    need(set(declared) == set(SOURCE_ARTIFACTS) | set(STATIC_PINS), 'closed SOURCE payload set')
    need(set(owner) == set(declared) | {SOURCE+'/source-freeze.json', SOURCE+'/summary.json'}, 'closed406 source owner set')
    need(declared.get(MODULE) == freeze['module'] and owner.get(release['source_freeze']['path']) == release['source_freeze'],
         'owner covers freeze/module')
    for name, row in declared.items():
        need(owner.get(name) == row, 'owner covers every frozen leaf')
        if name in STATIC_PINS:
            need(row == STATIC_PINS[name], 'fixed source descriptor')
        else:
            read_regular(canonical(root, name), row, TOTAL_BYTES, io)
    review = metadata(root, release['source_review'], io)
    review_owner = owned_index(metadata(root, release['source_review_owner'], io))
    need(review_owner.get(release['source_review']['path']) == release['source_review'], 'actual owned407 review')
    need(review.get('status') == REVIEW_STATUS and review.get('source_freeze') == release['source_freeze'] and
         review.get('source_owner') == release['source_owner'], '407 binds actual406 freeze and owner')
    need(all(type(review.get(k)) is int and review[k] == 0 for k in ('models','native','inputbuild','old_SUT_calls','schema_calls')),
         'review does not grant engine or schema execution')
    exact(release['input_files'], INPUT_NAMES, 'exact lawful12 names')
    for name, row in release['input_files'].items():
        exact(row, ('size','sha256'), 'lawful identity')
        descriptor(dict(path=name, **row))
    need(sum(row['size'] for row in release['input_files'].values()) <= TOTAL_BYTES, 'lawful12 total cap')
    allowed = {row['path'] for row in io}
    allowed.update(str(Path(release['input_directory']) / name) for name in INPUT_NAMES)
    return dict(root=root, release=release, output=output, allowed=allowed,
                controls=controls, source_freeze=release['source_freeze'], source_owner=release['source_owner'])


def install_io_guard(allowed_read, output, violations):
    def guard(event, args):
        if event == 'open':
            path, mode, flags = args
            if type(path) is int:
                return
            p = Path(os.fsdecode(path)).absolute()
            write = isinstance(mode, str) and any(c in mode for c in 'wax+') or type(flags) is int and bool(flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
            permitted = p.parent == output if write else str(p) in allowed_read or p == output or p.parent == output
            if not permitted:
                violations.append(dict(event=event, path=str(p)))
                raise PermissionError('audit file outside exact permission set')
        if event in ('subprocess.Popen','os.system','os.posix_spawn','socket.connect','socket.bind','ctypes.dlopen'):
            violations.append(dict(event=event));raise PermissionError('no process/network/native loading')
        if event == 'import':
            violations.append(dict(event=event, module=str(args[0])));raise PermissionError('no imports during audit execution')
        if event in ('os.remove','os.rename','os.rmdir','os.link','os.symlink','os.chmod','os.utime','os.truncate'):
            violations.append(dict(event=event));raise PermissionError('no filesystem mutation except new output files')
        if event == 'os.mkdir' and Path(os.fsdecode(args[0])).absolute() != output:
            violations.append(dict(event=event));raise PermissionError('only assigned output mkdir')
    sys.addaudithook(guard)


def read_lawful12_once(authority, io):
    decoded = {}
    seen = set()
    for name in INPUT_NAMES:
        row = dict(path=name, **authority['release']['input_files'][name])
        cap = 64*1024*1024 if name == 'king-clock-passes.jsonl' else 8*1024*1024 if name == 'king-ui-authority.jsonl' else TOTAL_BYTES
        raw = read_regular(Path(authority['release']['input_directory'])/name, row, cap, io)
        if not name.endswith('.jsonl'):
            value = strict_json(raw)
            need(type(value) is dict, 'lawful JSON object '+name)
            decoded[name] = value
            continue
        lines = raw.splitlines()
        count_cap = 200000 if name == 'king-clock-passes.jsonl' else 65536 if name == 'king-ui-authority.jsonl' else 300000
        line_cap = 1024 if name == 'king-clock-passes.jsonl' else 16384 if name == 'king-ui-authority.jsonl' else 2097152
        need(len(lines) <= count_cap, 'row cap '+name)
        records = [];previous = -1
        for line_number, line in enumerate(lines, 1):
            need(bool(line.strip()) and len(line) <= line_cap, 'bounded nonblank JSONL row')
            value = strict_json(line)
            need(type(value) is dict, 'JSONL object')
            if name in CHANNELS:
                seq = value.get('sequence')
                need(value.get('schema') == 'observer7-record/1' and value.get('channel') == CHANNELS[name] and
                     type(seq) is int and previous < seq < 1<<63 and seq not in seen, 'physical unique ordered observer sequence')
                seen.add(seq);previous = seq
            records.append((line_number, value))
        decoded[name] = records
    return decoded


def rawref(name, line, row, pointer, owner=None):
    return dict(file=name, line=line, sequence=row.get('sequence'), pointer=pointer, native_owner=owner)


def unique_records(rows, site, edge):
    return [(line, row) for line, row in rows if row.get('site') == site and row.get('edge') == edge]


def index_initial_observations(decoded):
    phases = {};findings = []
    def issue(label):
        findings.append(dict(kind='DOMAIN_REJECTED', detail=label))
    for phase, site in PHASES:
        cps = unique_records(decoded['observer7-input.jsonl'], site, 'checkpoint')
        entries = unique_records(decoded['observer7-input.jsonl'], site, 'enter')
        need(len(cps) == len(entries) == 1, 'unique checkpoint and entry '+phase)
        line, cp = cps[0];_, entry = entries[0]
        need(cp['sequence']+1 == entry['sequence'] and same(cp['stamp'], entry['stamp']) and
             same(cp['subject'], entry['subject']), 'checkpoint/entry immediate identity/stamp')
        payload = cp.get('payload')
        exact(payload, ('environment','nodes','items','source_resources'), 'checkpoint payload')
        nodes = {};native_ids = set();paths = set()
        need(type(payload['nodes']) is list and len(payload['nodes']) <= 16384, 'bounded actual nodes')
        for number, row in enumerate(payload['nodes']):
            exact(row, ('role','node','timer'), 'node envelope')
            node = row['node'];need(type(node) is dict, 'node object')
            role = row['role'];native = node.get('native_id');path = node.get('path')
            need(type(role) is str and role not in nodes and type(native) is str and re.fullmatch('[1-9][0-9]*', native) is not None and native not in native_ids and type(path) is str and path not in paths, 'unique actual node roles/IDs/paths')
            nodes[role] = (number,row);native_ids.add(native);paths.add(path)
        items = {}
        need(type(payload['items']) is list, 'checkpoint item rows')
        for number, item in enumerate(payload['items']):
            need(type(item) is dict and type(item.get('instance')) is str and item['instance'] not in items, 'unique checkpoint item')
            items[item['instance']] = (number,item)
        need(type(payload['source_resources']) is list, 'resource rows')
        resources = {}
        for number, resource in enumerate(payload['source_resources']):
            need(type(resource) is dict and resource.get('side') in ('P','O') and resource['side'] not in resources, 'unique resource side')
            resources[resource['side']] = (number,resource)
        if set(items) != {x['instance_id'] for x in SLOT_PLAN}:
            issue(phase+': exact39 slot identities required; O:12 absent')
        actual_timer_roles = {role for role, (_, row) in nodes.items() if row['timer'] is not None}
        if actual_timer_roles != set(TIMER_ROLES):
            issue(phase+': Timer membership differs from35 exact roles')
        phases[phase] = dict(line=line, checkpoint=cp, nodes=nodes, items=items, resources=resources)
    pre, act = phases['pre_prepare'], phases['pre_activate']
    need(pre['checkpoint']['sequence'] < act['checkpoint']['sequence'], 'prepare before activate')
    for role in set(pre['nodes']) | set(act['nodes']):
        if role not in pre['nodes'] or role not in act['nodes'] or any(not same(pre['nodes'][role][1]['node'].get(k),act['nodes'][role][1]['node'].get(k)) for k in ('native_id','role','path','name','class','positions','priority')):
            issue('node continuity '+role)
    binding = decoded['king-slot-bindings.json']
    need(type(binding.get('actual_bindings')) is list, 'actual binding array')
    if not same(binding.get('source_slot_table'), SLOT_PLAN):
        issue('fixed source slot plan')
    byrole = {};binding_ids = set()
    for number,row in enumerate(binding['actual_bindings']):
        need(type(row) is dict and type(row.get('instance_id')) is str and row['instance_id'] not in byrole, 'unique binding role')
        byrole[row['instance_id']] = (number,row)
        if row.get('native_id') in binding_ids:issue('binding native identity reused')
        binding_ids.add(row.get('native_id'))
    if set(byrole) != {x['instance_id'] for x in SLOT_PLAN}:issue('binding exact39 identities')
    lineage = decoded['observer7-lineage.jsonl']
    for spec in SLOT_PLAN:
        role = spec['instance_id'];pair = byrole.get(role)
        if pair is None:continue
        _, bound = pair
        if not same(bound.get('item_index'), {'type':'int','decimal':str(spec['item_index'])}) or not same(bound.get('orientation'), {'type':'int','decimal':str(spec['f'])}) or not same(bound.get('input_slot'), spec['input_slot']):
            issue('binding item/orientation/slot '+role)
        for phase, index in phases.items():
            item = index['nodes'].get('item:'+role);character = index['nodes'].get('character:'+spec['side'])
            if item is None or character is None or bound.get('native_id') != item[1]['node']['native_id'] or bound.get('character_id') != character[1]['node']['native_id']:
                issue(phase+': binding actual node owner '+role)
        scenes = [(ln,r) for ln,r in lineage if r.get('edge') == 'scene_instance' and r.get('payload',{}).get('item_id') == bound.get('native_id')]
        ready = [(ln,r) for ln,r in lineage if r.get('site') == 'Items/Item.gd::_ready' and r.get('edge') == 'enter' and r.get('subject',{}).get('native_id') == bound.get('native_id')]
        if len(scenes) != 1 or len(ready) != 1:
            issue('actual fresh scene/ready presence '+role)
        elif not (scenes[0][1]['sequence'] < ready[0][1]['sequence'] < pre['checkpoint']['sequence'] and scenes[0][1].get('payload',{}).get('pooled') is False and scenes[0][1].get('subject',{}).get('role') is None and ready[0][1].get('subject',{}).get('role') is None):
            issue('fresh lineage/earlyNULL order '+role)
    for side,name in [('P','player_fixture.json'),('O','fixture.json')]:
        fixture = decoded[name];planned = FIXED_FIXTURE['sides'][0 if side=='P' else 1]
        expected_items = [{k:v for k,v in item.items() if k!='instance_id'} for item in planned['items']]
        if fixture.get('class') != 0 or type(fixture.get('class')) is not int or not same(fixture.get('items'), expected_items):
            issue('fixed '+side+' fixture class/items')
        for field,target in [('health','hp'),('stamina','stamina')]:
            v=fixture.get(field)
            if type(v) not in (int,float) or not math.isfinite(v) or v != planned[target]:issue('fixed '+side+' initial '+field)
    return dict(phases=phases, findings=findings, raw_binding_rows=byrole,
                identity_scope='AUDIT_SUBSET_NOT_FULL391_BINDING_VALIDATION')


def typed_int(value):
    return type(value) is dict and set(value)=={'type','decimal'} and value['type']=='int' and type(value['decimal']) is str and re.fullmatch(r'0|-?[1-9][0-9]*',value['decimal']) is not None and -(1<<63)<=int(value['decimal'])<(1<<63)


def typed_real(value):
    return type(value) is dict and set(value)=={'type','binary64_be'} and value['type']=='float' and type(value['binary64_be']) is str and re.fullmatch('[0-9a-f]{16}',value['binary64_be']) is not None and math.isfinite(struct.unpack('>d',bytes.fromhex(value['binary64_be']))[0])


def direct_row(field, phase, role, actual, present, constraint, refs, supported):
    result = dict(field_id=field, phase=phase, side_or_role=role,
                  classification='DIRECT_OBSERVATION' if present else 'MISSING',
                  validation_result='SUPPORTED' if present and supported else 'REJECTED' if present else 'UNPROVEN',
                  proof_complete=bool(present and supported), constraint=constraint, input_refs=refs,
                  source_refs=[], unresolved=[] if present else ['actual lawful field absent'])
    if present:result['actual_value']=actual
    return result


def audit_direct_fields(index, decoded):
    rows = []
    for phase, item in index['phases'].items():
        cp=item['checkpoint'];line=item['line']
        def ref(pointer, owner=None):return rawref('observer7-input.jsonl',line,cp,pointer,owner)
        for side in ('P','O'):
            pair=item['resources'].get(side);node=item['nodes'].get('character:'+side)
            val=pair[1] if pair else {};owner=node[1]['node']['native_id'] if node else None
            present='buffProtectStacks' in val
            rows.append(direct_row('Character.buffProtectStacks',phase,side,val.get('buffProtectStacks'),present,{'type':'int','decimal':'0'},[ref('/payload/source_resources/'+str(pair[0])+'/buffProtectStacks',owner)] if pair else [],present and node is not None and val.get('native_id')==owner and same(val['buffProtectStacks'],{'type':'int','decimal':'0'})))
        king=item['items'].get('P:12');fields=king[1].get('fields',{}) if king else {};need(type(fields)is dict,'King fields object')
        for field,expected in [('invuCharges',{'type':'int','decimal':'0' if phase=='pre_prepare'else'3'}),('activations',{'type':'int','decimal':'0'}),('activationsToTrigger',{'type':'float','binary64_be':'4018000000000000'}),('protectedBuffs',{'type':'float','binary64_be':'4008000000000000'}),('manaCost',{'type':'float','binary64_be':'4010000000000000'})]:
            rows.append(direct_row('King.'+field,phase,'P:12',fields.get(field),field in fields,expected,[ref('/payload/items/'+str(king[0])+'/fields/'+field)]if king else [],field in fields and same(fields[field],expected)))
        for role in TIMER_ROLES:
            node=item['nodes'].get(role);timer=node[1]['timer'] if node else None
            if timer is not None:need(type(timer)is dict,'Timer object')
            timer=timer if timer is not None else {};n=timer.get('node',{})
            need(type(n)is dict,'Timer node')
            identity_ok=node is not None and same(n,node[1]['node']) and n.get('class')=='Timer'
            for field in ('process_mode','wait_time','time_left','one_shot','autostart','paused','stopped'):
                expected=1 if role.startswith(('king_hide:','king_drag:'))else 0
                valid = type(timer.get(field))is int and timer[field]==expected if field=='process_mode'else typed_real(timer.get(field)) if field=='wait_time'else same(timer.get(field),{'type':'float','binary64_be':'0000000000000000'})if field=='time_left'else timer.get(field) is (not role.startswith('tick:'))if field=='one_shot'else timer.get(field) is (field=='stopped')
                if field=='wait_time' and valid:valid=struct.unpack('>d',bytes.fromhex(timer[field]['binary64_be']))[0]>0
                rows.append(direct_row('Timer.'+field,phase,role,timer.get(field),field in timer,'fresh positive/configured public value; private unspecified',[ref('/payload/nodes/'+str(node[0])+'/timer/'+field,n.get('native_id'))]if node else [],identity_ok and valid))
            for field in ('native_id','role','path','name','class','positions','priority','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
                value=n.get(field);present=field in n
                valid = value is False if field in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')else value is True if field=='inside_tree'else type(value)is int if field=='priority'else type(value)is list and bool(value) and all(type(x)is int for x in value) if field=='positions'else (value is None or type(value)is str) if field=='role'else type(value)is str
                rows.append(direct_row('Timer.node.'+field,phase,role,value,present,'actual native node identity/configuration; fresh inactive flags',[ref('/payload/nodes/'+str(node[0])+'/timer/node/'+field,n.get('native_id'))]if node else [],identity_ok and valid))
    facts=decoded['king-input-facts.json'];kings=facts.get('kings');need(type(kings)is list,'facts kings array')
    king=kings[0]if len(kings)==1 and type(kings[0])is dict else {}
    actual_king=index['phases']['pre_activate']['nodes'].get('item:P:12')
    king_joined=actual_king is not None and same(king.get('node'),actual_king[1]['node'])
    ui_binds=[r.get('payload') for _,r in decoded['king-ui-authority.jsonl'] if r.get('kind')=='bind' and type(r.get('payload'))is dict and r['payload'].get('item_id')==king.get('node',{}).get('native_id')]
    if len(ui_binds)!=1: index['findings'].append(dict(kind='DOMAIN_REJECTED',detail='one actual King UI particle bind required'))
    for part in ('activation','drag'):
        values=king.get(part,{});need(type(values)is dict,'particle facts')
        particle_node=values.get('node',{});need(type(particle_node)is dict,'particle node')
        timer_role=('king_hide:'if part=='activation'else'king_drag:')+'P:12'
        timer_node=index['phases']['pre_activate']['nodes'].get(timer_role)
        particle_joined=king_joined and len(ui_binds)==1 and ui_binds[0].get(part+'_id')==particle_node.get('native_id') and timer_node is not None and same(values.get('timer'),timer_node[1]['timer']) and particle_node.get('class')=='Particles2D'
        for field,expected in [('visible',{'type':'bool','value':False}),('emitting',{'type':'bool','value':False}),('one_shot',{'type':'bool','value':False}),('lifetime',{'type':'float','binary64_be':'3fe6666660000000'}),('explosiveness',{'type':'float','binary64_be':'0000000000000000'}),('speed_scale',{'type':'float','binary64_be':'3ff0000000000000'})]:
            rows.append(direct_row('Particle.'+part+'.'+field,'pre_activate','P:12',values.get(field),field in values,expected,[dict(file='king-input-facts.json',pointer='/kings/0/'+part+'/'+field)],same(values.get(field),expected)and king.get('instance')=='P:12'and particle_joined))
    timers=facts.get('timers',{});need(type(timers)is dict,'five Timer fact map')
    if set(timers)!=set(FIVE_TIMER_ROLES):index['findings'].append(dict(kind='DOMAIN_REJECTED',detail='five Timer facts membership'))
    for role in FIVE_TIMER_ROLES:
        fact=timers.get(role,{});need(type(fact)is dict,'Timer fact')
        lineage=fact.get('lineage',{});need(type(lineage)is dict,'birth lineage object')
        node=index['phases']['pre_activate']['nodes'].get(role)
        current=fact.get('current');joined=node is not None and same(current,node[1]['timer'])
        owner_node=index['phases']['pre_activate']['nodes'].get('character:'+role[-1])if role.startswith('invu:')else actual_king if role.startswith('king_buff:')else None
        owner_id=owner_node[1]['node']['native_id']if owner_node else king.get('activation'if role.startswith('king_hide:')else'drag',{}).get('node',{}).get('native_id')
        expected_kind='Character.scene.ready'if role.startswith('invu:')else'King.scene.instance'if role.startswith('king_buff:')else'AutoHide.Timer.new'
        birth=lineage.get('birth',{})
        joined=joined and type(birth)is dict and type(birth.get('node'))is dict and lineage.get('timer_id')==node[1]['node']['native_id'] and lineage.get('owner_id')==owner_id and owner_id is not None and lineage.get('kind')==expected_kind and birth['node'].get('native_id')==node[1]['node']['native_id']
        if not joined:index['findings'].append(dict(kind='DOMAIN_REJECTED',detail='five Timer actual birth/current/owner join '+role))
        for field in ('timer_id','owner_id','kind','starts','stops','birth'):
            value=lineage.get(field);valid=type(value)is int and value==0 if field=='starts'else type(value)is int and value>=0 if field=='stops'else type(value)is dict if field=='birth'else type(value)is str
            rows.append(direct_row('Timer.lineage.'+field,'pre_activate',role,value,field in lineage,'observed birth/current ledger only; does not prove private constructor',[dict(file='king-input-facts.json',pointer='/timers/'+role+'/lineage/'+field)],valid and joined))
        rows.append(direct_row('Timer.private_provenance_label','pre_activate',role,fact.get('private_provenance'),'private_provenance'in fact,'source_constructor_minus_one_no_start_not_public_zero_inference',[dict(file='king-input-facts.json',pointer='/timers/'+role+'/private_provenance')],joined and fact.get('private_provenance')=='source_constructor_minus_one_no_start_not_public_zero_inference'))
    return rows


def audit_source_chain(index, direct, source_controls):
    rows=[]
    relevant=[row for name,row in STATIC_PINS.items() if name.endswith(('Core/Character.gd','Core/Game.gd','Items/Item.gd','Items/Exclusive/KingGoobert.gd','Utility/AutoHideParticles.gd','Core/Buff.gd','CombatTimer.gd','.tscn'))]
    for phase,_ in PHASES:
        groups=[('Character.'+field,side,['actual Character allocation branch (PLAYER reuse possible)','complete prepare and intervening-writer closure'])for side in ('P','O')for field in ('invulnerable','invulnerabilityItem','invulBubbleVisible')]
        groups += [('King.'+field,'P:12',['actual fresh constructor/scene configuration at this phase','complete setState/onStateChanged and no-intervening-writer proof'])for field in ('crown','light_visible','light_modulate')]
        groups += [('Timer.private_left',role,['complete native engine constructor/configuration provenance','actual no-start/all-writer coverage from allocation to this phase'])for role in TIMER_ROLES]
        for field,role,gaps in groups:
            refs=[r for row in direct if row['phase']==phase and row['side_or_role']==role for r in row['input_refs']]
            unique=[]
            for ref in refs:
                if ref not in unique:unique.append(ref)
            rows.append(dict(field_id=field,phase=phase,side_or_role=role,classification='MISSING',validation_result='UNPROVEN',proof_complete=False,
                             input_refs=unique,source_refs=relevant,unresolved=gaps,
                             missing_reason='AUDIT_RECIPE_NOT_ESTABLISHED_NOT_PROOF_ORIGINAL_DATA_ABSENT',explanation='SOURCE route candidates only. No complete reviewed derivation recipe in406. No actual initial value inferred; this does not imply recapture is necessary.'))
    return rows


def assess_initial_feasibility(rows, findings):
    if any(row['validation_result']=='REJECTED'for row in rows)or any(x['kind']=='DOMAIN_REJECTED'for x in findings):
        status='REJECTED_INITIAL_DOMAIN'
    elif any(row['classification']=='MISSING'or not row['proof_complete']for row in rows):
        status='BLOCKED_INITIAL_SOURCE_GAPS'
    else:
        status='FEASIBLE_PENDING_FULL_STRUCTURAL_VALIDATION'
    return dict(schema='phase406-initial-source-feasibility/1',status=status,fullschema='NOT_VALIDATED',
                source_derived_recipes_implemented=0,field_count=len(rows),classifications={k:sum(r['classification']==k for r in rows)for k in ('DIRECT_OBSERVATION','SOURCE_DERIVED','MISSING')},
                rejected_fields=sum(r['validation_result']=='REJECTED'for r in rows),models=0,inputbuild=0,projection=0,old_SUT_calls=0,schema_calls=0,
                genuine_input_accepted=False,King_admitted=False,reader361='CLOSED',model356='CLOSED')


def save_new(path, value):
    raw=(json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+'\n').encode()
    need(len(raw)<=64*1024*1024,'bounded report artifact')
    unlinked(path)
    with path.open('xb') as stream:
        stream.write(raw);stream.flush();os.fsync(stream.fileno())
    need(path.lstat().st_nlink==1 and path.read_bytes()==raw,'new output physical/byte readback')
    return dict(path=path.name,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def seal_audit_once(authority, report, rows, findings, io, error, violations):
    output=authority['output'];before=list(io);after=[]
    try:
        checked=set()
        for row in before:
            if row['path']in checked:continue
            checked.add(row['path']);p=Path(row['path'])
            read_regular(p,dict(path=row['path'],size=row['size'],sha256=row['sha256']),TOTAL_BYTES,after)
    except Exception:
        if error is None:error=traceback.format_exc()
        report=dict(schema='phase406-initial-source-feasibility/1',status='FAILED_SOURCE_INTEGRITY',fullschema='NOT_VALIDATED')
    owner=[]
    artifacts={'report.json':report,'rawtyped-field-index.json':rows,'identity-domain-findings.json':findings,
               'io-observations.json':dict(before=before,readback=after,violations=violations),
               'source-references.json':dict(source_freeze=authority['source_freeze'],source_owner=authority['source_owner'],static_pins=STATIC_PINS),
               'summary.json':dict(status=report['status'],audit_invocations=1,new_audit_module_execution=1,old_SUT_imports=0,old_SUT_calls=0,schema_calls=0,models=0,inputbuild=0,bundle=0,projection=0,native=0,restore=0,READY=0,fullschema='NOT_VALIDATED',first_error=error,automatic_retry=False,no_more_writes_after_owner=True)}
    for name,value in artifacts.items():owner.append(save_new(output/name,value))
    save_new(output/'owned-files.json',dict(schema='phase406-actual-initial-audit-owner/1',files=owner,no_more_writes=True))
    fd=os.open(output,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return report['status']


def run_audit(root, release_descriptor):
    io=[];violations=[]
    authority=verify_audit_release(root,release_descriptor,io)
    install_io_guard(authority['allowed'],authority['output'],violations)
    authority['output'].mkdir()
    rows=[];findings=[];error=None
    try:
        decoded=read_lawful12_once(authority,io)
        index=index_initial_observations(decoded)
        findings=index['findings']
        rows=audit_direct_fields(index,decoded)
        rows+=audit_source_chain(index,rows,authority['controls'])
        report=assess_initial_feasibility(rows,findings)
    except Exception:
        error=traceback.format_exc()
        report=dict(schema='phase406-initial-source-feasibility/1',status='FAILED_SOURCE_INTEGRITY',fullschema='NOT_VALIDATED')
    status=seal_audit_once(authority,report,rows,findings,io,error,violations)
    print(json.dumps(dict(status=status,output=str(authority['output']),models=0,inputbuild=0)))
    return 1 if status=='FAILED_SOURCE_INTEGRITY'else 0


def main():
    parser=argparse.ArgumentParser(description='SOURCE-bound readonly initial presence/route audit; no model or full schema')
    parser.add_argument('--source-root',type=Path,required=True)
    parser.add_argument('--release',required=True)
    parser.add_argument('--release-size',type=int,required=True)
    parser.add_argument('--release-sha256',required=True)
    args=parser.parse_args()
    return run_audit(args.source_root,dict(path=args.release,size=args.release_size,sha256=args.release_sha256))


if __name__=='__main__':
    sys.exit(main())
