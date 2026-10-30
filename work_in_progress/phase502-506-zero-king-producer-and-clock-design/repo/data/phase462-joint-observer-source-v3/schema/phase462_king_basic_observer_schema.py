"""Self-contained finite King typed schema SOURCE. No file/model/native operations."""


import hashlib, json, math, re, struct
from copy import deepcopy
from dataclasses import dataclass
from types import SimpleNamespace


VERSION = '7-king-basic-A-460'
PROFILE = 'observer7-king-basic-A-native-tape/1'
CASE='KING-K1-A-353'
NATIVE_AUTHORIZED=False


DESCRIPTOR_IDS = frozenset({1,4,11,19,22,23,262})


CONTRACT = {'Timer_source_forms': {'Core/Buff.gd::gainTemporary:start': {'argc': 1, 'args': ['REALduration'], 'operation': 'start', 'role': 'buff:<side>:<type>'}, 'Core/Buff.gd::onTimeout:start': {'argc': 1, 'args': ['REALdelay'], 'operation': 'start', 'role': 'buff:<side>:<type>'}, 'Core/Character.gd::combatStart:tick': {'argc': 0, 'args': [], 'operation': 'start', 'role': 'tick:<side>'}, 'Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage': {'argc': 1, 'args': ['INT1'], 'operation': 'start', 'role': 'fatigue:tick'}, 'Interface/CombatTimer/CombatTimer.gd::start': {'argc': 1, 'args': ['INT14'], 'operation': 'start', 'role': 'fatigue:start'}, 'Interface/CombatTimer/CombatTimer.gd::startFatigue': {'argc': 1, 'args': ['INT3'], 'operation': 'start', 'role': 'fatigue:tick'}, 'Items/CarrotGoobert.gd::doCooldownEffect:start': {'argc': 1, 'args': ['REALduration'], 'operation': 'start', 'role': 'particle:<instance>'}, 'all_known_stop_sites': {'argc': 0, 'args': [], 'operation': 'stop'}}, 'caps': {'array': 8192, 'depth': 16, 'descriptors': 7, 'dictionary': 512, 'failure_file_bytes': 4096, 'file_bytes': 268435456, 'first_error_bytes': 1024, 'flush_bytes': 4194304, 'host_capture_files': 64, 'native_ids': 8192, 'observer_files': 8, 'pending_rows': 64, 'record_bytes': 2097152, 'records': 300000, 'roles': 1024, 'sparse_nodes': 16384, 'string_utf8': 4096, 'total_bytes': 268435456}, 'computed_fields': {'allocation_counter': 'Game.combatLog.eventNum', 'connection_count': 'sum each EventBus.connections array length', 'event_count': 'CombatLog.events.size', 'native_reference': 'nativeintID retained; Objecttransientargs only; no Object saved', 'subtype_rules': 'goobert/carrot/potion include literalmergedItemfields; appropriate source-specific nullableconstructoronly'}, 'current_permissions': {'input_build': False, 'model': False, 'native': False}, 'envelope_exact': ['schema', 'sequence', 'channel', 'site', 'edge', 'subject', 'stamp', 'payload'], 'envelope_schema': 'observer7-record/1', 'failure_policy': 'boundedfirsterror durable+failedlatch; originalRNG/gameplay executes/returnsexactlyonce regardlessobserverrecordfailure; collector laterstops capturefalse', 'file_channels': {'allocation': 'observer7-allocations.jsonl', 'failure': 'observer7_failure.json', 'input': 'observer7-input.jsonl', 'lineage': 'observer7-lineage.jsonl', 'metadata': 'observer7-metadata.jsonl', 'primitive': 'observer7-primitives.jsonl', 'registration': 'observer7-registration.jsonl', 'runtime': 'observer7-runtime.jsonl'}, 'genuine_extraction_enabled': False, 'input_leaf_whitelist': ['fixture.json', 'player_fixture.json', 'observer7-input.jsonl', 'observer7-lineage.jsonl', 'observer7-metadata.jsonl', 'observer7-primitives.jsonl', 'king-clock-checkpoint.json', 'king-clock-passes.jsonl', 'king-input-facts.json', 'king-ui-authority.jsonl', 'king-rng-checkpoint.json'], 'lifecycle_api_exact': ['role', 'operation', 'argc', 'args', 'public_before', 'public_after'], 'primitive_context_exact': ['operation', 'item', 'target', 'ordinal', 'width', 'branch', 'stack', 'reflect_argument'], 'primitive_exact': ['kind', 'label', 'args', 'value', 'context'], 'primitive_sites': {'Items/Item.gd::adjustCooldown:belowMasterOpponent': {'args': ['REAL0.975', 'REAL1.05'], 'kind': 'randf_range'}, 'Items/Item.gd::adjustCooldown:other': {'args': ['REAL0.95', 'REAL1.05'], 'kind': 'randf_range'}, 'Utility/BalancedRange.gd::randIntRange': {'args': ['INTfrom', 'INTto'], 'kind': 'randi_range'}, 'Utility/DamageSource.gd::randDamage': {'args': ['INTminDamage', 'INTmaxDamage'], 'kind': 'randi_range'}, 'Utility/Util.gd::flip': {'args': [], 'kind': 'randf'}, 'Utility/Util.gd::pickRandomElement': {'args': ['INT0', 'INTsizeMinus1'], 'kind': 'randi_range'}, 'Utility/Util.gd::randPitch': {'kind': 'randf_range'}, 'Utility/Util.gd::roll': {'args': ['INT0', 'REALmaximum'], 'default_maximum': 'REAL100.0', 'kind': 'randf_range'}, 'fixed7fraction_shuffle': {'args': [], 'instance_context': True, 'kind': 'global_u32', 'widths': [7, 6, 5, 4, 3, 2]}}, 'raw_to_numeric_tape': 'onlylistedexactsiteconversion, retainedrawtypes/sourceview, directreturncopyunchanged; genuineextraction/modelviewdisabledpendinglatergate', 'return_semantics': 'SOURCE_EXPRESSION_BEFORE_ORIGINAL_TYPED_BOUNDARY', 'schema': 'phase357-king-typed-record-contract/1', 'stamp_exact': ['physics_frame', 'idle_frame', 'util_time', 'combat_time', 'phase'], 'state_schemas': {'auto_hide': {'emitting': 'bool', 'explosiveness': 'float', 'lifetime': 'float', 'one_shot': 'bool', 'speed_scale': 'float', 'timer': 'timer|null', 'visible': 'bool'}, 'buff': {'character': 'native_ref|null', 'cleanseProtectionChancePercent': 'float', 'current': 'int', 'nextTemporaryTimeout': 'int', 'permanentStacks': 'int', 'reflectChancePercent': 'float', 'resistChancePercent': 'float', 'resistStacks': 'int', 'temporaryStacks': 'temporary_array', 'timer': 'timer|null', 'type': 'int'}, 'character': {'allowStaminaOverflow': 'bool', 'autoRageItem': 'native_ref|null', 'battleRageBonusDur': 'float', 'battleRageTimer': 'timer', 'buffProtectStacks': 'int', 'critResistStacks': 'int', 'critResistance': 'float', 'critTokens': 'int', 'curHealth': 'float', 'curStamina': 'float', 'damageResistance': 'float', 'debuffReflectStacks': 'int', 'healingEfficiency': 'float', 'invulBubbleVisible': 'bool', 'invulnerabilityItem': 'native_ref|null', 'invulnerabilityTimer': 'timer', 'invulnerable': 'bool', 'isDead': 'bool', 'maxHealth': 'float', 'maxStamina': 'float', 'playerId': 'int', 'stunnedDuration': 'float', 'temporaryMaxHealth': 'float', 'temporaryMaxStamina': 'float', 'tickCounter': 'int', 'typedDamageFactors': 'dictionary', 'unhealingAmount': 'float'}, 'combat_log': {'eventNum': 'int', 'event_count': 'int', 'eventsLogged': 'int', 'loggingFinished': 'bool'}, 'combat_timer': {'combatTime': 'float', 'fatigueCounter': 'int', 'fatigueStartTimer': 'timer', 'fatigueTickTimer': 'timer', 'timeAdvance': 'float'}, 'event_bus': {'connection_count': 'int', 'loggingMode': 'int', 'signalQueue': 'array'}, 'game': {'allocation_counter': 'int', 'curClass': 'int', 'curMode': 'int', 'curRound': 'int', 'fightEnded': 'bool', 'roundResults': 'array'}, 'generic': {'native_id': 'id'}, 'goobert': {'activations': 'int', 'activationsThisFrame': 'int', 'activationsToTrigger': 'float', 'cachedAffectedItems': 'dictionary', 'consumed': 'bool', 'currentAffectedItems': 'dictionary', 'descriptorIndex': 'int', 'faceDirection': 'int', 'iterationCooldown': 'float', 'lastActivationTime': 'float', 'lastTriggerTime': 'float', 'ownerType': 'int', 'placed': 'bool', 'speedScale': 'float', 'triggerTime': 'float', 'triggersThisFrame': 'int'}, 'item': {'activationsThisFrame': 'int', 'cachedAffectedItems': 'dictionary', 'consumed': 'bool', 'currentAffectedItems': 'dictionary', 'descriptorIndex': 'int', 'faceDirection': 'int', 'iterationCooldown': 'float', 'lastActivationTime': 'float', 'lastTriggerTime': 'float', 'ownerType': 'int', 'placed': 'bool', 'speedScale': 'float', 'triggerTime': 'float', 'triggersThisFrame': 'int'}, 'king': {'activationParticles': 'auto_hide', 'activations': 'int', 'activationsThisFrame': 'int', 'activationsToTrigger': 'float', 'buffTimer': 'timer', 'cachedAffectedItems': 'dictionary', 'consumed': 'bool', 'currentAffectedItems': 'dictionary', 'descriptorIndex': 'int', 'faceDirection': 'int', 'invuCharges': 'int', 'iterationCooldown': 'float', 'lastActivationTime': 'float', 'lastTriggerTime': 'float', 'manaCost': 'float', 'ownerType': 'int', 'placed': 'bool', 'protectedBuffs': 'float', 'speedScale': 'float', 'triggerTime': 'float', 'triggersThisFrame': 'int'}, 'node': {'class': 'string', 'inside_tree': 'bool', 'internal_idle': 'bool', 'internal_physics': 'bool', 'name': 'string', 'native_id': 'id', 'ordinary_idle': 'bool', 'ordinary_physics': 'bool', 'path': 'string|nulloutsideTree', 'positions': 'int_array', 'priority': 'int', 'role': 'string|null'}, 'plain_item': {'activationsThisFrame': 'int', 'cachedAffectedItems': 'dictionary', 'consumed': 'bool', 'currentAffectedItems': 'dictionary', 'descriptorIndex': 'int', 'faceDirection': 'int', 'iterationCooldown': 'float', 'lastActivationTime': 'float', 'lastTriggerTime': 'float', 'ownerType': 'int', 'placed': 'bool', 'speedScale': 'float', 'triggerTime': 'float', 'triggersThisFrame': 'int'}, 'potion': {'activationsThisFrame': 'int', 'cachedAffectedItems': 'dictionary', 'consumed': 'bool', 'currentAffectedItems': 'dictionary', 'descriptorIndex': 'int', 'faceDirection': 'int', 'isFull': 'bool', 'iterationCooldown': 'float', 'lastActivationTime': 'float', 'lastTriggerTime': 'float', 'ownerType': 'int', 'placed': 'bool', 'speedScale': 'float', 'triggerTime': 'float', 'triggersThisFrame': 'int'}, 'temporary_constructor': {'amount': 'int', 'item': 'native_ref|null', 'timeout': 'float'}, 'timer': {'autostart': 'bool', 'node': 'node', 'one_shot': 'bool', 'paused': 'bool', 'process_mode': 'int', 'stopped': 'bool', 'time_left': 'float', 'wait_time': 'float'}, 'util': {'clockTime': 'float', 'frameCounter': 'int', 'time': 'float'}}, 'status': 'SOURCE_SCHEMA_IMPLEMENTED_ADMISSION_CLOSED', 'typed_exact': {'array': ['type', 'values'], 'bool': ['type', 'value'], 'damage_result': ['type', 'native_id', 'event', 'damageSource', 'damage', 'healthDamage', 'hit', 'critical', 'damageReduction'], 'damage_source': ['type', 'native_id', 'minDamage', 'maxDamage', 'types', 'accuracy', 'critChancePercent', 'origin', 'flags'], 'dictionary': ['type', 'entries'], 'event_ref': ['type', 'native_id', 'event_id'], 'float': ['type', 'binary64_be'], 'int': ['type', 'decimal'], 'native_ref': ['type', 'native_id', 'role', 'class'], 'null': ['type'], 'string': ['type', 'value'], 'temporary': ['type', 'native_id', 'ordinal', 'amount', 'timeout', 'item']}}
CAPS=CONTRACT["caps"]


MATRIX={'Timer_API_statement_sites': [{'argc': 0, 'line': 343, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'timer', 'site': 'Core/Buff.gd::combatEnd'}, {'argc': 1, 'line': 161, 'operation': 'start', 'original_args_source': 'duration', 'receiver_local': 'timer', 'site': 'Core/Buff.gd::gainTemporary'}, {'argc': 0, 'line': 165, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'timer', 'site': 'Core/Buff.gd::gainTemporary'}, {'argc': 1, 'line': 166, 'operation': 'start', 'original_args_source': 'duration', 'receiver_local': 'timer', 'site': 'Core/Buff.gd::gainTemporary'}, {'argc': 0, 'line': 278, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'timer', 'site': 'Core/Buff.gd::loseStacks'}, {'argc': 1, 'line': 340, 'operation': 'start', 'original_args_source': 'delay', 'receiver_local': 'timer', 'site': 'Core/Buff.gd::onTimeout'}, {'argc': 0, 'line': 340, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'tickTimer', 'site': 'Core/Character.gd::combatEnd'}, {'argc': 0, 'line': 345, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'battleRageTimer', 'site': 'Core/Character.gd::combatEnd'}, {'argc': 0, 'line': 346, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'autoRageTimer', 'site': 'Core/Character.gd::combatEnd'}, {'argc': 0, 'line': 347, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'invulnerabilityTimer', 'site': 'Core/Character.gd::combatEnd'}, {'argc': 0, 'line': 333, 'operation': 'start', 'original_args_source': '', 'receiver_local': 'tickTimer', 'site': 'Core/Character.gd::combatStart'}, {'argc': 1, 'line': 336, 'operation': 'start', 'original_args_source': 'AUTO_RAGE_DELAY', 'receiver_local': 'autoRageTimer', 'site': 'Core/Character.gd::combatStart'}, {'argc': 0, 'line': 1568, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'battleRageTimer', 'site': 'Core/Character.gd::endBattleRage'}, {'argc': 1, 'line': 1041, 'operation': 'start', 'original_args_source': 'invuDur', 'receiver_local': 'invulnerabilityTimer', 'site': 'Core/Character.gd::makeInvulnerable'}, {'argc': 1, 'line': 1560, 'operation': 'start', 'original_args_source': 'fullDur', 'receiver_local': 'battleRageTimer', 'site': 'Core/Character.gd::startBattleRage'}, {'argc': 0, 'line': 100, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'fatigueStartTimer', 'site': 'Interface/CombatTimer/CombatTimer.gd::combatEnd'}, {'argc': 0, 'line': 101, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'fatigueTickTimer', 'site': 'Interface/CombatTimer/CombatTimer.gd::combatEnd'}, {'argc': 1, 'line': 179, 'operation': 'start', 'original_args_source': '1', 'receiver_local': 'fatigueTickTimer', 'site': 'Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage'}, {'argc': 0, 'line': 116, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'fatigueStartTimer', 'site': 'Interface/CombatTimer/CombatTimer.gd::start'}, {'argc': 0, 'line': 117, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'fatigueTickTimer', 'site': 'Interface/CombatTimer/CombatTimer.gd::start'}, {'argc': 1, 'line': 119, 'operation': 'start', 'original_args_source': 'FATIGUE_TIME - 3', 'receiver_local': 'fatigueStartTimer', 'site': 'Interface/CombatTimer/CombatTimer.gd::start'}, {'argc': 1, 'line': 151, 'operation': 'start', 'original_args_source': '3', 'receiver_local': 'fatigueTickTimer', 'site': 'Interface/CombatTimer/CombatTimer.gd::startFatigue'}, {'argc': 1, 'line': 36, 'operation': 'start', 'original_args_source': 'invuDur', 'receiver_local': 'buffTimer', 'site': 'Items/Exclusive/KingGoobert.gd::doCooldownEffect'}, {'argc': 0, 'line': 47, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'buffTimer', 'site': 'Items/Exclusive/KingGoobert.gd::onCombatEnd'}, {'argc': 0, 'line': 13, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'timer', 'site': 'Utility/AutoHideParticles.gd::activate'}, {'argc': 0, 'line': 36, 'operation': 'stop', 'original_args_source': '', 'receiver_local': 'timer', 'site': 'Utility/AutoHideParticles.gd::instantClear'}, {'argc': 1, 'line': 30, 'operation': 'start', 'original_args_source': 'lifetime * (1 + (1 - explosiveness) / speed_scale)', 'receiver_local': 'timer', 'site': 'Utility/AutoHideParticles.gd::startTimer'}, {'argc': 1, 'line': 1593, 'operation': 'start', 'original_args_source': 't + timeLeft', 'receiver_local': 'timer', 'site': 'Utility/Util.gd::changeTimer'}], 'extra_edges': {'allocation_complete': ['event_data'], 'checkpoint': ['environment', 'nodes', 'items'], 'loaded_descriptors': ['descriptors', 'locale'], 'scene_instance': ['descriptor_id', 'item_id', 'item_index', 'pooled', 'scene_path', 'particle']}, 'sites': {'Core/Buff.gd::TemporaryStacks._init': {'argument_types': {}, 'arguments_exact': ['_amount', '_timeout', '_item'], 'channel': 'lineage', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'TemporaryStacks._init', 'function_sha256': '89b0de5339e090ec851007a41be0b7a0420d03e433da93d5f74dcd1bc185f87a', 'function_size': 109, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 361, 'line_start': 351, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Buff.gd', 'state_schema': 'temporary_constructor'}, 'Core/Buff.gd::changeCleanseProtectionChance': {'argument_types': {}, 'arguments_exact': ['chance'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'buff'}, 'Core/Buff.gd::changeCurrentLogShowLabel': {'argument_types': {'amount': 'int', 'isTimeout': 'bool', 'used': 'bool'}, 'arguments_exact': ['isTimeout', 'amount', 'item', 'triggerEvent', 'used'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 313}, {'line': 315}], 'function': 'changeCurrentLogShowLabel', 'function_sha256': '8c55139842769de33e635c04213a4fac2e20ec09dbdd97a4fe668566e5750b0c', 'function_size': 915, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 316, 'line_start': 283, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Buff.gd', 'state_schema': 'buff'}, 'Core/Buff.gd::changeReflectChance': {'argument_types': {}, 'arguments_exact': ['amount'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'buff'}, 'Core/Buff.gd::changeResistChance': {'argument_types': {}, 'arguments_exact': ['chance'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'buff'}, 'Core/Buff.gd::combatEnd': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'combatEnd', 'function_sha256': '56520ea40e402739ff4497d71435c1d5f47854cb307466f2ac10ace06fa06fc6', 'function_size': 58, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 345, 'line_start': 342, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Buff.gd', 'state_schema': 'buff'}, 'Core/Buff.gd::gainTemporary': {'argument_types': {'amount': 'int', 'duration': 'float', 'reflect': 'bool'}, 'arguments_exact': ['amount', 'duration', 'item', 'triggerEvent', 'reflect'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit', 'temporary_append'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 148}, {'line': 196}], 'function': 'gainTemporary', 'function_sha256': '385039ee0ba49fbaea0425752922c03728df65eeaacb1f21024009793f85841b', 'function_size': 3290, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 198, 'line_start': 76, 'mid': {'temporary_append': {'classification': 'assertion/provenance only', 'exact_payload': ['entry', 'buff', 'timer'], 'literal': '\t\t\t\ttemporaryStacks.push_back(tempStacks)', 'literal_sha256': '7691069fcac04fd24dbfca0665a74e71c97d92905eae92e58c51f22121328314', 'placement': 'after', 'wholefile_count': 1}}, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Buff.gd', 'state_schema': 'buff'}, 'Core/Buff.gd::init': {'argument_types': {}, 'arguments_exact': ['_type', '_character', '_counter', '_signalName'], 'channel': 'lineage', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 43}], 'function': 'init', 'function_sha256': 'e62b4fb80b552569f479cb81eaa2e0c1148930a03af17e182a8bd445c4cee653', 'function_size': 448, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 44, 'line_start': 25, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Buff.gd', 'state_schema': 'buff'}, 'Core/Buff.gd::loseStacks': {'argument_types': {'amount': 'int'}, 'arguments_exact': ['amount', 'item', 'triggerEvent', 'used'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 280}], 'function': 'loseStacks', 'function_sha256': 'e3ee6d0bce4c5c60164ccd562955129d892222d9684132b461b7d3d7a3007f80', 'function_size': 2139, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 282, 'line_start': 199, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Buff.gd', 'state_schema': 'buff'}, 'Core/Buff.gd::onTimeout': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit', 'temporary_remove'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'onTimeout', 'function_sha256': '538d354e7084516fdca7a29a15abc8285241b3a198c850ebd72d218e286b4044', 'function_size': 636, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 341, 'line_start': 317, 'mid': {'temporary_remove': {'classification': 'assertion/provenance only', 'exact_payload': ['buff', 'timer'], 'literal': '\ttemporaryStacks.remove(nextTemporaryTimeout)', 'literal_sha256': '939dd28b221c8d6d5ec04038bb580302d9964a1925951da5a7a0bcba30f10d81', 'placement': 'after', 'wholefile_count': 1}}, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Buff.gd', 'state_schema': 'buff'}, 'Core/Character.gd::_physics_process': {'argument_types': {'delta': 'float'}, 'arguments_exact': ['delta'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': '_physics_process', 'function_sha256': 'fedb90d907d81a35a3f322fd8952303dec9599780e7d03e0bea5ee8c7ecc7306', 'function_size': 187, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 1036, 'line_start': 1029, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Character.gd', 'state_schema': 'character'}, 'Core/Character.gd::_ready': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::changeBuffProtectStacks': {'argument_types': {}, 'arguments_exact': ['amount'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::changeDebuffReflectStacks': {'argument_types': {}, 'arguments_exact': ['amount'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::changeMaxHealthTemporary': {'argument_types': {}, 'arguments_exact': ['amount', 'item', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::cleanse': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::combatEnd': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'combatEnd', 'function_sha256': 'aaa57772d5227b3b11696abad5932e103472eede591f8887a5427604ef4fcac1', 'function_size': 217, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 348, 'line_start': 338, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Character.gd', 'state_schema': 'character'}, 'Core/Character.gd::combatStart': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'combatStart', 'function_sha256': 'e6a9c9563ec92963fc396dfc4e9d5a761e1f10df3ca57f98c066633a100ebe7a', 'function_size': 214, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 337, 'line_start': 328, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Character.gd', 'state_schema': 'character'}, 'Core/Character.gd::endBattleRage': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::endStun': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::gainMana': {'argument_types': {'amount': 'int'}, 'arguments_exact': ['amount', 'item', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 1280}], 'state_schema': 'character'}, 'Core/Character.gd::gainStacks': {'argument_types': {'amount': 'int', 'reflect': 'bool'}, 'arguments_exact': ['buffType', 'amount', 'item', 'triggerEvent', 'reflect'], 'channel': 'runtime', 'explicit_returns': [{'line': 1152}], 'state_schema': 'character'}, 'Core/Character.gd::gainStacksTemporary': {'argument_types': {'amount': 'int', 'reflect': 'bool'}, 'arguments_exact': ['buffType', 'amount', 'duration', 'item', 'triggerEvent', 'reflect'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 1157}], 'function': 'gainStacksTemporary', 'function_sha256': '14f08f31d925c784c74b6ab136bb7b4810a372db1370b2ddc802a20c5df1cb7f', 'function_size': 207, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 1159, 'line_start': 1154, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Character.gd', 'state_schema': 'character'}, 'Core/Character.gd::invulnerabilityEnded': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::loseHealth': {'argument_types': {}, 'arguments_exact': ['amount', 'item', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 869}], 'state_schema': 'character'}, 'Core/Character.gd::makeInvulnerable': {'argument_types': {}, 'arguments_exact': ['invuDur', 'item', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 1051}], 'state_schema': 'character'}, 'Core/Character.gd::onTick': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'onTick', 'function_sha256': '8331593a21e5edc9eb4426da830c7b5a21c10bf7b809a566b20090f4863ce9e8', 'function_size': 388, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 415, 'line_start': 401, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Character.gd', 'state_schema': 'character'}, 'Core/Character.gd::prepare': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'prepare', 'function_sha256': 'bb0281bf5e7bb4d4b3487a02288aa2ff2b81f6aa9da94a507ff3d089e2a6b58c', 'function_size': 928, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 327, 'line_start': 294, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Character.gd', 'state_schema': 'character'}, 'Core/Character.gd::startBattleRage': {'argument_types': {}, 'arguments_exact': ['item', 'duration', 'triggerEvent', 'applyBonus'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::stun': {'argument_types': {}, 'arguments_exact': ['duration', 'item', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'character'}, 'Core/Character.gd::takeDamage': {'argument_types': {'damageSource': 'damage_source|null'}, 'arguments_exact': ['damageSource', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 505}, {'line': 653}], 'state_schema': 'character'}, 'Core/Character.gd::useMana': {'argument_types': {'amount': 'int'}, 'arguments_exact': ['amount', 'item', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 1285}], 'state_schema': 'character'}, 'Core/Character.gd::useStacks': {'argument_types': {'amount': 'int'}, 'arguments_exact': ['buffType', 'amount', 'item', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 1164}], 'state_schema': 'character'}, 'Core/CombatLog.gd::createEvent': {'argument_types': {}, 'arguments_exact': ['triggerEvent', 'origin', 'type'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit', 'allocation_increment'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 249}], 'function': 'createEvent', 'function_sha256': 'b3e2e3ce13598dfe4749363d57cdfa61682b532131a461d554bcad8b4a91dab6', 'function_size': 293, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 251, 'line_start': 240, 'mid': {'allocation_increment': {'classification': 'assertion/provenance only', 'exact_payload': ['eventNum'], 'literal': '\teventNum += 1', 'literal_sha256': 'abaa54270cd781b84811d37502a3f48ed3ec7b38876d1a3405e3d76009eef372', 'placement': 'after', 'wholefile_count': 1}}, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/CombatLog.gd', 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::createEvent_BattleRageEnd': {'argument_types': {}, 'arguments_exact': ['playerId', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 846}], 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::createEvent_BattleRageStart': {'argument_types': {}, 'arguments_exact': ['item', 'duration', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 840}], 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::createEvent_InvulnerableEnd': {'argument_types': {}, 'arguments_exact': ['item', 'playerId', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 796}], 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::createEvent_InvulnerableStart': {'argument_types': {}, 'arguments_exact': ['item', 'duration', 'playerId', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 791}], 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::createEvent_Stack': {'argument_types': {'amount': 'int', 'item': 'native_ref|null', 'playerId': 'int', 'reflected': 'bool', 'triggerEvent': 'event_ref|null', 'type': 'int', 'used': 'bool'}, 'arguments_exact': ['type', 'item', 'amount', 'playerId', 'triggerEvent', 'used', 'reflected'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 750}], 'function': 'createEvent_Stack', 'function_sha256': '7dc8b46ff3f3f60aec710480b0e577d7a19cf75c604bb136f30f58a72d53d6f2', 'function_size': 1144, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 751, 'line_start': 722, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/CombatLog.gd', 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::createEvent_StackTemporary': {'argument_types': {'reflected': 'bool'}, 'arguments_exact': ['type', 'item', 'amount', 'duration', 'playerId', 'triggerEvent', 'reflected'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 757}], 'function': 'createEvent_StackTemporary', 'function_sha256': 'f14cb92522f5b357cb60bbbf377e793d3d104141c44913e5b241b9cc8270d809', 'function_size': 282, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 758, 'line_start': 752, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/CombatLog.gd', 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::createEvent_StackTimeout': {'argument_types': {}, 'arguments_exact': ['type', 'item', 'amount', 'playerId', 'triggerEvent'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 762}], 'function': 'createEvent_StackTimeout', 'function_sha256': 'eb97f7b740e90c09b61b4136a0266752731cd92c91fefea9aac9ca047bd7ca2b', 'function_size': 198, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 763, 'line_start': 759, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/CombatLog.gd', 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::logEvent': {'argument_types': {}, 'arguments_exact': ['event', 'afterFightAllowed'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit', 'append'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 267}], 'function': 'logEvent', 'function_sha256': 'befedbcc9b204c85363eae9b1515a80d80cce8077f52bc9e206de23374b5bdb3', 'function_size': 230, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 277, 'line_start': 266, 'mid': {'append': {'classification': 'assertion/provenance only', 'exact_payload': ['event', 'state'], 'literal': '\tevents.push_back(event)', 'literal_sha256': '4325b21393fd444a5099709259a13907b959da645dbea884d7b93026989ad536', 'placement': 'after', 'wholefile_count': 1}}, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/CombatLog.gd', 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::onCombatEnd': {'argument_types': {}, 'arguments_exact': ['roundResult'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'onCombatEnd', 'function_sha256': '08e31fae8e82b2f5979d7299260e4e864f900edf9a74994f9ed2023ee7a550ba', 'function_size': 777, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 225, 'line_start': 194, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/CombatLog.gd', 'state_schema': 'combat_log'}, 'Core/CombatLog.gd::snapshotItemState': {'argument_types': {'event': 'event_ref|null', 'withNextEvent': 'bool'}, 'arguments_exact': ['item', 'state', 'withNextEvent', 'event'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'snapshotItemState', 'function_sha256': '89cd95788263e6b2cab62cb6902d1a42d4306b021770f836832d2829dee623e8', 'function_size': 378, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 516, 'line_start': 503, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/CombatLog.gd', 'state_schema': 'combat_log'}, 'Core/Game.gd::activateItems': {'argument_types': {}, 'arguments_exact': ['items'], 'channel': 'input', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'activateItems', 'function_sha256': '007c1feade10ee128decb34393cf1b44d5da5871fc195497b102816fac9f8431', 'function_size': 266, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 3083, 'line_start': 3066, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Game.gd', 'state_schema': 'game'}, 'Core/Game.gd::combatEndDeferred': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'combatEndDeferred', 'function_sha256': 'f1b66ade553d36af1b25448dd0c70419de354bdceee06a267b22f091e96d9e41', 'function_size': 1713, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 3180, 'line_start': 3114, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Game.gd', 'state_schema': 'game'}, 'Core/Game.gd::endCombat': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 3086}], 'function': 'endCombat', 'function_sha256': '12bc1c002707660c489a1251d1361c0e101aceea404f378fc80889c986985643', 'function_size': 816, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 3113, 'line_start': 3084, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Game.gd', 'state_schema': 'game'}, 'Core/Game.gd::prepareItems': {'argument_types': {}, 'arguments_exact': ['items'], 'channel': 'input', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'prepareItems', 'function_sha256': '8799a2f3988a9060d43c9d94189b357ef8efcff41bc20a324e48996e70bb158f', 'function_size': 104, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 3065, 'line_start': 3059, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Core/Game.gd', 'state_schema': 'game'}, 'Interface/CombatTimer/CombatTimer.gd::_physics_process': {'argument_types': {'delta': 'float'}, 'arguments_exact': ['delta'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': '_physics_process', 'function_sha256': 'a61a3c93efd7fe3e535bb10135dfe9203da96d33a88eb327c61c8325f41de7d2', 'function_size': 83, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 125, 'line_start': 122, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Interface/CombatTimer/CombatTimer.gd', 'state_schema': 'combat_timer'}, 'Interface/CombatTimer/CombatTimer.gd::combatEnd': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'combatEnd', 'function_sha256': 'aa5f220eada602d17186204897396ad2f1cded9b50446f80bcf7e75b51fc7f10', 'function_size': 442, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 113, 'line_start': 98, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Interface/CombatTimer/CombatTimer.gd', 'state_schema': 'combat_timer'}, 'Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'dealFatigueDamage', 'function_sha256': 'a5c61c08fbc0785326b3c1d46fd2148359f09c0de833a209244cbefafe89537c', 'function_size': 949, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 180, 'line_start': 153, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Interface/CombatTimer/CombatTimer.gd', 'state_schema': 'combat_timer'}, 'Interface/CombatTimer/CombatTimer.gd::start': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'start', 'function_sha256': 'fea0b602a1bf9196c5db1d331e8574f398be27aa9ea976e1debc2c2de4371651', 'function_size': 140, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 121, 'line_start': 114, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Interface/CombatTimer/CombatTimer.gd', 'state_schema': 'combat_timer'}, 'Interface/CombatTimer/CombatTimer.gd::startFatigue': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'startFatigue', 'function_sha256': '967da52da40673cacc45c192b5c88ca075f4f106795b112818a174cacee760e0', 'function_size': 172, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 152, 'line_start': 145, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Interface/CombatTimer/CombatTimer.gd', 'state_schema': 'combat_timer'}, 'Items/Exclusive/KingGoobert.gd::buffEnded': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'king'}, 'Items/Exclusive/KingGoobert.gd::doCooldownEffect': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'king'}, 'Items/Exclusive/KingGoobert.gd::onCombatEnd': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'king'}, 'Items/Exclusive/KingGoobert.gd::onStateChanged': {'argument_types': {}, 'arguments_exact': ['_crownState'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'king'}, 'Items/Exclusive/KingGoobert.gd::prepare': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'king'}, 'Items/HealthPotion.gd::onDamaged': {'argument_types': {}, 'arguments_exact': ['_healthChange', 'event'], 'channel': 'runtime', 'explicit_returns': [{'line': 13}], 'state_schema': 'potion'}, 'Items/HealthPotion.gd::onPrepare': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'potion'}, 'Items/HealthPotion.gd::onTriggerPotion': {'argument_types': {}, 'arguments_exact': ['triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'potion'}, 'Items/Item.gd::_physics_process': {'argument_types': {'delta': 'float'}, 'arguments_exact': ['delta'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': '_physics_process', 'function_sha256': 'c4258175c89b0f0bce5b40591e3cd076c9a3dcc5233d746294d8c67446718dba', 'function_size': 202, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 4445, 'line_start': 4436, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Items/Item.gd', 'state_schema': 'item'}, 'Items/Item.gd::_ready': {'argument_types': {}, 'arguments_exact': [], 'channel': 'lineage', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': '_ready', 'function_sha256': '07614105a2dab6ac94d109bc20e4997264c7dd578d513da8108eefbe65de3eea', 'function_size': 3024, 'line_end': 627, 'line_start': 510, 'source': 'Items/Item.gd', 'state_schema': 'generic'}, 'Items/Item.gd::activate': {'argument_types': {}, 'arguments_exact': ['damageRes', 'playCombatAni', 'consume', 'animationOverride'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 4672}, {'line': 4673}, {'line': 4685}, {'line': 4720}], 'function': 'activate', 'function_sha256': 'babc0ca5e748234525bc36a01557199014d7f7e44da0551b899090ef78007828', 'function_size': 1073, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 4722, 'line_start': 4669, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Items/Item.gd', 'state_schema': 'item'}, 'Items/Item.gd::addBonusDamage': {'argument_types': {'removable': 'bool'}, 'arguments_exact': ['damage', 'removable'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Item.gd::cleanseRandomDebuffs': {'argument_types': {}, 'arguments_exact': ['numDebuffs', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Item.gd::combatEnd': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'combatEnd', 'function_sha256': '420f6162e6c714d86cb1be5a0b167e61021e4c3d8cc28d54190eb1387340b3df', 'function_size': 131, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 3421, 'line_start': 3414, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Items/Item.gd', 'state_schema': 'item'}, 'Items/Item.gd::consume': {'argument_types': {}, 'arguments_exact': ['damageRes', 'playCombatAni'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Item.gd::getMostStacks': {'argument_types': {}, 'arguments_exact': ['target', 'availableStacks'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 5561}], 'function': 'getMostStacks', 'function_sha256': 'e682309b125bb29256febb13c83083f2dd66eaea44649298adb4177a59bbb97b', 'function_size': 385, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 5562, 'line_start': 5546, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Items/Item.gd', 'state_schema': 'item'}, 'Items/Item.gd::giveMana': {'argument_types': {}, 'arguments_exact': ['amount', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Item.gd::giveMana_capped': {'argument_types': {}, 'arguments_exact': ['amount', 'maximum', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 5056}, {'line': 5058}], 'state_schema': 'item'}, 'Items/Item.gd::giveMaxHealth': {'argument_types': {}, 'arguments_exact': ['amount', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Item.gd::giveMostBuffs': {'argument_types': {}, 'arguments_exact': ['numBuffs', 'triggerEvent', 'availableBuffs'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'giveMostBuffs', 'function_sha256': 'bce705953d4eb718d3530101d6e9b6dac67f36e2c4f72cd27fe2fb406adbdd48', 'function_size': 258, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 5568, 'line_start': 5563, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Items/Item.gd', 'state_schema': 'item'}, 'Items/Item.gd::healthToBlock': {'argument_types': {'health': 'float'}, 'arguments_exact': ['health', 'block', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Item.gd::miniActivate': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Item.gd::pickRandomStacks': {'argument_types': {}, 'arguments_exact': ['stackTypes', 'numStacks', 'target', 'priorityStack'], 'channel': 'runtime', 'explicit_returns': [{'line': 5427}], 'state_schema': 'item'}, 'Items/Item.gd::prepare': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'prepare', 'function_sha256': 'ad66c806b5d4d2f1862828b1382e2f91648f5120354a00722da9711eda94839f', 'function_size': 171, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 3354, 'line_start': 3344, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Items/Item.gd', 'state_schema': 'item'}, 'Items/Item.gd::rollChance': {'argument_types': {}, 'arguments_exact': ['chance'], 'channel': 'runtime', 'explicit_returns': [{'line': 4391}], 'state_schema': 'item'}, 'Items/Item.gd::stealLife': {'argument_types': {'lifestealFactor': 'float'}, 'arguments_exact': ['damage', 'lifestealFactor', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 5123}], 'state_schema': 'item'}, 'Items/Item.gd::tryUseMana': {'argument_types': {}, 'arguments_exact': ['amount', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 5070}, {'line': 5072}], 'state_schema': 'item'}, 'Items/Item.gd::useMana': {'argument_types': {}, 'arguments_exact': ['amount', 'triggerEvent'], 'channel': 'runtime', 'explicit_returns': [{'line': 5064}], 'state_schema': 'item'}, 'Items/ItemDescriptor.gd::instantiate': {'argument_types': {}, 'arguments_exact': [], 'channel': 'lineage', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 92}], 'function': 'instantiate', 'function_sha256': 'bb2f1cb642403e4c34c75752ef26cf555dd3baeac031c1db504b21f2bd777b35', 'function_size': 87, 'line_end': 93, 'line_start': 89, 'source': 'Items/ItemDescriptor.gd', 'state_schema': 'generic'}, 'Items/ItemDescriptor.gd::instantiate_pooled': {'argument_types': {}, 'arguments_exact': [], 'channel': 'lineage', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 98}], 'function': 'instantiate_pooled', 'function_sha256': '8dc072a9c7a148c76916f040e4f84b0950d4d67f36704ee84f14d4e5f23632e2', 'function_size': 124, 'line_end': 99, 'line_start': 94, 'source': 'Items/ItemDescriptor.gd', 'state_schema': 'generic'}, 'Items/Potion.gd::activate': {'argument_types': {'emitSignal': 'bool'}, 'arguments_exact': ['damageRes', 'playCombatAni', 'consume', 'animationOverride', 'emitSignal'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'potion'}, 'Items/Potion.gd::consumePotion': {'argument_types': {'withActivate': 'bool'}, 'arguments_exact': ['event', 'withActivate'], 'channel': 'runtime', 'explicit_returns': [{'line': 58}], 'state_schema': 'potion'}, 'Items/Potion.gd::prepare': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'potion'}, 'Items/Potion.gd::triggerPotion': {'argument_types': {}, 'arguments_exact': ['triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'potion'}, 'Items/Weapon.gd::attack': {'argument_types': {}, 'arguments_exact': ['triggerEvent'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Items/Weapon.gd::doCooldownEffect': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'item'}, 'Sheets/ItemBook.gd::detectMentionedStacks': {'argument_types': {}, 'arguments_exact': [], 'channel': 'metadata', 'comparison': 'relational originalinitialization completion marker; directdescriptorread only afterthisreturn; no translationgetterinstrumentation', 'edges': ['enter', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'detectMentionedStacks', 'function_sha256': '4dfc76dfeb1ad9903f3ffcb980325e45f9c802fc768b30db893dd5e7a23a5f27', 'function_size': 668, 'implicit_edge': 'appendcompletion recordonly; noGamecall', 'line_end': 1388, 'line_start': 1363, 'nullable_fields': 'none', 'source': 'Sheets/ItemBook.gd', 'state_schema': 'generic'}, 'Utility/AutoHideParticles.gd::_ready': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'auto_hide'}, 'Utility/AutoHideParticles.gd::activate': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'auto_hide'}, 'Utility/AutoHideParticles.gd::deactivate': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'auto_hide'}, 'Utility/AutoHideParticles.gd::instantClear': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'auto_hide'}, 'Utility/AutoHideParticles.gd::startTimer': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'auto_hide'}, 'Utility/AutoHideParticles.gd::timeout': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'auto_hide'}, 'Utility/EventBus.gd::connectEvent': {'argument_types': {'emitter': 'native_ref|null', 'method': 'string', 'receiver': 'native_ref|null', 'signalName': 'string'}, 'arguments_exact': ['emitter', 'signalName', 'receiver', 'method'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit', 'registration'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'connectEvent', 'function_sha256': '3f6031d769974fba0e1c23fe8fff71db44234f917003a6999e83b5782664252a', 'function_size': 398, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 110, 'line_start': 98, 'mid': {'registration': {'classification': 'assertion/provenance only', 'exact_payload': ['emitter', 'signalName', 'receiver', 'method', 'emissionID', 'funcRefID', 'insertion_index'], 'literal': '\tUtil.dictAppend(connections, emissionID, funcRef)', 'literal_sha256': 'ddc55e120de7ed82a4b408d0e0473ccf229869c3162d8ab283b892b351ceba8e', 'placement': 'after', 'wholefile_count': 1}}, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Utility/EventBus.gd', 'state_schema': 'event_bus'}, 'Utility/EventBus.gd::disconnectAll': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'disconnectAll', 'function_sha256': '78a2571f417520c9ef7b2c1d5f11d12a6bc3efc147b5358d505c0fc64df7cea4', 'function_size': 47, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 133, 'line_start': 128, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Utility/EventBus.gd', 'state_schema': 'event_bus'}, 'Utility/EventBus.gd::emitAndLog': {'argument_types': {'arguments': 'array', 'emitter': 'native_ref|null', 'event': 'event_ref|null', 'signalName': 'string'}, 'arguments_exact': ['emitter', 'signalName', 'event', 'arguments'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit', 'receiver_attempt', 'receiver_return'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [{'line': 86}, {'line': 94}], 'function': 'emitAndLog', 'function_sha256': '02894443e26b9b30406cf21a6f7a091e357ce06b94091927654bb4d69c3b3c8a', 'function_size': 468, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 97, 'line_start': 56, 'mid': {'receiver_attempt': {'classification': 'assertion/provenance only', 'exact_payload': ['funcRefID', 'emissionID', 'event_id', 'fightEnded'], 'literal': '\tfor funcRef in connections.get(emissionID, []):', 'literal_sha256': 'ca298411f4a8f6cb6fd3f109deb14c3ab24be134349e8bef1bb5a54dfb6d5344', 'placement': 'inside', 'wholefile_count': 1}, 'receiver_return': {'classification': 'assertion/provenance only', 'exact_payload': ['funcRefID', 'emissionID', 'event_id', 'fightEnded'], 'literal': '\t\tfuncRef.call_funcv(arguments)', 'literal_sha256': 'ac6335571b3ae60e48c062127fa0005a1601e9eee7670503d4862dd3b4860214', 'placement': 'after', 'wholefile_count': 1}}, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Utility/EventBus.gd', 'state_schema': 'event_bus'}, 'Utility/EventBus.gd::flushLoggingQueue': {'argument_types': {}, 'arguments_exact': [], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit', 'mode_instant', 'queue_snapshot', 'queue_clear'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': 'flushLoggingQueue', 'function_sha256': '6ba47830ed17daf232ed8d9f0bd9f3a8cabdd0bcbc81282cf8b9ed28e9bbe25d', 'function_size': 321, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 37, 'line_start': 24, 'mid': {'mode_instant': {'classification': 'assertion/provenance only', 'exact_payload': ['state'], 'literal': '\tsetLoggingMode(LoggingMode.Instant)', 'literal_sha256': 'cb85de171e59f80e0b16d7387a87173f5f92215dfd35ee525114835b56df03f8', 'placement': 'after', 'wholefile_count': 1}, 'queue_clear': {'classification': 'assertion/provenance only', 'exact_payload': ['state'], 'literal': '\tsignalQueue.clear()', 'literal_sha256': '20550c6510453c1609962c520489322bbb15f4ea87d0e58df042cae79c6a1151', 'placement': 'after', 'wholefile_count': 1}, 'queue_snapshot': {'classification': 'assertion/provenance only', 'exact_payload': ['queue_snapshot', 'state'], 'literal': '\tvar queueDuplicate = signalQueue.duplicate()', 'literal_sha256': 'e72ff6c2767e9884ab578caff8aa45f0a541ed9f441647dc306b588aa1dcc927', 'placement': 'after', 'wholefile_count': 1}}, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Utility/EventBus.gd', 'state_schema': 'event_bus'}, 'Utility/Util.gd::_physics_process': {'argument_types': {}, 'arguments_exact': ['delta'], 'channel': 'runtime', 'comparison': 'input gate only actualGame entryinitial/order; allstateprepared/later output; IDsrelationalprovenance notPythoninput', 'edges': ['enter', 'return_explicit', 'return_implicit'], 'enter_payload': ['arguments', 'state'], 'exit_payload': ['return_value', 'state'], 'explicit_returns': [], 'function': '_physics_process', 'function_sha256': 'b4ec0241f8378ad4a17ad957ad6edc56d1b48f4f191d4df6f2a677c69b61f967', 'function_size': 213, 'implicit_edge': 'Recordfallthroughifcontrolcanreachfunctionend; neverinstrumentdifferentfunction/classblock', 'line_end': 157, 'line_start': 148, 'nullable_fields': 'Buff.init ENTER only unassignedcharacter/timer; tempconstructor ENTER fields notyetassigned; clockstampbootstrapnullable; othermissingfield fails', 'source': 'Utility/Util.gd', 'state_schema': 'util'}, 'Utility/Util.gd::_process': {'argument_types': {}, 'arguments_exact': ['delta'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'util'}, 'Utility/Util.gd::changeTimer': {'argument_types': {'t': 'float', 'timer': 'native_ref|null'}, 'arguments_exact': ['timer', 't'], 'channel': 'runtime', 'explicit_returns': [], 'state_schema': 'util'}, 'Items/Goobert.gd::prepare': {'channel': 'runtime', 'state_schema': 'goobert', 'arguments_exact': [], 'argument_types': {}, 'explicit_returns': []}, 'Items/Goobert.gd::onItemActivated': {'channel': 'runtime', 'state_schema': 'goobert', 'arguments_exact': ['event'], 'argument_types': {}, 'explicit_returns': []}, 'Items/Goobert.gd::doCooldownEffect': {'channel': 'runtime', 'state_schema': 'goobert', 'arguments_exact': [], 'argument_types': {}, 'explicit_returns': []}, 'Items/Food.gd::prepare': {'channel': 'runtime', 'state_schema': 'item', 'arguments_exact': [], 'argument_types': {}, 'explicit_returns': []}}}


def strict_json_loads(text):
    def pairs(rows):
        result={}
        for key,value in rows:
            if key in result: raise ValueError('duplicate JSON key: '+key)
            result[key]=value
        return result
    def number(s):
        v=float(s)
        if not math.isfinite(v): raise ValueError('nonfinite JSON number')
        return v
    return json.loads(text,object_pairs_hook=pairs,parse_float=number,parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite JSON '+s)))



def exact(value,keys):
    if type(value) is not dict or set(value)!=set(keys): raise ValueError('exact object keys required: '+str(keys))



def integer(value,low=-(1<<63),high=(1<<63)-1):
    if type(value) is not int or not low<=value<=high: raise ValueError('integer range/type')
    return value



def decimal(s,positive=False):
    if type(s) is not str or re.fullmatch(r'(?:0|-[1-9][0-9]*|[1-9][0-9]*)',s) is None: raise ValueError('canonical decimal required')
    return integer(int(s),1 if positive else -(1<<63))



def text(s):
    if type(s) is not str or len(s.encode('utf-8'))>CAPS['string_utf8']: raise ValueError('string type/UTF8 cap')
    return s



def validate_typed(v,depth=0):
    if depth>CAPS['depth']: raise ValueError('typed depth cap')
    if type(v) is not dict or v.get('type') not in CONTRACT['typed_exact']: raise ValueError('unknown typed value')
    t=v['type'];exact(v,CONTRACT['typed_exact'][t])
    if t=='null':return v
    if t=='bool':
        if type(v['value']) is not bool:raise ValueError('bool required')
    elif t=='string':text(v['value'])
    elif t=='int':decimal(v['decimal'])
    elif t=='float':
        s=v['binary64_be']
        if type(s) is not str or re.fullmatch('[0-9a-f]{16}',s) is None or not math.isfinite(struct.unpack('>d',bytes.fromhex(s))[0]):raise ValueError('finite BE64 required')
    elif t in ('native_ref','event_ref'):
        decimal(v['native_id'],True)
        if t=='event_ref':decimal(v['event_id'])
        else:
            if v['role'] is not None:text(v['role'])
            text(v['class'])
    elif t=='array':
        a=v['values']
        if type(a) is not list or len(a)>CAPS['array']:raise ValueError('array cap/type')
        for x in a:validate_typed(x,depth+1)
    elif t=='dictionary':
        a=v['entries'];seen=set()
        if type(a) is not list or len(a)>CAPS['dictionary']:raise ValueError('dictionary cap/type')
        for row in a:
            exact(row,['key','value']);validate_typed(row['key'],depth+1);validate_typed(row['value'],depth+1)
            k=json.dumps(row['key'],sort_keys=True,separators=(',',':'))
            if k in seen:raise ValueError('duplicate typed key')
            seen.add(k)
    elif t=='temporary':
        decimal(v['native_id'],True);integer(v['ordinal'],0,CAPS['array']-1)
        for k,kind in [('amount','int'),('timeout','float')]:
            validate_typed(v[k],depth+1)
            if v[k]['type']!=kind:raise ValueError('temporary field type '+k)
        validate_typed(v['item'],depth+1)
        if v['item']['type'] not in ('null','native_ref'):raise ValueError('temporary item ref')
    elif t in ('damage_result','damage_source'):
        decimal(v['native_id'],True)
        for k in v:
            if k not in ('type','native_id'):validate_typed(v[k],depth+1)
        fields=({'damage':'int','healthDamage':'int','hit':'bool','critical':'bool','damageReduction':'int'} if t=='damage_result' else {'minDamage':'int','maxDamage':'int','types':'array','accuracy':'float','critChancePercent':'float','flags':'int'})
        for k,kind in fields.items():
            if v[k]['type']!=kind:raise ValueError('damage field type '+k)
        refs={'event':('null','event_ref'),'damageSource':('null','damage_source')} if t=='damage_result' else {'origin':('null','native_ref')}
        for k,kinds in refs.items():
            if v[k]['type'] not in kinds:raise ValueError('damage reference type '+k)
    return v



def _base_validate_state(value,schema,constructor=False):
    if schema=='item':
        # Closed actual-source subtype schemas, never infer semantics from a name.
        candidates=[n for n in ('carrot','goobert','potion','item') if type(value) is dict and set(value)==set(CONTRACT['state_schemas'][n])]
        if not candidates:raise ValueError('unknown Item subtype field set')
        schema=candidates[0]
    fields=CONTRACT['state_schemas'][schema];exact(value,fields)
    for k,kind in fields.items():
        x=value[k]
        if kind in ('timer','timer|null','node'):
            if x is None and (kind.endswith('|null') or constructor):continue
            validate_state(x,'node' if kind=='node' else 'timer',constructor)
        elif kind=='id':decimal(x,True)
        elif schema=='node' and k in ('role','path'):
            if x is not None:text(x)
        elif schema=='node' and k in ('name','class'):text(x)
        elif kind=='int_array':
            if type(x) is not list or len(x)>CAPS['depth']:raise ValueError('ancestor path cap')
            for i in x:integer(i,-1,1<<31)
        elif schema=='node' and kind=='bool':
            if type(x) is not bool:raise ValueError('node bool')
        elif schema=='node' and kind=='int':integer(x,-(1<<31),(1<<31)-1)
        elif schema=='timer' and kind in ('bool','int','float'):
            if kind=='bool' and type(x) is not bool:raise ValueError('timer bool')
            if kind=='int':integer(x,0,1)
            if kind=='float':
                validate_typed(x)
                if x['type']!='float':raise ValueError('timer float raw type')
        else:
            validate_typed(x)
            allowed=kind.split('|')
            if kind=='temporary_array':
                if x['type']!='array' or any(y['type']!='temporary' or y['ordinal']!=i for i,y in enumerate(x['values'])):raise ValueError('temporary ordered projection')
            elif x['type'] not in allowed:raise ValueError('state raw type '+schema+'.'+k)
    return value



def _base_primitive_context(label,kind):
    text(label)
    c=dict.fromkeys(CONTRACT['primitive_context_exact'])
    inst=r'[PO]:[0-9]+'
    if kind=='global_u32':
        m=re.fullmatch(r'fraction_shuffle:('+inst+r'):([PO]):(direct|multiply|remove|steal):([0-5]):([2-7])',label)
        if not m:raise ValueError('fraction instance context')
        item,target,op,i,w=m.groups();i=int(i);w=int(w)
        if w!=7-i:raise ValueError('fraction ordinal/width')
        c.update(item=item,target=target,operation=op,ordinal=i,width=w)
    elif label.startswith('buff:'):
        m=re.fullmatch(r'buff:(resist|amplify|protect|unprotect):([PO]):('+inst+r'|null):([A-Za-z]+):([0-9]+)',label)
        if not m:raise ValueError('buff label')
        br,target,item,stack,i=m.groups();c.update(branch=br,target=target,item=item,stack=stack,ordinal=int(i))
    elif label.startswith('reflect:'):
        m=re.fullmatch(r'reflect:([PO]):('+inst+r'|null):([A-Za-z]+)',label)
        if not m:raise ValueError('reflect label')
        target,item,stack=m.groups();c.update(branch='reflect',target=target,item=item,stack=stack)
    elif label.startswith('random_stack:'):
        m=re.fullmatch(r'random_stack:('+inst+r'):([PO]):(take|give):([0-9]+)',label)
        if not m:raise ValueError('stack pick label')
        item,target,op,i=m.groups();c.update(item=item,target=target,operation=op,ordinal=int(i))
    elif not re.fullmatch(r'(?:(?:cooldown|damage|double_attack_effect):'+inst+r'|(?:accuracy|critical):[PO]:'+inst+r'|item_chance:'+inst+r':(?:primary|secondary)|(?:fatigue|spikes|poison):[PO])',label):raise ValueError('unknown primitive label')
    if c['stack'] is not None and c['stack'] not in ('Block','Lucky','Regeneration','Vampirism','Spikes','Mana','Empower','Heat','Poison','Blind','Cold'):raise ValueError('unknown stack label')
    return c



def scalar_number(v):
    validate_typed(v)
    if v['type']=='int':return int(v['decimal'])
    if v['type']=='float':return struct.unpack('>d',bytes.fromhex(v['binary64_be']))[0]
    raise ValueError('numeric scalar required')



def _base_validate_primitive(p):
    exact(p,CONTRACT['primitive_exact']);k=p['kind'];a=p['args'];v=p['value']
    if k not in ('randf','randf_range','randi_range','global_u32'):raise ValueError('primitive kind')
    expected_context=primitive_context(p['label'],k);exact(p['context'],CONTRACT['primitive_context_exact'])
    # reflect_argument is separate actual source context, never inferred from outcomes.
    actual=dict(p['context']);ref=actual.pop('reflect_argument');expected_context.pop('reflect_argument')
    if actual!=expected_context or (ref is not None and type(ref) is not bool):raise ValueError('primitive context mismatch')
    for context_key in ('ordinal','width'):
        if p['context'][context_key] is not None:integer(p['context'][context_key],0,8192)
    if type(a) is not list or len(a)!=(2 if k.endswith('_range') else 0):raise ValueError('primitive argc')
    for x in a:validate_typed(x)
    validate_typed(v)
    if k in ('global_u32','randi_range'):
        if v['type']!='int' or any(x['type']!='int' for x in a):raise ValueError('integer primitive raw type')
        n=int(v['decimal'])
        if k=='global_u32':integer(n,0,4294967295)
        elif not scalar_number(a[0])<=n<=scalar_number(a[1]):raise ValueError('integer primitive range')
    else:
        if v['type']!='float':raise ValueError('float primitive raw type')
        n=scalar_number(v)
        if k=='randf' and not 0<=n<=1:raise ValueError('randf range')
        if k=='randf_range' and not scalar_number(a[0])<=n<=scalar_number(a[1]):raise ValueError('float primitive range')
    # Exact sites have source Variant endpoint types, not just numeric equality.
    label=p['label']
    if label.startswith(('buff:','reflect:')):
        if k!='randf_range' or a!=[{'type':'int','decimal':'0'},{'type':'float','binary64_be':'4059000000000000'}]:raise ValueError('flipPercent source INT0 REAL100')
        branch=p['context']['branch']
        if branch in ('resist','amplify','reflect') and type(ref) is not bool:raise ValueError('actual source reflect argument required')
        if branch in ('protect','unprotect') and ref is not None:raise ValueError('protection has no reflect argument')
    elif label.startswith(('item_chance:','accuracy:','critical:')) and k!='randf':raise ValueError('BalancedRandom source randf')
    if label.startswith('cooldown:') and (k!='randf_range' or any(x['type']!='float' for x in a) or [scalar_number(x) for x in a] not in ([.975,1.05],[.95,1.05])):raise ValueError('cooldown args')
    if label.startswith('double_attack_effect:') and k!='randf':raise ValueError('double attack primitive')
    if label.startswith(('random_stack:','damage:','fatigue:','spikes:','poison:')) and k!='randi_range':raise ValueError('integer site primitive')
    return p



def _base_validate_record(row):
    exact(row,CONTRACT['envelope_exact'])
    if row['schema']!='observer7-record/1':raise ValueError('record schema')
    integer(row['sequence'],0,CAPS['records']-1)
    site=row['site'];edge=row['edge'];text(site);text(edge)
    validate_typed(row['subject'])
    if row['subject']['type'] not in ('null','native_ref'):raise ValueError('subject ref')
    s=row['stamp'];exact(s,CONTRACT['stamp_exact']);integer(decimal(s['physics_frame']),0);integer(decimal(s['idle_frame']),0);text(s['phase'])
    for name in ('util_time','combat_time'):
        validate_typed(s[name])
        if s[name]['type'] not in ('float','null'):raise ValueError('stamp clock')
    p=row['payload']
    if row['channel']=='primitive':
        if site not in CONTRACT['primitive_sites'] and site!='fixed7fraction_shuffle':raise ValueError('primitive site')
        if edge!='return_native_primitive':raise ValueError('primitive edge')
        if p['kind']!=CONTRACT['primitive_sites'][site]['kind']:raise ValueError('primitive source kind')
        validate_primitive(p)
        families={
            'Utility/Util.gd::roll':('buff:','reflect:'),
            'Utility/Util.gd::flip':('accuracy:','critical:','item_chance:','double_attack_effect:'),
            'Utility/Util.gd::pickRandomElement':('random_stack:',),
            'Utility/Util.gd::randPitch':('invulnerability_pitch:',),
            'Utility/BalancedRange.gd::randIntRange':('damage:',),
            'Utility/DamageSource.gd::randDamage':('fatigue:','spikes:','poison:'),
            'Items/Item.gd::adjustCooldown:belowMasterOpponent':('cooldown:',),
            'Items/Item.gd::adjustCooldown:other':('cooldown:',),
            'fixed7fraction_shuffle':('fraction_shuffle:',)}
        if not p['label'].startswith(families[site]):raise ValueError('primitive source label family')
        if site.startswith('Items/Item.gd::adjustCooldown:'):
            expected=[.975,1.05] if site.endswith('belowMasterOpponent') else [.95,1.05]
            if [scalar_number(x) for x in p['args']]!=expected:raise ValueError('cooldown branch endpoint')
    elif edge in ('timer_before','timer_after'):
        if site not in MATRIX['sites'] or row['channel']!='runtime':raise ValueError('timer site/channel')
        exact(p,CONTRACT['lifecycle_api_exact']);text(p['role']);integer(p['argc'],0,1)
        if p['operation'] not in ('start','stop') or type(p['args']) is not list or len(p['args'])!=p['argc'] or (p['operation']=='stop' and p['argc']!=0):raise ValueError('timer operation/argc')
        for a in p['args']:validate_typed(a);scalar_number(a)
        allowed=[x for x in MATRIX['Timer_API_statement_sites'] if x['site']==site and x['operation']==p['operation'] and x['argc']==p['argc']]
        if not allowed:raise ValueError('Timer source call site/argc')
        if p['operation']=='start' and p['args']:
            expected= {'Interface/CombatTimer/CombatTimer.gd::start':14,'Interface/CombatTimer/CombatTimer.gd::startFatigue':3,'Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage':1}
            if site in expected:
                if p['args']!=[{'type':'int','decimal':str(expected[site])}]:raise ValueError('Timer source INT argument')
            elif p['args'][0]['type']!='float':raise ValueError('Timer source REAL argument')
        for k in ('public_before','public_after'):
            if p[k] is not None:validate_state(p[k],'timer')
        if (edge=='timer_before' and p['public_after'] is not None) or (edge=='timer_after' and p['public_before'] is not None):raise ValueError('timer edge shape')
    elif edge=='checkpoint':
        if site not in ('Core/Game.gd::prepareItems','Core/Game.gd::activateItems') or row['channel']!='input':raise ValueError('checkpoint site')
        exact(p,['environment','nodes','items']);env=p['environment'];exact(env,['fps','scale','paused'])
        for key,kind in [('fps','int'),('scale','float'),('paused','bool')]:
            validate_typed(env[key])
            if env[key]['type']!=kind:raise ValueError('environment raw type')
        if type(p['nodes']) is not list or len(p['nodes'])>CAPS['sparse_nodes'] or type(p['items']) is not list or len(p['items'])>128:raise ValueError('checkpoint count')
        roles=set();native=set()
        for node in p['nodes']:
            exact(node,['role','node','timer']);text(node['role']);validate_state(node['node'],'node')
            if node['role'] in roles or node['node']['native_id'] in native:raise ValueError('checkpoint duplicate role/node')
            roles.add(node['role']);native.add(node['node']['native_id'])
            if node['timer'] is not None:
                validate_state(node['timer'],'timer')
                if node['timer']['node']!=node['node']:raise ValueError('Timer Node projection mismatch')
        seen=set()
        for item in p['items']:
            exact(item,['instance','fields','dragged','moveback_running','cachedAffectedItems','currentAffectedItems']);text(item['instance'])
            if item['instance'] in seen:raise ValueError('duplicate checkpoint item')
            seen.add(item['instance']);validate_state(item['fields'],'item')
            for k in ('dragged','moveback_running'):
                validate_typed(item[k])
                if item[k]['type']!='bool':raise ValueError('checkpoint guard bool')
            for k in ('cachedAffectedItems','currentAffectedItems'):
                validate_typed(item[k])
                if item[k]['type']!='dictionary':raise ValueError('checkpoint raw cache')
    elif edge=='scene_instance':
        if site not in ('Items/ItemDescriptor.gd::instantiate','Items/ItemDescriptor.gd::instantiate_pooled') or row['channel']!='lineage':raise ValueError('scene provenance site')
        exact(p,MATRIX['extra_edges']['scene_instance'])
        decimal(p['descriptor_id'],True);decimal(p['item_id'],True);validate_typed(p['item_index'])
        if p['item_index']['type']!='int' or type(p['pooled']) is not bool:raise ValueError('scene provenance types')
        text(p['scene_path'])
        if p['particle'] is not None:validate_state(p['particle'],'timer')
    elif edge=='allocation_complete':
        if not site.startswith('Core/CombatLog.gd::createEvent') or row['channel']!='allocation':raise ValueError('allocation site')
        exact(p,['event_data']);event=p['event_data'];exact(event,['native_id','id','timestamp','parentEvent','origin','target','type','params','snapshot']);decimal(event['native_id'],True)
        for k in event:
            if k!='native_id':validate_typed(event[k])
        if event['id']['type']!='int' or event['parentEvent']['type'] not in ('null','event_ref'):raise ValueError('event identity types')
    elif edge=='loaded_descriptors':
        if site!='Sheets/ItemBook.gd::detectMentionedStacks' or row['channel']!='metadata':raise ValueError('metadata site')
        exact(p,['descriptors','locale']);text(p['locale']);validate_typed(p['descriptors'])
        if p['descriptors']['type']!='array' or len(p['descriptors']['values'])!=CAPS['descriptors']:raise ValueError('descriptor count')
        ids=set()
        for desc in p['descriptors']['values']:
            if desc['type']!='dictionary':raise ValueError('descriptor dictionary')
            if len(desc['entries'])!=10 or any(r['key']['type']!='string' for r in desc['entries']):raise ValueError('descriptor exact string keys')
            fields={r['key']['value']:r['value'] for r in desc['entries']}
            exact(fields,['itemIndex','identifier','types','tags','gainedStacks','removedStacks','usedStacks','hasBattleRageEffect','descriptionKey','scene_path'])
            for k in ('itemIndex','tags','gainedStacks','removedStacks','usedStacks'):
                if fields[k]['type']!='int':raise ValueError('descriptor integer')
            if fields['hasBattleRageEffect']['type']!='bool' or fields['types']['type']!='array':raise ValueError('descriptor types')
            id=int(fields['itemIndex']['decimal'])
            if id in ids or id not in DESCRIPTOR_IDS:raise ValueError('descriptor ID duplicate/unknown')
            ids.add(id)
            for k in ('identifier','descriptionKey','scene_path'):
                if fields[k]['type']!='string':raise ValueError('descriptor string')
        if ids!=DESCRIPTOR_IDS:raise ValueError('exact descriptor ID set')
    elif site in MATRIX['sites']:
        spec=MATRIX['sites'][site]
        if edge in ('enter','return_explicit','return_implicit'):
            if row['channel']!=spec['channel']:raise ValueError('channel/site mismatch')
            if edge=='return_explicit' and not spec['explicit_returns']:raise ValueError('nonexistent explicit return')
            exact(p,['arguments','state'] if edge=='enter' else ['return_value','state'])
            validate_typed(p['arguments'] if edge=='enter' else p['return_value'])
            validate_state(p['state'],spec['state_schema'],site.endswith(('::init','::_init')) or site.endswith('TemporaryStacks._init'))
        elif edge in spec.get('mid',{}):
            channel='registration' if edge in ('registration','receiver_attempt','receiver_return') else ('allocation' if edge in ('allocation_increment','append') else 'runtime')
            if row['channel']!=channel:raise ValueError('mid edge channel')
            exact(p,spec['mid'][edge]['exact_payload'])
            for key,v in p.items():
                if key in ('state','buff'):
                    validate_state(v,'buff' if key=='buff' else spec['state_schema'])
                elif key=='timer':validate_state(v,'timer')
                else:validate_typed(v)
        else:raise ValueError('unknown site edge')
    else:raise ValueError('unknown record site')
    encoded=json.dumps(row,ensure_ascii=False,separators=(',',':')).encode()+b'\n'
    if len(encoded)>CAPS['record_bytes']:raise ValueError('record byte cap')
    return row



SINGLE_KING_GENUINE_PROFILE = 'observer7-king-basic-A-native-tape/1'


SINGLE_KING_OBSERVER_VERSION = '7-king-basic-A-460'


SINGLE_KING_CASE = 'KING-BASIC-A-460'


SINGLE_KING_TERMINAL = 'first-actual-idle-after-at-least-two-future-physics/1'


SINGLE_KING_ITEMS = frozenset({1,4,11,19,22,23,262})


SINGLE_KING_FIXTURE_SHA256 = '20c259d7a7b99ef18f006b049c362fde21830cbb557d5879016282bf7451c0a2'


SINGLE_KING_ROLES = frozenset(['P:0', 'P:1', 'P:2', 'P:3', 'P:4', 'P:5', 'P:6', 'P:7', 'P:8', 'P:9', 'P:10', 'P:11', 'P:12', 'P:13', 'O:0', 'O:1', 'O:2', 'O:3', 'O:4', 'O:5', 'O:6', 'O:7', 'O:8', 'O:9', 'O:10', 'O:11'])


_ui_CASE = 'NATIVE-V7-008-KING-UI-GUARDED-127'


_ui_FILE = 'king-ui-authority.jsonl'


_ui_SCHEMA = 'phase137-ui-authority/1'


_ui_MAX_BYTES = 8388608


_ui_MAX_ROWS = 65536


_ui_MAX_RECORD = 16384


_ui_ITEM_ALL = ('respondToHover', 'respondToHoverEnd', '_process:dragged', '_process:rigid')


_ui_ITEM_KING = ('activateDragParticles', 'deactivateDragParticles', 'onAddedToGridStorage', 'deactivateParticles')


_ui_AUTO = ('activate', 'deactivate', 'startTimer', 'instantClear')


_ui_SITES = tuple(('Items/Item.gd::' + x for x in _ui_ITEM_ALL + _ui_ITEM_KING)) + tuple(('Utility/AutoHideParticles.gd::' + x for x in _ui_AUTO))


_ui_KING_SCRIPT = 'res://Items/Exclusive/KingGoobert.gd'


_ui_KING_SCENE = 'res://Items/Exclusive/KingGoobert.tscn'


_ui_AUTO_SCRIPT = 'res://Utility/AutoHideParticles.gd'


_rng_SCHEMA = 'phase148-util-rng-checkpoint/1'


_rng_PROFILE = '7-king-rng-initial-148-family63'


_rng_CASE = 'NATIVE-V7-008-KING-UI-GUARDED-127'


_rng_SITE = 'Core/Game.gd::prepareItems'


_rng_MAX_BYTES = 16384


_rng_MAX_INPUT_BYTES = 268435456


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()



def _ui_need(ok,message):
 if not ok:raise ValueError(message)



def _ui_exact(x,keys):_ui_need(type(x)is dict and set(x)==set(keys),'exact keys '+str(keys))



def _ui_ident(x):_ui_need(type(x)is str and re.fullmatch('[1-9][0-9]{0,18}',x)is not None,'native identity');return x



def _ui_integer(x):_ui_need(type(x)is int and 0<=x<(1<<53),'bounded integer');return x



def _ui_controls(x):
 _ui_exact(x,('root_id','disable_input','physics_object_picking','ordinary_physics','ordinary_idle','internal_physics','internal_idle'))
 _ui_ident(x['root_id'])
 for k in set(x)-{'root_id'}:_ui_need(type(x[k])is bool,'control bool')



def _ui_require_admission(result):_ui_need(result['status']=='COMPLETE_INPUT_EVIDENCE' and result['unsupported']==0,'unsupported UI authority');return result



def _rng_keys(value,wanted,label):
    if type(value)is not dict or set(value)!=set(wanted):raise ValueError('closed '+label)



def _rng_decimal(value,positive=False):
    if type(value)is not str or re.fullmatch('0|[1-9][0-9]{0,18}',value)is None:raise ValueError('canonical counter/identity')
    n=int(value)
    if not int(positive)<=n<(1<<63):raise ValueError('counter/identity range')
    return n



def _rng_int64(value):
    _rng_keys(value,('type','decimal','int64_be'),'int64')
    d=value['decimal'];h=value['int64_be']
    if value['type']!='int' or type(d)is not str or re.fullmatch('0|-?[1-9][0-9]{0,18}',d)is None:raise ValueError('signed int64 decimal')
    n=int(d)
    if not -(1<<63)<=n<(1<<63)or type(h)is not str or re.fullmatch('[0-9a-f]{16}',h)is None or h!=((n&((1<<64)-1)).to_bytes(8,'big').hex()):raise ValueError('exact int64 bits')
    return n



def _rng_real(bits):
    if type(bits)is not str or re.fullmatch('[0-9a-f]{16}',bits)is None:raise ValueError('real bits')
    n=struct.unpack('>d',bytes.fromhex(bits))[0]
    if not math.isfinite(n)or math.copysign(1,n)<0:raise ValueError('nonnegative source clock')
    return n



def validate_single_king_fixture(fixture):
    if type(fixture) is not dict or canonical_sha(fixture) != SINGLE_KING_FIXTURE_SHA256:
        raise ValueError('single King outside predeclared fixed A fixture')
    if any(type(s['character_class']) is not int or s['character_class'] != 0 for s in fixture['sides']):
        raise ValueError('single King class0 only before RNG')
    kings = [i['instance_id'] for s in fixture['sides'] for i in s['items'] if i['item_index'] == 262]
    if kings != ['P:6'] or any(type(i['item_index']) is not int or i['item_index'] not in SINGLE_KING_ITEMS for s in fixture['sides'] for i in s['items']):
        raise ValueError('single unsocketed P King/six item source domain')
    return True



def _single_king_keys(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError('unknown/missing single King ' + label + ' keys')



def _single_king_validate_ui(rows):
 _ui_need(type(rows)is list and 2<=len(rows)<=_ui_MAX_ROWS,'rows')
 bindings={};particles={};ready=set();rolemap={};unsupported=0;entries=0;last=(0,0);closed=False;opened=None;rolebound=False;stack=[];nonking_particles=set();item_ids=set();auto_ids=set()
 for seq,row in enumerate(rows):
  _ui_exact(row,('schema','sequence','kind','site','physics_frame','idle_frame','in_physics','payload'))
  _ui_need(row['schema']=='phase355-king-ui-authority/1' and type(row['sequence'])is int and row['sequence']==seq,'schema/sequence')
  p=_ui_integer(row['physics_frame']);i=_ui_integer(row['idle_frame']);_ui_need(p>=last[0] and i>=last[1],'counter reversal');last=(p,i)
  _ui_need(type(row['in_physics'])is bool and not closed,'closed/phase');kind=row['kind'];v=row['payload']
  if seq==0:
   _ui_need(kind=='open' and row['site']=='sink._ready','open first')
   _ui_exact(v,('case','sites','before','after','drop_mouse_setting','window','limits'))
   _ui_need(v['case']==SINGLE_KING_CASE and v['sites']==list(_ui_SITES) and v['window']=='before_selected_birth_to_final_preinternal','closed coverage/window')
   _ui_need(v['limits']==dict(bytes=_ui_MAX_BYTES,rows=_ui_MAX_ROWS,record=_ui_MAX_RECORD),'limits')
   _ui_controls(v['before']);_ui_controls(v['after']);_ui_need(type(v['drop_mouse_setting'])is bool,'setting bool')
   _ui_need(v['after']['disable_input']is True and v['after']['physics_object_picking']is False,'public controls')
   _ui_need(all(v['before'][k]==v['after'][k]for k in ('root_id','ordinary_physics','ordinary_idle','internal_physics','internal_idle')),'processing preserved')
   opened=v;continue
  _ui_need(kind!='open','duplicate open')
  if kind=='bind':
   _ui_need(row['site']=='scene_instance','bind site');_ui_exact(v,('item_id','activation_id','drag_id','script','scene','pooled','inside_tree','generation'))
   ids=[_ui_ident(v[k])for k in ('item_id','activation_id','drag_id')]
   _ui_need(len(set(ids))==3 and opened['after']['root_id']not in ids,'distinct bound identities')
   _ui_need(ids[0]not in auto_ids and not set(ids[1:])&item_ids,'bound native identity kind')
   _ui_need(v['script']==_ui_KING_SCRIPT and v['scene']==_ui_KING_SCENE and type(v['pooled'])is bool and v['inside_tree']is False,'exact detached scene')
   _ui_need(type(v['generation'])is int and 1<=v['generation']<=65536,'bounded binding generation')
   previous=bindings.get(ids[0])
   if previous is None:
    _ui_need(v['generation']==1 and len(bindings)<128 and not set(ids)&(set(bindings)|set(particles)|ready),'distinct first binding')
   else:
    _ui_need(v['pooled']is True and previous['pooled']is True and v['generation']==previous['generation']+1,'pooled generation increment')
    _ui_need(all(v[k]==previous[k]for k in ('item_id','activation_id','drag_id','script','scene','inside_tree')),'same pooled identities')
   item_ids.add(ids[0]);auto_ids.update(ids[1:]);bindings[ids[0]]=v;particles[ids[1]]=(ids[0],'activation');particles[ids[2]]=(ids[0],'drag')
  elif kind=='ready':
   _ui_need(row['site']=='Utility/AutoHideParticles.gd::_ready','ready site');_ui_exact(v,('receiver_id','ancestry','script','viewport_id'))
   rid=_ui_ident(v['receiver_id']);_ui_need(rid not in item_ids and rid!=opened['after']['root_id'],'AutoHide identity kind');auto_ids.add(rid);_ui_need(v['script']==_ui_AUTO_SCRIPT and rid not in ready,'ready source/duplicate');_ui_need(v['viewport_id']==opened['after']['root_id'],'actual guarded viewport');ready.add(rid)
   ancestry=v['ancestry'];_ui_need(type(ancestry)is list and 1<=len(ancestry)<=32,'ancestry cap');seen=set();has_king=False
   for a in ancestry:
    _ui_exact(a,('native_id','king_source'));aid=_ui_ident(a['native_id']);_ui_need(aid not in seen and type(a['king_source'])is bool,'ancestry identity');seen.add(aid);has_king=has_king or a['king_source']
   _ui_need(ancestry[-1]['native_id']==opened['after']['root_id'],'root-ended ancestry')
   if rid in particles:_ui_need(has_king and any(a['native_id']==particles[rid][0] and a['king_source']is True for a in ancestry),'actual King parent identity')
   elif not has_king:nonking_particles.add(rid)
  elif kind=='roles':
   _ui_need(row['site']=='configure' and not rolebound,'roles one-time');_ui_exact(v,('kings','selected_guards','using_controller'))
   _ui_need(v['using_controller']is False,'controller initial domain');_ui_need(type(v['kings'])is list and len(v['kings'])==1,'one selected King')
   for r in v['kings']:
    _ui_exact(r,('item_id','role'));oid=_ui_ident(r['item_id']);_ui_need(oid in bindings and re.fullmatch('[PO]:[0-9]+',r['role'])is not None,'bound selected role')
    _ui_need(bindings[oid]['pooled']is False and bindings[oid]['generation']==1,'selected fresh nonpooled King')
    _ui_need(bindings[oid]['activation_id']in ready and bindings[oid]['drag_id']in ready,'both ready before configure');rolemap[oid]=r['role']
   guards=v['selected_guards'];_ui_need(type(guards)is list and len(guards)==len(SINGLE_KING_ROLES),'single A actual selected guards')
   guard_ids=set();guard_roles=set();guard_map={}
   for g in guards:
    _ui_exact(g,('item_id','role','focus','hovered','dragged','mode','viewport_id'));oid=_ui_ident(g['item_id'])
    _ui_need(oid not in auto_ids and oid!=opened['after']['root_id'],'selected Item identity kind');item_ids.add(oid)
    _ui_need(oid not in guard_ids and g['role']not in guard_roles and re.fullmatch('[PO]:[0-9]+',g['role'])is not None,'unique selected guards')
    guard_ids.add(oid);guard_roles.add(g['role']);guard_map[oid]=g['role']
    _ui_need(all(g[k]is False for k in ('focus','hovered','dragged'))and type(g['mode'])is int and g['mode']==1 and g['viewport_id']==opened['after']['root_id'],'fresh static unhovered selected input')
   _ui_need(all(guard_map.get(oid)==role for oid,role in rolemap.items()) and guard_roles==SINGLE_KING_ROLES,'fixed selected role guards');rolebound=True
  elif kind=='entry':
   _ui_need(row['site']in _ui_SITES,'unknown site');_ui_exact(v,('token','receiver_id','king_source','arguments','classification','source_phase'))
   rid=_ui_ident(v['receiver_id']);_ui_need(type(v['source_phase'])is str and 0<len(v['source_phase'])<=256,'source phase')
   _ui_need(type(v['king_source'])is bool and (rid not in bindings or v['king_source']is True),'receiver source identity')
   if row['site'].startswith('Utility/'):
    _ui_need(rid not in item_ids and rid!=opened['after']['root_id'],'AutoHide entry identity kind');auto_ids.add(rid)
   else:
    _ui_need(rid not in auto_ids and rid!=opened['after']['root_id'],'Item entry identity kind');item_ids.add(rid)
   args=v['arguments'];method=row['site'].split('::')[1]
   if method.startswith('_process:'):
    _ui_exact(args,('delta_bits',));_ui_need(type(args['delta_bits'])is str and re.fullmatch('[0-9a-f]{16}',args['delta_bits'])is not None,'typed delta bits');delta=struct.unpack('>d',bytes.fromhex(args['delta_bits']))[0];_ui_need(math.isfinite(delta)and delta>0,'direct positive finite delta')
   else:_ui_need(args=={},'no-argument source entry')
   classification='unsupported_item'
   if row['site'].startswith('Utility/'):
    classification='unsupported_unbound'
    if rid in nonking_particles:classification='supported_nonking_auto'
    elif rid in particles:
     if bindings[particles[rid][0]]['pooled']:classification='unsupported_nonselected_pooled_auto'
     elif rid in ready:classification='supported_activation' if particles[rid][1]=='activation' else 'unsupported_drag'
   elif method in _ui_ITEM_KING:
    # Non-King direct calls are retained conservatively too; no prebinding skip.
    classification=('unsupported_king_item' if rid in bindings else 'unsupported_unbound_item') if v['king_source'] else 'supported_nonking_item'
   _ui_need(v['classification']==classification,'classification must derive from earlier input bindings')
   _ui_need(type(v['token'])is int and v['token']==seq,'entry token');stack.append((seq,row['site'],rid))
   entries+=1
   if not classification.startswith('supported_'):unsupported+=1
  elif kind=='exit':
   _ui_exact(v,('token','receiver_id'));_ui_need(type(v['token'])is int and stack and stack[-1]==(v['token'],row['site'],v['receiver_id']),'matching source exit');stack.pop()
  elif kind=='close':
   _ui_need(seq==len(rows)-1 and row['site']=='finish_capture' and row['in_physics']is False and rolebound and not stack,'fixed final close')
   _ui_exact(v,('phase','completed','failed','overflow','dropped','entries','unsupported','rows_before_close','sites','controls','king_clock_closed','active_buff_calls'))
   _ui_need(v['phase']=='idle_pre_internal_flush' and v['completed']is True and v['failed']is False and v['overflow']is False and v['dropped']==0,'complete window')
   _ui_need(type(v['dropped'])is int and v['entries']==entries and v['unsupported']==unsupported and v['rows_before_close']==seq,'exact counts')
   _ui_need(all(type(v[k])is int for k in ('entries','unsupported','rows_before_close')),'typed counts')
   _ui_controls(v['controls'])
   _ui_need(all(v['controls'][k]==opened['after'][k]for k in ('root_id','disable_input','physics_object_picking','ordinary_physics','ordinary_idle','internal_idle')) and (opened['after']['internal_physics']is False or v['controls']['internal_physics']is True),'source-ready end controls')
   _ui_need(v['sites']==list(_ui_SITES) and v['king_clock_closed']is True and type(v['active_buff_calls'])is int and v['active_buff_calls']==0,'coverage/controls/closed source barrier')
   closed=True
  else:raise ValueError('unknown kind')
 _ui_need(closed and len(rolemap)==1,'complete selected binding')
 return dict(status='COMPLETE_INPUT_EVIDENCE',admission='NOT_ADMITTED_UNSUPPORTED_ENTRIES' if unsupported else 'ELIGIBLE_EMPTY_UNSUPPORTED',unsupported=unsupported,entries=entries,rows=len(rows),king_roles=rolemap,model_acceptance=False)



def _single_king_rng_checkpoint(data,records):
    _rng_keys(data,('schema','case','source_cut','source_profile','snapshot_complete','observed_count','checkpoint_sequence','game_id','util','rng','stamp','current_seed','state'),'initial checkpoint')
    if data['schema']!='phase355-util-rng-checkpoint/1' or data['case']!=SINGLE_KING_CASE or data['source_cut']!=_rng_SITE+':enter.before_original_body' or data['source_profile']!=SINGLE_KING_OBSERVER_VERSION or data['snapshot_complete']is not True or type(data['observed_count'])is not int or data['observed_count']!=1:raise ValueError('initial checkpoint contract')
    seq=data['checkpoint_sequence']
    if type(seq)is not int or not 0<=seq<1000000:raise ValueError('checkpoint sequence')
    _rng_decimal(data['game_id'],True)
    u=data['util'];r=data['rng'];s=data['stamp']
    _rng_keys(u,('native_id','path','class','script'),'Util identity');_rng_keys(r,('native_id','class'),'RNG identity')
    _rng_decimal(u['native_id'],True);_rng_decimal(r['native_id'],True)
    if len({u['native_id'],r['native_id'],data['game_id']})!=3 or u['path']!='/root/Util' or u['class']!='Node2D' or u['script']!='res://Utility/Util.gd' or r['class']!='RandomNumberGenerator':raise ValueError('source identity')
    _rng_keys(s,('physics_frame','idle_frame','in_physics','util_frame_counter','util_time_bits','util_clock_time_bits'),'source stamp')
    for k in ('physics_frame','idle_frame','util_frame_counter'):_rng_decimal(s[k])
    if type(s['in_physics'])is not bool:raise ValueError('source physics flag')
    _rng_real(s['util_time_bits']);_rng_real(s['util_clock_time_bits']);_rng_int64(data['current_seed']);_rng_int64(data['state'])
    if type(records)is not list or any(type(x)is not dict or x.get('channel')!='input' for x in records):raise ValueError('input-only records')
    cps=[x for x in records if x.get('site')==_rng_SITE and x.get('edge')=='checkpoint'];enters=[x for x in records if x.get('site')==_rng_SITE and x.get('edge')=='enter']
    if len(cps)!=1 or len(enters)!=1:raise ValueError('unique preparation checkpoint/enter')
    cp,en=cps[0],enters[0]
    if cp['sequence']!=seq or en['sequence']!=seq+1 or type(cp['sequence'])is not int or type(en['sequence'])is not int:raise ValueError('source checkpoint association')
    for row in (cp,en):
        if row['schema']!='observer7-record/1' or row['subject']['type']!='native_ref' or row['subject']['native_id']!=data['game_id']:raise ValueError('Game join')
        stamp=row['stamp']
        if stamp['physics_frame']!=s['physics_frame']or stamp['idle_frame']!=s['idle_frame']or stamp['phase']!=_rng_SITE+':enter' or stamp['util_time']!={'type':'float','binary64_be':s['util_time_bits']}:raise ValueError('source stamp join')
    nodes=[x['node']for x in cp['payload']['nodes']if x['role']=='util']
    if len(nodes)!=1 or any(nodes[0].get(k)!=u[k]for k in ('native_id','path','class')):raise ValueError('Util node join')
    return dict(schema='phase355-util-rng-checkpoint/1',status='PASS_INITIAL_CONDITION_ONLY',checkpoint=data,consumption_closed=False,genuine_enabled=False)



def _single_king_typed(value,kind,bits=None):
    keys={'float':('type','binary64_be'),'bool':('type','value'),'dictionary':('type','entries'),'null':('type',)}
    _single_king_keys(value,keys[kind],'typed '+kind)
    if value['type']!=kind:raise ValueError('raw type '+kind)
    if kind=='float':_single_king_real(value['binary64_be'])
    if bits is not None and value.get('binary64_be')!=bits:raise ValueError('source promoted getter bits')
    if kind=='bool' and type(value['value'])is not bool:raise ValueError('raw boolean')
    return value



def _single_king_node(value):
    _single_king_keys(value,('native_id','role','path','name','class','positions','priority','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle'),'actual Node')
    if not isinstance(value['native_id'],str) or re.fullmatch('[1-9][0-9]*',value['native_id'])is None:raise ValueError('native identity')
    for field in ('inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
        if type(value[field])is not bool:raise ValueError('actual independent group flags')
    if type(value['priority'])is not int or not -(1<<31)<=value['priority']<(1<<31):raise ValueError('priority')
    if type(value['positions'])is not list or not 1<=len(value['positions'])<=32 or any(type(v)is not int or v< -1 for v in value['positions']):raise ValueError('positions')
    for field in ('name','class'):
        if type(value[field])is not str:raise ValueError('node text')
    for field in ('path','role'):
        if value[field]is not None and type(value[field])is not str:raise ValueError('nullable node text')
    if value['inside_tree'] and (not value['path'] or not value['path'].startswith('/root')):raise ValueError('actual tree path')
    return value



def _single_king_timer(value):
    _single_king_keys(value,('node','process_mode','wait_time','time_left','one_shot','autostart','paused','stopped'),'actual Timer')
    _single_king_node(value['node'])
    if value['node']['class']!='Timer' or type(value['process_mode'])is not int or value['process_mode']not in (0,1):raise ValueError('Timer mode/class')
    for field in ('one_shot','autostart','paused','stopped'):
        if type(value[field])is not bool:raise ValueError('Timer bool')
    _single_king_typed(value['wait_time'],'float');_single_king_typed(value['time_left'],'float')
    return value



def _single_king_particle(value):
    _single_king_keys(value,('node','visible','emitting','one_shot','lifetime','explosiveness','speed_scale','timer'),'actual AutoHide')
    _single_king_node(value['node']);_single_king_timer(value['timer'])
    for field in ('visible','emitting','one_shot'):
        if _single_king_typed(value[field],'bool')['value']:raise ValueError('fresh hidden continuous AutoHide required')
    for field,bits in [('lifetime','3fe6666660000000'),('explosiveness','0000000000000000'),('speed_scale','3ff0000000000000')]:_single_king_typed(value[field],'float',bits)
    return value



def validate_single_king_fresh_facts(facts):
    _single_king_keys(facts,('schema','root_viewport','timers','kings','delayed_activation'),'King input facts')
    if facts['schema']!='phase355-king-input-facts/1':raise ValueError('facts schema')
    root=_single_king_node(facts['root_viewport'])
    if root['path']!='/root' or not root['inside_tree']:raise ValueError('root identity')
    # Each root flag is retained independently. No assumed idle/physics equality.
    kings=facts['kings']
    if type(kings)is not list or len(kings)!=1:raise ValueError('one fixed King')
    king=kings[0]
    _single_king_keys(king,('instance','node','sockets','gem_count','persistent','paramMult','paramAdd','doubleActivationChance','doubleAttackEffectChance','activation','drag'),'King facts')
    if king['instance']!='P:6' or _single_king_node(king['node'])['role']!='P:6':raise ValueError('fixed King identity')
    if type(king['gem_count'])is not int or king['gem_count']!=0 or king['persistent']is not False:raise ValueError('unsocketed/nonpersistent domain')
    if type(king['sockets'])is not list or len(king['sockets'])!=2:raise ValueError('exactly two empty sockets')
    ids=set()
    for socket in king['sockets']:
        _single_king_keys(socket,('node','gem'),'socket');n=_single_king_node(socket['node']);_single_king_typed(socket['gem'],'null')
        if n['native_id']in ids or not n['path'].startswith(king['node']['path']+'/Icon/Sockets/'):raise ValueError('distinct owned sockets')
        ids.add(n['native_id'])
    for field in ('paramMult','paramAdd'):
        if _single_king_typed(king[field],'dictionary')['entries']!=[]:raise ValueError('no modifiers')
    for field in ('doubleActivationChance','doubleAttackEffectChance'):_single_king_typed(king[field],'float','0000000000000000')
    for field in ('activation','drag'):_single_king_particle(king[field])
    expected={'invu:P':(0,'Character.scene.ready'),'invu:O':(0,'Character.scene.ready'),'king_buff:P:6':(0,'King.scene.instance'),'king_hide:P:6':(1,'AutoHide.Timer.new'),'king_drag:P:6':(1,'AutoHide.Timer.new')}
    _single_king_keys(facts['timers'],expected,'five selected Timer facts');timer_ids=set()
    for role,(mode,kind)in expected.items():
        fact=facts['timers'][role];_single_king_keys(fact,('lineage','current','private_provenance'),'fresh Timer fact')
        lineage=fact['lineage'];_single_king_keys(lineage,('timer_id','owner_id','kind','starts','stops','birth'),'birth lineage')
        birth=_single_king_timer(lineage['birth']);current=_single_king_timer(fact['current']);n=current['node']
        if lineage['kind']!=kind or type(lineage['starts'])is not int or lineage['starts']!=0 or type(lineage['stops'])is not int or lineage['stops']<0:raise ValueError('source no-start lineage')
        if lineage['timer_id']!=n['native_id'] or birth['node']['native_id']!=n['native_id'] or n['native_id']in timer_ids or n['role']!=role:raise ValueError('stable distinct Timer identity')
        timer_ids.add(n['native_id'])
        if type(lineage['owner_id'])is not str or re.fullmatch('[1-9][0-9]*',lineage['owner_id'])is None:raise ValueError('source owner')
        if fact['private_provenance']!='source_constructor_minus_one_no_start_not_public_zero_inference':raise ValueError('no invented private observation')
        for t in (birth,current):
            if t['process_mode']!=mode or t['autostart'] or t['paused'] or not t['stopped']:raise ValueError('fresh source Timer')
            _single_king_typed(t['wait_time'],'float','3ff0000000000000');_single_king_typed(t['time_left'],'float','0000000000000000')
            if any(t['node'][flag]for flag in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')):raise ValueError('fresh inactive Timer flags')
        if not current['one_shot'] or not n['inside_tree']:raise ValueError('configured in-tree Timer')
        if birth['one_shot']!=(kind!='AutoHide.Timer.new'):raise ValueError('actual birth flags, not configured defaults')
        if role.startswith('king_'):
            owner=king['node'] if role=='king_buff:P:6' else king['activation' if role=='king_hide:P:6' else 'drag']['node']
            if lineage['owner_id']!=owner['native_id'] or not n['path'].startswith(owner['path']+'/'):raise ValueError('Timer owner path')
            if role!='king_buff:P:6' and king['activation' if role=='king_hide:P:6' else 'drag']['timer']!=current:raise ValueError('particle Timer identity')
    delayed=facts['delayed_activation'];_single_king_keys(delayed,('target_id','method','delay','tree_timer_id','source','physics_frame','idle_frame'),'actual activation schedule')
    if delayed['method']!='activateItems' or delayed['source']!='Utility/Util.gd::callDelayed':raise ValueError('actual activation lineage')
    _single_king_typed(delayed['delay'],'float','4004000000000000');_single_king_counter(delayed['physics_frame']);_single_king_counter(delayed['idle_frame'])
    return facts



def validate_single_king_ui_authority(rows):
    return _ui_require_admission(_single_king_validate_ui(rows))



def _single_king_counter(value):
    if type(value) is not int or not 0 <= value <= ((1 << 63) - 1):
        raise ValueError('nonnegative bounded integer counter required')
    return value



def _single_king_real(bits):
    if type(bits) is not str or re.fullmatch('[0-9a-f]{16}', bits) is None:
        raise ValueError('BE64 lowercase hex required')
    value = struct.unpack('>d', bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError('finite BE64 required')
    return value



def validate_single_king_source_defaults(pre, act):
    """Proof-only observed fields. Never return these as model resource/charge state."""
    for record, charges in ((pre, 0), (act, 3)):
        rows = record['payload']['items']
        if type(rows) is not list:
            raise ValueError('single King source item rows required')
        matches = [row for row in rows if row.get('instance') == 'P:6']
        if len(matches) != 1:
            raise ValueError('one selected King source item state')
        fields = matches[0]['fields']
        for key, expected in (('descriptorIndex', 262), ('activations', 0), ('invuCharges', charges)):
            if fields.get(key) != dict(type='int', decimal=str(expected)):
                raise ValueError('single King source INT ' + key)
        for key, expected in (('activationsToTrigger', 6.0), ('protectedBuffs', 3.0), ('manaCost', 4.0)):
            if fields.get(key) != dict(type='float', binary64_be=struct.pack('>d', expected).hex()):
                raise ValueError('single King source REAL ' + key)
    for record, cooldown in ((pre, 0.0), (act, 5.0)):
        matches = [row for row in record['payload']['items'] if row.get('instance') == 'P:7']
        if len(matches) != 1:
            raise ValueError('one selected Basic source item state')
        fields = matches[0]['fields']
        for key, expected in (('descriptorIndex', 23), ('activations', 0)):
            if fields.get(key) != dict(type='int', decimal=str(expected)):
                raise ValueError('Basic source INT ' + key)
        for key, expected in (('activationsToTrigger', 5.0), ('iterationCooldown', cooldown), ('triggerTime', cooldown)):
            if fields.get(key) != dict(type='float', binary64_be=struct.pack('>d', expected).hex()):
                raise ValueError('Basic source REAL ' + key)
    return dict(kind='SOURCE_DEFAULTS_PROOF_ONLY_NOT_RUNTIME', phases=['pre_prepare', 'pre_activate'])



def validate_single_king_input_provenance(ui_rows, rng_checkpoint, input_records, lineage_records, facts, clock):
    """Validate lawful source joins; no bundle, no RNG restoration, no terminal command."""
    ui = validate_single_king_ui_authority(ui_rows)
    rng = _single_king_rng_checkpoint(rng_checkpoint, input_records)
    validate_single_king_fresh_facts(facts)
    def checkpoint(site):
        rows = [r for r in input_records if r.get('site') == site and r.get('edge') == 'checkpoint']
        if len(rows) != 1:
            raise ValueError('unique single King source checkpoint ' + site)
        return rows[0]
    pre = checkpoint('Core/Game.gd::prepareItems')
    act = checkpoint('Core/Game.gd::activateItems')
    if not pre['sequence'] < act['sequence']:
        raise ValueError('single King preparation before activation')
    defaults = validate_single_king_source_defaults(pre, act)
    byrole = {}
    for row in act['payload']['nodes']:
        if row['role'] in byrole:
            raise ValueError('duplicate raw activation envelope role')
        byrole[row['role']] = row
    selected = {}
    for role in SINGLE_KING_ROLES:
        raw = byrole['item:' + role]['node']
        if raw['role'] != role:
            raise ValueError('raw item node role differs from envelope item prefix')
        native = raw['native_id']
        if native in selected:
            raise ValueError('selected native item ID aliases')
        selected[native] = role
    root = byrole['root_viewport']['node']
    controls = ui_rows[0]['payload']['after']
    if facts['root_viewport'] != root or controls['root_id'] != root['native_id']:
        raise ValueError('single King fresh/UI/root source join')
    for flag in ('ordinary_physics', 'ordinary_idle', 'internal_physics', 'internal_idle'):
        if controls[flag] != root[flag]:
            raise ValueError('single King actual root processing join')
    guards = next(r['payload']['selected_guards'] for r in ui_rows if r['kind'] == 'roles')
    if {g['item_id']: g['role'] for g in guards} != selected:
        raise ValueError('complete selected UI/actual item join')
    king = facts['kings'][0]
    kid = king['node']['native_id']
    if king['node'] != byrole['item:P:6']['node'] or ui['king_roles'] != {kid: 'P:6'}:
        raise ValueError('single fresh King actual item join')
    binds = [r['payload'] for r in ui_rows if r['kind'] == 'bind' and r['payload']['item_id'] == kid]
    if len(binds) != 1 or any(binds[0][part + '_id'] != king[part]['node']['native_id'] for part in ('activation', 'drag')):
        raise ValueError('single King source particle join')
    for native, role in selected.items():
        scenes = [r for r in lineage_records if r.get('edge') == 'scene_instance' and r['payload']['item_id'] == native]
        ready = [r for r in lineage_records if r.get('site') == 'Items/Item.gd::_ready' and r.get('edge') == 'enter' and r['subject']['native_id'] == native]
        if len(scenes) != 1 or len(ready) != 1:
            raise ValueError('one selected scene and generic ready owner ' + role)
        scene, event = scenes[0], ready[0]
        if (scene['payload']['pooled'] is not False or event['payload']['state'] != {'native_id': native}
                or not scene['sequence'] < event['sequence'] < pre['sequence']):
            raise ValueError('fresh scene/ready/pre source owner chain ' + role)
    for role, fact in facts['timers'].items():
        if fact['current'] != byrole[role]['timer']:
            raise ValueError('single King fresh/activation direct Timer join ' + role)
        if role.startswith('invu:') and fact['lineage']['owner_id'] != byrole['character:' + role[-1]]['node']['native_id']:
            raise ValueError('single King invulnerability Timer owner join')
    if (rng_checkpoint['util']['native_id'] != byrole['util']['node']['native_id']
            or rng_checkpoint['game_id'] != byrole['game']['node']['native_id']):
        raise ValueError('single King prepare/activate identity continuity')
    if facts['delayed_activation']['target_id'] != rng_checkpoint['game_id']:
        raise ValueError('single King actual delayed activation target')
    first, last = ui_rows[0], ui_rows[-1]
    for key, initial in (('physics_frame', clock.physics_frame), ('idle_frame', clock.idle_frame)):
        if not first[key] <= int(rng_checkpoint['stamp'][key]) <= initial <= last[key]:
            raise ValueError('single King source preparation/clock UI window')
    if (not clock.passes or clock.passes[-1].kind != 'idle'
            or (last['physics_frame'], last['idle_frame']) != (clock.passes[-1].physics_frame, clock.passes[-1].idle_frame)):
        raise ValueError('single King complete source UI/finite clock close')
    return dict(schema='phase355-input-source-provenance/1', source_defaults=defaults,
                ready='READY_OWNER_ONLY_NOT_TIMER', private_origin='SOURCE_CONSTRUCTOR_NO_START_NOT_PUBLIC_ZERO',
                initial_rng=rng, ui_authority=ui, dataflow='PROOF_ONLY_STRIP_BEFORE_MODEL_RUNTIME',
                shared_consumption_closed=False, genuine_capture_accepted=False)



SCHEMA='phase105-exogenous-frame-clock/1'
MAX_PASSES=200000
MAX_JSON_BYTES=67108864
MAX_COUNTER=(1<<63)-1
PHYSICS_DELTA=struct.unpack('<f',struct.pack('<f',1/60))[0]


def f32(value):
    return struct.unpack('<f',struct.pack('<f',value))[0]


def _keys(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError('closed ' + label + ' keys required')



def _counter(value):
    if type(value) is not int or not 0 <= value <= MAX_COUNTER:
        raise ValueError('nonnegative bounded integer counter required')
    return value



def _real(bits):
    if type(bits) is not str or re.fullmatch('[0-9a-f]{16}', bits) is None:
        raise ValueError('BE64 lowercase hex required')
    value = struct.unpack('>d', bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError('finite BE64 required')
    return value



def _nonnegative_real(bits):
    value = _real(bits)
    if value < 0 or (value == 0 and math.copysign(1.0, value) < 0):
        raise ValueError('nonnegative clock with positive zero required')
    return value



@dataclass(frozen=True)
class FramePass:
    kind: str
    delta: float
    physics_frame: int
    idle_frame: int



@dataclass(frozen=True)
class ClockSchedule:
    physics_frame: int
    idle_frame: int
    util_frame_counter: int
    util_time: float
    util_clock_time: float
    passes: tuple



def decode_clock(carrier):
    """Validate every record before exposing immutable scalar inputs."""
    if type(carrier) is str:
        if len(carrier.encode('utf-8')) > MAX_JSON_BYTES:
            raise ValueError('clock JSON exceeds cap')
        def pairs(rows):
            result = {}
            for key, value in rows:
                if key in result:
                    raise ValueError('duplicate JSON clock key')
                result[key] = value
            return result
        def invalid(value):
            raise ValueError('nonfinite JSON number: ' + value)
        carrier = json.loads(carrier, object_pairs_hook=pairs, parse_constant=invalid)
    _keys(carrier, ('schema', 'lineage', 'environment', 'checkpoint', 'passes'), 'clock')
    if carrier['schema'] != SCHEMA or carrier['lineage'] != 'fresh_activate_idle_tail':
        raise ValueError('unsupported clock schema/lineage')
    env = carrier['environment']
    _keys(env, ('physics_fps', 'scale_bits', 'paused'), 'environment')
    if type(env['physics_fps']) is not int or env['physics_fps'] != 60:
        raise ValueError('fixed60 physics required')
    if env['scale_bits'] != '3ff0000000000000' or env['paused'] is not False:
        raise ValueError('only exact scale1/unpaused admitted')
    checkpoint = carrier['checkpoint']
    _keys(checkpoint, ('phase', 'physics_frame', 'idle_frame', 'util_frame_counter',
                       'util_time_bits', 'util_clock_time_bits'), 'checkpoint')
    if checkpoint['phase'] != 'activate_items_idle_tail':
        raise ValueError('only source activateItems idle-tail checkpoint admitted')
    physics = _counter(checkpoint['physics_frame'])
    idle = _counter(checkpoint['idle_frame'])
    util_frames = _counter(checkpoint['util_frame_counter'])
    util_time = _nonnegative_real(checkpoint['util_time_bits'])
    clock_time = _nonnegative_real(checkpoint['util_clock_time_bits'])
    rows = carrier['passes']
    if type(rows) is not list or not 1 <= len(rows) <= MAX_PASSES:
        raise ValueError('bounded nonempty pass list required')
    next_physics, next_idle = physics, idle + 1
    decoded = []
    for row in rows:
        _keys(row, ('kind', 'delta_bits', 'physics_frame', 'idle_frame'), 'frame pass')
        kind = row['kind']
        if type(kind) is not str or kind not in ('physics', 'idle'):
            raise ValueError('only physics/idle frame pass kinds')
        delta = _real(row['delta_bits'])
        if delta <= 0 or f32(delta) != delta:
            raise ValueError('positive source-promoted float32 delta required')
        if kind == 'physics':
            if delta != PHYSICS_DELTA:
                raise ValueError('non-source fixed60 physics delta')
            next_physics += 1
        p = _counter(row['physics_frame'])
        i = _counter(row['idle_frame'])
        if p != next_physics or i != next_idle:
            raise ValueError('missing/duplicate/reordered source frame counters')
        decoded.append(FramePass(kind, delta, p, i))
        if kind == 'idle':
            next_idle += 1
    return ClockSchedule(physics, idle, util_frames, util_time, clock_time, tuple(decoded))



INPUT_FILES = ('fixture.json', 'player_fixture.json', 'observer7-input.jsonl', 'observer7-lineage.jsonl', 'observer7-metadata.jsonl', 'observer7-primitives.jsonl', 'king-clock-checkpoint.json', 'king-clock-passes.jsonl', 'king-input-facts.json', 'king-ui-authority.jsonl', 'king-rng-checkpoint.json')


CHANNEL_FILES = {'observer7-input.jsonl': 'input', 'observer7-lineage.jsonl': 'lineage', 'observer7-metadata.jsonl': 'metadata', 'observer7-primitives.jsonl': 'primitive'}


TOTAL_BYTES = 268435456


FILE_CAPS = dict.fromkeys(INPUT_FILES, TOTAL_BYTES)


FILE_CAPS.update({'king-clock-checkpoint.json': 2097152, 'king-clock-passes.jsonl': 67108864, 'king-input-facts.json': 2097152, 'king-ui-authority.jsonl': 8388608, 'king-rng-checkpoint.json': 16384})


LINE_CAPS = dict.fromkeys(CHANNEL_FILES, 2097152)


LINE_CAPS.update({'king-clock-passes.jsonl': 1024, 'king-ui-authority.jsonl': 16384})


ROW_CAPS = dict.fromkeys(CHANNEL_FILES, 1000000)


ROW_CAPS.update({'king-clock-passes.jsonl': 200000, 'king-ui-authority.jsonl': 65536})


def strict_json(raw):
    return strict_json_loads(raw.decode('utf-8'))


FIXED_FIXTURE = {'below_master': False, 'game_version': '1.1.8', 'mode': 'Unranked', 'round': 1, 'rules': 'default', 'schema': 1, 'sides': [{'character_class': 0, 'hp': 240.0, 'items': [{'f': 0, 'instance_id': 'P:0', 'item_index': 11, 'x': 0, 'y': 0}, {'f': 0, 'instance_id': 'P:1', 'item_index': 11, 'x': 2, 'y': 0}, {'f': 0, 'instance_id': 'P:2', 'item_index': 11, 'x': 4, 'y': 0}, {'f': 0, 'instance_id': 'P:3', 'item_index': 11, 'x': 0, 'y': 2}, {'f': 0, 'instance_id': 'P:4', 'item_index': 11, 'x': 2, 'y': 2}, {'f': 0, 'instance_id': 'P:5', 'item_index': 11, 'x': 4, 'y': 2}, {'f': 0, 'instance_id': 'P:6', 'item_index': 262, 'x': 2, 'y': 0}, {'f': 0, 'instance_id': 'P:7', 'item_index': 23, 'x': 4, 'y': 0}, {'f': 0, 'instance_id': 'P:8', 'item_index': 22, 'x': 1, 'y': 0}, {'f': 0, 'instance_id': 'P:9', 'item_index': 22, 'x': 1, 'y': 1}, {'f': 0, 'instance_id': 'P:10', 'item_index': 22, 'x': 1, 'y': 2}, {'f': 0, 'instance_id': 'P:11', 'item_index': 22, 'x': 4, 'y': 2}, {'f': 0, 'instance_id': 'P:12', 'item_index': 1, 'x': 0, 'y': 0}, {'f': 0, 'instance_id': 'P:13', 'item_index': 1, 'x': 0, 'y': 2}], 'side': 'P', 'stamina': 5.0}, {'character_class': 0, 'hp': 260.0, 'items': [{'f': 0, 'instance_id': 'O:0', 'item_index': 11, 'x': 0, 'y': 0}, {'f': 0, 'instance_id': 'O:1', 'item_index': 11, 'x': 2, 'y': 0}, {'f': 0, 'instance_id': 'O:2', 'item_index': 11, 'x': 4, 'y': 0}, {'f': 0, 'instance_id': 'O:3', 'item_index': 11, 'x': 0, 'y': 2}, {'f': 0, 'instance_id': 'O:4', 'item_index': 11, 'x': 2, 'y': 2}, {'f': 0, 'instance_id': 'O:5', 'item_index': 11, 'x': 4, 'y': 2}, {'f': 0, 'instance_id': 'O:6', 'item_index': 1, 'x': 1, 'y': 0}, {'f': 0, 'instance_id': 'O:7', 'item_index': 1, 'x': 3, 'y': 0}, {'f': 0, 'instance_id': 'O:8', 'item_index': 4, 'x': 0, 'y': 2}, {'f': 0, 'instance_id': 'O:9', 'item_index': 19, 'x': 4, 'y': 0}, {'f': 0, 'instance_id': 'O:10', 'item_index': 22, 'x': 2, 'y': 2}, {'f': 0, 'instance_id': 'O:11', 'item_index': 22, 'x': 3, 'y': 2}], 'side': 'O', 'stamina': 5.0}]}


# SOURCE template appended by phase357_prepare_schema_source.py; no imports/calls.

FIXED_ROLES = SINGLE_KING_ROLES
ITEM_INDEX_BY_ROLE = {'P:0': 11, 'P:1': 11, 'P:2': 11, 'P:3': 11, 'P:4': 11, 'P:5': 11, 'P:6': 262, 'P:7': 23, 'P:8': 22, 'P:9': 22, 'P:10': 22, 'P:11': 22, 'P:12': 1, 'P:13': 1, 'O:0': 11, 'O:1': 11, 'O:2': 11, 'O:3': 11, 'O:4': 11, 'O:5': 11, 'O:6': 1, 'O:7': 1, 'O:8': 4, 'O:9': 19, 'O:10': 22, 'O:11': 22}
TIMER_ROLES = frozenset(['tick:P','tick:O','fatigue:start','fatigue:tick','invu:P','invu:O','king_buff:P:6','king_hide:P:6','king_drag:P:6'] + ['buff:'+side+':'+str(category) for side in ('P','O') for category in range(100,111)] + ['aux:'+side+':'+name for side in ('P','O') for name in ('battleRageTimer','autoRageTimer')])
KNOWN_REF_ROLES = FIXED_ROLES | TIMER_ROLES | {
    'P', 'O', 'root_viewport', 'game', 'util', 'combat_timer', 'combat_log', 'event_bus',
}

_base_validate_typed = validate_typed


def validate_typed(value, depth=0):
    _base_validate_typed(value, depth)
    if value['type'] == 'native_ref' and value['role'] is not None and value['role'] not in KNOWN_REF_ROLES:
        raise ValueError('unknown fixed A native reference role')
    return value


def validate_cache(value, current=False):
    validate_typed(value)
    if value['type'] != 'dictionary':
        raise ValueError('typed cache dictionary')
    if not value['entries'] and not current:
        return value  # genuine pre-prepare cache is not yet the four prepared arrays
    colors = set()
    for entry in value['entries']:
        key, content = entry['key'], entry['value']
        if key['type'] != 'int':
            raise ValueError('cache color must be actual INT, never BOOL/REAL alias')
        color = decimal(key['decimal'])
        if color not in (0, 2, 4, 7) or color in colors:
            raise ValueError('cache exact distinct SOURCE color')
        colors.add(color)
        if content['type'] != ('dictionary' if current else 'array'):
            raise ValueError('current ordered refs/bools versus prepared array cache')
        refs = content['entries'] if current else content['values']
        seen = set()
        for row in refs:
            ref = row['key'] if current else row
            if current and row['value'] != {'type': 'bool', 'value': True}:
                raise ValueError('current affected SOURCE BOOLtrue membership')
            if ref['type'] != 'native_ref' or ref['role'] not in FIXED_ROLES or ref['native_id'] in seen:
                raise ValueError('known unique ordered affected native refs')
            seen.add(ref['native_id'])
    if colors != {0, 2, 4, 7}:
        raise ValueError('missing SOURCE affected color')
    return value


def validate_state(value, kind, constructor=False):
    if kind not in CONTRACT['state_schemas']:
        raise ValueError('unknown K1 state schema')
    if kind in ('item', 'goobert', 'king', 'potion', 'plain_item'):
        if type(value) is not dict or 'descriptorIndex' not in value:
            raise ValueError('item descriptor raw identity required')
        validate_typed(value['descriptorIndex'])
        if value['descriptorIndex']['type'] != 'int':
            raise ValueError('item descriptor INT')
        index = decimal(value['descriptorIndex']['decimal'])
        if index not in DESCRIPTOR_IDS:
            raise ValueError('item descriptor outside fixed seven IDs')
        actual = 'king' if index == 262 else 'goobert' if index == 23 else 'potion' if index == 19 else 'plain_item'
        if kind == 'king' and actual != 'king' or kind == 'potion' and actual != 'potion' or kind == 'goobert' and actual not in ('king', 'goobert') or kind == 'plain_item' and actual != 'plain_item':
            raise ValueError('closed source Item subtype')
        kind = actual
    # Reuse the old field loop, bypass its ambiguous legacy item-shape dispatcher.
    fields = CONTRACT['state_schemas'][kind]
    exact(value, fields)
    for key, expected in fields.items():
        field = value[key]
        if expected == 'auto_hide':
            validate_state(field, 'auto_hide', constructor)
        elif expected in ('timer', 'timer|null', 'node'):
            if field is None and (expected.endswith('|null') or constructor):
                continue
            validate_state(field, 'node' if expected == 'node' else 'timer', constructor)
        elif expected == 'id':
            decimal(field, True)
        elif kind == 'node' and key in ('role', 'path'):
            if field is not None:
                text(field)
            if key == 'role' and field is not None and field not in KNOWN_REF_ROLES:
                raise ValueError('unknown actual node role')
        elif kind == 'node' and key in ('name', 'class'):
            text(field)
        elif expected == 'int_array':
            if type(field) is not list or len(field) > CAPS['depth']:
                raise ValueError('ancestor path cap/type')
            for position in field:
                integer(position, -1, (1 << 31) - 1)
        elif kind in ('node', 'timer') and expected in ('bool', 'int'):
            if expected == 'bool' and type(field) is not bool:
                raise ValueError('raw node/Timer BOOL')
            if expected == 'int':
                integer(field, 0 if kind == 'timer' else -(1 << 31), 1 if kind == 'timer' else (1 << 31) - 1)
        else:
            validate_typed(field)
            if expected == 'temporary_array':
                if field['type'] != 'array' or any(row['type'] != 'temporary' or row['ordinal'] != i for i, row in enumerate(field['values'])):
                    raise ValueError('ordered temporary ledger projection')
            elif field['type'] not in expected.split('|'):
                raise ValueError('exact raw property type ' + kind + '.' + key)
    for key in ('currentAffectedItems', 'cachedAffectedItems'):
        if key in value:
            validate_cache(value[key], key == 'currentAffectedItems')
    if kind == 'timer':
        if value['node']['class'] != 'Timer':
            raise ValueError('actual Timer class')
        if scalar_number(value['wait_time']) <= 0 or scalar_number(value['time_left']) < 0:
            raise ValueError('Timer public getter range')
    return value


def primitive_context(label, kind):
    if label.startswith('invulnerability_pitch:'):
        if label != 'invulnerability_pitch:P:6' or kind != 'randf_range':
            raise ValueError('fixed selected King pitch context')
        return dict.fromkeys(CONTRACT['primitive_context_exact']) | {'item': 'P:6'}
    result = _base_primitive_context(label, kind)
    if result['item'] not in (None, 'null') and result['item'] not in FIXED_ROLES:
        raise ValueError('primitive unknown selected item role')
    return result


def validate_primitive(payload):
    if payload.get('label') == 'invulnerability_pitch:P:6':
        if payload.get('args') != [{'type': 'float', 'binary64_be': '3feccccccccccccd'}, {'type': 'float', 'binary64_be': '3ff199999999999a'}]:
            raise ValueError('original randPitch0.1 exact REAL endpoints')
    return _base_validate_primitive(payload)


def argument_fields(value):
    validate_typed(value)
    if value['type'] != 'dictionary':
        raise ValueError('typed argument dictionary')
    result = {}
    for row in value['entries']:
        if row['key']['type'] != 'string' or row['key']['value'] in result:
            raise ValueError('unique actual argument names')
        result[row['key']['value']] = row['value']
    return result


def validate_resources(rows, nodes):
    if type(rows) is not list or len(rows) != 2:
        raise ValueError('two source resource panels')
    for row, side in zip(rows, ('P', 'O')):
        exact(row, ('side', 'native_id', 'buffProtectStacks', 'debuffReflectStacks', 'buffs'))
        owners = [n['node'] for n in nodes if n['role'] == 'character:' + side]
        if len(owners) != 1 or row['side'] != side or row['native_id'] != owners[0]['native_id']:
            raise ValueError('source resource actual Character owner')
        for name in ('buffProtectStacks', 'debuffReflectStacks'):
            validate_typed(row[name])
            if row[name]['type'] != 'int':
                raise ValueError('Character stored INT source property ' + name)
        if type(row['buffs']) is not list or len(row['buffs']) != 11:
            raise ValueError('complete eleven source buff ledgers')
        for ledger, category in zip(row['buffs'], range(100, 111)):
            exact(ledger, ('stack', 'state'))
            if ledger['stack'] != {'type': 'int', 'decimal': str(category)}:
                raise ValueError('source stack order/type')
            validate_state(ledger['state'], 'buff')
            state = ledger['state']
            if state['type'] != ledger['stack'] or state['character']['type'] != 'native_ref' or state['character']['native_id'] != row['native_id']:
                raise ValueError('source Buff owner/type join')
            current = decimal(state['current']['decimal'])
            permanent = decimal(state['permanentStacks']['decimal'])
            temporary = sum(decimal(entry['amount']['decimal']) for entry in state['temporaryStacks']['values'])
            if current != permanent + temporary:
                raise ValueError('checkpoint SOURCE current/permanent/temporary ledger invariant')
    return rows


def validate_record(row):
    # Full row validation is independent of physical-file sequence validation.
    if type(row) is dict and row.get('edge') == 'checkpoint':
        payload = row.get('payload')
        exact(payload, ('environment', 'nodes', 'items', 'source_resources'))
        shadow = deepcopy(row)
        del shadow['payload']['source_resources']
        _base_validate_record(shadow)
        validate_resources(payload['source_resources'], payload['nodes'])
        if payload['environment'] != {
            'fps': {'type': 'int', 'decimal': '60'},
            'scale': {'type': 'float', 'binary64_be': '3ff0000000000000'},
            'paused': {'type': 'bool', 'value': False},
        }:
            raise ValueError('fixed60 scale1 unpaused source environment')
    else:
        _base_validate_record(row)
    site, edge, payload = row['site'], row['edge'], row['payload']
    if site in MATRIX['sites'] and edge == 'enter':
        fields = argument_fields(payload['arguments'])
        spec = MATRIX['sites'][site]
        exact(fields, spec['arguments_exact'])
        for key, kind in spec['argument_types'].items():
            if fields[key]['type'] not in kind.split('|'):
                raise ValueError('actual GD entry declared type ' + site + ':' + key)
        expected = {
            'Items/Exclusive/KingGoobert.gd::onStateChanged': {'_crownState': ('int',)},
            'Core/Character.gd::makeInvulnerable': {'invuDur': ('float',), 'item': ('native_ref',), 'triggerEvent': ('null', 'event_ref')},
            'Core/Character.gd::changeBuffProtectStacks': {'amount': ('float',)},
            'Core/CombatLog.gd::createEvent_InvulnerableStart': {'item': ('native_ref',), 'duration': ('float',), 'playerId': ('int',), 'triggerEvent': ('null', 'event_ref')},
            'Core/CombatLog.gd::createEvent_InvulnerableEnd': {'item': ('native_ref',), 'playerId': ('int',), 'triggerEvent': ('null', 'event_ref')},
            'Core/Buff.gd::loseStacks': {'amount': ('int',), 'item': ('null', 'native_ref'), 'triggerEvent': ('null', 'event_ref'), 'used': ('bool',)},
        }.get(site, {})
        for key, kinds in expected.items():
            if fields[key]['type'] not in kinds:
                raise ValueError('specific SOURCE callsite Variant ' + site + ':' + key)
        if site == 'Items/Item.gd::useMana' and row['subject'].get('role') == 'P:6' and fields['amount'] != {'type': 'float', 'binary64_be': '4010000000000000'}:
            raise ValueError('King Item.useMana keeps REAL4 before Character INT coercion')
    if site in MATRIX['sites'] and edge in ('enter', 'return_explicit', 'return_implicit'):
        if row['subject']['type'] != 'native_ref':
            raise ValueError('method receiver actual native ref required')
        if edge == 'return_implicit' and payload['return_value'] != {'type': 'null'}:
            raise ValueError('original observer implicit return is NULL')
        state = payload['state']
        if site == 'Items/Food.gd::prepare' and state['descriptorIndex'] != {'type': 'int', 'decimal': '22'}:
            raise ValueError('Food.prepare receiver must be original thin-domain Food descriptor INT22')
        if MATRIX['sites'][site]['state_schema'] == 'character' and row['subject']['role'] is not None:
            side = row['subject']['role']
            if side not in ('P', 'O') or state['playerId'] != {'type': 'int', 'decimal': '0' if side == 'P' else '1'}:
                raise ValueError('actual Character receiver owner/playerId')
        if MATRIX['sites'][site]['state_schema'] == 'generic' and state['native_id'] != row['subject']['native_id']:
            raise ValueError('generic ready/receiver owner identity')
        if 'descriptorIndex' in state and row['subject']['role'] is not None:
            if row['subject']['role'] not in ITEM_INDEX_BY_ROLE or decimal(state['descriptorIndex']['decimal']) != ITEM_INDEX_BY_ROLE[row['subject']['role']]:
                raise ValueError('actual receiver role/source descriptor join')
    if edge in ('timer_before', 'timer_after'):
        if row['subject']['type'] != 'native_ref':
            raise ValueError('Timer API actual receiver')
        native = row['subject']['native_id']
        if payload['role'] not in TIMER_ROLES and payload['role'] != 'native:' + native:
            raise ValueError('unknown Timer API role/receiver')
        state = payload['public_before' if edge == 'timer_before' else 'public_after']
        if state is None or state['node']['native_id'] != native:
            raise ValueError('Timer API direct receiver state identity')
    if edge == 'scene_instance':
        if decimal(payload['item_index']['decimal']) not in DESCRIPTOR_IDS or payload['pooled'] is not False or payload['particle'] is not None:
            raise ValueError('K1 unpooled six-ID scene provenance; no53/168 Timer')
    if len((json.dumps(row, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n').encode()) > CAPS['record_bytes']:
        raise ValueError('complete record cap including source proof')
    return row


def _validate_call_pairs(records):
    stack = []
    pending = []
    for row in records:
        site, edge = row['site'], row['edge']
        subject = row['subject']
        native = subject.get('native_id')
        if site in MATRIX['sites'] and edge == 'enter':
            stack.append((site, native))
        elif site in MATRIX['sites'] and edge in ('return_implicit', 'return_explicit'):
            if not stack or stack.pop() != (site, native):
                raise ValueError('source call return/order without matching enter')
        if edge == 'timer_before':
            pending.append((site, native, row['payload']['operation'], row['payload']['args']))
        elif edge == 'timer_after':
            if not pending or pending.pop() != (site, native, row['payload']['operation'], row['payload']['args']):
                raise ValueError('Timer API paired source order')
    if stack or pending:
        raise ValueError('source stream EOF inside method/API call')


# Source transport implementation is copied mechanically from the sealed355
# framing interface; the public decoder additionally invokes the actual schema.
def _transport_only_decode(raw_by_name):
    """Validate framing/order before filtering, grouping or typed delegation.

    The returned lists retain their original physical order and primitive DTOs.
    They are transport-checked data, not admitted runtime or an input bundle.
    """
    if type(raw_by_name) is not dict or set(raw_by_name) != set(INPUT_FILES):
        raise ValueError('exact eleven lawful source names; no expected files')
    if any(type(raw_by_name[n]) is not bytes or not 0 < len(raw_by_name[n]) <= FILE_CAPS[n]
           for n in INPUT_FILES):
        raise ValueError('nonempty bounded raw source bytes required')
    if sum(len(value) for value in raw_by_name.values()) > TOTAL_BYTES:
        raise ValueError('eleven-source total byte cap')
    decoded = {}
    seen = set()
    for name in INPUT_FILES:
        raw = raw_by_name[name]
        if not name.endswith('.jsonl'):
            decoded[name] = strict_json(raw)
            continue
        if not raw.endswith(b'\n'):
            raise ValueError('source JSONL final newline ' + name)
        lines = raw.splitlines(keepends=True)
        if not 1 <= len(lines) <= ROW_CAPS[name]:
            raise ValueError('source JSONL row cap ' + name)
        rows = []
        previous = -1
        for line in lines:
            if not line.strip() or len(line) > LINE_CAPS[name]:
                raise ValueError('source JSONL record cap ' + name)
            row = strict_json(line)
            if type(row) is not dict:
                raise ValueError('source JSONL object required ' + name)
            if name in CHANNEL_FILES:
                seq = row.get('sequence')
                if (row.get('schema') != 'observer7-record/1'
                        or row.get('channel') != CHANNEL_FILES[name]
                        or type(seq) is not int or not previous < seq < (1 << 63)
                        or seq in seen):
                    raise ValueError('physical source channel/order/global sequence ' + name)
                previous = seq
                seen.add(seq)
            rows.append(row)
        decoded[name] = rows
    for row in decoded['observer7-primitives.jsonl']:
        payload = row.get('payload')
        if type(payload) is not dict or payload.get('kind') not in ('randf', 'randf_range', 'randi_range'):
            raise ValueError('K1 Util primitive ABI only; no Mirror/global_u32')
    return decoded



def decode_sources(raw_by_name):
    decoded = _transport_only_decode(raw_by_name)
    for name in CHANNEL_FILES:
        for row in decoded[name]:
            validate_record(row)
    return decoded


def validate_source_carriers(raw_by_name):
    decoded = decode_sources(raw_by_name)
    fixture = deepcopy(FIXED_FIXTURE)
    validate_single_king_fixture(fixture)
    for side, name in (('P', 'player_fixture.json'), ('O', 'fixture.json')):
        raw = decoded[name]
        exact(raw, ('schema_version', 'game_version', 'class', 'health', 'stamina', 'items'))
        expected = fixture['sides'][0 if side == 'P' else 1]
        if type(raw['schema_version']) is not int or raw['schema_version'] != 1 or raw['game_version'] != '1.1.8' or type(raw['class']) is not int or raw['class'] != 0:
            raise ValueError('closed fixed A native fixture schema/class')
        if any(type(raw[key]) not in (int, float) or not math.isfinite(raw[key]) or raw[key] != expected[target] for key, target in (('health', 'hp'), ('stamina', 'stamina'))):
            raise ValueError('fixed A lawful resource initial values')
        expected_items = [{key: value for key, value in item.items() if key != 'instance_id'} for item in expected['items']]
        if canonical_sha(raw['items']) != canonical_sha(expected_items):
            raise ValueError('fixed inventory/geometry/order, no slot renumbering')
    header = decoded['king-clock-checkpoint.json']
    exact(header, ('schema', 'lineage', 'environment', 'checkpoint'))
    clock = decode_clock(dict(header, passes=decoded['king-clock-passes.jsonl']))
    proof = validate_single_king_input_provenance(
        decoded['king-ui-authority.jsonl'], decoded['king-rng-checkpoint.json'],
        decoded['observer7-input.jsonl'], decoded['observer7-lineage.jsonl'],
        decoded['king-input-facts.json'], clock,
    )
    combined = sorted((row for name in CHANNEL_FILES for row in decoded[name]), key=lambda row: row['sequence'])
    _validate_call_pairs(combined)  # only after all physical order/unique gates pass
    metadata = [row for row in decoded['observer7-metadata.jsonl'] if row['edge'] == 'loaded_descriptors']
    if len(metadata) != 1:
        raise ValueError('one complete metadata close observation')
    act = next(row for row in decoded['observer7-input.jsonl'] if row['site'] == 'Core/Game.gd::activateItems' and row['edge'] == 'checkpoint')
    if (decimal(act['stamp']['physics_frame']) != clock.physics_frame
            or decimal(act['stamp']['idle_frame']) != clock.idle_frame
            or act['stamp']['util_time'] != {'type': 'float', 'binary64_be': struct.pack('>d', clock.util_time).hex()}):
        raise ValueError('actual activation checkpoint/external clock source cut join')
    identities = {}
    roles = {}
    for record in act['payload']['nodes']:
        node = record['node']
        if node['native_id'] in identities or record['role'] in roles:
            raise ValueError('actual node identity aliases')
        identities[node['native_id']] = record['role']
        roles[record['role']] = node['native_id']
    return dict(schema='phase357-eleven-carrier-source-proof/1', proof=proof,
                source_identity=dict(native_to_role=identities, role_to_native=roles),
                clocks=dict(passes=len(clock.passes), checkpoint=deepcopy(header)),
                dataflow='PROOF_ONLY_NOT_MODEL_RUNTIME_OR_SEED', input_bundle_created=False,
                native_capture_accepted=False, model_calls=0)


def validate_observation_records(records, source_identity):
    """Expected-only API; never called by decode_sources, no output-to-input path."""
    if type(records) is not list or len(records) > CAPS['records']:
        raise ValueError('bounded observation records')
    exact(source_identity, ('native_to_role', 'role_to_native'))
    previous = -1
    for row in records:
        validate_record(row)
        if row['channel'] not in ('runtime', 'allocation', 'registration') or row['sequence'] <= previous:
            raise ValueError('ordered expected channels only')
        previous = row['sequence']
        if row['edge'] in ('timer_before', 'timer_after'):
            native = row['subject']['native_id']
            role = source_identity['native_to_role'].get(native)
            if role not in TIMER_ROLES or source_identity['role_to_native'].get(role) != native:
                raise ValueError('unknown/unproven observed Timer owner')
            if row['payload']['role'] not in (role, 'native:' + native):
                raise ValueError('observed Timer role disguised by caller')
    _validate_call_pairs(records)
    return dict(status='TYPED_EXPECTED_OBSERVATIONS_ONLY', records=len(records), no_input_projection=True)


"""New terminal helpers appended to the frozen typed schema; expected/control only."""

TERMINAL_POLICY = 'first-actual-idle-after-at-least-two-future-physics/1'
TERMINAL_ENDPOINT_SCHEMA = 'phase390-first-eligible-idle-endpoint/1'
TERMINAL_CONTROL_SCHEMA = 'phase390-terminal-cut-control/1'
TERMINAL_CUT_KEYS = ('schema', 'terminal_policy', 'cleanup_anchor_pass', 'first_eligible_idle_pass',
                     'minimum_future_physics_signals', 'observed_future_physics_signals')
TERMINAL_ENDPOINT_KEYS = ('schema', 'terminal_policy', 'phase', 'physics_frame', 'idle_frame', 'passes',
                         'minimum_future_physics_signals', 'observed_future_physics_signals',
                         'cleanup_anchor_pass', 'first_eligible_idle_pass', 'fx_exact_comparison')
TERMINAL_RECEIPT_KEYS = ('source_window_complete', 'failed', 'clock_closed', 'ui_closed', 'cleanup',
                        'clock_passes', 'native_capture_accepted', 'collector_archive_pending', 'terminal_cut')
TERMINAL_DISPATCH_KEYS = ('phase', 'dispatching', 'emit_count', 'receiver_available', 'receiver_id',
                        'physics', 'idle', 'ack', 'script_emit_return', 'script_emit_return_observed',
                        'native_emit_error_available', 'native_emit_error', 'finish_return', 'failed',
                        'closed', 'complete', 'clock_closed', 'ui_closed', 'first_error', 'ready_connect',
                        'diagnostic_error', 'terminal_cut')


def _terminal_clock_rows(clock):
    # The public helper also rejects a manually built, type-contaminated ClockSchedule.
    if type(clock) is not ClockSchedule or type(clock.passes) is not tuple or not 1 <= len(clock.passes) <= MAX_PASSES:
        raise ValueError('actual bounded decoded clock required')
    _counter(clock.util_frame_counter)
    for value in (clock.util_time, clock.util_clock_time):
        if type(value) is not float or not math.isfinite(value) or value < 0 or (value == 0 and math.copysign(1.0, value) < 0):
            raise ValueError('actual checkpoint clock scalar')
    p, i = _counter(clock.physics_frame), _counter(clock.idle_frame) + 1
    for row in clock.passes:
        if type(row) is not FramePass or type(row.kind) is not str or row.kind not in ('physics', 'idle'):
            raise ValueError('terminal actual frame row kind')
        if type(row.delta) is not float or not math.isfinite(row.delta) or row.delta <= 0 or f32(row.delta) != row.delta:
            raise ValueError('terminal actual frame delta')
        if row.kind == 'physics':
            if row.delta != PHYSICS_DELTA:
                raise ValueError('terminal actual fixed60 delta')
            p += 1
        if (_counter(row.physics_frame), _counter(row.idle_frame)) != (p, i):
            raise ValueError('terminal missing/duplicate/reordered actual clock')
        if row.kind == 'idle':
            i += 1
    return clock.passes


def validate_terminal_evidence(endpoint, clock, cleanup):
    """Expected/control proof only; never a model cleanup or stop command."""
    exact(endpoint, TERMINAL_ENDPOINT_KEYS)
    if (endpoint['schema'] != TERMINAL_ENDPOINT_SCHEMA or endpoint['terminal_policy'] != TERMINAL_POLICY
            or endpoint['phase'] != 'idle_pre_internal_flush'
            or endpoint['fx_exact_comparison'] != 'NOT_EVALUATED_REQUIRES_MODEL'):
        raise ValueError('new exact terminal policy/endpoint required')
    for key in ('physics_frame', 'idle_frame', 'passes', 'cleanup_anchor_pass', 'first_eligible_idle_pass',
                'minimum_future_physics_signals', 'observed_future_physics_signals'):
        _counter(endpoint[key])
    if endpoint['minimum_future_physics_signals'] != 2 or endpoint['observed_future_physics_signals'] < 2:
        raise ValueError('minimum2 and actual future count required')
    rows = _terminal_clock_rows(clock)
    exact(cleanup, ('physics_frame', 'idle_frame', 'is_in_physics_frame'))
    cp, ci = _counter(cleanup['physics_frame']), _counter(cleanup['idle_frame'])
    if type(cleanup['is_in_physics_frame']) is not bool:
        raise ValueError('actual cleanup phase BOOL')
    kind = 'physics' if cleanup['is_in_physics_frame'] else 'idle'
    anchors = [index + 1 for index, row in enumerate(rows)
               if (row.kind, row.physics_frame, row.idle_frame) == (kind, cp, ci)]
    if len(anchors) == 1:
        anchor = anchors[0]
    elif not anchors and kind == 'idle' and (cp, ci) == (clock.physics_frame, clock.idle_frame):
        anchor = 0
    else:
        raise ValueError('unique actual cleanup row/checkpoint association')
    count = 0
    candidate = None
    for index in range(anchor, len(rows)):
        row = rows[index]
        if row.kind == 'physics':
            if row.physics_frame <= cp:
                raise ValueError('only strictly future physics signals count')
            count += 1
        if row.physics_frame - cp != count:
            raise ValueError('cleanup/future clock continuity')
        if row.kind == 'idle' and count >= 2:
            candidate = index + 1
            break
    if candidate is None:
        raise ValueError('EOF before first actual eligible idle')
    if candidate != len(rows):
        raise ValueError('missed first eligible idle or trailing clock records')
    last = rows[-1]
    if (endpoint['physics_frame'], endpoint['idle_frame'], endpoint['passes'], endpoint['cleanup_anchor_pass'],
            endpoint['first_eligible_idle_pass'], endpoint['observed_future_physics_signals']) != (
            last.physics_frame, last.idle_frame, len(rows), anchor, candidate, count):
        raise ValueError('actual first-idle frames/ordinals/count mismatch')
    return dict(schema='phase391-expected-terminal-proof/1', status='EXPECTED_ONLY_FIRST_ACTUAL_ELIGIBLE_IDLE',
                terminal_policy=TERMINAL_POLICY, cleanup_anchor_pass=anchor, first_eligible_idle_pass=candidate,
                minimum_future_physics_signals=2, observed_future_physics_signals=count,
                physics_frame=last.physics_frame, idle_frame=last.idle_frame, passes=len(rows),
                cleanup=dict(cleanup), no_model_stop_command=True)


def _terminal_cut_matches(value, proof):
    exact(value, TERMINAL_CUT_KEYS)
    if value['schema'] != TERMINAL_CONTROL_SCHEMA or value['terminal_policy'] != TERMINAL_POLICY:
        raise ValueError('terminal receipt/control policy version')
    for key in TERMINAL_CUT_KEYS[2:]:
        if _counter(value[key]) != proof[key]:
            raise ValueError('terminal receipt/control count/ordinal mismatch')


def validate_terminal_receipt(endpoint, clock, receipt, control, validation):
    """Public expected/control join used directly by the actual new host."""
    exact(receipt, TERMINAL_RECEIPT_KEYS)
    for key in ('source_window_complete', 'clock_closed', 'ui_closed', 'collector_archive_pending'):
        if receipt[key] is not True:
            raise ValueError('complete actual source receipt required')
    if receipt['failed'] is not False or receipt['native_capture_accepted'] is not False:
        raise ValueError('receipt failure or self native acceptance')
    proof = validate_terminal_evidence(endpoint, clock, receipt['cleanup'])
    if _counter(receipt['clock_passes']) != proof['passes']:
        raise ValueError('receipt actual clock pass count')
    _terminal_cut_matches(receipt['terminal_cut'], proof)
    _terminal_dispatch_shape(control, 'FINALIZED')
    if control['phase'] != 'FINALIZED' or _counter(control['emit_count']) != 1:
        raise ValueError('actual once FINALIZED dispatch required')
    for key in ('receiver_available', 'script_emit_return_observed', 'finish_return', 'closed', 'complete', 'clock_closed', 'ui_closed'):
        if control[key] is not True:
            raise ValueError('actual terminal BOOL evidence required')
    for key in ('dispatching', 'native_emit_error_available', 'failed'):
        if control[key] is not False:
            raise ValueError('dispatch/native Error/failure evidence')
    for key in ('script_emit_return', 'native_emit_error', 'first_error', 'diagnostic_error'):
        if control[key] is not None:
            raise ValueError('actual NIL/unavailable/no-error evidence')
    native = control['receiver_id']
    if type(native) is not str or re.fullmatch('[1-9][0-9]*', native) is None or int(native) > MAX_COUNTER:
        raise ValueError('actual receiver decimal native identity')
    if (_counter(control['physics']), _counter(control['idle'])) != (proof['physics_frame'], proof['idle_frame']):
        raise ValueError('same actual terminal dispatch frames')
    exact(control['ready_connect'], ('physics', 'idle'))
    if any(type(control['ready_connect'][key]) is not int or control['ready_connect'][key] != 0 for key in ('physics', 'idle')):
        raise ValueError('actual SceneTree connection Error values')
    exact(control['ack'], ('receiver_id', 'physics', 'idle', 'serial'))
    ack = control['ack']
    if (ack['receiver_id'] != native or (_counter(ack['physics']), _counter(ack['idle']), _counter(ack['serial']))
            != (proof['physics_frame'], proof['idle_frame'], 1)):
        raise ValueError('exact actual acknowledgement identity')
    _terminal_cut_matches(control['terminal_cut'], proof)
    # Other collector business fields remain opaque here and are not promoted to input.
    if type(validation) is not dict or not {'cut', 'full_snapshot_reads', 'terminal_cut', 'native_checks_pass', 'end_barrier'} <= set(validation):
        raise ValueError('actual collector terminal control subset')
    exact(validation['cut'], ('physics', 'idle', 'preinternal'))
    cut = validation['cut']
    if ((_counter(cut['physics']), _counter(cut['idle'])) != (proof['physics_frame'], proof['idle_frame'])
            or cut['preinternal'] is not True or type(validation['full_snapshot_reads']) is not int
            or validation['full_snapshot_reads'] != 1 or validation['native_checks_pass'] is not True
            or validation['end_barrier'] is not True):
        raise ValueError('one same-frame preinternal readonly collector cut')
    _terminal_cut_matches(validation['terminal_cut'], proof)
    return proof


def validate_terminal_diagnostics(rows):
    """Validate control headers/milestones only; other payloads are opaque."""
    if type(rows) is not list or not 1 <= len(rows) <= 64:
        raise ValueError('bounded actual source-control rows')
    keys = ('schema', 'control_sequence', 'site', 'reason', 'physics', 'idle', 'in_physics',
            'observer_sequence', 'ui_sequence', 'clock_passes', 'payload')
    milestones = []
    for index, row in enumerate(rows):
        exact(row, keys)
        if row['schema'] != 'phase391-source-control/1' or _counter(row['control_sequence']) != index:
            raise ValueError('actual diagnostic version/physical sequence')
        for key in ('physics', 'idle', 'observer_sequence', 'ui_sequence', 'clock_passes'):
            _counter(row[key])
        if type(row['in_physics']) is not bool or type(row['site']) is not str or type(row['reason']) is not str:
            raise ValueError('diagnostic primitive control header')
        if row['site'] == 'emit_source_idle_cut_once' and row['reason'] in ('EMITTING', 'RETURNED_ACK_CHECKED', 'FINALIZED'):
            milestones.append(row)
    if [row['reason'] for row in milestones] != ['EMITTING', 'RETURNED_ACK_CHECKED', 'FINALIZED'] or milestones[-1] is not rows[-1]:
        raise ValueError('unique ordered terminal milestones and final EOF required')
    final = rows[-1]
    exact(final['payload'], ('control',))
    control = final['payload']['control']
    _terminal_dispatch_shape(control, 'FINALIZED')
    if final['clock_passes'] != control['terminal_cut']['first_eligible_idle_pass']:
        raise ValueError('FINALIZED diagnostic/terminal ordinal')
    if final['in_physics'] is not False or (final['physics'], final['idle']) != (control['physics'], control['idle']):
        raise ValueError('actual idle FINALIZED control frame')
    # Intermediate milestone contexts are SOURCE-control evidence, not business state.
    for row, phase in zip(milestones[:2], ('EMITTING', 'RETURNED')):
        payload = row['payload']
        exact(payload, ('control', 'private_connections', 'tree_connections') if phase == 'EMITTING' else ('control',))
        value = payload['control']
        _terminal_dispatch_shape(value, phase)
        if row['in_physics'] is not False or row['clock_passes'] != final['clock_passes'] or row['observer_sequence'] != final['observer_sequence'] or row['ui_sequence'] != final['ui_sequence']:
            raise ValueError('same-stack diagnostic phase/counters')
        _binding_same_source(value['terminal_cut'], control['terminal_cut'])
        if value['phase'] != phase or value['emit_count'] != 1 or type(value['emit_count']) is not int:
            raise ValueError('actual synchronous emission phase')
        if (row['physics'], row['idle'], value['physics'], value['idle'], value['receiver_id'], value['terminal_cut']) != (
                final['physics'], final['idle'], control['physics'], control['idle'], control['receiver_id'], control['terminal_cut']):
            raise ValueError('same-stack milestone identities')
        if value['native_emit_error_available'] is not False or value['native_emit_error'] is not None or value['script_emit_return'] is not None:
            raise ValueError('actual script NIL, native Error unavailable')
        if phase == 'EMITTING':
            _terminal_emitting_connections(payload, value)
            if value['dispatching'] is not True or value['script_emit_return_observed'] is not False or value['ack'] is not None:
                raise ValueError('precall synchronous bracket')
        elif value['dispatching'] is not False or value['script_emit_return_observed'] is not True or value['ack'] != control['ack']:
            raise ValueError('returned actual NIL/ack bracket')
    return control


def _terminal_dispatch_shape(control, phase):
    exact(control, TERMINAL_DISPATCH_KEYS)
    if control['phase'] != phase or _counter(control['emit_count']) != 1:
        raise ValueError('exact actual dispatch phase/once')
    for key in ('receiver_available', 'closed', 'complete', 'clock_closed', 'ui_closed'):
        if control[key] is not True:
            raise ValueError('complete actual dispatch BOOL')
    for key in ('native_emit_error_available', 'failed'):
        if control[key] is not False:
            raise ValueError('dispatch failure/native Error')
    for key in ('native_emit_error', 'script_emit_return', 'first_error', 'diagnostic_error'):
        if control[key] is not None:
            raise ValueError('dispatch NIL/clean evidence')
    _terminal_native_id(control['receiver_id'])
    _counter(control['physics']); _counter(control['idle'])
    exact(control['ready_connect'], ('physics', 'idle'))
    if any(type(v) is not int or v != 0 for v in control['ready_connect'].values()):
        raise ValueError('actual ready connection return values')
    exact(control['terminal_cut'], TERMINAL_CUT_KEYS)
    cut = control['terminal_cut']
    if cut['schema'] != TERMINAL_CONTROL_SCHEMA or cut['terminal_policy'] != TERMINAL_POLICY:
        raise ValueError('exact terminal control policy')
    for key in TERMINAL_CUT_KEYS[2:]:
        _counter(cut[key])
    if cut['minimum_future_physics_signals'] != 2 or cut['observed_future_physics_signals'] < 2 or cut['cleanup_anchor_pass'] >= cut['first_eligible_idle_pass']:
        raise ValueError('terminal control ordinal/count domain')
    if control['dispatching'] is not (phase == 'EMITTING') or control['script_emit_return_observed'] is not (phase != 'EMITTING'):
        raise ValueError('actual synchronous dispatch bracket')
    if phase == 'EMITTING':
        if control['ack'] is not None:
            raise ValueError('early acknowledgement')
    else:
        exact(control['ack'], ('receiver_id', 'physics', 'idle', 'serial'))
        ack = control['ack']
        if ack['receiver_id'] != control['receiver_id'] or (_counter(ack['physics']), _counter(ack['idle']), _counter(ack['serial'])) != (control['physics'], control['idle'], 1):
            raise ValueError('actual same-frame exact acknowledgement')
    if phase == 'FINALIZED':
        if control['finish_return'] is not True:
            raise ValueError('actual finalizer BOOLtrue')
    elif control['finish_return'] is not None:
        raise ValueError('early finalizer return marker')


def _terminal_native_id(value):
    if type(value) is not str or re.fullmatch('[1-9][0-9]*', value) is None or int(value) > MAX_COUNTER:
        raise ValueError('actual decimal native identity')
    return value


def _terminal_connection_table(table):
    exact(table, ('complete_seen', 'row_count', 'rows', 'reason'))
    if table['complete_seen'] is not True or table['reason'] is not None or type(table['rows']) is not list or _counter(table['row_count']) != len(table['rows']) or len(table['rows']) > 1024:
        raise ValueError('complete bounded actual connection table')
    keys = ('ordinal', 'source_has_key', 'source_variant_type', 'source_available', 'source_native_id',
            'target_has_key', 'target_variant_type', 'target_available', 'target_native_id', 'method', 'flags', 'binds_count', 'binds')
    for index, row in enumerate(table['rows']):
        exact(row, keys)
        if _counter(row['ordinal']) != index or type(row['method']) is not str:
            raise ValueError('physical connection ordinal/method')
        for prefix in ('source', 'target'):
            if row[prefix + '_has_key'] is not True or row[prefix + '_available'] is not True or type(row[prefix + '_variant_type']) is not int or row[prefix + '_variant_type'] not in (2, 17):
                raise ValueError('actual connection source/target availability')
            _terminal_native_id(row[prefix + '_native_id'])
        _counter(row['flags'])
        if type(row['binds']) is not list or _counter(row['binds_count']) != len(row['binds']) or len(row['binds']) > 64:
            raise ValueError('actual connection binds count')
    return table['rows']


def _terminal_emitting_connections(payload, control):
    private = _terminal_connection_table(payload['private_connections'])
    tree = _terminal_connection_table(payload['tree_connections'])
    if len(private) != 1:
        raise ValueError('unique private receiver')
    row = private[0]
    if row['target_native_id'] != control['receiver_id'] or row['method'] != 'on_idle_source_cut' or row['flags'] != 0 or row['binds_count'] != 0:
        raise ValueError('private receiver identity/flags/binds')
    sink = [r for r in tree if r['target_native_id'] == row['source_native_id'] and r['method'] == 'clock_idle_signal']
    if len(sink) != 1 or sink[0]['source_native_id'] != control['receiver_id'] or sink[0]['flags'] != 0 or sink[0]['binds_count'] != 0:
        raise ValueError('actual unique SceneTree sink connection')
    if any(r['target_native_id'] == control['receiver_id'] and r['method'] == 'on_idle_source_cut' for r in tree):
        raise ValueError('obsolete SceneTree collector callback')

schema = SimpleNamespace(
    validate_terminal_evidence=validate_terminal_evidence, validate_terminal_receipt=validate_terminal_receipt,
    validate_terminal_diagnostics=validate_terminal_diagnostics,
    validate_record=validate_record, validate_state=validate_state, validate_typed=validate_typed,
    validate_primitive=validate_primitive, primitive_context=primitive_context,
    strict_json_loads=strict_json_loads, exact=exact, integer=integer, decimal=decimal,
    text=text, CAPS=CAPS, CONTRACT=CONTRACT, MATRIX=MATRIX,
)


# phase360 auxiliary SOURCE interface; no projection or admission.
BINDING_MAX_BYTES = 2097152
BINDING_FIXED_PLAN = [{'side': 'P', 'input_slot': 0, 'instance_id': 'P:0', 'item_index': 11, 'x': 0, 'y': 0, 'f': 0, 'cells': [[0, 0], [0, 1], [1, 0], [1, 1]]}, {'side': 'P', 'input_slot': 1, 'instance_id': 'P:1', 'item_index': 11, 'x': 2, 'y': 0, 'f': 0, 'cells': [[2, 0], [2, 1], [3, 0], [3, 1]]}, {'side': 'P', 'input_slot': 2, 'instance_id': 'P:2', 'item_index': 11, 'x': 4, 'y': 0, 'f': 0, 'cells': [[4, 0], [4, 1], [5, 0], [5, 1]]}, {'side': 'P', 'input_slot': 3, 'instance_id': 'P:3', 'item_index': 11, 'x': 0, 'y': 2, 'f': 0, 'cells': [[0, 2], [0, 3], [1, 2], [1, 3]]}, {'side': 'P', 'input_slot': 4, 'instance_id': 'P:4', 'item_index': 11, 'x': 2, 'y': 2, 'f': 0, 'cells': [[2, 2], [2, 3], [3, 2], [3, 3]]}, {'side': 'P', 'input_slot': 5, 'instance_id': 'P:5', 'item_index': 11, 'x': 4, 'y': 2, 'f': 0, 'cells': [[4, 2], [4, 3], [5, 2], [5, 3]]}, {'side': 'P', 'input_slot': 6, 'instance_id': 'P:6', 'item_index': 262, 'x': 2, 'y': 0, 'f': 0, 'cells': [[2, 0], [2, 1], [2, 2], [3, 0], [3, 1], [3, 2]]}, {'side': 'P', 'input_slot': 7, 'instance_id': 'P:7', 'item_index': 23, 'x': 4, 'y': 0, 'f': 0, 'cells': [[4, 0], [4, 1], [5, 0], [5, 1]]}, {'side': 'P', 'input_slot': 8, 'instance_id': 'P:8', 'item_index': 22, 'x': 1, 'y': 0, 'f': 0, 'cells': [[1, 0]]}, {'side': 'P', 'input_slot': 9, 'instance_id': 'P:9', 'item_index': 22, 'x': 1, 'y': 1, 'f': 0, 'cells': [[1, 1]]}, {'side': 'P', 'input_slot': 10, 'instance_id': 'P:10', 'item_index': 22, 'x': 1, 'y': 2, 'f': 0, 'cells': [[1, 2]]}, {'side': 'P', 'input_slot': 11, 'instance_id': 'P:11', 'item_index': 22, 'x': 4, 'y': 2, 'f': 0, 'cells': [[4, 2]]}, {'side': 'P', 'input_slot': 12, 'instance_id': 'P:12', 'item_index': 1, 'x': 0, 'y': 0, 'f': 0, 'cells': [[0, 0], [0, 1]]}, {'side': 'P', 'input_slot': 13, 'instance_id': 'P:13', 'item_index': 1, 'x': 0, 'y': 2, 'f': 0, 'cells': [[0, 2], [0, 3]]}, {'side': 'O', 'input_slot': 0, 'instance_id': 'O:0', 'item_index': 11, 'x': 0, 'y': 0, 'f': 0, 'cells': [[0, 0], [0, 1], [1, 0], [1, 1]]}, {'side': 'O', 'input_slot': 1, 'instance_id': 'O:1', 'item_index': 11, 'x': 2, 'y': 0, 'f': 0, 'cells': [[2, 0], [2, 1], [3, 0], [3, 1]]}, {'side': 'O', 'input_slot': 2, 'instance_id': 'O:2', 'item_index': 11, 'x': 4, 'y': 0, 'f': 0, 'cells': [[4, 0], [4, 1], [5, 0], [5, 1]]}, {'side': 'O', 'input_slot': 3, 'instance_id': 'O:3', 'item_index': 11, 'x': 0, 'y': 2, 'f': 0, 'cells': [[0, 2], [0, 3], [1, 2], [1, 3]]}, {'side': 'O', 'input_slot': 4, 'instance_id': 'O:4', 'item_index': 11, 'x': 2, 'y': 2, 'f': 0, 'cells': [[2, 2], [2, 3], [3, 2], [3, 3]]}, {'side': 'O', 'input_slot': 5, 'instance_id': 'O:5', 'item_index': 11, 'x': 4, 'y': 2, 'f': 0, 'cells': [[4, 2], [4, 3], [5, 2], [5, 3]]}, {'side': 'O', 'input_slot': 6, 'instance_id': 'O:6', 'item_index': 1, 'x': 1, 'y': 0, 'f': 0, 'cells': [[1, 0], [1, 1]]}, {'side': 'O', 'input_slot': 7, 'instance_id': 'O:7', 'item_index': 1, 'x': 3, 'y': 0, 'f': 0, 'cells': [[3, 0], [3, 1]]}, {'side': 'O', 'input_slot': 8, 'instance_id': 'O:8', 'item_index': 4, 'x': 0, 'y': 2, 'f': 0, 'cells': [[0, 2], [0, 3], [1, 2], [1, 3]]}, {'side': 'O', 'input_slot': 9, 'instance_id': 'O:9', 'item_index': 19, 'x': 4, 'y': 0, 'f': 0, 'cells': [[4, 0], [4, 1]]}, {'side': 'O', 'input_slot': 10, 'instance_id': 'O:10', 'item_index': 22, 'x': 2, 'y': 2, 'f': 0, 'cells': [[2, 2]]}, {'side': 'O', 'input_slot': 11, 'instance_id': 'O:11', 'item_index': 22, 'x': 3, 'y': 2, 'f': 0, 'cells': [[3, 2]]}]
BINDING_SOURCE_CONTRACT = {'schema': 'phase360-binding-source-contract/1', 'schema_origin': {'path': 'tests/phase391_king_observer_schema.py', 'size': 208243, 'sha256': 'ffcddfd2cbe58307f7258c1aefad5586a9179c6c452dc59c3342f9047f31457c'}, 'producer_source_origin': {'path': 'data/phase462-joint-observer-source-v3/source-authority.json', 'size': 1054, 'sha256': '53fcd7f2ce1153d86b79f5cdf2c562cb0f86a00de800c4d6455d003ad54dfd63'}, 'fixed_slot_map': {'path': 'data/phase462-joint-observer-source-v3/fixed-plan.json', 'size': 21163, 'sha256': '06feb02caf7e29dc19e2aa402264c31739fde98c58f464bdfaf67db2ef1a0e9f'}, 'fixed_fixture': {'path': 'data/phase462-joint-observer-source-v3/fixed-v8-fixture.json', 'size': 3881, 'sha256': '209704d584e9719841834163758606afd5738f0de14fa90669627b1a52e39963'}, 'evidence_policy': 'SOURCE_ORIGIN_ONLY_NOT_INDEPENDENT_ACCEPTANCE_OR_RUNTIME_ADMISSION'}

"""Appended SOURCE template: auxiliary binding proof, never model admission.

The generator embeds the exact fixed plan and SOURCE-origin descriptors.  This
template deliberately has no imports, runtime calls, filesystem or entry point.
"""


def _binding_same_source(value, expected):
    if type(value) is not type(expected):
        raise ValueError('SOURCE value has a different primitive/container type')
    if type(expected) is dict:
        exact(value, expected)
        for key in expected:
            _binding_same_source(value[key], expected[key])
    elif type(expected) is list:
        if len(value) != len(expected):
            raise ValueError('SOURCE list length')
        for actual, planned in zip(value, expected):
            _binding_same_source(actual, planned)
    elif type(expected) not in (str, int, bool, type(None)) or value != expected:
        raise ValueError('exact frozen SOURCE literal required')


def _binding_id(value):
    decimal(value, True)
    return value


def _binding_integer_value(value):
    validate_typed(value)
    if value['type'] != 'int':
        raise ValueError('binding actual INT required')
    return decimal(value['decimal'])


def _binding_real_value(value):
    validate_typed(value)
    if value['type'] != 'float':
        raise ValueError('binding actual REAL required')
    return _single_king_real(value['binary64_be'])


def _binding_cells(cells, expected):
    if type(cells) is not list or len(cells) != len(expected):
        raise ValueError('binding occupied cell count')
    seen = set()
    wanted = {tuple(cell) for cell in expected}
    for cell in cells:
        if type(cell) is not list or len(cell) != 2:
            raise ValueError('binding occupied cell pair')
        point = tuple(integer(coordinate, 0, 127) for coordinate in cell)
        if point not in wanted or point in seen:
            raise ValueError('binding duplicate/foreign occupied cell')
        seen.add(point)
    if seen != wanted:
        raise ValueError('binding missing occupied cell')


def _binding_validate_value(value, fixed_plan):
    _binding_same_source(fixed_plan, BINDING_FIXED_PLAN)
    exact(value, ('schema', 'source_slot_table', 'actual_bindings',
                  'raw_early_rows_unchanged', 'model_input_admitted', 'remaining_interface'))
    if (value['schema'] != 'phase359-source-slot-bindings/1'
            or value['raw_early_rows_unchanged'] is not True
            or value['model_input_admitted'] is not False
            or value['remaining_interface'] != 'NOT_IN_358_ELEVEN_CARRIER_SCHEMA'):
        raise ValueError('exact359 auxiliary SOURCE format, not an admission flag')
    _binding_same_source(value['source_slot_table'], BINDING_FIXED_PLAN)
    rows = value['actual_bindings']
    if type(rows) is not list or len(rows) != len(BINDING_FIXED_PLAN):
        raise ValueError('exact26 actual slot bindings')
    planned = {row['instance_id']: row for row in BINDING_FIXED_PLAN}
    roles, natives, characters, inventories = set(), set(), {}, {}
    descriptor_by_index, index_by_descriptor = {}, {}
    encountered = {'P': [], 'O': []}
    sides = []
    for row in rows:
        exact(row, ('instance_id', 'input_slot', 'native_id', 'descriptor_id', 'item_index',
                    'top_left', 'orientation', 'occupiedCells', 'inventory_id', 'character_id',
                    'inventory_encounter_index'))
        role = row['instance_id']
        if type(role) is not str or role not in planned or role in roles:
            raise ValueError('unknown/duplicate fixed binding role; no O:12 renumbering')
        roles.add(role)
        spec = planned[role]
        side = spec['side']
        sides.append(side)
        if integer(row['input_slot'], 0, 19) != spec['input_slot']:
            raise ValueError('binding original fixture slot differs')
        if _binding_integer_value(row['item_index']) != spec['item_index']:
            raise ValueError('binding descriptor differs from SOURCE slot')
        if _binding_integer_value(row['orientation']) != spec['f']:
            raise ValueError('binding orientation differs from SOURCE slot')
        exact(row['top_left'], ('x', 'y'))
        for axis in ('x', 'y'):
            if _binding_real_value(row['top_left'][axis]) != spec[axis]:
                raise ValueError('binding actual top-left differs from SOURCE geometry')
        _binding_cells(row['occupiedCells'], spec['cells'])
        native, descriptor, inventory, character = [_binding_id(row[key]) for key in
            ('native_id', 'descriptor_id', 'inventory_id', 'character_id')]
        if native in natives:
            raise ValueError('actual item nativeID reused across slots')
        natives.add(native)
        if (side in characters and characters[side] != character
                or side in inventories and inventories[side] != inventory):
            raise ValueError('one actual character/inventory per side')
        characters[side], inventories[side] = character, inventory
        index = spec['item_index']
        if (index in descriptor_by_index and descriptor_by_index[index] != descriptor
                or descriptor in index_by_descriptor and index_by_descriptor[descriptor] != index):
            raise ValueError('actual descriptor/index association inconsistent')
        descriptor_by_index[index], index_by_descriptor[descriptor] = descriptor, index
        position = integer(row['inventory_encounter_index'], 0, 19)
        encountered[side].append(position)
    if roles != set(planned) or sides != [row['side'] for row in BINDING_FIXED_PLAN]:
        raise ValueError('exact fixed sides and source traversal groups')
    for side in ('P', 'O'):
        if encountered[side] != list(range(len(encountered[side]))):
            raise ValueError('actual inventory encounter order; never sorted into place')
    objects = list(characters.values()) + list(inventories.values())
    if (len(objects) != len(set(objects)) or set(objects) & natives
            or set(index_by_descriptor) & (natives | set(objects))):
        raise ValueError('item/character/inventory/descriptor native object aliases')
    return deepcopy(value)


def validate_binding_carrier(binding_bytes, fixed_plan):
    """Local closed DTO validation only, not a fullbundle/native positive."""
    if type(binding_bytes) is not bytes or not 0 < len(binding_bytes) <= BINDING_MAX_BYTES:
        raise ValueError('bounded auxiliary raw bytes required')
    if not binding_bytes.endswith(b'\n'):
        raise ValueError('auxiliary single JSON terminal newline')
    value = strict_json_loads(binding_bytes.decode('utf-8'))
    return _binding_validate_value(value, fixed_plan)


def _binding_check_channels(decoded11):
    exact(decoded11, INPUT_FILES)
    seen = set()
    for name in INPUT_FILES:
        value = decoded11[name]
        if name.endswith('.jsonl'):
            if type(value) is not list or not 1 <= len(value) <= ROW_CAPS[name]:
                raise ValueError('decoded SOURCE stream count')
        elif type(value) is not dict:
            raise ValueError('decoded SOURCE single object')
        if name not in CHANNEL_FILES:
            continue
        previous = -1
        for row in value:
            if type(row) is not dict or row.get('channel') != CHANNEL_FILES[name]:
                raise ValueError('physical filename/source channel mismatch')
            sequence = integer(row.get('sequence'), 0, CAPS['records'] - 1)
            if sequence <= previous or sequence in seen:
                raise ValueError('physical SOURCE order/global sequence uniqueness')
            previous = sequence
            seen.add(sequence)
            validate_record(row)


def _binding_one(rows, site, edge):
    found = [row for row in rows if row['site'] == site and row['edge'] == edge]
    if len(found) != 1:
        raise ValueError('unique binding SOURCE observation ' + site + ':' + edge)
    return found[0]


def _binding_checkpoint(row):
    nodes = {entry['role']: entry['node'] for entry in row['payload']['nodes']}
    wanted = ({'root_viewport', 'game', 'util', 'combat_timer', 'character:P', 'character:O'}
              | TIMER_ROLES | {'item:' + role for role in FIXED_ROLES})
    if set(nodes) != wanted:
        raise ValueError('exact frozen SOURCE checkpoint topology')
    native_to_role, role_to_native = {}, {}
    for envelope, node in nodes.items():
        role = envelope.split(':', 1)[1] if envelope.startswith(('item:', 'character:')) else envelope
        native = _binding_id(node['native_id'])
        if node['role'] != role or native in native_to_role or role in role_to_native:
            raise ValueError('actual checkpoint envelope/inner role/native identity')
        native_to_role[native], role_to_native[role] = role, native
    items = {entry['instance']: entry for entry in row['payload']['items']}
    if set(items) != FIXED_ROLES:
        raise ValueError('complete39 selected SOURCE checkpoint item states')
    return nodes, items, native_to_role, role_to_native


def join_binding_provenance(decoded11, binding, source_contract):
    """Relation-only SOURCE join. Complete11 validation is a separate caller step.

    No trusted 'verified' object shortcut, row mutation, role restamping, sorted
    primitive Tape, resource/default projection, runtime or patch admission.
    """
    _binding_same_source(source_contract, BINDING_SOURCE_CONTRACT)
    binding = _binding_validate_value(binding, BINDING_FIXED_PLAN)
    _binding_check_channels(decoded11)
    before = hashlib.sha256(json.dumps(decoded11, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    records = decoded11['observer7-input.jsonl']
    pre = _binding_one(records, 'Core/Game.gd::prepareItems', 'checkpoint')
    act = _binding_one(records, 'Core/Game.gd::activateItems', 'checkpoint')
    if pre['sequence'] >= act['sequence']:
        raise ValueError('binding preparation must precede activation')
    pre_nodes, pre_items, pre_natives, pre_roles = _binding_checkpoint(pre)
    act_nodes, act_items, act_natives, act_roles = _binding_checkpoint(act)
    if pre_natives != act_natives or pre_roles != act_roles:
        raise ValueError('actual pre/activate complete identity continuity')
    for role in pre_nodes:
        if pre_nodes[role]['class'] != act_nodes[role]['class']:
            raise ValueError('native class changed across source checkpoints')
    meta = _binding_one(decoded11['observer7-metadata.jsonl'], 'Sheets/ItemBook.gd::detectMentionedStacks', 'loaded_descriptors')
    descriptors = {}
    for encoded in meta['payload']['descriptors']['values']:
        fields = argument_fields(encoded)
        index = _binding_integer_value(fields['itemIndex'])
        descriptors[index] = fields['scene_path']['value']
    if set(descriptors) != DESCRIPTOR_IDS:
        raise ValueError('binding complete selected SOURCE descriptors')
    lineage = decoded11['observer7-lineage.jsonl']
    planned = {row['instance_id']: row for row in BINDING_FIXED_PLAN}
    evidence, inventory_order = {}, {'P': [], 'O': []}
    for actual in binding['actual_bindings']:
        role = actual['instance_id']
        spec, native = planned[role], actual['native_id']
        side = spec['side']
        if (act_roles.get(role) != native or actual['character_id'] != act_roles[side]):
            raise ValueError('binding actual item/Character differs from checkpoints')
        for nodes, items in ((pre_nodes, pre_items), (act_nodes, act_items)):
            fields = items[role]['fields']
            if (fields['descriptorIndex'] != actual['item_index']
                    or fields['faceDirection'] != actual['orientation']
                    or fields['placed'] != {'type': 'bool', 'value': True}
                    or fields['ownerType'] != {'type': 'int', 'decimal': '1' if side == 'P' else '3'}):
                raise ValueError('actual item descriptor/orientation/placed/Owner source join')
        scenes = [row for row in lineage if row['edge'] == 'scene_instance' and row['payload']['item_id'] == native]
        readies = [row for row in lineage if row['site'] == 'Items/Item.gd::_ready' and row['edge'] == 'enter'
                   and row['subject'].get('native_id') == native]
        if len(scenes) != 1 or len(readies) != 1:
            raise ValueError('one actual scene/ready per selected binding')
        scene, ready = scenes[0], readies[0]
        if (scene['subject']['type'] != 'native_ref' or scene['subject']['native_id'] != native
                or scene['subject']['role'] is not None or ready['subject']['role'] is not None
                or scene['subject']['class'] != act_nodes['item:' + role]['class']
                or ready['subject']['class'] != act_nodes['item:' + role]['class']
                or scene['payload']['descriptor_id'] != actual['descriptor_id']
                or scene['payload']['item_index'] != actual['item_index']
                or scene['payload']['scene_path'] != descriptors[spec['item_index']]
                or scene['payload']['pooled'] is not False
                or ready['payload']['state'] != {'native_id': native}
                or not scene['sequence'] < ready['sequence'] < pre['sequence']):
            raise ValueError('unchanged early NULL-role owner/descriptor/scene/ready chain')
        for counter in ('physics_frame', 'idle_frame'):
            values = [decimal(row['stamp'][counter]) for row in (scene, ready, pre, act)]
            if any(value < 0 for value in values) or values != sorted(values):
                raise ValueError('source birth/ready/checkpoint frame order')
        inventory_order[side].append(role)
        evidence[role] = dict(native_id=native, descriptor_id=actual['descriptor_id'], inventory_id=actual['inventory_id'],
                              character_id=actual['character_id'], scene_sequence=scene['sequence'], ready_sequence=ready['sequence'],
                              pre_sequence=pre['sequence'], activate_sequence=act['sequence'])
    after = hashlib.sha256(json.dumps(decoded11, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    if before != after:
        raise ValueError('binding join mutated decoded original observations')
    return dict(schema='phase360-auxiliary-binding-join/1', status='RELATION_PROOF_ONLY_NOT_FULL_ELEVEN_VALIDATION_OR_ADMISSION',
                native_to_role=deepcopy(act_natives), role_to_native=deepcopy(act_roles),
                input_order={side: [row['instance_id'] for row in BINDING_FIXED_PLAN if row['side'] == side] for side in ('P', 'O')},
                inventory_order=inventory_order, evidence_refs=evidence, decoded_observations_sha256=before,
                source_contract=deepcopy(BINDING_SOURCE_CONTRACT),
                source_limits=['359 inventory association derives from actual bind method getter/control-flow SOURCE; no second inventory-node direct sample',
                               '359 has no independent binding stamp; no timestamp was invented', '359 independent producer review is still pending'],
                input_bundle_created=False, native_admitted=False, model_calls=0)


def validate_sources_with_binding(raw11, binding_bytes, source_contract):
    """Full11 checks plus auxiliary relation proof; no projection or admission."""
    _binding_same_source(source_contract, BINDING_SOURCE_CONTRACT)
    if type(raw11) is not dict or set(raw11) != set(INPUT_FILES):
        raise ValueError('exact original eleven SOURCE names; auxiliary stays separate')
    if any(type(value) is not bytes for value in raw11.values()) or type(binding_bytes) is not bytes:
        raise ValueError('raw immutable SOURCE bytes required')
    if sum(map(len, raw11.values())) + len(binding_bytes) > TOTAL_BYTES:
        raise ValueError('combined eleven plus auxiliary total byte cap')
    binding = validate_binding_carrier(binding_bytes, BINDING_FIXED_PLAN)
    eleven = validate_source_carriers(raw11)
    decoded = decode_sources(raw11)
    joined = join_binding_provenance(decoded, binding, source_contract)
    pins = {name: dict(size=len(raw), sha256=hashlib.sha256(raw).hexdigest()) for name, raw in raw11.items()}
    pins['king-slot-bindings.json'] = dict(size=len(binding_bytes), sha256=hashlib.sha256(binding_bytes).hexdigest())
    return dict(schema='phase360-twelve-source-proof/1', status='SOURCE_PROOF_ONLY_NOT_INPUT_BUNDLE_OR_NATIVE_ACCEPTANCE',
                original_eleven_schema=eleven['schema'], binding_join=joined, raw_sources=pins,
                producer_independent_acceptance='PENDING_NOT_ASSERTED_BY_SCHEMA', input_bundle_created=False,
                native_admitted=False, model_calls=0, projection_implemented=False)


schema.validate_binding_carrier = validate_binding_carrier
schema.join_binding_provenance = join_binding_provenance
schema.validate_sources_with_binding = validate_sources_with_binding
