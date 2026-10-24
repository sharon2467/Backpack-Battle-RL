"""Native capture-shaped independently computed rule state for the supported slice."""
from copy import deepcopy
from .histories import STACK_NAMES


EXCLUDED_CHARACTER_FIELDS = ('characterName', 'chibi')
EXCLUDED_ITEM_FIELDS = ()


def rng_state(rng=None):
    result = dict(expectedWins=0.0, wins=0, balancedness=3.0, lastResult=False,
                  extraLuck=0.0, lastTarget=0.0, accChance=0.0)
    if rng is not None:
        result.update(expectedWins=rng.expected_wins, wins=rng.wins,
                      balancedness=rng.balancedness, lastResult=rng.last_result)
    return result


def native_rule_state(engine):
    characters = []
    for side in ('P', 'O'):
        char = engine.characters[side]
        fields = dict(playerId=0 if side == 'P' else 1, characterClass=engine.fixture['sides'][0 if side == 'P' else 1]['character_class'],
                      isDead=char.dead, maxHealth=char.max_hp, curHealth=char.hp,
                      temporaryMaxHealth=char.temporary_max_hp, temporaryMaxHealthGain=char.temporary_max_health_gain,
                      baseMaxStamina=char.base_max_stamina, maxStamina=char.max_stamina,
                      curStamina=char.stamina, temporaryMaxStamina=char.temporary_max_stamina,
                      baseStaminaRegen=char.base_stamina_regen, staminaRegen=char.stamina_regen,
                      allowStaminaOverflow=char.allow_stamina_overflow, stunnedDuration=char.stunned,
                      invulnerable=char.invulnerable, unhealingAmount=char.unhealing_amount, healingEfficiency=char.healing_efficiency,
                      damageResistance=char.damage_resistance, damageReduction=char.damage_reduction, dodgeStacks=char.dodge_stacks,
                      critResistance=char.crit_resistance, critResistStacks=char.crit_resist_stacks, stunResistance=char.stun_resistance,
                      debuffResistStacks=char.debuff_resist_stacks,
                      debuffReflectStacks=char.debuff_reflect_stacks, buffProtectStacks=char.buff_protect_stacks,
                      critTokens=char.crit_tokens, battleRageBonusDur=char.battle_rage_bonus_duration, bonusFatigueDamage=char.bonus_fatigue_damage,
                      meleeSpikesLimit=char.melee_spikes_limit, rangedSpikesLimit=char.ranged_spikes_limit, effectSpikesLimit=char.effect_spikes_limit,
                      meleeVampirismLimit=char.melee_vampirism_limit, rangedVampirismLimit=char.ranged_vampirism_limit, empowerDamage=char.empower_damage,
                      typedDamageFactors=deepcopy(char.typed_damage_factors),
                      tickCounter=engine.tick_counter[side])
        if engine.king_mode:
            fields.update(invulnerabilityItem=engine.invu_origins[side],invulBubbleVisible=engine.invu_bubbles[side])
        stats = {i: engine.histories.character_stat(side, i) for i in range(22)}
        buffs = []
        for stack_id, name in enumerate(STACK_NAMES, 100):
            value = getattr(char, name, 0)
            buffs.append(dict(stack_type=stack_id,
                              fields=dict(type=stack_id, current=value, **project_buff_fields(char.buff_fields[stack_id]))))
        items = []
        for item in engine.side_items[side]:
            item_fields = dict(ownerType=1 if side == 'P' else 3, placed=True,
                               occupiedCells=[dict(x=float(x), y=float(y)) for x, y in item.ordered_cells],
                               faceDirection=item.orientation, consumed=item.consumed,
                               activationsThisFrame=item.activations_this_frame,
                               lastActivationTime=item.last_activation_time, lastTriggerTime=item.last_trigger_time, triggersThisFrame=item.triggers_this_frame,
                               triggerTime=item.trigger_time, iterationCooldown=item.iteration_cooldown,
                               baseCooldownOverride=float(item.definition.get('cooldown', 0.0)),
                               speedScale=item.speed_scale,
                               bonusMaxDam=float(item.bonus_damage + item.varying_damage + item.bonus_max_only),
                               bonusMinDam=float(item.bonus_damage + item.varying_damage), removableDam=float(item.bonus_damage),
                               bonusDamageFactor=1.0, staminaFactor=1.0,
                               critChancePercent=item.crit_chance, critTokens=0, critSeverity=2.0,
                               bonusChancePercent_mult=0.0, bonusChancePercent_additive1=0.0,
                               bonusChancePercent_additive2=0.0, bonusAccuracy=0.0,
                               buffPowers=deepcopy(item.buff_powers),
                               buffAmplificationChances=deepcopy(item.buff_amplification_chances),
                               doubleActivationChance=item.double_activation_chance,
                               doubleAttackEffectChance=item.double_attack_effect_chance,
                               paramMult={}, paramAdd={}, numCharges=0,
                               itemMetrics=deepcopy(engine.histories.item_metrics[item.instance_id]))
            if item.item_index in (23,38,52,53,54,74,168,169,204,205,219,220,262,296,340,400,401,416,468,469):
                item_fields.update(activations=item.goobert_activations,activationsToTrigger=float(item.definition['activations_to_trigger']))
                if item.item_index==262:
                    k=engine.king_states[item.instance_id]
                    item_fields.update(invuCharges=k['invuCharges'],protectedBuffs=k['protectedBuffs'],manaCost=k['manaCost'])
                if item.item_index==340:item_fields['numBuffs']=int(item.definition['most_buffs'])
                if item.item_index==469:
                    item_fields.update(vampirism=int(item.definition['vampirism']),regen=int(item.definition['regeneration']),
                                       stamina=float(item.definition['stamina_gain']),blind=int(item.definition['blind']),
                                       dambonus=float(item.definition['damage_each']))
                if item.item_index==53:item_fields['blindAmount']=float(item.definition['blind'])
                if item.item_index==54:item_fields.update(dam=float(item.definition['effect_damage']),vampirism=int(item.definition['vampirism']))
                if item.item_index==168:item_fields['empower']=float(item.definition['empower'])
                if item.item_index==52:item_fields['affectedWeapons']=list(item.steel_affected_weapons)
                if item.item_index==400:
                    item_fields.update(luck=item.definition['lucky_amount'],luckNeeded=item.definition['lucky_threshold'],regen=item.definition['regeneration'])
                if item.item_index==468:
                    item_fields.update(staminaThreshold=item.definition['stamina_threshold'],stamina=item.definition['stamina_gain'],regen=item.definition['regeneration'])
            if (engine.runtime_inputs.data['mode'] == 'synthetic' or engine.runtime_inputs.data['profile_id'] == 'observer7-298-headless-support68-layout/1'):
                # Source defaults; only the new finite genuine68 profile is added.
                if item.item_index == 62:
                    item_fields.update(reflects=int(item.definition['reflect_stacks']), heat=int(item.definition['heat']))
                elif item.item_index == 179:
                    item_fields.update(manaNeeded=int(item.definition['mana_cost']), cold=int(item.definition['cold']), spellSpeed=float(item.definition['spell_speed']))
                elif item.item_index == 332:
                    item_fields.update(buffFactor=float(item.definition['buff_factor']), buffLimit=int(item.definition['buff_limit']))
                elif item.item_index == 374:
                    item_fields.update(cleanses=int(item.definition['cleanse_count']), potionSpeed=float(item.definition['potion_speed']))
            if item.item_index == 129:item_fields['activated'] = item.rage_has_activated
            if item.definition.get('potion') and (item.item_index==172 and engine.runtime_inputs.data['mode']=='synthetic' or engine.runtime_inputs.data['profile_id'] in ('observer7-214-headless-potion-trigger-layout/1','observer7-218-headless-existing-weapon-layout/1','observer7-223-headless-start-collar-layout/1','observer7-228-headless-carrot-burning-layout/1','observer7-233-headless-mana-pair-layout/1','observer7-237-headless-basic-goobert-layout/1','observer7-247-headless-secondary-goobert-layout/1', 'observer7-270-headless-logic-random-goobert-layout/1', 'observer7-298-headless-support68-layout/1')):
                item_fields['isFull']=item.potion_full
            if item.item_index==3 and engine.runtime_inputs.data['profile_id'] in ('observer7-218-headless-existing-weapon-layout/1','observer7-223-headless-start-collar-layout/1','observer7-228-headless-carrot-burning-layout/1','observer7-233-headless-mana-pair-layout/1','observer7-237-headless-basic-goobert-layout/1','observer7-247-headless-secondary-goobert-layout/1', 'observer7-270-headless-logic-random-goobert-layout/1', 'observer7-298-headless-support68-layout/1'):
                item_fields['broomBonusDam']=item.broom_bonus_damage
            if item.item_index==39 and (engine.runtime_inputs.data['profile_id'] in ('observer7-223-headless-start-collar-layout/1','observer7-228-headless-carrot-burning-layout/1','observer7-233-headless-mana-pair-layout/1','observer7-237-headless-basic-goobert-layout/1','observer7-247-headless-secondary-goobert-layout/1', 'observer7-270-headless-logic-random-goobert-layout/1', 'observer7-298-headless-support68-layout/1') or engine.runtime_inputs.data['mode']=='synthetic'):
                item_fields['affectedItems']=[target.instance_id for target in engine.collar_targets[item.instance_id]] if item.instance_id in engine.collar_targets else None
            if item.item_index==209 and (engine.runtime_inputs.data['profile_id'] in ('observer7-228-headless-carrot-burning-layout/1','observer7-233-headless-mana-pair-layout/1','observer7-237-headless-basic-goobert-layout/1','observer7-247-headless-secondary-goobert-layout/1', 'observer7-270-headless-logic-random-goobert-layout/1', 'observer7-298-headless-support68-layout/1') or engine.runtime_inputs.data['mode']=='synthetic'):
                item_fields['permDamBonus']=1.0  # Source getP2()->float, frozen default CSV1; no modifier ingress.
            if item.item_index in (32,172) and (engine.runtime_inputs.data['profile_id'] in ('observer7-233-headless-mana-pair-layout/1','observer7-237-headless-basic-goobert-layout/1','observer7-247-headless-secondary-goobert-layout/1', 'observer7-270-headless-logic-random-goobert-layout/1', 'observer7-298-headless-support68-layout/1') or engine.runtime_inputs.data['mode']=='synthetic'):
                if item.item_index==32:
                    # Source immutable onready getP1/2/3()->float; closed defaults only.
                    item_fields.update(manaCost=float(item.definition['mana_cost']),tempDamBonus=float(item.definition['temporary_damage']),permDamBonus=float(item.definition['permanent_damage']))
                else:
                    item_fields['healthThreshold']=float(item.definition['health_threshold'])
            items.append(dict(instance=item.instance_id, fields=item_fields,
                              physics_processing=item.cooldown_active and not engine.finalized,
                              chance_rng=rng_state(item.chance_rng), damage_rng=dict(acc=item.damage_range.acc)))
        characters.append(dict(instance=side, fields=fields, stats=stats, buffs=buffs, items=items,
                               physics_processing=engine.activated and not engine.finalized,
                               balanced_rng=dict(accuracyRng=rng_state(char.accuracy), critRng=rng_state(char.critical),
                                                 critResistanceRng=rng_state(char.crit_resistance_rng), stunResistanceRng=rng_state(char.stun_resistance_rng))))
    return dict(characters=characters, rules=dict(customRulesActive=False,
                values={0: -1, 1: 0, 2: 0, 3: 100, 4: 0, 5: 0, 6: 0, 7: False, 8: 0}))


def project_native_rule_state(native):
    characters = deepcopy(native['characters'])
    for char in characters:
        for key in EXCLUDED_CHARACTER_FIELDS:
            del char['fields'][key]
        for item in char['items']:
            if 'observer7_fields' in item:
                extra = item.pop('observer7_fields')
                if type(extra) is not dict or set(extra) & set(item['fields']):
                    raise ValueError('observer7 item fields must be a disjoint dictionary')
                item['fields'].update(extra)
            for key in EXCLUDED_ITEM_FIELDS:
                del item['fields'][key]
    return dict(characters=characters, rules=native['rules'])


def restore_integer_table(table):
    result = {}
    for key, value in table.items():
        if type(key) is int:
            restored = key
        elif type(key) is str and key == str(int(key)):
            restored = int(key)
        else:
            raise ValueError("noncanonical serialized integer dictionary key")
        if restored in result:
            raise ValueError("duplicate serialized integer dictionary key")
        result[restored] = value
    return result


def restore_state_json_keys(state):
    state = deepcopy(state)
    def restore(table):
        return restore_integer_table(table)
    state['rules']['values'] = restore(state['rules']['values'])
    for char in state['characters']:
        char['stats'] = restore(char['stats'])
        char['fields']['typedDamageFactors'] = restore(char['fields']['typedDamageFactors'])
        for item in char['items']:
            for key in ('buffPowers', 'buffAmplificationChances'):
                item['fields'][key] = restore(item['fields'][key])
    return state


import json

def strict_json_loads(text):
    """Reject duplicate keys at every nesting before dict conversion."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON constant: ' + value)
    def real(text):
        value=float(text)
        import math
        if not math.isfinite(value):raise ValueError('nonfinite JSON number')
        return value
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid, parse_float=real)


def project_buff_fields(fields):
    result=deepcopy(fields)
    result['temporaryStacks']=[dict(amount=e.amount,timeout=e.timeout,item=e.item_id)for e in fields['temporaryStacks']]
    return result
