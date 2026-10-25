extends Node
#111 passive source hooks plus readonly SceneTree frame-signal clock sampler; no gameplay signal subscriptions.
# Not parser/runtime/native accepted by phase040.
const CAPS = {"array": 8192, "depth": 16, "descriptors": 6, "dictionary": 512, "failure_file_bytes": 4096, "file_bytes": 268435456, "first_error_bytes": 1024, "flush_bytes": 4194304, "host_capture_files": 64, "native_ids": 8192, "observer_files": 8, "pending_rows": 64, "record_bytes": 2097152, "records": 300000, "roles": 1024, "sparse_nodes": 16384, "string_utf8": 4096, "total_bytes": 268435456}
const STATE_SCHEMAS = {"auto_hide": {"emitting": "bool", "explosiveness": "float", "lifetime": "float", "one_shot": "bool", "speed_scale": "float", "timer": "timer|null", "visible": "bool"}, "buff": {"character": "native_ref|null", "cleanseProtectionChancePercent": "float", "current": "int", "nextTemporaryTimeout": "int", "permanentStacks": "int", "reflectChancePercent": "float", "resistChancePercent": "float", "resistStacks": "int", "temporaryStacks": "temporary_array", "timer": "timer|null", "type": "int"}, "character": {"allowStaminaOverflow": "bool", "autoRageItem": "native_ref|null", "battleRageBonusDur": "float", "battleRageTimer": "timer", "buffProtectStacks": "int", "critResistStacks": "int", "critResistance": "float", "critTokens": "int", "curHealth": "float", "curStamina": "float", "damageResistance": "float", "debuffReflectStacks": "int", "healingEfficiency": "float", "invulBubbleVisible": "bool", "invulnerabilityItem": "native_ref|null", "invulnerabilityTimer": "timer", "invulnerable": "bool", "isDead": "bool", "maxHealth": "float", "maxStamina": "float", "playerId": "int", "stunnedDuration": "float", "temporaryMaxHealth": "float", "temporaryMaxStamina": "float", "tickCounter": "int", "typedDamageFactors": "dictionary", "unhealingAmount": "float"}, "combat_log": {"eventNum": "int", "event_count": "int", "eventsLogged": "int", "loggingFinished": "bool"}, "combat_timer": {"combatTime": "float", "fatigueCounter": "int", "fatigueStartTimer": "timer", "fatigueTickTimer": "timer", "timeAdvance": "float"}, "event_bus": {"connection_count": "int", "loggingMode": "int", "signalQueue": "array"}, "game": {"allocation_counter": "int", "curClass": "int", "curMode": "int", "curRound": "int", "fightEnded": "bool", "roundResults": "array"}, "generic": {"native_id": "id"}, "goobert": {"activations": "int", "activationsThisFrame": "int", "activationsToTrigger": "float", "cachedAffectedItems": "dictionary", "consumed": "bool", "currentAffectedItems": "dictionary", "descriptorIndex": "int", "faceDirection": "int", "iterationCooldown": "float", "lastActivationTime": "float", "lastTriggerTime": "float", "ownerType": "int", "placed": "bool", "speedScale": "float", "triggerTime": "float", "triggersThisFrame": "int"}, "item": {"activationsThisFrame": "int", "cachedAffectedItems": "dictionary", "consumed": "bool", "currentAffectedItems": "dictionary", "descriptorIndex": "int", "faceDirection": "int", "iterationCooldown": "float", "lastActivationTime": "float", "lastTriggerTime": "float", "ownerType": "int", "placed": "bool", "speedScale": "float", "triggerTime": "float", "triggersThisFrame": "int"}, "king": {"activationParticles": "auto_hide", "activations": "int", "activationsThisFrame": "int", "activationsToTrigger": "float", "buffTimer": "timer", "cachedAffectedItems": "dictionary", "consumed": "bool", "currentAffectedItems": "dictionary", "descriptorIndex": "int", "faceDirection": "int", "invuCharges": "int", "iterationCooldown": "float", "lastActivationTime": "float", "lastTriggerTime": "float", "manaCost": "float", "ownerType": "int", "placed": "bool", "protectedBuffs": "float", "speedScale": "float", "triggerTime": "float", "triggersThisFrame": "int"}, "node": {"class": "string", "inside_tree": "bool", "internal_idle": "bool", "internal_physics": "bool", "name": "string", "native_id": "id", "ordinary_idle": "bool", "ordinary_physics": "bool", "path": "string|nulloutsideTree", "positions": "int_array", "priority": "int", "role": "string|null"}, "plain_item": {"activationsThisFrame": "int", "cachedAffectedItems": "dictionary", "consumed": "bool", "currentAffectedItems": "dictionary", "descriptorIndex": "int", "faceDirection": "int", "iterationCooldown": "float", "lastActivationTime": "float", "lastTriggerTime": "float", "ownerType": "int", "placed": "bool", "speedScale": "float", "triggerTime": "float", "triggersThisFrame": "int"}, "potion": {"activationsThisFrame": "int", "cachedAffectedItems": "dictionary", "consumed": "bool", "currentAffectedItems": "dictionary", "descriptorIndex": "int", "faceDirection": "int", "isFull": "bool", "iterationCooldown": "float", "lastActivationTime": "float", "lastTriggerTime": "float", "ownerType": "int", "placed": "bool", "speedScale": "float", "triggerTime": "float", "triggersThisFrame": "int"}, "temporary_constructor": {"amount": "int", "item": "native_ref|null", "timeout": "float"}, "timer": {"autostart": "bool", "node": "node", "one_shot": "bool", "paused": "bool", "process_mode": "int", "stopped": "bool", "time_left": "float", "wait_time": "float"}, "util": {"clockTime": "float", "frameCounter": "int", "time": "float"}}
const SITES = {"Core/Buff.gd::TemporaryStacks._init": {"channel": "lineage", "state_schema": "temporary_constructor"}, "Core/Buff.gd::changeCleanseProtectionChance": {"channel": "runtime", "state_schema": "buff"}, "Core/Buff.gd::changeCurrentLogShowLabel": {"channel": "runtime", "state_schema": "buff"}, "Core/Buff.gd::changeReflectChance": {"channel": "runtime", "state_schema": "buff"}, "Core/Buff.gd::changeResistChance": {"channel": "runtime", "state_schema": "buff"}, "Core/Buff.gd::combatEnd": {"channel": "runtime", "state_schema": "buff"}, "Core/Buff.gd::gainTemporary": {"channel": "runtime", "state_schema": "buff"}, "Core/Buff.gd::init": {"channel": "lineage", "state_schema": "buff"}, "Core/Buff.gd::loseStacks": {"channel": "runtime", "state_schema": "buff"}, "Core/Buff.gd::onTimeout": {"channel": "runtime", "state_schema": "buff"}, "Core/Character.gd::_physics_process": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::_ready": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::changeBuffProtectStacks": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::changeDebuffReflectStacks": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::changeMaxHealthTemporary": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::cleanse": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::combatEnd": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::combatStart": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::endBattleRage": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::endStun": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::gainMana": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::gainStacks": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::gainStacksTemporary": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::invulnerabilityEnded": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::loseHealth": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::makeInvulnerable": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::onTick": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::prepare": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::startBattleRage": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::stun": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::takeDamage": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::useMana": {"channel": "runtime", "state_schema": "character"}, "Core/Character.gd::useStacks": {"channel": "runtime", "state_schema": "character"}, "Core/CombatLog.gd::createEvent": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::createEvent_BattleRageEnd": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::createEvent_BattleRageStart": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::createEvent_InvulnerableEnd": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::createEvent_InvulnerableStart": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::createEvent_Stack": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::createEvent_StackTemporary": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::createEvent_StackTimeout": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::logEvent": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::onCombatEnd": {"channel": "runtime", "state_schema": "combat_log"}, "Core/CombatLog.gd::snapshotItemState": {"channel": "runtime", "state_schema": "combat_log"}, "Core/Game.gd::activateItems": {"channel": "input", "state_schema": "game"}, "Core/Game.gd::combatEndDeferred": {"channel": "runtime", "state_schema": "game"}, "Core/Game.gd::endCombat": {"channel": "runtime", "state_schema": "game"}, "Core/Game.gd::prepareItems": {"channel": "input", "state_schema": "game"}, "Interface/CombatTimer/CombatTimer.gd::_physics_process": {"channel": "runtime", "state_schema": "combat_timer"}, "Interface/CombatTimer/CombatTimer.gd::combatEnd": {"channel": "runtime", "state_schema": "combat_timer"}, "Interface/CombatTimer/CombatTimer.gd::dealFatigueDamage": {"channel": "runtime", "state_schema": "combat_timer"}, "Interface/CombatTimer/CombatTimer.gd::start": {"channel": "runtime", "state_schema": "combat_timer"}, "Interface/CombatTimer/CombatTimer.gd::startFatigue": {"channel": "runtime", "state_schema": "combat_timer"}, "Items/Exclusive/KingGoobert.gd::buffEnded": {"channel": "runtime", "state_schema": "king"}, "Items/Exclusive/KingGoobert.gd::doCooldownEffect": {"channel": "runtime", "state_schema": "king"}, "Items/Exclusive/KingGoobert.gd::onCombatEnd": {"channel": "runtime", "state_schema": "king"}, "Items/Exclusive/KingGoobert.gd::onStateChanged": {"channel": "runtime", "state_schema": "king"}, "Items/Exclusive/KingGoobert.gd::prepare": {"channel": "runtime", "state_schema": "king"}, "Items/Goobert.gd::doCooldownEffect": {"channel": "runtime", "state_schema": "goobert"}, "Items/Goobert.gd::onItemActivated": {"channel": "runtime", "state_schema": "goobert"}, "Items/Goobert.gd::prepare": {"channel": "runtime", "state_schema": "goobert"}, "Items/HealthPotion.gd::onDamaged": {"channel": "runtime", "state_schema": "potion"}, "Items/HealthPotion.gd::onPrepare": {"channel": "runtime", "state_schema": "potion"}, "Items/HealthPotion.gd::onTriggerPotion": {"channel": "runtime", "state_schema": "potion"}, "Items/Item.gd::_physics_process": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::_ready": {"channel": "lineage", "state_schema": "generic"}, "Items/Item.gd::activate": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::addBonusDamage": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::cleanseRandomDebuffs": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::combatEnd": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::consume": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::getMostStacks": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::giveMana": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::giveMana_capped": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::giveMaxHealth": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::giveMostBuffs": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::healthToBlock": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::miniActivate": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::pickRandomStacks": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::prepare": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::rollChance": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::stealLife": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::tryUseMana": {"channel": "runtime", "state_schema": "item"}, "Items/Item.gd::useMana": {"channel": "runtime", "state_schema": "item"}, "Items/ItemDescriptor.gd::instantiate": {"channel": "lineage", "state_schema": "generic"}, "Items/ItemDescriptor.gd::instantiate_pooled": {"channel": "lineage", "state_schema": "generic"}, "Items/Potion.gd::activate": {"channel": "runtime", "state_schema": "potion"}, "Items/Potion.gd::consumePotion": {"channel": "runtime", "state_schema": "potion"}, "Items/Potion.gd::prepare": {"channel": "runtime", "state_schema": "potion"}, "Items/Potion.gd::triggerPotion": {"channel": "runtime", "state_schema": "potion"}, "Items/Weapon.gd::attack": {"channel": "runtime", "state_schema": "item"}, "Items/Weapon.gd::doCooldownEffect": {"channel": "runtime", "state_schema": "item"}, "Sheets/ItemBook.gd::detectMentionedStacks": {"channel": "metadata", "state_schema": "generic"}, "Utility/AutoHideParticles.gd::_ready": {"channel": "runtime", "state_schema": "auto_hide"}, "Utility/AutoHideParticles.gd::activate": {"channel": "runtime", "state_schema": "auto_hide"}, "Utility/AutoHideParticles.gd::deactivate": {"channel": "runtime", "state_schema": "auto_hide"}, "Utility/AutoHideParticles.gd::instantClear": {"channel": "runtime", "state_schema": "auto_hide"}, "Utility/AutoHideParticles.gd::startTimer": {"channel": "runtime", "state_schema": "auto_hide"}, "Utility/AutoHideParticles.gd::timeout": {"channel": "runtime", "state_schema": "auto_hide"}, "Utility/EventBus.gd::connectEvent": {"channel": "runtime", "state_schema": "event_bus"}, "Utility/EventBus.gd::disconnectAll": {"channel": "runtime", "state_schema": "event_bus"}, "Utility/EventBus.gd::emitAndLog": {"channel": "runtime", "state_schema": "event_bus"}, "Utility/EventBus.gd::flushLoggingQueue": {"channel": "runtime", "state_schema": "event_bus"}, "Utility/Util.gd::_physics_process": {"channel": "runtime", "state_schema": "util"}, "Utility/Util.gd::_process": {"channel": "runtime", "state_schema": "util"}, "Utility/Util.gd::changeTimer": {"channel": "runtime", "state_schema": "util"}}
const CHANNEL_FILES = {"allocation": "observer7-allocations.jsonl", "input": "observer7-input.jsonl", "lineage": "observer7-lineage.jsonl", "metadata": "observer7-metadata.jsonl", "primitive": "observer7-primitives.jsonl", "registration": "observer7-registration.jsonl", "runtime": "observer7-runtime.jsonl"}
const OUT = "user://native-capture"
const SOURCE_SLOT_TABLE = [{"cells": [[0, 0], [1, 0], [0, 1], [1, 1]], "f": 0, "input_slot": 0, "instance_id": "P:0", "item_index": 11, "side": "P", "x": 0, "y": 0}, {"cells": [[2, 0], [3, 0], [2, 1], [3, 1]], "f": 0, "input_slot": 1, "instance_id": "P:1", "item_index": 11, "side": "P", "x": 2, "y": 0}, {"cells": [[4, 0], [5, 0], [4, 1], [5, 1]], "f": 0, "input_slot": 2, "instance_id": "P:2", "item_index": 11, "side": "P", "x": 4, "y": 0}, {"cells": [[6, 0], [7, 0], [6, 1], [7, 1]], "f": 0, "input_slot": 3, "instance_id": "P:3", "item_index": 11, "side": "P", "x": 6, "y": 0}, {"cells": [[0, 2], [1, 2], [0, 3], [1, 3]], "f": 0, "input_slot": 4, "instance_id": "P:4", "item_index": 11, "side": "P", "x": 0, "y": 2}, {"cells": [[2, 2], [3, 2], [2, 3], [3, 3]], "f": 0, "input_slot": 5, "instance_id": "P:5", "item_index": 11, "side": "P", "x": 2, "y": 2}, {"cells": [[4, 2], [5, 2], [4, 3], [5, 3]], "f": 0, "input_slot": 6, "instance_id": "P:6", "item_index": 11, "side": "P", "x": 4, "y": 2}, {"cells": [[6, 2], [7, 2], [6, 3], [7, 3]], "f": 0, "input_slot": 7, "instance_id": "P:7", "item_index": 11, "side": "P", "x": 6, "y": 2}, {"cells": [[0, 4], [1, 4], [0, 5], [1, 5]], "f": 0, "input_slot": 8, "instance_id": "P:8", "item_index": 11, "side": "P", "x": 0, "y": 4}, {"cells": [[2, 4], [3, 4], [2, 5], [3, 5]], "f": 0, "input_slot": 9, "instance_id": "P:9", "item_index": 11, "side": "P", "x": 2, "y": 4}, {"cells": [[4, 4], [5, 4], [4, 5], [5, 5]], "f": 0, "input_slot": 10, "instance_id": "P:10", "item_index": 11, "side": "P", "x": 4, "y": 4}, {"cells": [[6, 4], [7, 4], [6, 5], [7, 5]], "f": 0, "input_slot": 11, "instance_id": "P:11", "item_index": 11, "side": "P", "x": 6, "y": 4}, {"cells": [[2, 1], [3, 1], [2, 2], [3, 2], [2, 3], [3, 3]], "f": 0, "input_slot": 12, "instance_id": "P:12", "item_index": 262, "side": "P", "x": 2, "y": 1}, {"cells": [[1, 1]], "f": 0, "input_slot": 13, "instance_id": "P:13", "item_index": 22, "side": "P", "x": 1, "y": 1}, {"cells": [[1, 2]], "f": 0, "input_slot": 14, "instance_id": "P:14", "item_index": 22, "side": "P", "x": 1, "y": 2}, {"cells": [[1, 3]], "f": 0, "input_slot": 15, "instance_id": "P:15", "item_index": 22, "side": "P", "x": 1, "y": 3}, {"cells": [[4, 1], [4, 2]], "f": 0, "input_slot": 16, "instance_id": "P:16", "item_index": 1, "side": "P", "x": 4, "y": 1}, {"cells": [[4, 3]], "f": 0, "input_slot": 17, "instance_id": "P:17", "item_index": 22, "side": "P", "x": 4, "y": 3}, {"cells": [[6, 0], [6, 1]], "f": 0, "input_slot": 18, "instance_id": "P:18", "item_index": 19, "side": "P", "x": 6, "y": 0}, {"cells": [[6, 4], [7, 4], [6, 5], [7, 5]], "f": 0, "input_slot": 19, "instance_id": "P:19", "item_index": 4, "side": "P", "x": 6, "y": 4}, {"cells": [[0, 0], [1, 0], [0, 1], [1, 1]], "f": 0, "input_slot": 0, "instance_id": "O:0", "item_index": 11, "side": "O", "x": 0, "y": 0}, {"cells": [[2, 0], [3, 0], [2, 1], [3, 1]], "f": 0, "input_slot": 1, "instance_id": "O:1", "item_index": 11, "side": "O", "x": 2, "y": 0}, {"cells": [[4, 0], [5, 0], [4, 1], [5, 1]], "f": 0, "input_slot": 2, "instance_id": "O:2", "item_index": 11, "side": "O", "x": 4, "y": 0}, {"cells": [[6, 0], [7, 0], [6, 1], [7, 1]], "f": 0, "input_slot": 3, "instance_id": "O:3", "item_index": 11, "side": "O", "x": 6, "y": 0}, {"cells": [[0, 2], [1, 2], [0, 3], [1, 3]], "f": 0, "input_slot": 4, "instance_id": "O:4", "item_index": 11, "side": "O", "x": 0, "y": 2}, {"cells": [[2, 2], [3, 2], [2, 3], [3, 3]], "f": 0, "input_slot": 5, "instance_id": "O:5", "item_index": 11, "side": "O", "x": 2, "y": 2}, {"cells": [[4, 2], [5, 2], [4, 3], [5, 3]], "f": 0, "input_slot": 6, "instance_id": "O:6", "item_index": 11, "side": "O", "x": 4, "y": 2}, {"cells": [[6, 2], [7, 2], [6, 3], [7, 3]], "f": 0, "input_slot": 7, "instance_id": "O:7", "item_index": 11, "side": "O", "x": 6, "y": 2}, {"cells": [[0, 4], [1, 4], [0, 5], [1, 5]], "f": 0, "input_slot": 8, "instance_id": "O:8", "item_index": 11, "side": "O", "x": 0, "y": 4}, {"cells": [[2, 4], [3, 4], [2, 5], [3, 5]], "f": 0, "input_slot": 9, "instance_id": "O:9", "item_index": 11, "side": "O", "x": 2, "y": 4}, {"cells": [[4, 4], [5, 4], [4, 5], [5, 5]], "f": 0, "input_slot": 10, "instance_id": "O:10", "item_index": 11, "side": "O", "x": 4, "y": 4}, {"cells": [[6, 4], [7, 4], [6, 5], [7, 5]], "f": 0, "input_slot": 11, "instance_id": "O:11", "item_index": 11, "side": "O", "x": 6, "y": 4}, {"cells": [[1, 1]], "f": 0, "input_slot": 12, "instance_id": "O:13", "item_index": 22, "side": "O", "x": 1, "y": 1}, {"cells": [[1, 2]], "f": 0, "input_slot": 13, "instance_id": "O:14", "item_index": 22, "side": "O", "x": 1, "y": 2}, {"cells": [[1, 3]], "f": 0, "input_slot": 14, "instance_id": "O:15", "item_index": 22, "side": "O", "x": 1, "y": 3}, {"cells": [[4, 1], [4, 2]], "f": 0, "input_slot": 15, "instance_id": "O:16", "item_index": 1, "side": "O", "x": 4, "y": 1}, {"cells": [[4, 3]], "f": 0, "input_slot": 16, "instance_id": "O:17", "item_index": 22, "side": "O", "x": 4, "y": 3}, {"cells": [[6, 0], [6, 1]], "f": 0, "input_slot": 17, "instance_id": "O:18", "item_index": 19, "side": "O", "x": 6, "y": 0}, {"cells": [[6, 4], [7, 4], [6, 5], [7, 5]], "f": 0, "input_slot": 18, "instance_id": "O:19", "item_index": 4, "side": "O", "x": 6, "y": 4}]
var ids = {} # integer native IDs -> immutable role strings only
var seen_ids = {} # integer -> class string, never Object
var file_sizes = {}
var sequence = 0
var total_bytes = 0
var failed = false
var first_error = null
var configured = false
var enabled = false
var metadata_ready = false
var closed = false
var active_buff_calls = [] # primitive-only nested source-call context
var connection_ids = {} # actual FuncRef int ID -> original emission int ID
var source_types = {} # int native ID -> known qualified constructor type, never Object
var source_lifetimes = {} # integer IDs -> primitive counters only
var source_phase = "bootstrap"
var activation_checkpoints = 0
var registered_connections = 0
var encoding_remaining = 2097152

# SOURCE-only extension template. The generator merges these actual methods into154.
var source_fixture_window = false
var source_fixture_bound = false
var source_buffer = [] # fully encoded primitive rows, never Node/Event objects
var source_buffer_bytes = 0
var source_cleanup = null
var source_window_complete = false
var source_crowns = {} # nativeID -> actual last onStateChanged INT argument
var source_binding_proof = null


func begin_encoding():
	encoding_remaining = CAPS.record_bytes

func reserve_encoding(amount):
	if amount < 0 or amount > encoding_remaining:
		return fail("ENCODER_PREALLOCATION_CAP", source_phase)
	encoding_remaining -= amount
	return true

func _ready():
	get_tree().connect("physics_frame", self, "clock_physics_signal")
	get_tree().connect("idle_frame", self, "clock_idle_signal")
	var status = Directory.new().make_dir_recursive(OUT)
	if status != OK:
		fail("BOOTSTRAP_DIRECTORY", "sink", status)
		return
	var existing = File.new()
	for filename in CHANNEL_FILES.values() + ["observer7_failure.json"]:
		if existing.file_exists(OUT.plus_file(filename)):
			fail("PREEXISTING_OBSERVER_FILE", "sink")
			return
	ui_open()

func fail(code, site, detail = null):
	if failed:
		return false
	failed = true
	# Fixed-size fields only; never stringifies an unknown Object or unbounded detail.
	var safe_detail = detail if typeof(detail) in [TYPE_NIL, TYPE_INT, TYPE_BOOL] else null
	first_error = {"schema": "observer7-failure/1", "code": code, "site": site.substr(0, 256), "sequence": sequence, "detail": safe_detail, "capture_complete": false}
	var message = JSON.print(first_error)
	if message.to_utf8().size() > CAPS.first_error_bytes:
		message = '{"schema":"observer7-failure/1","code":"FAILURE_ENCODING","capture_complete":false}'
	var file = File.new()
	if not file.file_exists(OUT.plus_file("observer7_failure.json")) and file.open(OUT.plus_file("observer7_failure.json"), File.WRITE) == OK:
		file.store_string(message + "\n")
		file.flush()
		file.close()
	return false

func native_id(object):
	if object == null or not is_instance_valid(object):
		fail("INVALID_NATIVE_REFERENCE", source_phase)
		return null
	var id = object.get_instance_id()
	if not seen_ids.has(id):
		if seen_ids.size() >= CAPS.native_ids:
			fail("NATIVE_ID_CAP", source_phase)
			return null
		seen_ids[id] = object.get_class()
	elif seen_ids[id] != object.get_class():
		fail("NATIVE_ID_COLLISION", source_phase)
	return str(id)

func reference(object):
	if object == null:
		return {"type": "null"}
	var id = native_id(object)
	if id == null:
		return {"type": "null"}
	return {"type": "native_ref", "native_id": id, "role": ids.get(object.get_instance_id(), null), "class": object.get_class()}

func float_bits(value):
	var buffer = StreamPeerBuffer.new()
	buffer.big_endian = true
	buffer.put_double(value)
	return buffer.data_array.hex_encode()

func encode(value, depth = 0, ordinal = 0):
	if not reserve_encoding(64):
		return {"type": "null"}
	if failed:
		return {"type": "null"}
	if depth > CAPS.depth:
		fail("DEPTH_CAP", source_phase)
		return {"type": "null"}
	match typeof(value):
		TYPE_NIL:
			return {"type": "null"}
		TYPE_BOOL:
			return {"type": "bool", "value": value}
		TYPE_INT:
			return {"type": "int", "decimal": str(value)}
		TYPE_REAL:
			if is_nan(value) or is_inf(value):
				fail("NONFINITE", source_phase)
				return {"type": "null"}
			return {"type": "float", "binary64_be": float_bits(value)}
		TYPE_STRING:
			if value.length() > CAPS.string_utf8 or value.to_utf8().size() > CAPS.string_utf8 or not reserve_encoding(value.length() * 24):
				fail("STRING_CAP", source_phase)
				return {"type": "null"}
			return {"type": "string", "value": value}
		TYPE_ARRAY:
			if value.size() > CAPS.array or not reserve_encoding(value.size() * 16):
				fail("ARRAY_CAP", source_phase)
				return {"type": "null"}
			var rows = []
			for i in range(value.size()):
				if failed:
					break
				rows.append(encode(value[i], depth + 1, i))
			return {"type": "array", "values": rows}
		TYPE_DICTIONARY:
			if value.size() > CAPS.dictionary or not reserve_encoding(value.size() * 32):
				fail("DICTIONARY_CAP", source_phase)
				return {"type": "null"}
			var rows = []
			for key in value:
				if failed:
					break
				rows.append({"key": encode(key, depth + 1), "value": encode(value[key], depth + 1)})
			return {"type": "dictionary", "entries": rows}
		TYPE_OBJECT:
			if not is_instance_valid(value):
				fail("FREED_REFERENCE", source_phase)
				return {"type": "null"}
			if is_temporary(value):
				return temporary(value, ordinal, depth + 1)
			if source_is(value, "res://Utility/DamageResult.gd"):
				var result = {"type": "damage_result", "native_id": native_id(value)}
				for key in ["event", "damageSource", "damage", "healthDamage", "hit", "critical", "damageReduction"]:
					result[key] = encode(value.get(key), depth + 1)
				return result
			if source_is(value, "res://Utility/DamageSource.gd"):
				var result = {"type": "damage_source", "native_id": native_id(value)}
				for key in ["minDamage", "maxDamage", "types", "accuracy", "critChancePercent", "origin", "flags"]:
					result[key] = encode(value.get(key), depth + 1)
				return result
			if source_is(value, "res://Core/CombatEvent.gd"):
				return {"type": "event_ref", "native_id": native_id(value), "event_id": str(value.id)}
			if value is Node or source_types.get(value.get_instance_id(), "") == "buff":
				return reference(value)
			fail("UNKNOWN_REFERENCE", source_phase)
			return {"type": "null"}
	fail("UNKNOWN_VARIANT", source_phase, typeof(value))
	return {"type": "null"}

func temporary(value, ordinal, depth = 0):
	if depth > CAPS.depth or not is_temporary(value):
		fail("TEMPORARY_REFERENCE", source_phase)
		return {"type": "null"}
	return {"type": "temporary", "native_id": native_id(value), "ordinal": ordinal, "amount": encode(value.amount, depth + 1), "timeout": encode(value.timeout, depth + 1), "item": reference(value.item)}

func node_state(node):
	if not node is Node:
		fail("NODE_REQUIRED", source_phase)
		return null
	var positions = []
	var cursor = node
	while cursor != null:
		if positions.size() >= CAPS.depth:
			fail("ANCESTOR_DEPTH", source_phase)
			return null
		positions.push_front(cursor.get_index())
		cursor = cursor.get_parent()
	return {"native_id": native_id(node), "role": ids.get(node.get_instance_id(), null), "path": str(node.get_path()) if node.is_inside_tree() else null, "name": str(node.name), "class": node.get_class(), "positions": positions, "priority": node.get_process_priority(), "inside_tree": node.is_inside_tree(), "ordinary_physics": node.is_physics_processing(), "internal_physics": node.is_physics_processing_internal(), "ordinary_idle": node.is_processing(), "internal_idle": node.is_processing_internal()}

func timer_state(timer):
	if timer == null:
		return null
	if not timer is Timer:
		fail("TIMER_REQUIRED", source_phase)
		return null
	return {"node": node_state(timer), "process_mode": timer.process_mode, "wait_time": encode(timer.wait_time), "time_left": encode(timer.time_left), "one_shot": timer.one_shot, "autostart": timer.autostart, "paused": timer.paused, "stopped": timer.is_stopped()}

func state(object, schema):
	if schema in ["item", "goobert", "king", "potion"]:
		var index = object.descriptor.itemIndex
		if not index in [1, 4, 11, 19, 22, 262]:
			fail("SOURCE_ITEM_DOMAIN", source_phase)
			return {}
		schema = "king" if index == 262 else ("potion" if index == 19 else "item")
	if not STATE_SCHEMAS.has(schema):
		fail("SOURCE_STATE_SCHEMA", source_phase)
		return {}
	if schema == "node":
		return node_state(object)
	if schema == "timer":
		return timer_state(object)
	var result = {}
	for key in STATE_SCHEMAS[schema]:
		if key == "descriptorIndex":
			result[key] = encode(object.descriptor.itemIndex)
		elif key == "native_id":
			result[key] = native_id(object)
		elif key == "allocation_counter":
			result[key] = encode(object.combatLog.eventNum)
		elif key == "event_count":
			result[key] = encode(object.events.size())
		elif key == "connection_count":
			var count = 0
			for emission in object.connections:
				count += object.connections[emission].size()
			result[key] = encode(count)
		elif STATE_SCHEMAS[schema][key] in ["timer", "timer|null"]:
			result[key] = timer_state(object.get(key))
		elif STATE_SCHEMAS[schema][key] == "auto_hide":
			result[key] = state(object.get(key), "auto_hide")
		else:
			result[key] = encode(object.get(key))
	return result


func stamp():
	var util = get_node_or_null("/root/Util")
	var game = get_node_or_null("/root/Game")
	var clock = null
	if game != null and game.combatTimer != null:
		clock = game.combatTimer.combatTime
	return {"physics_frame": str(Engine.get_physics_frames()), "idle_frame": str(Engine.get_idle_frames()), "util_time": encode(util.time if util != null else null), "combat_time": encode(clock), "phase": source_phase}

# Bound the JSON allocation before JSON.print; all stored values are copied primitives.
func estimated_bytes(value, depth = 0):
	if depth > CAPS.depth + 8:
		return CAPS.record_bytes + 1
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_REAL:
			return 32
		TYPE_STRING:
			if value.length() > CAPS.record_bytes:
				return CAPS.record_bytes + 1
			return 2 + value.to_utf8().size() * 6
		TYPE_ARRAY, TYPE_DICTIONARY:
			var n = 2
			if value.size() > CAPS.array:
				return CAPS.record_bytes + 1
			for key in value:
				if typeof(value) == TYPE_DICTIONARY:
					n += estimated_bytes(key, depth + 1) + estimated_bytes(value[key], depth + 1) + 2
				else:
					n += estimated_bytes(key, depth + 1) + 1
				if n > CAPS.record_bytes:
					return n
			return n
	return CAPS.record_bytes + 1

func write_record(channel, site, edge, subject, payload):
	if failed or closed:
		return false
	if not CHANNEL_FILES.has(channel) or sequence >= CAPS.records:
		return fail("SOURCE_RECORD_CAP_OR_CHANNEL", site)
	var row = {"schema": "observer7-record/1", "sequence": sequence, "channel": channel, "site": site, "edge": edge, "subject": reference(subject), "stamp": stamp(), "payload": payload}
	sequence += 1
	if not source_fixture_bound:
		if not source_fixture_window or channel != "lineage":
			return true
		var bytes = (JSON.print(row) + "\n").to_utf8()
		if source_buffer.size() >= 384 or source_buffer_bytes + bytes.size() > 2097152:
			return fail("SOURCE_PREBIND_PRIMITIVE_BUFFER_CAP", site)
		source_buffer.append(row) # already primitive; stamp/seq/role remain original
		source_buffer_bytes += bytes.size()
		return true
	return source_write_row(row)


func configure(registry):
	if configured or registry.size() > CAPS.roles:
		return fail("REGISTRY_RECONFIGURE_OR_CAP", "configure")
	var roles_seen = {}
	for id in registry:
		if typeof(id) != TYPE_INT or typeof(registry[id]) != TYPE_STRING or roles_seen.has(registry[id]):
			return fail("REGISTRY_ID_ROLE", "configure")
		if registry[id].length() > CAPS.string_utf8 or registry[id].to_utf8().size() > CAPS.string_utf8:
			return fail("ROLE_STRING_CAP", "configure")
		roles_seen[registry[id]] = true
		ids[id] = registry[id]
	configured = true
	return ui_bind_roles(registry)

func identity(object):
	if not enabled:
		return "UNOBSERVED"
	if object == null:
		return "null"
	var id = object.get_instance_id()
	if ids.has(id):
		return ids[id]
	fail("UNREGISTERED_SELECTED_REFERENCE", source_phase)
	return "UNREGISTERED"

func item_id(item):
	return identity(item)

func side(character):
	return identity(character)

func entry(site, object, arguments):
	if failed or closed:
		return
	# Native IDs and primitive constructor counters are captured even before the
	# selected inventory can be geometrically associated. No event object is kept.
	if site in ["Core/Buff.gd::init", "Core/Buff.gd::TemporaryStacks._init"]:
		var source_id = native_id(object)
		if source_id == null:
			return
		var source_type = "temporary" if site == "Core/Buff.gd::TemporaryStacks._init" else "buff"
		var key = object.get_instance_id()
		if source_types.has(key) and source_types[key] != source_type:
			fail("SOURCE_TYPE_ID_COLLISION", site)
			return
		source_types[key] = source_type
	if site in ["Items/Item.gd::_ready", "Items/Item.gd::prepare", "Core/Buff.gd::init"]:
		var id = object.get_instance_id()
		native_id(object)
		if not source_lifetimes.has(id):
			source_lifetimes[id] = {"scene": 0, "ready": 0, "prepare": 0, "buff_init": 0, "pooled": false}
		var counter = "ready" if site == "Items/Item.gd::_ready" else ("prepare" if site == "Items/Item.gd::prepare" else "buff_init")
		source_lifetimes[id][counter] += 1
	if site == "Core/Game.gd::prepareItems" and not source_fixture_bound:
		fail("SOURCE_PREPARE_WITHOUT_ACTUAL_SLOT_BINDING", site)
		return
	if not source_observable(site, object):
		return
	if not SITES.has(site):
		fail("SOURCE_UNDECLARED_SELECTED_SITE", site)
		return
	begin_encoding()
	source_phase = site + ":enter"
	if site == "Core/Game.gd::prepareItems":
		if not source_fixture_bound or not selected_lineage(arguments.items, [object.PLAYER, object.OPPONENT]) or not rng_initial_capture(object):
			fail("SOURCE_PREPARE_WITHOUT_BOUND_FRESH_PROOF", site)
			return
		enabled = true
	if site == "Core/Game.gd::activateItems":
		if not rng_initial_continuity() or not begin_king_clock(object, arguments.items):
			return
		activation_checkpoints += 1
		if activation_checkpoints != 1:
			fail("SOURCE_ACTIVATE_MULTIPLE", site)
	if site == "Items/Exclusive/KingGoobert.gd::onStateChanged":
		if typeof(arguments._crownState) != TYPE_INT:
			fail("SOURCE_CROWN_ARGUMENT_TYPE", site)
			return
		source_crowns[str(object.get_instance_id())] = arguments._crownState
	if site == "Core/Buff.gd::gainTemporary":
		if active_buff_calls.size() >= CAPS.depth:
			fail("SOURCE_BUFF_CONTEXT_DEPTH", site)
		else:
			active_buff_calls.append({"target": ids.get(object.character.get_instance_id(), null), "stack": buff_name(object.type), "reflect": arguments.reflect})
	if site in ["Core/Game.gd::prepareItems", "Core/Game.gd::activateItems"]:
		checkpoint(site, object, arguments.items)
	var spec = SITES[site]
	write_record(spec.channel, site, "enter", object, {"arguments": encode(arguments), "state": state(object, spec.state_schema)})


func leave(site, object, value, edge):
	if failed or closed:
		return
	if site == "Sheets/ItemBook.gd::detectMentionedStacks":
		metadata_ready = true
	if site in ["Items/ItemDescriptor.gd::instantiate", "Items/ItemDescriptor.gd::instantiate_pooled"]:
		scene_instance(object, value, site.ends_with("instantiate_pooled"))
	if not source_observable(site, object):
		return
	if not SITES.has(site):
		fail("SOURCE_UNDECLARED_SELECTED_RETURN", site)
		return
	begin_encoding()
	if site.begins_with("Core/CombatLog.gd::createEvent") and source_is(value, "res://Core/CombatEvent.gd"):
		write_record("allocation", site, "allocation_complete", object, {"event_data": event_data(value)})
	source_phase = site + ":" + edge
	var spec = SITES[site]
	write_record(spec.channel, site, edge, object, {"return_value": encode(value), "state": state(object, spec.state_schema)})
	if site == "Core/Buff.gd::gainTemporary":
		if active_buff_calls.empty():
			fail("SOURCE_BUFF_CONTEXT_UNBALANCED", site)
		else:
			active_buff_calls.pop_back()
	if site == "Core/Game.gd::combatEndDeferred":
		enabled = false
		source_mark_cleanup()


func middle(site, edge, object, values):
	if failed or closed:
		return
	begin_encoding()
	source_phase = site + ":" + edge
	if edge == "registration":
		if connection_ids.size() >= CAPS.native_ids or connection_ids.has(values.funcRefID):
			fail("CONNECTION_ID_CAP_COLLISION", site)
		else:
			connection_ids[values.funcRefID] = values.emissionID
	if edge in ["receiver_attempt", "receiver_return"]:
		if not connection_ids.has(values.funcRefID) or connection_ids[values.funcRefID] != values.emissionID:
			fail("UNREGISTERED_CALLBACK_ID", site)
	var payload = {}
	for key in values:
		if key in ["state", "buff", "timer", "entry"]:
			payload[key] = values[key]
		else:
			payload[key] = encode(values[key])
	var channel = "registration" if edge in ["registration", "receiver_attempt", "receiver_return"] else "allocation"
	if edge in ["mode_instant", "queue_snapshot", "queue_clear", "temporary_append", "temporary_remove"]:
		channel = "runtime"
	write_record(channel, site, edge, object, payload)

func timer_before(timer, operation, args, site):
	track_king_timer_api(timer, operation)
	if failed or closed or not source_fixture_bound:
		return
	if not ids.has(timer.get_instance_id()):
		# Foreign visual AutoHide calls stay in the complete UI authority stream.
		if site.begins_with("Utility/AutoHideParticles.gd::"):
			return
		fail("SOURCE_UNKNOWN_TIMER_API_OWNER", site)
		return
	if not SITES.has(site):
		fail("SOURCE_UNKNOWN_TIMER_API_SITE", site)
		return
	begin_encoding()
	source_phase = site + ":timer_before"
	var raw_args = []
	for arg in args:
		raw_args.append(encode(arg))
	write_record("runtime", site, "timer_before", timer, {"role": ids[timer.get_instance_id()], "operation": operation, "argc": args.size(), "args": raw_args, "public_before": timer_state(timer), "public_after": null})


func timer_after(timer, operation, args, site):
	if failed or closed or not source_fixture_bound:
		return
	if not ids.has(timer.get_instance_id()):
		if site.begins_with("Utility/AutoHideParticles.gd::"):
			return
		fail("SOURCE_UNKNOWN_TIMER_API_OWNER_AFTER", site)
		return
	if not SITES.has(site):
		fail("SOURCE_UNKNOWN_TIMER_API_SITE_AFTER", site)
		return
	begin_encoding()
	source_phase = site + ":timer_after"
	var raw_args = []
	for arg in args:
		raw_args.append(encode(arg))
	write_record("runtime", site, "timer_after", timer, {"role": ids[timer.get_instance_id()], "operation": operation, "argc": args.size(), "args": raw_args, "public_before": null, "public_after": timer_state(timer)})


func buff_name(buff_type):
	var game = get_node("/root/Game")
	for name in game.EventType:
		if game.EventType[name] == buff_type:
			return name
	fail("BUFF_TYPE", source_phase)
	return "INVALID"

func buff_label(character, item, buff_type, branch, index):
	return "buff:" + branch + ":" + side(character) + ":" + item_id(item) + ":" + buff_name(buff_type) + ":" + str(index)

func reflect_label(character, item, buff_type):
	return "reflect:" + side(character) + ":" + item_id(item) + ":" + buff_name(buff_type)

func stack_pick_label(item, target, operation, index):
	if target == null:
		target = item.character()
	return "random_stack:" + item_id(item) + ":" + side(target) + ":" + operation + ":" + str(index)

func most_buff_label(item):
	return "most_buff:" + item_id(item) + ":" + side(item.character())

func damage_label(character, item, damage_source):
	if item != null:
		return "damage:" + item_id(item)
	for pair in [[99, "fatigue"], [104, "spikes"], [108, "poison"]]:
		if damage_source.hasType(pair[0]):
			return pair[1] + ":" + side(character)
	return ""

func fraction_context(item, target, operation):
	if not enabled:
		return ""
	return "fraction_shuffle:" + item_id(item) + ":" + side(target) + ":" + operation

func context(label, kind):
	var result = {"operation": null, "item": null, "target": null, "ordinal": null, "width": null, "branch": null, "stack": null, "reflect_argument": null}
	var parts = label.split(":")
	if label.begins_with("fraction_shuffle:"):
		result.item = parts[1] + ":" + parts[2]
		result.target = parts[3]
		result.operation = parts[4]
		result.ordinal = int(parts[5])
		result.width = int(parts[6])
	elif label.begins_with("invulnerability_pitch:"):
		result.item = parts[1] + ":" + parts[2]
	elif label.begins_with("most_buff:"):
		result.item = parts[1] + ":" + parts[2]
		result.target = parts[3]
		result.operation = "most"
	elif label.begins_with("random_stack:"):
		result.item = parts[1] + ":" + parts[2]
		result.target = parts[3]
		result.operation = parts[4]
		result.ordinal = int(parts[5])
	elif label.begins_with("buff:"):
		result.branch = parts[1]
		result.target = parts[2]
		var is_null = parts[3] == "null"
		result.item = "null" if is_null else parts[3] + ":" + parts[4]
		result.stack = parts[4] if is_null else parts[5]
		result.ordinal = int(parts[5] if is_null else parts[6])
	elif label.begins_with("reflect:"):
		result.branch = "reflect"
		result.target = parts[1]
		result.item = "null" if parts[2] == "null" else parts[2] + ":" + parts[3]
		result.stack = parts[3] if parts[2] == "null" else parts[4]
	if result.branch in ["resist", "amplify", "reflect"]:
		if active_buff_calls.empty():
			fail("MISSING_BUFF_SOURCE_CONTEXT", source_phase)
		else:
			var current = active_buff_calls.back()
			if current.target != result.target or current.stack != result.stack:
				fail("BUFF_SOURCE_CONTEXT_MISMATCH", source_phase)
			result.reflect_argument = current.reflect
	return result

func primitive(site, kind, label, args, value):
	if enabled and label != "" and not failed and not closed:
		source_phase = site + ":return_native_primitive"
		begin_encoding()
		var raw_args = []
		for arg in args:
			raw_args.append(encode(arg))
		write_record("primitive", site, "return_native_primitive", null, {"kind": kind, "label": label, "args": raw_args, "value": encode(value), "context": context(label, kind)})
	return value

func cooldown(item, low, high):
	var value = get_node("/root/Util").rng.randf_range(low, high)
	primitive("Items/Item.gd::adjustCooldown:" + ("belowMasterOpponent" if low == 0.975 else "other"), "randf_range", "cooldown:" + item_id(item), [low, high], value)
	return value

func fraction_shuffle(values, label):
	if values.size() != 7:
		fail("FRACTION_FIXED7", source_phase)
		# Original unsupported route still executes once; it cannot be accepted.
		values.shuffle()
		return
	var ordinal = 0
	for i in range(6, 0, -1):
		var value = randi()
		primitive("fixed7fraction_shuffle", "global_u32", label + ":" + str(ordinal) + ":" + str(i + 1), [], value)
		var index = value % (i + 1)
		var previous = values[index]
		values[index] = values[i]
		values[i] = previous
		ordinal += 1

func export_data():
	return {"schema": "observer7-status/1", "failed": failed, "first_error": first_error, "records": sequence, "bytes": total_bytes, "files": file_sizes.duplicate(), "activation_checkpoints": activation_checkpoints, "metadata_ready": metadata_ready, "genuine_enabled": false, "capture_complete": false}

func scene_instance(descriptor, item, pooled):
	if failed or closed:
		return
	ui_bind_scene(descriptor, item, pooled)
	if descriptor.itemIndex == 262:
		timer_birth(item.get_node("BuffTimer"), item, "King.scene.instance")
	var id = native_id(item)
	var key = item.get_instance_id()
	if not source_lifetimes.has(key):
		source_lifetimes[key] = {"scene": 0, "ready": 0, "prepare": 0, "buff_init": 0, "pooled": false}
	source_lifetimes[key].scene += 1
	source_lifetimes[key].pooled = pooled
	if not source_fixture_window:
		return
	begin_encoding()
	var row = {"descriptor_id": native_id(descriptor), "item_id": id, "item_index": encode(descriptor.itemIndex), "pooled": pooled, "scene_path": descriptor.scene.resource_path, "particle": null}
	# This thin domain has no53/168 ParticleTimer; never invent a ready sample.
	if source_fixture_bound and not ids.has(key):
		var observation = {"schema": "observer7-record/1", "sequence": sequence, "channel": "lineage", "site": "Items/ItemDescriptor.gd::instantiate_pooled" if pooled else "Items/ItemDescriptor.gd::instantiate", "edge": "scene_instance", "subject": reference(item), "stamp": stamp(), "payload": row}
		sequence += 1
		source_write_diagnostic(observation)
	else:
		write_record("lineage", "Items/ItemDescriptor.gd::instantiate_pooled" if pooled else "Items/ItemDescriptor.gd::instantiate", "scene_instance", item, row)


func event_data(event):
	var result = {"native_id": native_id(event)}
	for key in ["id", "timestamp", "parentEvent", "origin", "target", "type", "params", "snapshot"]:
		result[key] = encode(event.get(key))
	return result

func metadata(descriptor_ids):
	if not metadata_ready or descriptor_ids.size() != CAPS.descriptors:
		return fail("METADATA_NOT_READY_OR_63", "loaded_descriptors")
	begin_encoding()
	var wanted = {}
	for id in descriptor_ids:
		if wanted.has(id):
			return fail("DUPLICATE_DESCRIPTOR_ID", "loaded_descriptors")
		wanted[id] = true
	var rows = []
	var found = {}
	var book = get_node("/root/ItemBook")
	for descriptor in book.items.values():
		if not wanted.has(descriptor.itemIndex):
			continue
		if found.has(descriptor.itemIndex):
			return fail("DUPLICATE_LOADED_DESCRIPTOR", "loaded_descriptors")
		found[descriptor.itemIndex] = true
		var row = {}
		for key in ["itemIndex", "identifier", "types", "tags", "gainedStacks", "removedStacks", "usedStacks", "hasBattleRageEffect", "descriptionKey"]:
			row[key] = descriptor.get(key)
		row.scene_path = descriptor.scene.resource_path
		rows.append(encode(row))
	if rows.size() != CAPS.descriptors:
		return fail("MISSING_LOADED_DESCRIPTOR", "loaded_descriptors")
	write_record("metadata", "Sheets/ItemBook.gd::detectMentionedStacks", "loaded_descriptors", book, {"descriptors": {"type": "array", "values": rows}, "locale": TranslationServer.get_locale()})
	for descriptor in book.items.values():
		if wanted.has(descriptor.itemIndex) and descriptor.hasBattleRageEffect:
			return fail("PRECONDITION_UNSUPPORTED_RAGE", "loaded_descriptors", descriptor.itemIndex)
	return not failed

func selected_lineage(items, characters):
	for character in characters:
		for buff in character.buffs.values():
			var id = buff.get_instance_id()
			if not source_lifetimes.has(id) or source_lifetimes[id].buff_init != 1:
				return fail("BUFF_LINEAGE_MISSING_REUSED", "selected_lineage")
	for item in items:
		var id = item.get_instance_id()
		if not source_lifetimes.has(id):
			return fail("ITEM_LINEAGE_MISSING", "selected_lineage")
		var life = source_lifetimes[id]
		if life.scene != 1 or life.ready != 1 or life.prepare != 0 or life.pooled:
			return fail("ITEM_LINEAGE_REUSED_OR_PREPARED", "selected_lineage")
	return not failed

func checkpoint(site, game, items):
	begin_encoding()
	var rows = []
	var nodes = []
	append_node(nodes, "root_viewport", get_tree().get_root())
	append_node(nodes, "game", game)
	append_node(nodes, "util", get_node("/root/Util"))
	append_node(nodes, "combat_timer", game.combatTimer)
	append_node(nodes, "fatigue:start", game.combatTimer.fatigueStartTimer)
	append_node(nodes, "fatigue:tick", game.combatTimer.fatigueTickTimer)
	for character in [game.PLAYER, game.OPPONENT]:
		var label = ids.get(character.get_instance_id(), "UNREGISTERED")
		append_node(nodes, "character:" + label, character)
		append_node(nodes, "tick:" + label, character.tickTimer)
		for name in ["battleRageTimer", "autoRageTimer", "invulnerabilityTimer"]:
			append_node(nodes, "invu:" + label if name == "invulnerabilityTimer" else "aux:" + label + ":" + name, character.get(name))
		for buff in character.buffs.values():
			append_node(nodes, "buff:" + label + ":" + str(buff.type), buff.timer)
	if items.size() > 128:
		fail("CHECKPOINT_ITEM_CAP", site)
		return
	for item in items:
		var schema = "carrot" if item.descriptor.itemIndex == 168 else ("goobert" if source_is(item, "res://Items/Goobert.gd") else "item")
		var fields = state(item, schema)
		var tween = item.movebackTween
		rows.append({"instance": ids.get(item.get_instance_id(), null), "fields": fields, "dragged": encode(item.dragged), "moveback_running": encode(is_instance_valid(tween) and tween.is_valid()), "cachedAffectedItems": encode(item.cachedAffectedItems), "currentAffectedItems": encode(item.currentAffectedItems)})
		append_node(nodes, "item:" + ids.get(item.get_instance_id(), "UNREGISTERED"), item)
		if item.descriptor.itemIndex in [53, 168]:
			append_node(nodes, "particle:" + ids.get(item.get_instance_id(), "UNREGISTERED"), item.particleTimer)
		if item.descriptor.itemIndex == 262:
			var label = ids.get(item.get_instance_id(), "UNREGISTERED")
			append_node(nodes, "king_buff:" + label, item.buffTimer)
			append_node(nodes, "king_hide:" + label, item.activationParticles.timer)
			append_node(nodes, "king_drag:" + label, item.get_node("Icon/SpecificDragParticles").timer)
	write_record("input", site, "checkpoint", game, {"environment": {"fps": encode(Engine.iterations_per_second), "scale": encode(Engine.time_scale), "paused": encode(get_tree().paused)}, "nodes": nodes, "items": rows, "source_resources": source_resources(game)})

func append_node(rows, role, node):
	if failed:
		return
	if rows.size() >= CAPS.sparse_nodes or not reserve_encoding(512):
		fail("SPARSE_NODE_CAP", source_phase)
		return
	rows.append({"role": role, "node": node_state(node), "timer": timer_state(node) if node is Timer else null})

# Pure runtime Script metadata, never load/preload or global gameplay class access.
func source_is(value, expected_path):
	if value == null or not is_instance_valid(value):
		return false
	var script = value.get_script()
	for _depth in range(16):
		if script == null:
			return false
		if script.resource_path == expected_path:
			return true
		script = script.get_base_script()
	fail("SCRIPT_CHAIN_DEPTH", source_phase)
	return false

func is_temporary(value):
	return value != null and is_instance_valid(value) and source_types.get(value.get_instance_id(), "") == "temporary"

#111 input-only clock and source birth ledger. No gameplay mutations or retained Objects.
var king_clock_active = false
var king_clock_closed = false
var king_clock_count = 0
var king_clock_bytes = 0
var king_input_bytes = 0
var king_clock_last_kind = ""
var king_clock_p = 0
var king_clock_i = 0
var king_timer_births = {}
var king_delayed = null
var king_input_facts = null

func timer_birth(timer, owner, kind):
	if failed or closed:
		return
	var key = timer.get_instance_id()
	if king_timer_births.has(key) or king_timer_births.size() >= CAPS.native_ids:
		fail("KING_TIMER_BIRTH_REUSED_OR_CAP", kind)
		return
	begin_encoding()
	king_timer_births[key] = {"timer_id": native_id(timer), "owner_id": native_id(owner), "kind": kind, "starts": 0, "stops": 0, "birth": timer_state(timer)}

func track_king_timer_api(timer, operation):
	var key = timer.get_instance_id()
	if king_timer_births.has(key):
		king_timer_births[key]["starts" if operation == "start" else "stops"] += 1

func capture_delayed(target, method, delay, timer):
	if method != "activateItems" or target != get_node_or_null("/root/Game"):
		return
	if king_delayed != null:
		fail("KING_ACTIVATION_SCHEDULE_REUSED", "Utility/Util.gd::callDelayed")
		return
	begin_encoding()
	king_delayed = {"target_id": native_id(target), "method": method, "delay": encode(delay), "tree_timer_id": native_id(timer), "source": "Utility/Util.gd::callDelayed", "physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames()}

func king_timer_fact(timer, owner, kind, mode):
	var key = timer.get_instance_id()
	if not king_timer_births.has(key):
		fail("KING_TIMER_BIRTH_MISSING", kind)
		return null
	var born = king_timer_births[key]
	if born.owner_id != str(owner.get_instance_id()) or born.kind != kind or born.starts != 0 or timer.autostart or timer.paused or not timer.one_shot or timer.process_mode != mode or timer.wait_time != 1.0 or not timer.is_stopped():
		fail("KING_TIMER_NOT_SOURCE_FRESH", kind)
		return null
	return {"lineage": born.duplicate(true), "current": timer_state(timer), "private_provenance": "source_constructor_minus_one_no_start_not_public_zero_inference"}

func auto_hide_state(particle):
	return {"node": node_state(particle), "visible": encode(particle.visible), "emitting": encode(particle.emitting), "one_shot": encode(particle.one_shot), "lifetime": encode(particle.lifetime), "explosiveness": encode(particle.explosiveness), "speed_scale": encode(particle.speed_scale), "timer": timer_state(particle.timer)}

func selected_king_facts(items, characters):
	begin_encoding()
	var result = {"schema": "phase355-king-input-facts/1", "root_viewport": node_state(get_tree().get_root()), "timers": {}, "kings": [], "delayed_activation": king_delayed}
	for character in characters:
		var label = ids.get(character.get_instance_id(), "UNREGISTERED")
		result.timers["invu:" + label] = king_timer_fact(character.invulnerabilityTimer, character, "Character.scene.ready", 0)
	for item in items:
		if item.descriptor.itemIndex != 262:
			continue
		if not source_is(item, "res://Items/Exclusive/KingGoobert.gd") or item.sockets.size() != 2 or not item.getGemsNoNull().empty() or item.has_method("getDataPersistent") or not item.paramMult.empty() or not item.paramAdd.empty() or item.doubleActivationChance != 0.0 or item.doubleAttackEffectChance != 0.0:
			fail("KING_UNSUPPORTED_SOCKET_MODIFIER_SOURCE", "selected_king_facts")
			return null
		var sockets = []
		for socket in item.sockets:
			if socket.getGem() != null:
				fail("KING_SOCKET_NOT_EMPTY", "selected_king_facts")
				return null
			sockets.append({"node": node_state(socket), "gem": encode(socket.getGem())})
		var label = ids.get(item.get_instance_id(), "UNREGISTERED")
		var buff = item.get_node("BuffTimer")
		var activation = item.get_node("ActivationParticles")
		var drag = item.get_node("Icon/SpecificDragParticles")
		for particle in [activation, drag]:
			if not source_is(particle, "res://Utility/AutoHideParticles.gd") or particle.visible or particle.emitting or particle.one_shot or float_bits(particle.lifetime) != "3fe6666660000000" or particle.explosiveness != 0.0 or particle.speed_scale != 1.0:
				fail("KING_PARTICLE_NOT_FRESH_DEFAULT", "selected_king_facts")
				return null
		result.timers["king_buff:" + label] = king_timer_fact(buff, item, "King.scene.instance", 0)
		result.timers["king_hide:" + label] = king_timer_fact(activation.timer, activation, "AutoHide.Timer.new", 1)
		result.timers["king_drag:" + label] = king_timer_fact(drag.timer, drag, "AutoHide.Timer.new", 1)
		result.kings.append({"instance": label, "node": node_state(item), "sockets": sockets, "gem_count": 0, "persistent": false, "paramMult": encode(item.paramMult), "paramAdd": encode(item.paramAdd), "doubleActivationChance": encode(item.doubleActivationChance), "doubleAttackEffectChance": encode(item.doubleAttackEffectChance), "activation": auto_hide_state(activation), "drag": auto_hide_state(drag)})
	if result.kings.size() != 1:
		fail("KING_FIXED_INSTANCE_COUNT", "selected_king_facts")
	return result

func write_king_json(name, data):
	if failed:
		return false
	var bytes = (JSON.print(data) + "\n").to_utf8()
	if bytes.size() > CAPS.record_bytes or total_bytes + king_input_bytes + bytes.size() > CAPS.total_bytes:
		return fail("KING_INPUT_BYTE_CAP", name)
	var file = File.new()
	if file.file_exists(OUT.plus_file(name)) or file.open(OUT.plus_file(name), File.WRITE) != OK:
		return fail("KING_INPUT_EXISTS_OR_OPEN", name)
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if ok:
		king_input_bytes += bytes.size()
	return ok if ok else fail("KING_INPUT_WRITE", name)

func begin_king_clock(game, items):
	if king_clock_active or king_clock_closed or king_delayed == null or king_delayed.target_id != str(game.get_instance_id()) or Engine.is_in_physics_frame() or Engine.iterations_per_second != 60 or Engine.time_scale != 1.0 or get_tree().paused:
		return fail("KING_CLOCK_ACTIVATION_DOMAIN", "Core/Game.gd::activateItems")
	king_input_facts = selected_king_facts(items, [game.PLAYER, game.OPPONENT])
	if failed:
		return false
	var util = get_node("/root/Util")
	king_clock_p = Engine.get_physics_frames()
	king_clock_i = Engine.get_idle_frames() + 1
	var checkpoint = {"schema": "phase105-exogenous-frame-clock/1", "lineage": "fresh_activate_idle_tail", "environment": {"physics_fps": Engine.iterations_per_second, "scale_bits": float_bits(Engine.time_scale), "paused": get_tree().paused}, "checkpoint": {"phase": "activate_items_idle_tail", "physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames(), "util_frame_counter": util.frameCounter, "util_time_bits": float_bits(util.time), "util_clock_time_bits": float_bits(util.clockTime)}}
	if not write_king_json("king-input-facts.json", king_input_facts) or not write_king_json("king-clock-checkpoint.json", checkpoint):
		return false
	king_clock_active = true
	return true

func clock_physics_signal():
	ui_check_controls()
	if king_clock_active:
		clock_pass("physics", get_physics_process_delta_time())

func clock_idle_signal():
	ui_check_controls()
	if king_clock_active:
		clock_pass("idle", get_process_delta_time())
		if source_cleanup != null and Engine.get_physics_frames() >= source_cleanup.physics_frame + 2:
			if Engine.get_physics_frames() != source_cleanup.physics_frame + 2:
				fail("SOURCE_MISSED_FIRST_IDLE_CUT", "clock_idle_signal")
				return
			if not close_king_clock():
				return
			if not write_king_json("king-final-source.json", source_runtime_snapshot()):
				return
			if not ui_close():
				return
			source_window_complete = not failed
			closed = true


func clock_pass(kind, delta):
	if failed or not king_clock_active or king_clock_closed:
		return
	if Engine.time_scale != 1.0 or get_tree().paused or Engine.iterations_per_second != 60 or delta <= 0 or is_nan(delta) or is_inf(delta) or king_clock_count >= 200000:
		fail("KING_CLOCK_DOMAIN_OR_CAP", "clock_pass")
		return
	if kind == "physics":
		king_clock_p += 1
	if Engine.get_physics_frames() != king_clock_p or Engine.get_idle_frames() != king_clock_i:
		fail("KING_CLOCK_COUNTER_ORDER", "clock_pass")
		return
	var row = {"kind": kind, "delta_bits": float_bits(delta), "physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames()}
	var bytes = (JSON.print(row) + "\n").to_utf8()
	if king_clock_bytes + bytes.size() > 67108864 or total_bytes + king_input_bytes + bytes.size() > CAPS.total_bytes:
		fail("KING_CLOCK_BYTE_CAP", "clock_pass")
		return
	var file = File.new()
	var path = OUT.plus_file("king-clock-passes.jsonl")
	if king_clock_count == 0 and file.file_exists(path):
		fail("KING_CLOCK_PREEXISTING", "clock_pass")
		return
	if file.open(path, File.READ_WRITE if king_clock_count > 0 else File.WRITE) != OK:
		fail("KING_CLOCK_OPEN", "clock_pass")
		return
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		fail("KING_CLOCK_WRITE", "clock_pass")
		return
	king_clock_count += 1
	king_clock_bytes += bytes.size()
	king_input_bytes += bytes.size()
	king_clock_last_kind = kind
	if kind == "idle":
		king_clock_i += 1

func close_king_clock():
	if not king_clock_active or king_clock_closed or king_clock_last_kind != "idle":
		return fail("KING_CLOCK_ENDPOINT", "finish_capture")
	king_clock_active = false
	king_clock_closed = true
	return write_king_json("king-capture-endpoint.json", {"schema": "phase111-fixed-endpoint/1", "phase": "idle_pre_internal_flush", "physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames(), "passes": king_clock_count, "two_future_physics_signals": 2, "fx_exact_comparison": "NOT_EVALUATED_REQUIRES_MODEL"})

func king_runtime_snapshot():
	begin_encoding()
	var game = get_node("/root/Game")
	var util = get_node("/root/Util")
	var timers = {}
	var particles = {}
	var nodes = []
	append_node(nodes, "root_viewport", get_tree().get_root())
	for character in [game.PLAYER, game.OPPONENT]:
		var label = ids.get(character.get_instance_id(), "UNREGISTERED")
		for name in ["tickTimer", "battleRageTimer", "autoRageTimer", "invulnerabilityTimer"]:
			timers[label + ":" + name] = timer_state(character.get(name))
		for buff in character.buffs.values():
			timers["buff:" + label + ":" + str(buff.type)] = timer_state(buff.timer)
		for item in character.INVENTORY.getItems():
			if item.descriptor.itemIndex != 262:
				continue
			var identity = ids.get(item.get_instance_id(), "UNREGISTERED")
			timers["king_buff:" + identity] = timer_state(item.buffTimer)
			particles[identity] = {"activation": auto_hide_state(item.activationParticles), "drag": auto_hide_state(item.get_node("Icon/SpecificDragParticles")), "light_visible": encode(item.light.visible), "light_modulate_rgba": encode([item.light.self_modulate.r, item.light.self_modulate.g, item.light.self_modulate.b, item.light.self_modulate.a])}
	timers["fatigue:start"] = timer_state(game.combatTimer.fatigueStartTimer)
	timers["fatigue:tick"] = timer_state(game.combatTimer.fatigueTickTimer)
	return {"nodes": nodes, "timers": timers, "particles": particles, "physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames(), "util_time": encode(util.time), "util_clockTime": encode(util.clockTime), "util_frameCounter": encode(util.frameCounter), "is_in_physics_frame": Engine.is_in_physics_frame(), "private_timer_values": "NOT_EXPOSED_SOURCE_FRESHNESS_AND_CLOCK_ONLY"}

#127 input-only source entry authority; no gameplay outcome or Timer sampling.
const UI_FILE = "king-ui-authority.jsonl"
const UI_SCHEMA = "phase355-king-ui-authority/1"
const UI_SITES = ["Items/Item.gd::respondToHover", "Items/Item.gd::respondToHoverEnd", "Items/Item.gd::_process:dragged", "Items/Item.gd::_process:rigid", "Items/Item.gd::activateDragParticles", "Items/Item.gd::deactivateDragParticles", "Items/Item.gd::onAddedToGridStorage", "Items/Item.gd::deactivateParticles", "Utility/AutoHideParticles.gd::activate", "Utility/AutoHideParticles.gd::deactivate", "Utility/AutoHideParticles.gd::startTimer", "Utility/AutoHideParticles.gd::instantClear"]
var ui_opened = false
var ui_closed = false
var ui_sequence = 0
var ui_bytes = 0
var ui_entries = 0
var ui_unsupported = 0
var ui_kings = {}
var ui_particles = {}
var ui_particle_owners = {}
var ui_ready_ids = {}
var ui_nonking_particles = {}
var ui_stack = []
var ui_root_id = ""

func ui_controls():
	var root = get_tree().get_root()
	return {"root_id": str(root.get_instance_id()), "disable_input": root.is_input_disabled(), "physics_object_picking": root.get_physics_object_picking(), "ordinary_physics": root.is_physics_processing(), "ordinary_idle": root.is_processing(), "internal_physics": root.is_physics_processing_internal(), "internal_idle": root.is_processing_internal()}

func ui_check_controls():
	if not ui_opened or ui_closed:
		return true
	var root = get_tree().get_root()
	if str(root.get_instance_id()) != ui_root_id or not root.is_input_disabled() or root.get_physics_object_picking():
		return fail("UI_CONTROL_CHANGED", "ui_check_controls")
	var game = get_node_or_null("/root/Game")
	if game != null and game.usingController:
		return fail("UI_CONTROLLER_CHANGED", "ui_check_controls")
	return true

func ui_write(kind, site, payload):
	if failed or ui_closed:
		return false
	if not ui_check_controls():
		return false
	if not ui_opened or ui_sequence >= 65536:
		return fail("UI_WINDOW_OR_RECORD_CAP", site)
	var row = {"schema": UI_SCHEMA, "sequence": ui_sequence, "kind": kind, "site": site, "physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames(), "in_physics": Engine.is_in_physics_frame(), "payload": payload}
	var bytes = (JSON.print(row) + "\n").to_utf8()
	if bytes.size() > 16384 or ui_bytes + bytes.size() > 8388608 or total_bytes + king_input_bytes + bytes.size() > CAPS.total_bytes:
		return fail("UI_BYTE_CAP", site)
	var file = File.new()
	var path = OUT.plus_file(UI_FILE)
	if ui_sequence == 0 and file.file_exists(path):
		return fail("UI_PREEXISTING", site)
	if file.open(path, File.READ_WRITE if ui_sequence > 0 else File.WRITE) != OK:
		return fail("UI_FILE_OPEN", site)
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		return fail("UI_FILE_WRITE", site)
	ui_sequence += 1
	ui_bytes += bytes.size()
	king_input_bytes += bytes.size()
	return true

func ui_open():
	if ui_opened or ui_closed:
		return fail("UI_REOPEN", "sink._ready")
	var before = ui_controls()
	var root = get_tree().get_root()
	root.set_disable_input(true)
	root.set_physics_object_picking(false)
	ui_root_id = str(root.get_instance_id())
	ui_opened = true
	return ui_write("open", "sink._ready", {"case": "KING-K1-A-353", "sites": UI_SITES, "before": before, "after": ui_controls(), "drop_mouse_setting": ProjectSettings.get_setting("gui/common/drop_mouse_on_gui_input_disabled"), "window": "before_selected_birth_to_final_preinternal", "limits": {"bytes": 8388608, "rows": 65536, "record": 16384}})

func ui_bind_scene(descriptor, item, pooled):
	if not ui_opened or ui_closed:
		return fail("UI_BIRTH_WINDOW", "scene_instance")
	if descriptor.itemIndex != 262:
		return true
	if descriptor.scene.resource_path != "res://Items/Exclusive/KingGoobert.tscn" or item.get_script().resource_path != "res://Items/Exclusive/KingGoobert.gd" or typeof(pooled) != TYPE_BOOL or item.is_inside_tree():
		return fail("UI_KING_SCENE_BINDING", "scene_instance")
	var activation = item.get_node("ActivationParticles")
	var drag = item.get_node("Icon/SpecificDragParticles")
	var id = str(item.get_instance_id())
	var aid = str(activation.get_instance_id())
	var did = str(drag.get_instance_id())
	if id == aid or id == did or aid == did or id == ui_root_id or aid == ui_root_id or did == ui_root_id:
		return fail("UI_BINDING_COLLISION", "scene_instance")
	var generation = 1
	if ui_kings.has(id):
		var previous = ui_kings[id]
		if not pooled or not previous.pooled or previous.activation != aid or previous.drag != did or previous.generation >= 65536:
			return fail("UI_POOLED_REUSE_IDENTITY", "scene_instance")
		generation = previous.generation + 1
	elif ui_particles.has(aid) or ui_particles.has(did) or ui_kings.size() >= 128:
		return fail("UI_BINDING_COLLISION", "scene_instance")
	if activation.get_script().resource_path != "res://Utility/AutoHideParticles.gd" or drag.get_script().resource_path != "res://Utility/AutoHideParticles.gd":
		return fail("UI_PARTICLE_SOURCE", "scene_instance")
	ui_kings[id] = {"activation": aid, "drag": did, "pooled": pooled, "generation": generation}
	ui_particles[aid] = "activation"
	ui_particles[did] = "drag"
	ui_particle_owners[aid] = id
	ui_particle_owners[did] = id
	return ui_write("bind", "scene_instance", {"item_id": id, "activation_id": aid, "drag_id": did, "script": item.get_script().resource_path, "scene": descriptor.scene.resource_path, "pooled": pooled, "inside_tree": item.is_inside_tree(), "generation": generation})

func ui_check_pooled_timer_reuse(timer, owner):
	var owner_id = str(owner.get_instance_id())
	var key = timer.get_instance_id()
	if not ui_kings.has(owner_id) or not ui_kings[owner_id].pooled or ui_kings[owner_id].generation <= 1 or not king_timer_births.has(key):
		return fail("KING_POOLED_TIMER_LINEAGE", "King.scene.instance")
	var born = king_timer_births[key]
	if born.timer_id != str(key) or born.owner_id != owner_id or born.kind != "King.scene.instance":
		return fail("KING_POOLED_TIMER_LINEAGE", "King.scene.instance")
	return true

func ui_ready(particle):
	var id = str(particle.get_instance_id())
	if ui_ready_ids.has(id) or ui_ready_ids.size() >= 8192:
		return fail("UI_READY_IDENTITY", "Utility/AutoHideParticles.gd::_ready")
	var ancestry = []
	var node = particle.get_parent()
	var king_ancestor = false
	while node != null:
		if ancestry.size() >= 32:
			return fail("UI_ANCESTRY_CAP", "Utility/AutoHideParticles.gd::_ready")
		var king = source_is(node, "res://Items/Exclusive/KingGoobert.gd")
		king_ancestor = king_ancestor or king
		ancestry.append({"native_id": str(node.get_instance_id()), "king_source": king})
		node = node.get_parent()
	if ancestry.empty() or ancestry.back().native_id != ui_root_id:
		return fail("UI_UNKNOWN_VIEWPORT", "Utility/AutoHideParticles.gd::_ready")
	if not king_ancestor:
		ui_nonking_particles[id] = true
	ui_ready_ids[id] = true
	return ui_write("ready", "Utility/AutoHideParticles.gd::_ready", {"receiver_id": id, "ancestry": ancestry, "script": particle.get_script().resource_path, "viewport_id": str(particle.get_viewport().get_instance_id())})

func ui_bind_roles(registry):
	var kings = []
	var guards = []
	for id in registry:
		var object = instance_from_id(id)
		if source_is(object, "res://Items/Item.gd"):
			guards.append({"item_id": str(id), "role": registry[id], "focus": object.focus, "hovered": object.hovered, "dragged": object.dragged, "mode": object.mode, "viewport_id": str(object.get_viewport().get_instance_id())})
		var key = str(id)
		if ui_kings.has(key):
			if ui_kings[key].pooled or ui_kings[key].generation != 1:
				return fail("UI_SELECTED_KING_NOT_FRESH", "configure")
			kings.append({"item_id": key, "role": registry[id]})
	return ui_write("roles", "configure", {"kings": kings, "selected_guards": guards, "using_controller": get_node("/root/Game").usingController})

func ui_entry(site, receiver, arguments):
	if not UI_SITES.has(site):
		return fail("UI_UNKNOWN_SITE", site)
	var id = str(receiver.get_instance_id())
	var king_source = source_is(receiver, "res://Items/Exclusive/KingGoobert.gd")
	var classification = "unsupported_item"
	if site.begins_with("Utility/"):
		classification = "unsupported_unbound"
		if ui_nonking_particles.has(id):
			classification = "supported_nonking_auto"
		elif ui_particles.has(id):
			if ui_kings[ui_particle_owners[id]].pooled:
				classification = "unsupported_nonselected_pooled_auto"
			elif ui_ready_ids.has(id):
				classification = "supported_activation" if ui_particles[id] == "activation" else "unsupported_drag"
	elif site in ["Items/Item.gd::activateDragParticles", "Items/Item.gd::deactivateDragParticles", "Items/Item.gd::onAddedToGridStorage", "Items/Item.gd::deactivateParticles"]:
		classification = ("unsupported_king_item" if ui_kings.has(id) else "unsupported_unbound_item") if king_source else "supported_nonking_item"
	var token = ui_sequence
	ui_stack.append({"token": token, "site": site, "receiver_id": id})
	ui_entries += 1
	if not classification.begins_with("supported_"):
		ui_unsupported += 1
	ui_write("entry", site, {"token": token, "receiver_id": id, "king_source": king_source, "arguments": arguments, "classification": classification, "source_phase": source_phase.substr(0, 256)})
	return token

func ui_leave(token, site, receiver):
	var row = {"token": token, "site": site, "receiver_id": str(receiver.get_instance_id())}
	if ui_stack.empty() or ui_stack.back().token != row.token or ui_stack.back().site != row.site or ui_stack.back().receiver_id != row.receiver_id:
		return fail("UI_CALL_STACK", site)
	ui_stack.pop_back()
	return ui_write("exit", site, {"token": token, "receiver_id": row.receiver_id})

func ui_close():
	if not king_clock_closed or Engine.is_in_physics_frame() or not active_buff_calls.empty() or not ui_stack.empty():
		return fail("UI_FINAL_SOURCE_BARRIER", "finish_capture")
	var ok = ui_write("close", "finish_capture", {"phase": "idle_pre_internal_flush", "completed": true, "failed": failed, "overflow": false, "dropped": 0, "entries": ui_entries, "unsupported": ui_unsupported, "rows_before_close": ui_sequence, "sites": UI_SITES, "controls": ui_controls(), "king_clock_closed": king_clock_closed, "active_buff_calls": active_buff_calls.size()})
	ui_closed = ok
	return ok

#148 one passive initial condition, not shared-stream consumption closure.
var rng_initial_count = 0
var rng_initial_util_id = ""
var rng_initial_rng_id = ""
const RNG_INITIAL_PROFILE = "7-king-single-A-355"
const RNG_INITIAL_FILE = "king-rng-checkpoint.json"
const RNG_INITIAL_PENDING = "user://king-rng-checkpoint.pending"

func rng_int64(value):
	var bytes = PoolByteArray()
	for shift in [56, 48, 40, 32, 24, 16, 8, 0]:
		bytes.append((value >> shift) & 255)
	return {"type": "int", "decimal": str(value), "int64_be": bytes.hex_encode()}

func rng_initial_capture(game):
	if rng_initial_count != 0 or not configured or not ui_opened or ui_closed:
		return fail("RNG_INITIAL_WINDOW", "prepareItems")
	var util148 = get_node_or_null("/root/Util")
	if game != get_node_or_null("/root/Game") or not source_is(game, "res://Core/Game.gd") or util148 == null or not source_is(util148, "res://Utility/Util.gd"):
		return fail("RNG_INITIAL_SOURCE", "prepareItems")
	var rng148 = util148.rng
	if not rng148 is RandomNumberGenerator or rng148.get_class() != "RandomNumberGenerator" or rng148.get_script() != null:
		return fail("RNG_INITIAL_CLASS", "prepareItems")
	var seed148 = rng148.get_seed()
	var state148 = rng148.get_state()
	if typeof(seed148) != TYPE_INT or typeof(state148) != TYPE_INT or typeof(util148.frameCounter) != TYPE_INT or typeof(util148.time) != TYPE_REAL or typeof(util148.clockTime) != TYPE_REAL:
		return fail("RNG_INITIAL_TYPES", "prepareItems")
	rng_initial_util_id = str(util148.get_instance_id())
	rng_initial_rng_id = str(rng148.get_instance_id())
	if util148 != get_node_or_null("/root/Util") or rng148 != util148.rng:
		return fail("RNG_INITIAL_IDENTITY", "prepareItems")
	rng_initial_count = 1
	var data148 = {"schema": "phase355-util-rng-checkpoint/1", "case": "KING-K1-A-353", "source_cut": "Core/Game.gd::prepareItems:enter.before_original_body", "source_profile": RNG_INITIAL_PROFILE, "snapshot_complete": true, "observed_count": 1, "checkpoint_sequence": sequence, "game_id": str(game.get_instance_id()), "util": {"native_id": rng_initial_util_id, "path": str(util148.get_path()), "class": util148.get_class(), "script": "res://Utility/Util.gd"}, "rng": {"native_id": rng_initial_rng_id, "class": rng148.get_class()}, "stamp": {"physics_frame": str(Engine.get_physics_frames()), "idle_frame": str(Engine.get_idle_frames()), "in_physics": Engine.is_in_physics_frame(), "util_frame_counter": str(util148.frameCounter), "util_time_bits": float_bits(util148.time), "util_clock_time_bits": float_bits(util148.clockTime)}, "current_seed": rng_int64(seed148), "state": rng_int64(state148)}
	return rng_initial_write(data148)

func rng_initial_continuity():
	var util148 = get_node_or_null("/root/Util")
	if rng_initial_count != 1 or util148 == null or str(util148.get_instance_id()) != rng_initial_util_id:
		return fail("RNG_INITIAL_UTIL_REPLACED", "activateItems")
	var rng148 = util148.rng
	if not rng148 is RandomNumberGenerator or str(rng148.get_instance_id()) != rng_initial_rng_id or rng148.get_script() != null:
		return fail("RNG_INITIAL_RNG_REPLACED", "activateItems")
	return true

func rng_initial_write(data148):
	var target148 = OUT.plus_file(RNG_INITIAL_FILE)
	var file148 = File.new()
	var directory148 = Directory.new()
	if file148.file_exists(target148) or file148.file_exists(RNG_INITIAL_PENDING) or directory148.dir_exists(target148) or directory148.dir_exists(RNG_INITIAL_PENDING):
		return fail("RNG_INITIAL_OCCUPIED", "prepareItems")
	if estimated_bytes(data148) > 16384:
		return fail("RNG_INITIAL_ALLOCATION", "prepareItems")
	var bytes148 = (JSON.print(data148) + "\n").to_utf8()
	if bytes148.size() > 16384 or total_bytes + king_input_bytes + bytes148.size() > CAPS.total_bytes:
		return fail("RNG_INITIAL_BYTE_CAP", "prepareItems")
	var status148 = file148.open(RNG_INITIAL_PENDING, File.WRITE)
	if status148 != OK:
		return fail("RNG_INITIAL_OPEN", "prepareItems", status148)
	file148.store_buffer(bytes148)
	file148.flush()
	var error148 = file148.get_error()
	file148.close()
	if error148 != OK:
		return fail("RNG_INITIAL_WRITE", "prepareItems", error148)
	if file148.file_exists(target148) or directory148.dir_exists(target148):
		return fail("RNG_INITIAL_OCCUPIED", "prepareItems")
	status148 = directory148.rename(RNG_INITIAL_PENDING, target148)
	if status148 != OK:
		return fail("RNG_INITIAL_RENAME", "prepareItems", status148)
	king_input_bytes += bytes148.size()
	return true

func begin_fixture_window(slot_table):
	if failed or closed or source_fixture_window or configured or not ui_opened:
		return fail("SOURCE_FIXTURE_WINDOW_ORDER", "begin_fixture_window")
	if not source_same_slot_value(slot_table, SOURCE_SLOT_TABLE):
		return fail("SOURCE_FIXED_SLOT_TABLE", "begin_fixture_window")
	source_fixture_window = true
	return true


func source_register(registry, object, role):
	if object == null or not is_instance_valid(object) or registry.has(object.get_instance_id()):
		return fail("SOURCE_ROLE_OBJECT_ALIAS", role)
	for old_role in registry.values():
		if old_role == role:
			return fail("SOURCE_ROLE_DUPLICATE", role)
	registry[object.get_instance_id()] = role
	return true


func bind_fixed_inventory(slot_table):
	if failed or closed or not source_fixture_window or source_fixture_bound or configured:
		return fail("SOURCE_BIND_ORDER", "bind_fixed_inventory")
	if not source_same_slot_value(slot_table, SOURCE_SLOT_TABLE):
		return fail("SOURCE_BIND_FIXED_TABLE", "bind_fixed_inventory")
	var game = get_node("/root/Game")
	var registry = {}
	var proof = []
	for side in ["P", "O"]:
		var character = game.PLAYER if side == "P" else game.OPPONENT
		if character.characterClass != 0 or not source_is(character, "res://Core/Character.gd"):
			return fail("SOURCE_CHARACTER_DOMAIN", side)
		if not source_register(registry, character, side):
			return false
		var inventory = character.INVENTORY
		var actual = inventory.getItems()
		var wanted = []
		for spec in SOURCE_SLOT_TABLE:
			if spec.side == side:
				wanted.append(spec)
		if actual.size() != wanted.size():
			return fail("SOURCE_INVENTORY_COUNT", side)
		var used = {}
		var encounter = []
		for item in actual:
			if not source_is(item, "res://Items/Item.gd") or item.inventory != inventory:
				return fail("SOURCE_FOREIGN_ITEM", side)
			var matches = []
			var top_left = item.getTopLeftCell()
			for spec in wanted:
				if item.descriptor.itemIndex == spec.item_index and top_left == Vector2(spec.x, spec.y) and item.faceDirection == spec.f:
					matches.append(spec)
			if matches.size() != 1:
				return fail("SOURCE_SLOT_GEOMETRY_AMBIGUOUS", side)
			var spec = matches[0]
			if used.has(spec.instance_id) or not item.placed or item.getGemsNoNull().size() != 0:
				return fail("SOURCE_SLOT_DUPLICATE_OR_GEMS", spec.instance_id)
			if item.occupiedCells.size() != spec.cells.size():
				return fail("SOURCE_OCCUPIED_SIZE", spec.instance_id)
			var cells = []
			for cell in item.occupiedCells:
				if cell.x != int(cell.x) or cell.y != int(cell.y) or not spec.cells.has([int(cell.x), int(cell.y)]) or cells.has([int(cell.x), int(cell.y)]):
					return fail("SOURCE_OCCUPIED_MEMBERS", spec.instance_id)
				cells.append([int(cell.x), int(cell.y)])
			if not source_register(registry, item, spec.instance_id):
				return false
			used[spec.instance_id] = true
			encounter.append(spec.instance_id)
			proof.append({"instance_id": spec.instance_id, "input_slot": spec.input_slot, "native_id": native_id(item), "descriptor_id": native_id(item.descriptor), "item_index": encode(item.descriptor.itemIndex), "top_left": {"x": encode(top_left.x), "y": encode(top_left.y)}, "orientation": encode(item.faceDirection), "occupiedCells": cells, "inventory_id": native_id(inventory), "character_id": native_id(character), "inventory_encounter_index": actual.find(item)})
		if used.size() != wanted.size():
			return fail("SOURCE_SLOT_MISSING", side)
		for name in ["tickTimer", "invulnerabilityTimer", "battleRageTimer", "autoRageTimer"]:
			var role = "tick:" + side if name == "tickTimer" else ("invu:" + side if name == "invulnerabilityTimer" else "aux:" + side + ":" + name)
			if not source_register(registry, character.get(name), role):
				return false
		for category in range(100, 111):
			if not source_register(registry, character.buffs[category].timer, "buff:" + side + ":" + str(category)):
				return false
	for pair in [[get_tree().get_root(), "root_viewport"], [game, "game"], [get_node("/root/Util"), "util"], [game.combatTimer, "combat_timer"], [game.combatTimer.fatigueStartTimer, "fatigue:start"], [game.combatTimer.fatigueTickTimer, "fatigue:tick"]]:
		if not source_register(registry, pair[0], pair[1]):
			return false
	for item in game.PLAYER.INVENTORY.getItems():
		if item.descriptor.itemIndex == 262:
			for pair in [[item.buffTimer, "king_buff:P:12"], [item.activationParticles.timer, "king_hide:P:12"], [item.get_node("Icon/SpecificDragParticles").timer, "king_drag:P:12"]]:
				if not source_register(registry, pair[0], pair[1]):
					return false
	if not configure(registry):
		return false
	source_fixture_bound = true
	source_binding_proof = {"schema": "phase359-source-slot-bindings/1", "source_slot_table": SOURCE_SLOT_TABLE, "actual_bindings": proof, "raw_early_rows_unchanged": true, "model_input_admitted": false, "remaining_interface": "NOT_IN_358_ELEVEN_CARRIER_SCHEMA"}
	if not write_king_json("king-slot-bindings.json", source_binding_proof):
		return false
	for row in source_buffer:
		var native = int(row.subject.native_id)
		if registry.has(native) and (registry[native].begins_with("P:") or registry[native].begins_with("O:")):
			if not source_write_row(row):
				return false
		else:
			# The early observation is retained as provenance, never silently dropped.
			if not source_write_diagnostic(row):
				return false
	source_buffer.clear()
	source_buffer_bytes = 0
	return metadata([1, 4, 11, 19, 22, 262])


func source_write_diagnostic(row):
	var bytes = (JSON.print(row) + "\n").to_utf8()
	var previous = file_sizes.get("unselected-source-lineage.jsonl", 0)
	if bytes.size() > CAPS.record_bytes or previous + bytes.size() > CAPS.file_bytes or total_bytes + king_input_bytes + bytes.size() > CAPS.total_bytes:
		return fail("SOURCE_DIAGNOSTIC_CAP", row.site)
	var file = File.new()
	var path = OUT.plus_file("unselected-source-lineage.jsonl")
	if file.open(path, File.READ_WRITE if file.file_exists(path) else File.WRITE) != OK:
		return fail("SOURCE_DIAGNOSTIC_OPEN", row.site)
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		return fail("SOURCE_DIAGNOSTIC_WRITE", row.site)
	file_sizes["unselected-source-lineage.jsonl"] = previous + bytes.size()
	total_bytes += bytes.size()
	return true


func source_write_row(row):
	if not CHANNEL_FILES.has(row.channel):
		return fail("SOURCE_UNKNOWN_CHANNEL", row.site)
	var bytes = (JSON.print(row) + "\n").to_utf8()
	var previous = file_sizes.get(CHANNEL_FILES[row.channel], 0)
	if bytes.size() > CAPS.record_bytes or previous + bytes.size() > CAPS.file_bytes or total_bytes + king_input_bytes + bytes.size() > CAPS.total_bytes:
		return fail("SOURCE_ROW_CAP", row.site)
	var file = File.new()
	var path = OUT.plus_file(CHANNEL_FILES[row.channel])
	if file.open(path, File.READ_WRITE if previous > 0 else File.WRITE) != OK:
		return fail("SOURCE_ROW_OPEN", row.site)
	file.seek_end()
	file.store_buffer(bytes)
	file.flush()
	var ok = file.get_error() == OK
	file.close()
	if not ok:
		return fail("SOURCE_ROW_WRITE", row.site)
	file_sizes[CHANNEL_FILES[row.channel]] = previous + bytes.size()
	total_bytes += bytes.size()
	return true


func source_observable(site, object):
	if site == "Items/Item.gd::_ready":
		return source_fixture_window and (not source_fixture_bound or ids.has(object.get_instance_id()))
	if not source_fixture_bound:
		return false
	if not SITES.has(site):
		if object != null and ids.has(object.get_instance_id()):
			fail("SOURCE_UNKNOWN_SELECTED_HOOK", site)
		return false
	if object != null and source_is(object, "res://Items/Item.gd"):
		return ids.has(object.get_instance_id())
	if source_is(object, "res://Utility/AutoHideParticles.gd"):
		return source_selected_auto(object)
	return true


func source_selected_auto(object):
	var id = str(object.get_instance_id())
	if not ui_particles.has(id):
		return false
	var owner = ui_particle_owners.get(id, "")
	return ui_kings.has(owner) and ui_kings[owner].pooled == false and ids.get(int(owner), "") == "P:12"


func source_resources(game):
	var result = []
	for character in [game.PLAYER, game.OPPONENT]:
		var rows = []
		for category in range(100, 111):
			rows.append({"stack": encode(category), "state": state(character.buffs[category], "buff")})
		result.append({"side": side(character), "native_id": native_id(character), "buffProtectStacks": encode(character.buffProtectStacks), "debuffReflectStacks": encode(character.debuffReflectStacks), "buffs": rows})
	return result


func source_mark_cleanup():
	if source_cleanup != null or not king_clock_active or failed:
		return fail("SOURCE_CLEANUP_ORDER", "Core/Game.gd::combatEndDeferred")
	source_cleanup = {"physics_frame": Engine.get_physics_frames(), "idle_frame": Engine.get_idle_frames(), "is_in_physics_frame": Engine.is_in_physics_frame()}
	return write_king_json("king-post-cleanup-source.json", source_runtime_snapshot())


func source_runtime_snapshot():
	var value = king_runtime_snapshot()
	var game = get_node("/root/Game")
	var chars = {}
	for side in ["P", "O"]:
		var character = game.PLAYER if side == "P" else game.OPPONENT
		chars[side] = {"invulnerable": encode(character.invulnerable), "invulnerabilityItem": encode(character.invulnerabilityItem), "invulBubbleVisible": encode(character.invulBubbleVisible), "buffProtectStacks": encode(character.buffProtectStacks)}
	var kings = {}
	for item in game.PLAYER.INVENTORY.getItems():
		if item.descriptor.itemIndex == 262:
			var id = str(item.get_instance_id())
			if not source_crowns.has(id):
				fail("SOURCE_CROWN_NOT_OBSERVED", "source_runtime_snapshot")
				return {}
			kings[ids[item.get_instance_id()]] = {"fields": state(item, "king"), "crown_last_observed_argument": encode(source_crowns[id]), "crown_origin": "ACTUAL_ON_STATE_CHANGED_ARGUMENT_NOT_NATIVE_STORED_GETTER"}
	value["characters_invu"] = chars
	value["king_source_state"] = kings
	value["cleanup_clock"] = source_cleanup
	value["partition"] = "EXPECTED_ONLY_NOT_MODEL_INPUT"
	return value


func source_completion_receipt():
	return {"source_window_complete": source_window_complete, "failed": failed, "clock_closed": king_clock_closed, "ui_closed": ui_closed, "cleanup": source_cleanup, "clock_passes": king_clock_count, "native_capture_accepted": false, "collector_archive_pending": true}

func source_same_slot_value(actual, expected):
	# Native JSON numbers are REAL; accepting exact integral values here is a
	# SOURCE fixture representation rule, never a cast of observed typed values.
	match typeof(expected):
		TYPE_ARRAY:
			if typeof(actual) != TYPE_ARRAY or actual.size() != expected.size():
				return false
			for index in range(expected.size()):
				if not source_same_slot_value(actual[index], expected[index]):
					return false
		TYPE_DICTIONARY:
			if typeof(actual) != TYPE_DICTIONARY or actual.size() != expected.size():
				return false
			for key in expected:
				if not actual.has(key) or not source_same_slot_value(actual[key], expected[key]):
					return false
		TYPE_INT:
			if (typeof(actual) != TYPE_INT and typeof(actual) != TYPE_REAL) or actual != expected:
				return false
		TYPE_STRING:
			if typeof(actual) != TYPE_STRING or actual != expected:
				return false
		_:
			return false
	return true


func shortbow_debuff_label(item):
	return "shortbow_debuff:" + item_id(item)

