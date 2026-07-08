from dataclasses import dataclass, field


class BattleItem:
    item_id = None
    item_key = None
    player_id = None
    is_active_item = False
    triggers = ()
    effects = ()
    linked_items = ()

    def __init__(
        self,
        item_id=None,
        item_key=None,
        player_id=None,
        is_active_item=None,
        triggers=None,
        effects=None,
        linked_items=None,
    ):
        self.item_id = type(self).item_id if item_id is None else item_id
        self.item_key = type(self).item_key if item_key is None else item_key
        self.player_id = type(self).player_id if player_id is None else player_id
        self.is_active_item = type(self).is_active_item if is_active_item is None else is_active_item
        self.triggers = list(self.triggers if triggers is None else triggers)
        self.effects = list(self.effects if effects is None else effects)
        self.linked_items = list(self.linked_items if linked_items is None else linked_items)
        self.triggered = False

        if not self.triggers:
            raise ValueError("battle item must have at least one trigger")
        if not self.effects:
            raise ValueError("battle item must have at least one effect")

    def update_triggers(self, context):
        raise NotImplementedError("concrete items must update their own triggers")

    def is_triggered(self):
        return bool(self.triggered)

    def run_effects(self, context):
        self.run_own_effects(context)
        self.run_linked_items(context)

    def run_own_effects(self, context):
        raise NotImplementedError("concrete items must run their own effects")

    def run_linked_items(self, context):
        for linked_key in list(self.linked_items):
            linked_item = context.owner.items[linked_key]
            linked_context = context.for_item(linked_item)
            linked_item.update_triggers(linked_context)

            if linked_item.is_triggered():
                linked_item.run_effects(linked_context)

    def add_linked_item(self, linked_key):
        if linked_key not in self.linked_items:
            self.linked_items.append(linked_key)


@dataclass
class PlayerState:
    player_id: object = None
    health: int = 0
    block: int = 0
    buffs: dict = field(default_factory=dict)
    debuffs: dict = field(default_factory=dict)
    items: dict = field(default_factory=dict)


@dataclass
class BattleContext:
    battle_state: object
    item: object
    owner: PlayerState
    opponent: PlayerState

    def for_item(self, item):
        if item.player_id == self.owner.player_id:
            return BattleContext(self.battle_state, item, self.owner, self.opponent)
        if item.player_id == self.opponent.player_id:
            return BattleContext(self.battle_state, item, self.opponent, self.owner)
        raise ValueError(f"item has unknown player_id: {item.player_id}")


@dataclass
class BattleState:
    frame: int = 0
    time: float = 0.0
    players: list = field(default_factory=list)
    active_items: list = field(default_factory=list)
    winner: object = None

    def step(self, frame_delta=1.0):
        for active_item in list(self.active_items):
            context = self.build_context(active_item)
            active_item.update_triggers(context)

            if active_item.is_triggered():
                active_item.run_effects(context)

        self.frame += 1
        self.time += frame_delta
        self.check_battle_end()
        return self.winner

    def run(self, max_frames, frame_delta=1.0):
        for _ in range(max_frames):
            if self.winner is not None:
                break
            self.step(frame_delta)
        return self.winner

    def check_battle_end(self):
        if len(self.players) < 2:
            return

        alive_players = [player for player in self.players if player.health > 0]
        if len(alive_players) == 1:
            self.winner = alive_players[0].player_id

    def build_context(self, item):
        owner = self.get_player(item.player_id)
        opponent = self.get_opponent(item.player_id)
        return BattleContext(self, item, owner, opponent)

    def get_player(self, player_id):
        for player in self.players:
            if player.player_id == player_id:
                return player
        raise ValueError(f"unknown player_id: {player_id}")

    def get_opponent(self, player_id):
        opponents = [player for player in self.players if player.player_id != player_id]
        if len(opponents) != 1:
            raise ValueError("battle context requires exactly one opponent")
        return opponents[0]


def evaluate_layout(placements, opponent):
    raise NotImplementedError(
        "layout scoring requires a backpack analyzer, concrete battle items, and score rules"
    )
