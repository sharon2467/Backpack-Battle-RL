"""Source-derived native StatHistory/CombatStatLogger recording, not event replay."""
from copy import deepcopy


class StatHistory:
    def __init__(self):
        self.event_numbers = []
        self.values = []

    def add_value(self, event_num, value):
        # Util.equals compares Variant typeof then equality (+0 == -0).
        if not self.values or type(self.values[-1]) is not type(value) or self.values[-1] != value:
            self.event_numbers.append(event_num)
            self.values.append(deepcopy(value))

    def add_acc(self, event_num, value):
        self.add_value(event_num, (self.values[-1] if self.values else 0) + value)

    def snapshot(self):
        return dict(event_numbers=deepcopy(self.event_numbers), values=deepcopy(self.values))


STACK_NAMES = ('block', 'lucky', 'regeneration', 'vampirism', 'spikes', 'mana',
               'empower', 'heat', 'poison', 'blind', 'cold')
NUM_METRICS = 80


class CombatHistories:
    def __init__(self, engine):
        self.engine = engine
        self.loggers = []
        self.item_metrics = {identity: [0] * NUM_METRICS for identity in engine.items}
        for side in ('P', 'O'):
            logger = dict(playerId=0 if side == 'P' else 1,
                          characterStatHistories={i: StatHistory() for i in range(22)},
                          stackHistories={i: StatHistory() for i in range(100, 111)},
                          itemTooltipHistories={}, itemMetricHistories={}, itemStateHistories={},
                          metricHistories=[{} for _ in range(NUM_METRICS)])
            logger['metricHistories'][0] = {i: StatHistory() for i in (99, 108, 104, 98)}
            for metric in (1, 2):
                logger['metricHistories'][metric] = {i: StatHistory() for i in (102, 103)}
            self.loggers.append(logger)
            for stat in range(22):
                logger['characterStatHistories'][stat].add_value(-1, float(self.character_stat(side, stat)))
            for stack in range(100, 111):
                logger['stackHistories'][stack].add_value(-1, self.stack_value(side, stack))
            for identity, item in engine.items.items():
                histories = [StatHistory() for _ in range(NUM_METRICS)]
                for history in histories:
                    history.add_value(-1, 0)
                logger['itemMetricHistories'][identity] = histories
                if item.side == side:
                    histories = [StatHistory() for _ in range(10)]
                    for stat, history in enumerate(histories):
                        history.add_value(-1, self.item_stat(item, stat))
                    logger['itemTooltipHistories'][identity] = histories
                    logger['itemStateHistories'][identity] = StatHistory()
            for table in logger['metricHistories']:
                for history in table.values():
                    history.add_acc(-1, 0)
        self.global_time = StatHistory()
        self.global_time.add_value(0.0, -1)  # Preserve CombatLog.onPrepare reversed arguments.

    def logger(self, side):
        return self.loggers[0 if side == 'P' else 1]

    def stack_value(self, side, stat):
        return getattr(self.engine.characters[side], STACK_NAMES[stat - 100], 0)

    def character_stat(self, side, stat):
        char = self.engine.characters[side]
        return {0: char.hp, 1: char.temporary_max_hp, 2: char.stamina,
                3: char.max_stamina + char.temporary_max_stamina,
                4: char.invulnerable, 5: char.stunned, 6: self.engine.is_battle_raging(side),
                7: char.debuff_reflect_stacks, 8: char.debuff_resist_stacks,
                9: char.crit_tokens, 10: char.dodge_stacks, 11: char.crit_resist_stacks,
                12: char.crit_resistance, 13: char.stun_resistance,
                14: (max(0.0, char.healing_efficiency) - 1) * 100,
                15: char.damage_resistance, 16: char.typed_damage_factors[0] * 100,
                17: char.typed_damage_factors[1] * 100, 18: char.typed_damage_factors[2] * 100,
                19: char.unhealing_amount * 100, 20: (char.stamina_regen - 1) * 100.0,
                21: (char.temporary_max_health_gain - 1.0) * 100}[stat]

    def item_stat(self, item, stat):
        char = self.engine.characters[item.side]
        if stat in (0, 1):
            key = 'min_damage' if stat == 0 else 'max_damage'
            return float(self.engine.damage_bounds(item)[stat]) if key in item.definition else 0
        if stat == 2:
            return float(item.definition.get('stamina', 0.0))
        if stat == 3:
            return self.engine.speed(item)
        if stat == 4:
            return float(item.definition.get('cooldown', 0.0))
        if stat == 5:
            return float(item.definition.get('accuracy', 0.0) + (char.lucky - char.blind) * 5)
        if stat == 6:
            return max(0.0, min(100.0, item.crit_chance))
        if stat in (7, 8):
            if item.item_index == 67:
                return 12.0 if stat == 7 else 3.0
            return float(item.definition.get('chance' if stat == 7 else 'chance2', 0.0))
        if stat == 9:
            if item.iteration_cooldown == 0:
                return -1
            progress = 1.0 - item.trigger_time / item.iteration_cooldown
            rate = self.engine.speed(item) / item.iteration_cooldown if item.cooldown_active and not self.engine.finalized else 0.0
            return (int(progress * 100000.0) << 32) + int(rate * 100000.0)
        raise ValueError('unknown item tooltip stat')

    def character(self, side, stat, next_event=False, event_num=None):
        self.logger(side)['characterStatHistories'][stat].add_value(
            self.engine.event_num + int(next_event) if event_num is None else event_num,
            float(self.character_stat(side, stat)))

    def item_state(self, item, value, next_event=False):
        self.logger(item.side)['itemStateHistories'][item.instance_id].add_value(
            self.engine.event_num + int(next_event), value)

    def stack(self, side, stat):
        self.logger(side)['stackHistories'][stat].add_value(self.engine.event_num, self.stack_value(side, stat))

    def tooltip(self, item, stat, event_num=None):
        self.logger(item.side)['itemTooltipHistories'][item.instance_id][stat].add_value(
            self.engine.event_num if event_num is None else event_num, self.item_stat(item, stat))

    def item_metric(self, item, metric, amount=1, side=None, next_event=False):
        values = self.item_metrics[item.instance_id]
        values[metric] += amount
        self.logger(side or item.side)['itemMetricHistories'][item.instance_id][metric].add_value(
            self.engine.event_num + int(next_event), values[metric])

    def metric(self, side, metric, origin, amount):
        # CombatStatLogger.logMetric's typed int parameter truncates real overheal.
        self.logger(side)['metricHistories'][metric][origin].add_acc(self.engine.event_num, int(amount))

    def snapshot(self):
        def freeze(value):
            if isinstance(value, StatHistory):
                return value.snapshot()
            if isinstance(value, dict):
                return {key: freeze(item) for key, item in value.items()}
            if isinstance(value, list):
                return [freeze(item) for item in value]
            return deepcopy(value)
        engine = self.engine
        active_stats = [[logger['characterStatHistories'][i].values[-1] for i in range(22)]
                        for logger in self.loggers] if engine.finalized else [[], []]
        return {
            'stat_loggers': freeze(self.loggers),
            'global': dict(eventNum=engine.event_num, timestamps=[event['timestamp'] for event in engine.events],
                           globalStatHistories=[self.global_time.snapshot()],
                           activeItemState={identity: history.values[-1] for logger in self.loggers
                                            for identity, history in logger['itemStateHistories'].items()
                                            if engine.finalized and len(history.values) > 1},
                           activeCharacterStats=active_stats,
                           itemsWithCooldown=[[item.instance_id for item in engine.side_items[side] if item.logs_cooldown]
                                              for side in ('P', 'O')],
                           electricalCharges=[], emitterEventToChargeInstance={}, numPlayerCharges=0)}
