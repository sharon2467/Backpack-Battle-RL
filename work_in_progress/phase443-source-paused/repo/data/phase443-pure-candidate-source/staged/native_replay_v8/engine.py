"""Small independent implementation derived from migrated native GDScript 1.1.8.

Supported items are explicit; unsupported content raises rather than silently doing
nothing. Step scheduling is configurable because Godot's actual node/frame schedule
must be compared against captured evidence separately from mathematical rules.
"""
from copy import deepcopy
from dataclasses import asdict, dataclass, field, replace
import math
import struct
import hashlib
import re
from native_replay_v7.timer_runtime import TimerRuntime, TimerRecord, f32
import native_replay_v7.timer_runtime as timer_component
from native_replay_v7.frame_driver import FrameDriver, FramePass, decode_clock
from types import SimpleNamespace
from pathlib import Path

from .randomness import BalancedRange, BalancedRng, SeededRandom, TapeRandom
from .genuine import PURE441_PROFILE, PURE441_SCHEMA, PURE441_CONTRACT, validate_pure441_profile
from .histories import CombatHistories
from .state import native_rule_state


def model_source_hashes():
    files = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(Path(__file__).parent.glob("*.py"))}
    for name in ("__init__.py", "timer_runtime.py", "frame_driver.py"):
        files["component:" + name] = hashlib.sha256((Path(timer_component.__file__).parent / name).read_bytes()).hexdigest()
    return files


_MODEL_SOURCE_AT_IMPORT = model_source_hashes()


def assert_model_source_stable():
    current = model_source_hashes()
    if current != _MODEL_SOURCE_AT_IMPORT:
        raise ValueError("model_source_changed_since_import; restart in a stable source version")
    return dict(current)


CATALOG = {
    35: dict(name="Strong Health Potion",shape=((0,0),(0,1)),bag=False,potion=True,priority=1001,
             health_threshold=0.5,heal=24,cleanse_poison=4,regeneration=3.0,socket_count=0,default_gem=None),
    37: dict(name="Stone Skin Potion",shape=((0,0),(0,1)),bag=False,potion=True,
             block_threshold=45.0,health_cost=15.0,converted_block=30,socket_count=0,default_gem=None),
    46: dict(name="Strong Stone Skin Potion",shape=((0,0),(0,1)),bag=False,potion=True,
             block_threshold=45.0,health_cost=15.0,converted_block=35,spikes=2,duration=4.0,socket_count=0,default_gem=None),
    50: dict(name="Vampiric Armor",shape=((0,0),(1,0),(0,1),(1,1),(0,2),(1,2)),bag=False,armor=True,vampiric=True,
             cooldown=2.8,start_health=50.0,start_block=100,vampirism=5.0,health_cost=10.0,converted_block=20.0,
             socket_count=2,default_gem=None),
    29: {'name': 'Hero Sword', 'shape': ((0, 0), (0, 1)), 'stars': ((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (0, 2)), 'bag': False, 'metal': True, 'cooldown': 1.4, 'stamina': 0.7, 'accuracy': 90.0, 'min_damage': 2, 'max_damage': 4, 'socket_count': 1, 'default_gem': None, 'start_damage': 1.0},
    82: {'name': 'Hero Longsword', 'shape': ((0, 0), (0, 1), (0, 2)), 'stars': ((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (-1, 2), (1, 2), (0, 3)), 'bag': False, 'metal': True, 'cooldown': 1.6, 'stamina': 1.0, 'accuracy': 90.0, 'min_damage': 8, 'max_damage': 10, 'socket_count': 2, 'default_gem': None, 'start_damage': 3.0},
    83: {'name': 'Falcon Blade', 'shape': ((0, 0), (0, 1), (0, 2)), 'stars': ((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (-2, 2), (-1, 2), (1, 2), (2, 2), (0, 3)), 'bag': False, 'metal': True, 'cooldown': 1.7, 'stamina': 1.0, 'accuracy': 100.0, 'min_damage': 4, 'max_damage': 5, 'socket_count': 2, 'default_gem': None, 'start_speed': 0.4},
    84: {'name': 'Crossblades', 'shape': ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)), 'stars': ((1, -1),), 'bag': False, 'metal': True, 'cooldown': 1.4, 'stamina': 1.0, 'accuracy': 100.0, 'min_damage': 8, 'max_damage': 11, 'socket_count': 3, 'default_gem': None, 'secondary_stars': ((3, 1),), 'start_damage': 10.0, 'start_speed': 0.65, 'growth_damage': 1.0, 'growth_speed': 0.04},
    182: dict(name="Shortbow", shape=((0,0),(0,1)), bag=False, ranged=True, bow=True,
              cooldown=1.7, stamina=0.7, accuracy=85.0, min_damage=2, max_damage=3,
              socket_count=1, default_gem=None, params=(1.0,)),
    233: dict(name="Thorn Shortbow", shape=((0,0),(0,1)), bag=False, ranged=True, bow=True, nature=True,
              cooldown=1.7, stamina=0.7, accuracy=85.0, min_damage=2, max_damage=3, chance=50.0,
              socket_count=1, default_gem=None),
    234: dict(name="Lucky Shortbow", shape=((0,0),(0,1)), bag=False, ranged=True, bow=True, nature=True,
              cooldown=1.7, stamina=0.7, accuracy=100.0, min_damage=3, max_damage=4, chance=90.0,
              socket_count=1, default_gem=None),
    235: dict(name="Poison Shortbow", shape=((0,0),(0,1)), bag=False, ranged=True, bow=True, nature=True,
              cooldown=1.7, stamina=0.7, accuracy=85.0, min_damage=4, max_damage=11, chance=70.0, poison=2,
              socket_count=1, default_gem=None),
    129: dict(name="Berserker Bag", shape=((0,0),(1,0),(2,0),(0,1),(1,1),(2,1)),
              bag=True, battle_rage_starter=True, priority=1010, health_threshold=0.4999,
              rage_duration=5.5, rage_speed=0.35, damage_resistance=25.0),
    262: dict(name="King Goobert", shape=((0,0),(1,0),(0,1),(1,1),(0,2),(1,2)),
              stars=((-1,0),(2,0),(-1,1),(2,1),(-1,2),(2,2)), bag=False,pet=True,holy=True,magic=True,
              log_cooldown=True,activations_to_trigger=6,heal=35,protected_buffs=3.0,mana_cost=4.0,
              duration=1.5,charges=3.0,gem_power=50.0,socket_count=2,default_gem=None),
    204: {'socket_count': 0, 'default_gem': None, 'name': 'Cheese Goobert', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, 0), (2, 0), (-1, 1), (2, 1)), 'bag': False, 'pet': True, 'log_cooldown': True, 'activations_to_trigger': 5, 'nature': True, 'max_health': 22.0, 'random_buffs': 2.0},
    220: {'name': 'Rainbow Goobert Berserker', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2)), 'bag': False, 'pet': True, 'log_cooldown': True, 'activations_to_trigger': 9, 'nature': True, 'max_health': 40.0, 'random_buffs': 2.0, 'holy': True, 'vampiric': True, 'block': 20, 'vampirism': 2.0, 'blind': 3.0, 'damage_each': 4.0, 'socket_count': 0, 'default_gem': None},
    340: {'socket_count': 0, 'default_gem': None, 'name': 'Cupcake Goobert', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, 0), (2, 0), (-1, 1), (2, 1)), 'bag': False, 'pet': True, 'log_cooldown': True, 'activations_to_trigger': 6, 'magic': True, 'heal': 35, 'most_buffs': 2},
    416: {'name': 'Rainbow Goobert Mage', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2)), 'bag': False, 'pet': True, 'log_cooldown': True, 'activations_to_trigger': 9, 'holy': True, 'vampiric': True, 'block': 20, 'vampirism': 2.0, 'blind': 3.0, 'damage_each': 4.0, 'magic': True, 'heal': 40, 'most_buffs': 2.0, 'socket_count': 0, 'default_gem': None},
    74: {'name': 'Rainbow Goobert', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2)), 'bag': False, 'pet': True, 'holy': True, 'vampiric': True, 'log_cooldown': True, 'activations_to_trigger': 9, 'heal': 40, 'block': 20, 'vampirism': 2, 'blind': 3, 'damage_each': 4.0, 'nature': True, 'poison': 3, 'socket_count': 0, 'default_gem': None},
    169: {'name': 'Rainbow Goobert Ranger', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2)), 'bag': False, 'pet': True, 'holy': True, 'vampiric': True, 'log_cooldown': True, 'activations_to_trigger': 9, 'heal': 40, 'block': 20, 'vampirism': 2, 'blind': 3, 'damage_each': 4.0, 'nature': True, 'empower': 2, 'socket_count': 0, 'default_gem': None},
    219: {'name': 'Rainbow Goobert Pyromancer', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2)), 'bag': False, 'pet': True, 'holy': True, 'vampiric': True, 'log_cooldown': True, 'activations_to_trigger': 9, 'heal': 40, 'block': 20, 'vampirism': 2, 'blind': 3, 'damage_each': 4.0, 'nature': True, 'heat': 4, 'socket_count': 0, 'default_gem': None},
    401: {'name': 'Rainbow Goobert Adventurer', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2)), 'bag': False, 'pet': True, 'holy': True, 'vampiric': True, 'log_cooldown': True, 'activations_to_trigger': 9, 'heal': 40, 'block': 20, 'vampirism': 2, 'blind': 3, 'damage_each': 4.0, 'nature': True, 'regeneration': 2, 'socket_count': 0, 'default_gem': None},
    469: {'name': 'Rainbow Goobert Engineer', 'shape': ((0, 0), (1, 0), (0, 1), (1, 1)), 'stars': ((-1, -1), (0, -1), (1, -1), (2, -1), (-1, 0), (2, 0), (-1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2)), 'bag': False, 'pet': True, 'holy': True, 'vampiric': True, 'log_cooldown': True, 'activations_to_trigger': 9, 'heal': 40, 'block': 20, 'vampirism': 2, 'blind': 3, 'damage_each': 4.0, 'regeneration': 1, 'stamina_gain': 2.0, 'socket_count': 0, 'default_gem': None},
    53: dict(socket_count=0,default_gem=None,name="Light Goobert",shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,holy=True,log_cooldown=True,
             activations_to_trigger=6,heal=25,blind=7,duration=3.0,stars=((-1,0),(2,0),(-1,1),(2,1))),
    54: dict(socket_count=0,default_gem=None,name="Blood Goobert",shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,vampiric=True,lifesteal_tag=True,log_cooldown=True,
             activations_to_trigger=6,effect_damage=10.0,vampirism=5,lifesteal_factor=1.0,stars=((-1,0),(2,0),(-1,1),(2,1))),
    52: dict(socket_count=0,default_gem=None,name="Steel Goobert",shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,log_cooldown=True,
             activations_to_trigger=6,damage_each=2.0,block=16,stars=((-1,0),(2,0),(-1,1),(2,1)),
             secondary_stars=((0,-1),(1,-1),(0,2),(1,2))),
    400: dict(socket_count=0,default_gem=None,name="Broccoli Goobert",shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,nature=True,log_cooldown=True,
              activations_to_trigger=6,lucky_amount=3,lucky_threshold=5,regeneration=3,stars=((-1,0),(2,0),(-1,1),(2,1))),
    468: dict(socket_count=0,default_gem=None,name="Toast Goobert",shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,log_cooldown=True,
              activations_to_trigger=6,stamina_threshold=2.5,stamina_gain=1.7,regeneration=3,stars=((-1,0),(2,0),(-1,1),(2,1))),
    38: dict(name="Poison Goobert", shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,nature=True,log_cooldown=True,
             activations_to_trigger=5,heal=10,poison=4,socket_count=0,default_gem=None,stars=((-1,0),(2,0),(-1,1),(2,1))),
    205: dict(name="Chili Goobert", shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,nature=True,log_cooldown=True,
              activations_to_trigger=6,heal=16,heat=2,socket_count=0,default_gem=None,stars=((-1,0),(2,0),(-1,1),(2,1))),
    296: dict(name="Goobling",shape=((0,0),),bag=False,pet=True,log_cooldown=True,
              activations_to_trigger=3,heal=4,socket_count=0,default_gem=None,stars=((-1,0),(1,0))),
    168: dict(socket_count=0,default_gem=None,name="Carrot Goobert",shape=((0,0),(1,0),(0,1),(1,1)),bag=False,pet=True,log_cooldown=True,
              activations_to_trigger=6,empower=2,duration=8.0,stars=((-1,0),(2,0),(-1,1),(2,1))),
    332: dict(socket_count=0,default_gem=None,name="Magic Mirror", shape=((0, 0), (0, 1)), bag=False,
              spell=True, holy=True, ice=True, magic=True, cooldown=6.0,
              chance=20.0, chance2=2.0, buff_factor=0.2, buff_limit=20,
              stars=((3, -2), (2, -1), (1, 0), (2, 1), (3, 2))),
    351: dict(socket_count=0,default_gem=None,name="Shepherds Crook", shape=((0, 0), (1, 0), (0, 1), (0, 2), (0, 3)),
              bag=False, chance=35.0, chance2=50.0, bonus_damage=2.0,
              stars=((1, 1), (1, 2), (1, 3), (0, 4), (1, 4))),
    374: dict(socket_count=0,default_gem=None,nature=True,name="Shelly", shape=((0, 0), (1, 0)), bag=False, pet=True, holy=True,
              cooldown=13.0, chance=25.0, cleanse_count=6, heal=40, potion_speed=0.2, priority=1000,
              stars=((-1, 1), (0, 1), (1, 1), (2, 1))),
    405: dict(name="Puzzlebag S", shape=((1, 0), (2, 0), (0, 1), (1, 1)), bag=True,
              bag_layer=1, chance=20.0),
    124: dict(name="Carrot", shape=((0, 0), (1, 0)), bag=False, food=True,
              cooldown=2.7, chance=55.0, lucky_threshold=4, empower=1,socket_count=0,default_gem=None,
              stars=((0, -1), (1, -1), (-1, 0), (2, 0), (0, 1), (1, 1))),
    117: dict(name="Chili Pepper", shape=((0, 0), (0, 1)), bag=False, food=True,
              cooldown=4.5, heat=1, heal=5, heat_threshold=10,
              stars=((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (0, 2))),
    14: dict(name="Spear", shape=((0, 0), (0, 1), (0, 2), (0, 3)), bag=False,
             cooldown=1.5, stamina=1.0, accuracy=85.0, min_damage=3, max_damage=8,
             block_per_empty_cell=4,
             stars=((0, -5), (0, -4), (0, -3), (0, -2), (0, -1))),
    27: dict(name="Thorn Whip", shape=((0, 0), (1, 0), (1, 1), (1, 2), (2, 2)), bag=False,
             cooldown=2.2, stamina=2.2, accuracy=80.0, min_damage=4, max_damage=9,nature=True,socket_count=2,default_gem=None),
    28: dict(name="Hungry Blade", shape=((0, 0), (0, 1), (0, 2)), bag=False,
             cooldown=1.6, stamina=1.0, accuracy=90.0, min_damage=3, max_damage=6,vampiric=True,socket_count=1,default_gem=None),
    36: dict(name="Pestilence Flask", shape=((0, 0), (0, 1)), bag=False, potion=True),
    3: dict(name="Broom", shape=((0, 0), (0, 1), (0, 2), (0, 3)), bag=False,
            cooldown=1.7, stamina=1.2, accuracy=95.0, min_damage=2, max_damage=4, chance=33.0,socket_count=1,default_gem=None),
    12: dict(name="Hammer", shape=((0, 0), (1, 0), (2, 0), (1, 1), (1, 2)), bag=False,
             cooldown=2.0, stamina=3.0, accuracy=75.0, min_damage=10, max_damage=13, chance=45.0,socket_count=2,default_gem=None),
    19: dict(name="Health Potion", shape=((0, 0), (0, 1)), bag=False, potion=True, priority=1000),
    172: dict(name="Mana Potion", shape=((0, 0), (0, 1)), bag=False, potion=True,
              health_threshold=0.5 - 0.0001, mana=4, max_health=18,socket_count=0,default_gem=None),
    32: dict(name="Magic Staff", shape=((0, 0), (0, 1), (0, 2), (0, 3)), bag=False, ranged=True,
             cooldown=1.8, stamina=1.0, accuracy=90.0, min_damage=6, max_damage=8,
             mana_cost=3, temporary_damage=6, permanent_damage=2,socket_count=1,default_gem=None),
    34: dict(name="Leather Boots", shape=((0, 0), (0, 1)), bag=False, priority=1002,
             health_threshold=0.7 - 0.0001, lucky=1, empower=1, block=15,socket_count=1,default_gem=None),
    62: dict(socket_count=0,default_gem=None,name="Ruby Egg", shape=((0, 0), (1, 0), (0, 1), (1, 1)), bag=False,
             pet=True, fire=True, reflect_stacks=3, heat=4),
    179: dict(socket_count=0,default_gem=None,magic=True,name="Book of Ice", shape=((0, 0), (0, 1)), bag=False, book=True, ice=True,
              cooldown=2.8, mana_cost=1, cold=2, spell_speed=0.1,
              stars=((-2, -1), (0, -1), (2, -1), (-1, 0), (1, 0),
                     (-1, 1), (1, 1), (-2, 2), (0, 2), (2, 2))),
    208: dict(name="Torch", shape=((0, 0), (0, 1)), bag=False,
              cooldown=1.4, stamina=1.0, accuracy=90.0, min_damage=2, max_damage=3, chance=25.0),
    209: dict(name="Burning Torch", shape=((0, 0), (0, 1)), bag=False,
              cooldown=1.4, stamina=1.0, accuracy=90.0, min_damage=2, max_damage=3, chance=30.0,socket_count=1,default_gem=None),
    4: dict(name="Wooden Buckler", shape=((0, 0), (1, 0), (0, 1), (1, 1)), bag=False,
            chance=30.0, shield=True, damage_block=7.0),
    16: dict(name="Spiked Shield", shape=((0, 0), (1, 0), (0, 1), (1, 1)), bag=False,
             chance=30.0, shield=True, damage_block=9.0),
    6: dict(name="Garlic", shape=((0, 0), (0, 1)), bag=False, food=True, cooldown=4.0,
            chance=30.0, stars=((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (0, 2))),
    21: dict(name="Fly Agaric", shape=((0, 0), (0, 1)), bag=False, food=True,
             cooldown=3.5, poison=1,
             stars=((0, -1), (-1, 0), (1, 0), (-1, 1), (1, 1), (0, 2))),
    23: dict(name="Goobert",socket_count=0,default_gem=None, shape=((0, 0), (1, 0), (0, 1), (1, 1)), bag=False,
             pet=True, log_cooldown=True, activations_to_trigger=5, heal=9,
             stars=((-1, 0), (2, 0), (-1, 1), (2, 1))),
    26: dict(name="Fanny Pack", shape=((0, 0), (1, 0)), bag=True, bag_speed=0.1),
    39: dict(name="Acorn Collar", shape=((0, 0),), bag=False, chance=5.0,
             crit_per_lucky=5.0, can_activate=False, socket_count=0, default_gem=None,
             stars=((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0),
                    (-1, 1), (0, 1), (1, 1))),
    15: dict(name="Dagger", shape=((0, 0), (0, 1)), bag=False, cooldown=3.5,
             stamina=0.0, accuracy=95.0, min_damage=2, max_damage=5),
    30: dict(name="Poison Dagger", shape=((0, 0), (0, 1)), bag=False, cooldown=1.9,
             stamina=0.0, accuracy=95.0, min_damage=5, max_damage=7),
    0: dict(name="Stone", shape=((0, 0),), bag=False, ranged=True,
            cooldown=2.5, stamina=0.0, accuracy=70.0, min_damage=2, max_damage=4),
    2: dict(name="Pan", shape=((1, 0), (0, 1), (1, 1)), bag=False,
            cooldown=2.2, stamina=2.0, accuracy=85.0, min_damage=5, max_damage=6,
            stars=((1, -1), (0, 0), (2, 0), (-1, 1), (2, 1), (0, 2), (1, 2))),
    17: dict(name="Leather Armor", shape=((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)), bag=False,armor=True,socket_count=2,default_gem=None),
    18: dict(name="Gloves of Haste", shape=((0, 0), (1, 0)), bag=False, stars=((-1, 0), (2, 0)),socket_count=0,default_gem=None),
    48: dict(name="Blood Amulet", shape=((0, 0),), bag=False, socket_count=0, default_gem=None),
    1: dict(name="Wooden Sword", shape=((0, 0), (0, 1)), bag=False,
            cooldown=1.4, stamina=1.0, accuracy=90.0, min_damage=1, max_damage=3),
    5: dict(name="Banana", shape=((0, 0), (0, 1), (1, 1)), bag=False, food=True,
            cooldown=5.0, stars=((0, -1), (-1, 0), (1, 0), (-1, 1), (2, 1), (0, 2), (1, 2))),
    7: dict(name="Healing Herbs", shape=((0, 0),), bag=False, socket_count=0, default_gem=None),
    8: dict(name="Walrus Tusk", shape=((0, 0), (0, 1)), bag=False, socket_count=0, default_gem=None),
    10: dict(name="Whetstone", shape=((0, 0),), bag=False, stars=((0, -1), (0, 1))),
    11: dict(name="Leather Bag", shape=((0, 0), (1, 0), (0, 1), (1, 1)), bag=True),
    24: dict(name="Lucky Clover", shape=((0, 0),), bag=False),
    20: dict(name="Pocket Sand", shape=((0, 0),), bag=False, socket_count=0, default_gem=None),
    22: dict(name="Blueberries", shape=((0, 0),), bag=False, food=True,
             cooldown=3.5, stars=((0, -1), (-1, 0), (1, 0), (0, 1))),
    67: dict(name="Ranger Bag", shape=((0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)), bag=True),
}
RAINBOW_GOOBERT_IDS = frozenset({74,169,219,401,469})
BUFF_GOOBERT_IDS = frozenset({204,220,340,416})
GOOBERT_IDS = frozenset({262,23,38,52,53,54,168,205,296,400,468}) | RAINBOW_GOOBERT_IDS | BUFF_GOOBERT_IDS
STATE_PARTICLE_IDS = frozenset({53,168})
POTION_IDS = frozenset({19,35,36,37,46,172})
CACHED_AFFECTED_IDS = GOOBERT_IDS | POTION_IDS | frozenset({5,6,21,22,117,124}) | frozenset({18,29,82,83,84,179,332,351,374})
EMPOWERABLE_WEAPON_IDS = frozenset([29, 82, 83, 84, 182, 233, 234, 235, 0, 1, 2, 3, 12, 14, 15, 27, 28, 30, 32, 208, 209])

EVENT_TYPES = {"LoseHealth": 5, "Activation": 0, "DealDamage": 1, "CriticalDamage": 2,
               "MissedAttack": 3, "InvulnerableStart": 7, "InvulnerableEnd": 8, "Health": 12, "Stamina": 13,
               "DrainStamina": 14, "OutofStamina": 15, "Lucky": 101, "Regeneration": 102,
               "Block": 100, "Vampirism": 103, "Spikes": 104, "Mana": 105, "Blind": 109,
               "TemporaryMaxHealth": 19, "Empower": 106, "Poison": 108, "Heat": 107, "Cold": 110, "Stun": 9,
               "BattleRageStart": 21, "BattleRageEnd": 22, "Win": 111, "Loss": 112}
DEBUFF_TYPES = ("Blind", "Poison", "Cold")
GAINED_STACK_FLAGS = {35:4,37:0,46:16,50:8,29:0,82:0,83:0,84:0,182:0,233:16,234:2,235:1792,129:0,262:0,204:254,220:254,340:254,416:766,74:776,169:584,219:648,401:524,469:524,53:512,54:8,52:0,400:6,468:4,38:256,205:128,296:0,168: 64, 0: 0, 1: 0, 2: 0, 3: 512, 4: 0, 5: 0, 6: 0, 7: 4, 8: 16, 10: 0, 11: 0, 12: 0, 14: 0, 15: 0, 16: 16, 17: 0, 18: 0, 19: 0, 20: 512, 21: 256, 22: 34, 23: 0, 24: 2, 26: 0, 27: 16, 28: 8, 30: 256, 32: 0, 34: 66, 36: 256, 39: 0, 48: 8, 62: 128, 67: 0, 117: 128, 124: 64, 172: 32, 179: 1024, 208: 0, 209: 128, 332: 254, 351: 0, 374: 0, 405: 0}
STACK_NAMES_BY_TYPE = {value: name for name, value in EVENT_TYPES.items() if 100 <= value <= 110}


def fresh_buff_fields():
    return {key: dict(permanentStacks=0, resistChancePercent=0.0, resistStacks=0,
                      reflectChancePercent=0.0, cleanseProtectionChancePercent=0.0,
                      temporaryStacks=[], nextTemporaryTimeout=0) for key in range(100, 111)}
# The shipped Godot build passes real_t(float32) physics delta into GDScript.
# Native probe-003 timestamp 1.450000075623393 == 87 * this value.
NATIVE_PHYSICS_DELTA = struct.unpack("f", struct.pack("f", 1.0 / 60.0))[0]


def starter_fixture():
    items = [dict(item_index=index, x=x, y=y, f=0) for index, x, y in
             ((67, 3, 2), (11, 5, 3), (11, 1, 3), (24, 4, 4), (1, 3, 3))]
    sides = []
    for side in ("P", "O"):
        entries = [dict(item, instance_id=f"{side}:{slot}") for slot, item in enumerate(items)]
        sides.append(dict(side=side, character_class=0, hp=25.0, stamina=5.0, items=entries))
    return dict(schema=1, game_version="1.1.8", mode="Unranked", round=1,
                below_master=True, rules="default", sides=sides)


def transformed_cells(entry, layer="shape"):
    if layer == "stars" and CATALOG[entry["item_index"]].get("potion"):
        # Potion keeps its connector above the selected rotated endpoint.
        points = ordered_occupied_cells(entry)
        x, y = points[1 if entry.get("f", 0) == 2 else 0]
        return {(x, y - 1)}
    points = list(CATALOG[entry["item_index"]]["shape"])
    selected = list(CATALOG[entry["item_index"]].get(layer, ()))
    for _ in range(entry.get("f", 0)):
        points = [(-y, x) for x, y in points]
        selected = [(-y, x) for x, y in selected]
    minimum_x, minimum_y = min(x for x, _ in points), min(y for _, y in points)
    return {(x - minimum_x + entry["x"], y - minimum_y + entry["y"]) for x, y in selected}


def ordered_occupied_cells(entry):
    points = list(CATALOG[entry["item_index"]]["shape"])
    for _ in range(entry["f"]):
        points = [(-y, x) for x, y in points]
    minimum_x, minimum_y = min(x for x, _ in points), min(y for _, y in points)
    return [(x - minimum_x + entry["x"], y - minimum_y + entry["y"]) for x, y in points]


def occupied_cells(entry):
    return set(ordered_occupied_cells(entry))


def _fixture_from_custom_side(data):
    if not isinstance(data, dict):
        raise ValueError("native custom-opponent root must be an object")
    if set(data) != {"schema_version", "game_version", "class", "health", "stamina", "items"}:
        raise ValueError("native custom-opponent fields must match schema exactly")
    def native_integer(value, name, low, high):
        if (type(value) not in (int, float) or not math.isfinite(value)
                or not low <= value <= high or value != int(value)):
            raise ValueError(f"native custom-opponent {name} must be an integer in [{low},{high}]")
        return int(value)
    native_integer(data["schema_version"], "schema_version", 1, 1)
    if data["game_version"] != "1.1.8":
        raise ValueError("expected native game1.1.8")
    character_class = native_integer(data["class"], "class", 0, 6)
    hp = native_integer(data["health"], "health", 1, 999)
    stamina = native_integer(data["stamina"], "stamina", 0, 999)
    if not isinstance(data["items"], list):
        raise ValueError("native custom-opponent items must be an array")
    entries = []
    for index, source in enumerate(data["items"]):
        if not isinstance(source, dict) or set(source) != {"item_index", "x", "y", "f"}:
            raise ValueError("unknown/missing item field or unsupported explicit gems/persistent_data")
        entry = dict(source, instance_id=f"O:{index}")
        for key, low, high in (("item_index", 0, math.inf), ("x", 0, 8), ("y", 0, 6), ("f", 0, 3)):
            entry[key] = native_integer(source[key], f"items[{index}].{key}", low, high)
        entries.append(entry)
    fixture = starter_fixture()
    opponent = fixture["sides"][1]
    opponent.update(character_class=character_class, hp=float(hp), stamina=float(stamina), items=entries)
    validate_fixture(fixture)
    return fixture


def fixture_from_custom_opponent(data, player_data=None):
    fixture = _fixture_from_custom_side(data)
    if player_data is not None:
        parsed = _fixture_from_custom_side(player_data)['sides'][1]
        if parsed['character_class'] not in (0, 2):
            raise ValueError("controlled player requires source Ranger0 or Berserker2")
        if not 1 <= len(parsed['items']) <= 64:
            raise ValueError("controlled player requires 1..64 items")
        ordinary_seen = False
        bag_seen = False
        allowed_player_items = {129,262,204,220,340,416,74,169,219,401,469,53,54,52,400,468,38,205,296,168, 0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 30, 32, 34, 36, 39, 48, 62, 67, 117, 124, 172, 179, 208, 209, 332, 351, 374, 405}
        for item in parsed['items']:
            if item['item_index'] not in allowed_player_items:
                raise ValueError("controlled player item outside audited driver subset")
            if CATALOG[item['item_index']]['bag']:
                if ordinary_seen:
                    raise ValueError("controlled player bags must precede ordinary items")
                bag_seen = True
            else:
                ordinary_seen = True
        if not bag_seen:
            raise ValueError("controlled player requires a bag")
        parsed['side'] = 'P'
        for slot, item in enumerate(parsed['items']):
            item['instance_id'] = f'P:{slot}'
        fixture['sides'][0] = parsed
        validate_fixture(fixture)
    return fixture


def validate_fixture(fixture):
    if set(fixture) != {"schema", "game_version", "mode", "round", "below_master", "rules", "sides"}:
        raise ValueError("unknown or missing fixture field")
    for key, value in (("schema", 1), ("game_version", "1.1.8"), ("mode", "Unranked"),
                       ("round", 1), ("rules", "default")):
        if fixture.get(key) != value or type(fixture[key]) is not type(value):
            raise ValueError(f"unsupported fixture {key}: {fixture.get(key)!r}")
    if not isinstance(fixture.get("below_master"), bool):
        raise ValueError("below_master must be explicit boolean")
    sides = fixture.get("sides", [])
    if len(sides) != 2 or [side.get("side") for side in sides] != ["P", "O"]:
        raise ValueError("exactly P, O sides are required")
    identifiers = set()
    for side in sides:
        if set(side) != {"side", "character_class", "hp", "stamina", "items"}:
            raise ValueError("unknown or missing side field")
        if type(side.get("character_class")) is not int or side.get("character_class") not in (0, 2):
            raise ValueError("only Ranger0 and Berserker2 are implemented")
        for stat in ("hp", "stamina"):
            value = side.get(stat)
            minimum = 1 if stat == "hp" else 0
            if (isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
                    or value != int(value) or not minimum <= value <= 999):
                raise ValueError(f"invalid side {stat}")
        bag_cells, filled_cells = set(), set()
        for entry in side["items"]:
            if set(entry) != {"item_index", "x", "y", "f", "instance_id"}:
                raise ValueError("unknown or missing item field")
            if type(entry["item_index"]) is not int or entry["item_index"] not in CATALOG:
                raise ValueError(f"unsupported item {entry['item_index']}")
            identity = entry.get("instance_id")
            if not isinstance(identity, str) or not identity or identity in identifiers:
                raise ValueError("duplicate or missing instance identity")
            identifiers.add(identity)
            if entry["f"] not in range(4) or any(type(entry.get(k)) is not int for k in ("x", "y", "f")):
                raise ValueError("orientation/position invalid")
            cells = occupied_cells(entry)
            if not all(0 <= x < 9 and 0 <= y < 7 for x, y in cells):
                raise ValueError("layout outside native 9x7 boundary")
            if CATALOG[entry["item_index"]]["bag"]:
                if cells & bag_cells:
                    raise ValueError("bags overlap")
                bag_cells |= cells
        for entry in side["items"]:
            if CATALOG[entry["item_index"]]["bag"]:
                continue
            cells = occupied_cells(entry)
            if not cells <= bag_cells:
                raise ValueError("item outside bag coverage")
            if cells & filled_cells:
                raise ValueError("ordinary item collision")
            filled_cells |= cells
    return True


@dataclass
class CharacterState:
    side: str
    hp: float
    max_hp: float
    stamina: float
    max_stamina: float
    base_max_stamina: float = 0.0
    stamina_regen: float = 1.0
    temporary_max_hp: float = 0.0
    vampirism: int = 0
    debuff_resist_stacks: int = 0
    debuff_reflect_stacks: int = 0
    lucky: int = 0
    blind: int = 0
    poison: int = 0
    heat: int = 0
    cold: int = 0
    block: int = 0
    regeneration: int = 0
    mana: int = 0
    empower: int = 0
    spikes: int = 0
    dead: bool = False
    stunned: float = 0.0
    buff_fields: dict = field(default_factory=fresh_buff_fields)
    buff_protect_stacks: int = 0
    temporary_max_health_gain: float = 1.0
    temporary_max_stamina: float = 0.0
    base_stamina_regen: float = 1.0
    allow_stamina_overflow: bool = False
    invulnerable: bool = False
    battle_raging: bool = False
    unhealing_amount: float = 0.0
    healing_efficiency: float = 1.0
    damage_resistance: float = 0.0
    damage_reduction: int = 0
    dodge_stacks: int = 0
    crit_resistance: float = 0.0
    crit_resist_stacks: int = 0
    stun_resistance: float = 0.0
    crit_tokens: int = 0
    battle_rage_bonus_duration: float = 0.0
    bonus_fatigue_damage: int = 0
    melee_spikes_limit: float = 1.0
    ranged_spikes_limit: float = 0.0
    effect_spikes_limit: float = 0.0
    melee_vampirism_limit: float = 1.0
    ranged_vampirism_limit: float = 0.0
    empower_damage: float = 1.0
    typed_damage_factors: dict = field(default_factory=lambda: {key: 0.0 for key in (0, 1, 2, 3, 98, 104, 108, 99)})
    accuracy: BalancedRng = field(default_factory=BalancedRng)
    critical: BalancedRng = field(default_factory=BalancedRng)
    crit_resistance_rng: BalancedRng = field(default_factory=BalancedRng)
    stun_resistance_rng: BalancedRng = field(default_factory=BalancedRng)


@dataclass
class ItemState:
    instance_id: str
    item_index: int
    side: str
    cells: set
    stars: set = field(default_factory=set)
    ordered_cells: list = field(default_factory=list)
    activations_this_frame: int = 0
    last_activation_frame: int = -1
    last_activation_time: float = 0.0
    last_trigger_time: float = 0.0
    triggers_this_frame: int = 0
    cache_prepared: bool = False
    orientation: int = 0
    top_left: tuple = (0, 0)
    cooldown_active: bool = False
    ammunition: int = 1
    iteration_cooldown: float = 0.0
    trigger_time: float = 0.0
    speed_scale: float = 0.0
    crit_chance: float = 0.0
    damage_range: BalancedRange = field(default_factory=BalancedRange)
    chance_rng: BalancedRng = field(default_factory=BalancedRng)
    buff_powers: dict = field(default_factory=lambda: {key: 1.0 for key in range(100, 111)})
    buff_amplification_chances: dict = field(default_factory=lambda: {key: 0.0 for key in range(100, 111)})
    spikes_given: int = 0
    broom_bonus_damage: int = 0
    potion_full: bool = True
    boots_has_activated: bool = False
    rage_has_activated: bool = False
    goobert_activations: int = 0
    steel_affected_weapons: list = field(default_factory=list)
    double_activation_chance: float = 0.0
    double_attack_effect_chance: float = 0.0
    spear_block_removal: int = 0
    consumed: bool = False
    damage: int = 0
    activations: int = 0
    misses: int = 0
    out_of_stamina: int = 0
    bonus_damage: int = 0
    varying_damage: float = 0.0
    bonus_max_only: float = 0.0
    healing: int = 0
    overheal: float = 0.0

    @property
    def definition(self):
        return CATALOG[self.item_index]

    @property
    def has_cooldown(self):
        return self.definition.get("cooldown", 0.0) != 0

    @property
    def logs_cooldown(self):
        return self.has_cooldown or self.definition.get("log_cooldown", False)

    @property
    def can_activate(self):
        return self.definition.get("can_activate", True)

    @property
    def can_damage(self):
        return self.definition.get("min_damage", 0) > 0 or self.definition.get("lifesteal_tag", False)


def opponent_inventory_order(items):
    """Predict Game.initOpponent's Godot 3.6.2 unstable bag-first sort.

    Identities remain the original input slots. No captured inventory/state is
    used; see docs/native_inventory_sort_fix_spec.md for source and algorithm.
    """
    result = list(items)

    def before(a, b):
        return int(a.definition["bag"]) > int(b.definition["bag"])

    def adjust_heap(first, hole, length, value):
        top = hole
        child = 2 * hole + 2
        while child < length:
            if before(result[first + child], result[first + child - 1]):
                child -= 1
            result[first + hole] = result[first + child]
            hole = child
            child = 2 * (child + 1)
        if child == length:
            result[first + hole] = result[first + child - 1]
            hole = child - 1
        while hole > top:
            parent = (hole - 1) // 2
            if not before(result[first + parent], value):
                break
            result[first + hole] = result[first + parent]
            hole = parent
        result[first + hole] = value

    def heap_sort(first, last):
        length = last - first
        for parent in range((length - 2) // 2, -1, -1):
            adjust_heap(first, parent, length, result[first + parent])
        while last - first > 1:
            value = result[last - 1]
            result[last - 1] = result[first]
            last -= 1
            adjust_heap(first, 0, last - first, value)

    def intro(first, last, depth):
        while last - first > 16:
            if depth == 0:
                heap_sort(first, last)
                return
            depth -= 1
            a, b, c = result[first], result[first + (last - first) // 2], result[last - 1]
            if before(a, b):
                pivot = b if before(b, c) else (c if before(a, c) else a)
            else:
                pivot = a if before(a, c) else (c if before(b, c) else b)
            left, right = first, last
            while True:
                while before(result[left], pivot):
                    left += 1
                right -= 1
                while before(pivot, result[right]):
                    right -= 1
                if left >= right:
                    break
                result[left], result[right] = result[right], result[left]
                left += 1
            intro(left, last, depth)
            last = left

    if result:
        intro(0, len(result), 2 * (len(result).bit_length() - 1))
        # The first sixteen sorted entries supply the original algorithm's
        # sentinel. A guarded insertion is equivalent for this valid comparator.
        for index in range(1, len(result)):
            value, hole = result[index], index
            while hole > 0 and before(value, result[hole - 1]):
                result[hole] = result[hole - 1]
                hole -= 1
            result[hole] = value
    return result



# Reviewed profiles are HOST CODE, never caller-supplied readiness assertions.
from .genuine import PROFILE as GENUINE_PROFILE, TERMINAL as GENUINE_TERMINAL, PROFILES as GENUINE_PROFILES, observer_label, KING_GENUINE_PROFILE, SINGLE_KING_GENUINE_PROFILE
GENUINE_TERMINAL_PROFILES = frozenset({GENUINE_TERMINAL, 'source-two-physics-idle-pre-internal/1'})
SYNTHETIC_PROFILE = 'synthetic-fixed60-physics-tail/1'
SYNTHETIC_TERMINAL = 'synthetic-after-ordinary/1'


def _be_float(bits):
    if type(bits) is not str or re.fullmatch('[0-9a-f]{16}', bits) is None:
        raise ValueError('expected binary64 BE hex16')
    value = struct.unpack('>d', bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError('nonfinite runtime float')
    return value


def _float_bits(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('finite float required')
    return struct.pack('>d', float(value)).hex()


def _keys(value, keys, label):
    if type(value) is not dict or set(value) != set(keys):
        raise ValueError('unknown/missing ' + label + ' keys')


@dataclass(frozen=True)
class RuntimeDTO:
    data: dict
    prepare_order: tuple
    util_time: float


KING_PROFILE = 'phase108-king-default-synthetic/1'
KING_TERMINAL = 'source-two-physics-idle-pre-internal/1'


def _has_king(fixture):
    return any(i['item_index']==262 for side in fixture['sides'] for i in side['items'])


def _king_particle_facts(values):
    _keys(values, ('lifetime_bits','explosiveness_bits','speed_scale_bits','one_shot','visible','emitting'), 'King particle')
    expected = {'lifetime_bits':f32(0.7),'explosiveness_bits':0.0,'speed_scale_bits':1.0}
    for key,value in expected.items():
        if values[key] != _float_bits(value):
            raise ValueError('default promoted REAL32 particle getter bits required')
    if any(values[k] is not False for k in ('one_shot','visible','emitting')):
        raise ValueError('fresh default non-one-shot hidden nonemitting particles required')


SOURCE_KING_PROFILE = 'source-headless-king-fixed60-idle60/1'
SOURCE_KING_ITEMS = frozenset({1, 4, 11, 19, 22, 262})
SOURCE_KING_MAX_SECONDS = 120.0
SOURCE_KING_QUANTA = 7200
SOURCE_KING_PASS_CAPACITY = 14404


def validate_source_king_domain(fixture):
    """Geometry/schema and the thin global-one-King domain precede any RNG."""
    validate_fixture(fixture)
    if _has_rage(fixture):
        raise ValueError('source King plus class2/129 rage is not admitted')
    entries = [entry for side in fixture['sides'] for entry in side['items']]
    if sum(entry['item_index'] == 262 for entry in entries) != 1:
        raise ValueError('source King first domain requires exactly one global King')
    if any(side['character_class'] != 0 for side in fixture['sides']):
        raise ValueError('source King requires two class0 sides')
    if any(entry['item_index'] not in SOURCE_KING_ITEMS for entry in entries):
        raise ValueError('source King mixed family outside six-ID thin domain')


def source_king_policy():
    return dict(schema=SOURCE_KING_PROFILE, physics_fps=60, idle_fps=60,
                physics_delta_bits=_float_bits(NATIVE_PHYSICS_DELTA),
                idle_delta_bits=_float_bits(NATIVE_PHYSICS_DELTA),
                hard_seconds_bits=_float_bits(SOURCE_KING_MAX_SECONDS),
                ordinary_physics_quanta=SOURCE_KING_QUANTA,
                pass_capacity=SOURCE_KING_PASS_CAPACITY, terminal_future_physics=2,
                checkpoint='fresh_activate_idle_tail_positive_zero')


def source_king_fresh_defaults(fixture):
    validate_source_king_domain(fixture)
    particles = dict(lifetime_bits=_float_bits(f32(0.7)), explosiveness_bits=_float_bits(0.0),
                     speed_scale_bits=_float_bits(1.0), one_shot=False, visible=False, emitting=False)
    return dict(characters={side: dict(invulnerable=False, invulnerabilityItem=None,
                                      invulBubbleVisible=False, buffProtectStacks=0)
                            for side in ('P', 'O')},
                kings={entry['instance_id']: dict(invuCharges=0, protectedBuffs_bits=_float_bits(3.0),
                       manaCost_bits=_float_bits(4.0), crown=0, light_visible=True,
                       light_modulate_bits=[_float_bits(1.0)] * 4,
                       activation=deepcopy(particles), drag=deepcopy(particles))
                       for side in fixture['sides'] for entry in side['items'] if entry['item_index'] == 262})


def source_king_topology(fixture):
    """Independently reconstruct SOURCE coordinates; no caller topology/provider."""
    validate_source_king_domain(fixture)
    roles, nodes = _required_roles(fixture), []

    def node(role, path, positions):
        value = dict(role=role, path=path, positions=positions, priority=0, kind=roles[role])
        if roles[role] == 'timer':
            value.update(wait_time_bits=_float_bits(1.0), one_shot=not role.startswith('tick:'),
                         process_mode=1 if role.startswith(('king_hide:', 'king_drag:')) else 0)
        nodes.append(value)

    node('util', '/root/Util', [-1, 0])
    for side in ('O', 'P'):
        parent = '/root/Main/Combat/Opponent' if side == 'O' else '/root/Main/Player'
        pos = [-1, 1, 0, 0] if side == 'O' else [-1, 1, 1]
        node('character:' + side, parent + '/Character', pos + [0])
        node('tick:' + side, parent + '/Character/TickTimer', pos + [0, 3])
        node('invu:' + side, parent + '/Character/InvulnerabilityTimer', pos + [0, 5])
        for index, category in enumerate(range(100, 111)):
            node('buff:' + side + ':' + STACK_NAMES_BY_TYPE[category],
                 parent + '/Character/Buff' + str(index), pos + [0, 100 + index])
        entries = fixture['sides'][0 if side == 'P' else 1]['items']
        # The accepted native bag-first sort only reads definition['bag'].
        inventory = [SimpleNamespace(definition=CATALOG[e['item_index']], entry=e) for e in entries]
        if side == 'O':
            inventory = opponent_inventory_order(inventory)
        # Thin domain has only equal-layer bag11; fresh bag insertion preserves this order.
        for index, value in enumerate(inventory):
            entry = value.entry
            item_path, item_pos = parent + '/Item' + str(index), pos + [index + 2]
            node('item:' + entry['instance_id'], item_path, item_pos)
            if entry['item_index'] == 262:
                identity = entry['instance_id']
                node('king_buff:' + identity, item_path + '/BuffTimer', item_pos + [7])
                node('king_hide:' + identity, item_path + '/ActivationParticles/Timer', item_pos + [8, 0])
                node('king_drag:' + identity, item_path + '/Icon/SpecificDragParticles/Timer', item_pos + [1, 2, 0])
    path, pos = '/root/Main/Combat/UI/CombatTimer', [-1, 1, 0, 1, 0]
    node('combat_timer', path, pos)
    node('fatigue:start', path + '/FatigueStartTimer', pos + [1])
    node('fatigue:tick', path + '/FatigueTickTimer', pos + [2])
    data = dict(nodes=nodes, timer_lineage={role: 'fresh_configured' for role, kind in roles.items() if kind == 'timer'})
    _validate_runtime_nodes(data, fixture, True)
    return data


def _source_king_equal(actual, expected):
    """Exact primitive types and float bits; Python BOOL/INT aliases cannot pass."""
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return actual.keys() == expected.keys() and all(_source_king_equal(actual[k], v) for k, v in expected.items())
    if type(expected) in (list, tuple):
        return len(actual) == len(expected) and all(_source_king_equal(a, b) for a, b in zip(actual, expected))
    if type(expected) is float:
        return _float_bits(actual) == _float_bits(expected)
    return actual == expected


def _source_king_data(fixture, order):
    topology = source_king_topology(fixture)
    ids = [entry['instance_id'] for side in fixture['sides'] for entry in side['items']]
    if (type(order) is not list or any(type(x) is not str for x in order)
            or len(order) != len(ids) or set(order) != set(ids)):
        raise ValueError('source King order must contain every instance exactly once')
    defaults = source_king_fresh_defaults(fixture)
    return dict(schema='native-v8-runtime-input/1', mode='synthetic', profile_id=SOURCE_KING_PROFILE,
                checkpoint=dict(util_time_bits=_float_bits(0.0), combat_time_bits=_float_bits(0.0),
                                source_phase='synthetic-before-activate'),
                environment=dict(fps=60, scale=1.0, paused=False, no_pending_gameplay_transform=True),
                nodes=topology['nodes'], timer_lineage=topology['timer_lineage'],
                initial_items={identity: dict(lastActivationTime_bits=_float_bits(0.0), activationsThisFrame=0,
                    lastTriggerTime_bits=_float_bits(0.0), triggersThisFrame=0, dragged=False,
                    moveback_running=False, cache_fresh=True) for identity in ids},
                prepare_order=order.copy(), activate_order=order.copy(), terminal_profile=KING_TERMINAL,
                clock_policy=source_king_policy(), fresh_king_defaults=defaults,
                king_particles={identity: deepcopy(value['activation']) for identity, value in defaults['kings'].items()})


def source_king_runtime_inputs(fixture, order, topology=None):
    data = _source_king_data(fixture, order)
    if topology is not None and not _source_king_equal(topology, {k: data[k] for k in ('nodes', 'timer_lineage')}):
        raise ValueError('source King topology differs from independent SOURCE reconstruction')
    return validate_runtime_inputs(data, fixture)


def _validate_source_king_runtime(data, fixture, original):
    if type(data) is not dict or type(data.get('prepare_order')) is not list:
        raise ValueError('closed source King runtime required')
    expected = _source_king_data(fixture, data['prepare_order'])
    if not _source_king_equal(data, expected):
        raise ValueError('source King requires exact code-generated fresh defaults/topology/policy')
    if isinstance(original, RuntimeDTO) and (type(original.prepare_order) is not tuple
            or original.prepare_order != tuple(data['prepare_order']) or type(original.util_time) is not float
            or _float_bits(original.util_time) != _float_bits(0.0)):
        raise ValueError('source King RuntimeDTO convenience fields disagree')
    return RuntimeDTO(data, tuple(data['prepare_order']), 0.0)


def _source_king_profile(runtime):
    value = runtime.data if isinstance(runtime, RuntimeDTO) else runtime
    return type(value) is dict and value.get('profile_id') == SOURCE_KING_PROFILE


def _has_rage(fixture):
    return any(side["character_class"] == 2 or any(item["item_index"] == 129 for item in side["items"])
               for side in fixture["sides"])


def _required_roles(fixture):
    result = {'util': 'ordinary', 'combat_timer': 'ordinary', 'character:P': 'ordinary', 'character:O': 'ordinary',
              'tick:P': 'timer', 'tick:O': 'timer', 'fatigue:start': 'timer', 'fatigue:tick': 'timer'}
    for side in ('P', 'O'):
        for stack in STACK_NAMES_BY_TYPE.values():
            result['buff:' + side + ':' + stack] = 'timer'
    for side in fixture['sides']:
        for item in side['items']:
            result['item:' + item['instance_id']] = 'ordinary'
            if item['item_index'] in STATE_PARTICLE_IDS:
                result['particle:' + item['instance_id']] = 'timer'
    if _has_rage(fixture):
        result.update({'rage:P': 'timer', 'rage:O': 'timer'})
    if _has_king(fixture):
        result.update({'invu:P':'timer','invu:O':'timer'})
        for side in fixture['sides']:
            for item in side['items']:
                if item['item_index']==262:
                    for prefix in ('king_buff:','king_hide:','king_drag:'):
                        result[prefix+item['instance_id']]='timer'
    return result


#134 source/helper integration contract. No genuine King profile is admitted.
KING_INTEGRATION_PROFILE = 'phase134-king-authority-synthetic-integration/1'
AUX_ROLES = frozenset('aux:'+side+':'+name for side in ('P','O') for name in ('battleRageTimer','autoRageTimer'))
NODE_INPUT_KEYS = ('native_id','role','path','name','class','positions','priority','inside_tree','ordinary_physics','internal_physics','ordinary_idle','internal_idle')
AUX_LEMMA = 'original1.1.8-Ranger-fixed-King-no-Rage-callers/1'


def _integration_domain(data):
    return _pure441_profile(data) or data.get('profile_id') in (KING_INTEGRATION_PROFILE, KING_GENUINE_PROFILE, SINGLE_KING_GENUINE_PROFILE)


def _validate_processing_inputs(data,fixture):
    if data.get('profile_id') == SINGLE_KING_GENUINE_PROFILE:
        return _validate_single_king_processing_inputs(data, fixture)
    from .genuine import validate_ui_authority
    authority=validate_ui_authority(data['ui_authority'])
    # No guessed flags or caller-supplied verified booleans: raw complete carrier is revalidated.
    if authority['unsupported']!=0:raise ValueError('NOT_ADMITTED: unsupported UI entry')
    required=set(_required_roles(fixture))|AUX_ROLES|{'root_viewport','game'}
    rows=data['processing_nodes']
    if type(rows)is not list or len(rows)!=len(required) or len(rows)!=64:raise ValueError('closed64 processing association roles')
    if {i['item_index']for side in fixture['sides']for i in side['items']} != {67,262,22,1,16,19,21,332} or any(side['character_class']!=0 for side in fixture['sides']):
        raise ValueError('fixed Ranger King integration family required')
    table={};native_ids=set();paths=set();positions=set();prefixes={}
    for n in rows:
        _keys(n,NODE_INPUT_KEYS,'processing node')
        if n['role']not in required or n['role']in table or type(n['native_id'])is not str or re.fullmatch('[1-9][0-9]*',n['native_id'])is None or n['native_id']in native_ids:
            raise ValueError('processing identity/role')
        if n['inside_tree']is not True or type(n['path'])is not str or n['path']in paths or type(n['positions'])is not list or tuple(n['positions'])in positions:
            raise ValueError('processing actual path/index')
        names=n['path'].split('/')[1:]
        if not(n['path']=='/root' or n['path'].startswith('/root/')) or len(names)!=len(n['positions']) or n['positions'][0]!=-1 or any(type(x)is not int or not 0<=x<=4096 for x in n['positions'][1:]) or n['name']!=names[-1]:raise ValueError('processing node coordinates')
        if type(n['priority'])is not int or type(n['class'])is not str:raise ValueError('processing scalar types')
        for flag in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
            if type(n[flag])is not bool:raise ValueError('actual independent processing flags')
        for j in range(1,len(names)+1):
            key=tuple(n['positions'][:j]);value=tuple(names[:j])
            if key in prefixes and prefixes[key]!=value:raise ValueError('raw processing prefix conflict')
            prefixes[key]=value
        table[n['role']]=n;native_ids.add(n['native_id']);paths.add(n['path']);positions.add(tuple(n['positions']))
    root=table['root_viewport']
    if data['root_node']!=root or root['path']!='/root' or root['positions']!=[-1] or root['priority']!=0 or root['class']!='Viewport' or not root['internal_physics'] or root['ordinary_physics'] or root['ordinary_idle']:
        raise ValueError('unsupported actual root flags')
    for node in data['nodes']:
        actual=table[node['role']]
        if any(node[k]!=actual[k]for k in ('path','positions','priority')):raise ValueError('model/raw topology mismatch')
        if node['kind']=='timer' and actual['class']!='Timer':raise ValueError('Timer class')
    for role,n in table.items():
        if role=='root_viewport':continue
        if n['internal_physics'] or n['internal_idle']:raise ValueError('nonroot initial internal callback')
        flags=(n['ordinary_physics'],n['ordinary_idle'])
        expected=(True,True)if role in ('util','game')else (True,False)if role.startswith('character:')else (False,True)if role.startswith('item:')else(False,False)
        if flags!=expected:raise ValueError('unsupported initial ordinary membership '+role)
    _keys(data['inactive_auxiliaries'],AUX_ROLES,'inactive auxiliary table')
    for role,x in data['inactive_auxiliaries'].items():
        _keys(x,('source_lemma','lineage','wait_time_bits','one_shot','process_mode'),'auxiliary fact')
        if x['source_lemma']!=AUX_LEMMA or x['lineage']!='fresh_configured' or x['one_shot']is not True or type(x['process_mode'])is not int or x['process_mode']!=0 or table[role]['class']!='Timer':raise ValueError('source inactive auxiliary')
        wait=_be_float(x['wait_time_bits'])
        if wait<=0 or f32(wait)!=wait:raise ValueError('aux wait getter')
    for identity,parts in data['king_particles'].items():
        king=table['item:'+identity]
        binds=[r['payload']for r in data['ui_authority']if r['kind']=='bind' and r['payload']['item_id']==king['native_id']]
        if len(binds)!=1:raise ValueError('particle source binding')
        for kind,part in parts.items():
            n=part['node'];_keys(n,NODE_INPUT_KEYS,'actual particle node')
            timer=table[('king_hide:'if kind=='activation'else'king_drag:')+identity]
            if n['class']!='Particles2D' or n['role']is not None or n['native_id']!=binds[0][kind+'_id'] or timer['path'].rsplit('/',1)[0]!=n['path'] or timer['positions'][:-1]!=n['positions'] or n['name']!=n['path'].rsplit('/',1)[1] or n['inside_tree']is not True or type(n['priority'])is not int:
                raise ValueError('distinct actual particle identity')
            if n['native_id']in native_ids or any(n[k]is not False for k in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')):raise ValueError('continuous particle source inactive callback flags')
            native_ids.add(n['native_id'])
    first=data['ui_authority'][0];last=data['ui_authority'][-1];controls=last['payload']['controls']
    if controls['root_id']!=root['native_id'] or any(controls[k]!=root[k]for k in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')):raise ValueError('UI/root flags disagree')
    roles=next(r['payload']for r in data['ui_authority']if r['kind']=='roles')
    for guard in roles['selected_guards']:
        node=table.get('item:'+guard['role'])
        if node is None or node['native_id']!=guard['item_id'] or guard['viewport_id']!=root['native_id']:raise ValueError('UI selected native association')
    clock=decode_clock(data['frame_clock'])
    if not(first['physics_frame']<=clock.physics_frame<=last['physics_frame'] and first['idle_frame']<=clock.idle_frame<=last['idle_frame']):raise ValueError('activation outside complete UI window')
    # Source UI footer is authority only: it never ends the model or configures pass consumption.
    return table


def _validate_runtime_nodes(data,fixture,king=False):
    """Validate node defaults/topology/lineage without any prepare-order or RNG."""
    roles = _required_roles(fixture)
    if type(data['nodes']) is not list or len(data['nodes']) != len(roles) or len(roles) > 1024:
        raise ValueError('missing/extra runtime node roles')
    seen = set(); prefixes = {}; path_positions = {}; expected_timers = set()
    for node in data['nodes']:
        if type(node) is not dict or type(node.get('role')) is not str or node.get('role') not in roles or node['role'] in seen:
            raise ValueError('unknown/duplicate role')
        seen.add(node['role']); kind = roles[node['role']]
        _keys(node, ('role','path','positions','priority','kind') + (('wait_time_bits','one_shot') + (('process_mode',) if king or node['role'].startswith('particle:') else ()) if kind == 'timer' else ()), 'node')
        if node['kind'] != kind or type(node['priority']) is not int or not -(2**31) <= node['priority'] < 2**31:
            raise ValueError('invalid node kind/priority')
        if type(node['path']) is not str or not node['path'].startswith('/root/'):
            raise ValueError('absolute known-root path required')
        names = node['path'].split('/')[1:]; positions = node['positions']
        if (type(positions) is not list or len(positions) != len(names) or not 2 <= len(names) <= 32
                or any(type(i) is not int for i in positions) or positions[0] != -1
                or any(not 0 <= i <= 4096 for i in positions[1:])
                or any(not n or n in ('.','..') or ':' in n or n.startswith('__v8_gap_') for n in names)):
            raise ValueError('invalid bounded native path/index')
        for end in range(1, len(names)+1):
            pos = tuple(positions[:end]); name_path = tuple(names[:end])
            if pos in prefixes and prefixes[pos] != name_path or name_path in path_positions and path_positions[name_path] != pos:
                raise ValueError('conflicting native path/index prefixes')
            prefixes[pos] = name_path; path_positions[name_path] = pos
        if kind == 'timer':
            wait = _be_float(node['wait_time_bits'])
            if f32(wait) != wait or wait <= 0 or type(node['one_shot']) is not bool:
                raise ValueError('invalid native Timer configuration')
            expected_one_shot = not node['role'].startswith('tick:')
            if node['one_shot'] != expected_one_shot:
                raise ValueError('non-source Timer repeat configuration')
            if king:
                mode=1 if node['role'].startswith(('king_hide:','king_drag:')) else 0
                if node['role'].startswith(('invu:','king_buff:','king_hide:','king_drag:')) and wait!=1.0:
                    raise ValueError('fresh default King/Character/AutoHide Timer wait_time1 required')
                if type(node['process_mode']) is not int or node['process_mode']!=mode:
                    raise ValueError('non-source King Timer process mode')
            if node['role'].startswith('particle:'):
                parent=next(n for n in data['nodes'] if n['role']=='item:'+node['role'][9:])
                if (node['path']!=parent['path']+'/ParticleTimer' or node['positions']!=parent['positions']+[9]
                        or node['priority']!=0 or wait!=1.0 or node['one_shot'] is not True
                        or type(node['process_mode']) is not int or node['process_mode']!=0):
                    raise ValueError('source physics bool-reset Timer child9/fresh defaults required')
            expected_timers.add(node['role'])
    if len({n['path'] for n in data['nodes']}) != len(data['nodes']):
        raise ValueError('multiple actual roles at one node')
    _keys(data['timer_lineage'], expected_timers, 'Timer lineage')
    if any(v != 'fresh_configured' or type(v) is not str for v in data['timer_lineage'].values()):
        raise ValueError('unknown active/private Timer lineage')
    parents = {}
    for pos in prefixes:
        if len(pos)>1:
            parents[pos[:-1]] = max(parents.get(pos[:-1],0), pos[-1]+1)
    if sum(parents.values())+1 > 16384:
        raise ValueError('sparse scaffold budget exceeded')


def validate_runtime_inputs(runtime, fixture):
    data = deepcopy(runtime.data if isinstance(runtime, RuntimeDTO) else runtime)
    if _pure441_profile(data):
        return _validate_pure441_runtime(data, fixture, runtime)
    if _source_king_profile(data):
        return _validate_source_king_runtime(data, fixture, runtime)
    if _single_king_genuine_profile(data):
        from .genuine import validate_single_king_fixture, require_single_king_admission
        require_single_king_admission()
        validate_single_king_fixture(fixture)
    king = _has_king(fixture)
    if king and _has_rage(fixture):
        raise ValueError("combined King/rage runtime topology not admitted in this increment")
    integration = _integration_domain(data)
    _keys(data, ('schema','mode','profile_id','checkpoint','environment','nodes','timer_lineage','initial_items',
                 'prepare_order','activate_order','terminal_profile') + (('frame_clock','king_particles') if king else ()) + (('root_node','processing_nodes','inactive_auxiliaries','ui_authority')if integration else()), 'runtime')
    if king:
        if not ((data['mode']=='synthetic' and data['profile_id'] in (KING_PROFILE,KING_INTEGRATION_PROFILE)) or (data['mode']=='genuine' and data['profile_id'] in (KING_GENUINE_PROFILE, SINGLE_KING_GENUINE_PROFILE))) or data['terminal_profile']!=KING_TERMINAL:
            raise ValueError('King requires an exact code-approved finite or explicit synthetic profile')
        frame_clock=decode_clock(data['frame_clock'])
        kings={i['instance_id'] for side in fixture['sides'] for i in side['items'] if i['item_index']==262}
        _keys(data['king_particles'],kings,'King particle map')
        for value in data['king_particles'].values():
            if integration:
                _keys(value,('activation','drag'),'distinct particle inputs')
                for part in value.values():
                    _keys(part,('node','getters'),'particle source interface')
                    _king_particle_facts(part['getters'])
            else:_king_particle_facts(value)
    if any(type(data[k]) is not str for k in ('schema','mode','profile_id','terminal_profile')):
        raise ValueError('runtime discriminants must be strings')
    if data['schema'] != 'native-v8-runtime-input/1':
        raise ValueError('BLOCKED_INHERITED_INPUT: missing v8 runtime schema')
    if data['mode'] == 'genuine':
        if data['profile_id'] not in GENUINE_PROFILES or data['terminal_profile'] not in GENUINE_TERMINAL_PROFILES:
            raise ValueError('genuine/terminal profile is not code-approved; NOT_CAPTURE_READY')
        from .genuine import validate_profile
        validate_profile(data, fixture)
    elif not king and (data['mode'] != 'synthetic' or data['profile_id'] != SYNTHETIC_PROFILE or data['terminal_profile'] != SYNTHETIC_TERMINAL):
        raise ValueError('unsupported explicit synthetic profile')
    _keys(data['environment'], ('fps','scale','paused','no_pending_gameplay_transform'), 'environment')
    env = data['environment']
    if type(env['fps']) is not int or env['fps'] != 60 or type(env['scale']) is not float or env['scale'] != 1.0:
        raise ValueError('only declared60Hz scale1 profile')
    if env['paused'] is not False or env['no_pending_gameplay_transform'] is not True:
        raise ValueError('paused or unclosed gameplay transform')
    _keys(data['checkpoint'], ('util_time_bits','combat_time_bits','source_phase'), 'checkpoint')
    clock = _be_float(data['checkpoint']['util_time_bits'])
    if clock < 0 or _be_float(data['checkpoint']['combat_time_bits']) != 0.0 or data['checkpoint']['source_phase'] != ('Core/Game.gd::activateItems:enter' if data['mode']=='genuine' else 'synthetic-before-activate'):
        raise ValueError('invalid synthetic initial checkpoint')
    if king and _float_bits(clock)!=_float_bits(frame_clock.util_time):
        raise ValueError('King checkpoint and exogenous Util.time disagree')
    ids = {i['instance_id'] for side in fixture['sides'] for i in side['items']}
    for field_name in ('prepare_order','activate_order'):
        order = data[field_name]
        if type(order) is not list or any(type(i) is not str for i in order) or len(order) != len(ids) or set(order) != ids:
            raise ValueError('runtime order must contain each instance once')
    if data['prepare_order'] != data['activate_order']:
        raise ValueError('unsupported different preparation/activation order')
    _keys(data['initial_items'], ids, 'initial item table')
    for identity, values in data['initial_items'].items():
        _keys(values, ('lastActivationTime_bits','activationsThisFrame','lastTriggerTime_bits','triggersThisFrame',
                      'dragged','moveback_running','cache_fresh'), 'initial limiter')
        for key in ('lastActivationTime_bits','lastTriggerTime_bits'):
            if _be_float(values[key]) < 0:
                raise ValueError('negative source limiter time')
        for key in ('activationsThisFrame','triggersThisFrame'):
            if type(values[key]) is not int or not 0 <= values[key] <= 2147483647:
                raise ValueError('invalid limiter counter')
        if values['dragged'] is not False or values['moveback_running'] is not False or values['cache_fresh'] is not True:
            raise ValueError('unknown picking/tween/cache lineage')
    if _single_king_genuine_profile(data):
        _validate_single_king_initials(data)
    _validate_runtime_nodes(data,fixture,king)
    if integration:_validate_processing_inputs(data,fixture)
    if isinstance(runtime, RuntimeDTO):
        if (type(runtime.prepare_order) is not tuple or runtime.prepare_order != tuple(data['prepare_order'])
                or type(runtime.util_time) is not float or _float_bits(runtime.util_time) != _float_bits(clock)):
            raise ValueError('RuntimeDTO convenience fields disagree with validated data')
    return RuntimeDTO(data, tuple(data['prepare_order']), clock)


def _synthetic_runtime_data(fixture, util_time, ordinary_order=None):
    """Explicit synthetic fixture builder, never genuine provenance; clock required."""
    validate_fixture(fixture)
    ids = [i['instance_id'] for s in fixture['sides'] for i in s['items']]
    ordinary = ['util','combat_timer','character:O','character:P'] + ['item:' + i for i in ids]
    if ordinary_order is not None:
        if type(ordinary_order) is not list or len(ordinary_order)!=len(ordinary) or set(ordinary_order)!=set(ordinary):
            raise ValueError('synthetic ordinary order requires all roles once')
        ordinary = ordinary_order
    nodes=[]
    for index, role in enumerate(ordinary):
        nodes.append(dict(role=role,path='/root/Synthetic/Actor'+str(index),positions=[-1,0,index],priority=0,kind='ordinary'))
    timer_roles = [r for r,k in _required_roles(fixture).items() if k=='timer']
    for index, role in enumerate(timer_roles):
        if role.startswith('particle:'):
            parent=next(n for n in nodes if n['role']=='item:'+role[9:])
            nodes.append(dict(role=role,path=parent['path']+'/ParticleTimer',positions=parent['positions']+[9],priority=0,
                              kind='timer',wait_time_bits=_float_bits(1.0),one_shot=True,process_mode=0))
        else:
            nodes.append(dict(role=role,path='/root/SyntheticTimers/Timer'+str(index),positions=[-1,1,index],priority=0,
                              kind='timer',wait_time_bits=_float_bits(1.0),one_shot=not role.startswith('tick:')))
    order=[i['instance_id'] for side in fixture['sides'] for i in sorted(side['items'],key=lambda i:-CATALOG[i['item_index']].get('priority',0))]
    data=dict(schema='native-v8-runtime-input/1',mode='synthetic',profile_id=SYNTHETIC_PROFILE,
              checkpoint=dict(util_time_bits=_float_bits(util_time),combat_time_bits=_float_bits(0.0),source_phase='synthetic-before-activate'),
              environment=dict(fps=60,scale=1.0,paused=False,no_pending_gameplay_transform=True),nodes=nodes,
              timer_lineage={role:'fresh_configured' for role in timer_roles},initial_items={i:dict(lastActivationTime_bits=_float_bits(0.0),
              activationsThisFrame=0,lastTriggerTime_bits=_float_bits(0.0),triggersThisFrame=0,dragged=False,moveback_running=False,cache_fresh=True)for i in ids},
              prepare_order=order,activate_order=order.copy(),terminal_profile=SYNTHETIC_TERMINAL)
    return data


def synthetic_runtime_inputs(fixture,util_time,ordinary_order=None):
    if _has_king(fixture):
        raise ValueError('King requires explicit exogenous clock and typed particle facts')
    return validate_runtime_inputs(_synthetic_runtime_data(fixture,util_time,ordinary_order),fixture)


def synthetic_king_runtime_inputs(fixture,frame_clock,particle_facts,ordinary_order=None):
    if not _has_king(fixture):raise ValueError('King fixture required')
    clock=decode_clock(frame_clock)
    data=_synthetic_runtime_data(fixture,clock.util_time,ordinary_order)
    data.update(profile_id=KING_PROFILE,terminal_profile=KING_TERMINAL,
                frame_clock=deepcopy(frame_clock),king_particles=deepcopy(particle_facts))
    for node in data['nodes']:
        if node['kind']=='timer':
            node['process_mode']=1 if node['role'].startswith(('king_hide:','king_drag:')) else 0
    return validate_runtime_inputs(data,fixture)


def build_runtime_scaffold(dto):
    if _pure441_profile(dto):
        return _build_pure441_scaffold(dto)
    integration=_integration_domain(dto.data)
    runtime=TimerRuntime(root_internal_idle=dto.data['root_node']['internal_idle'])if integration else TimerRuntime()
    records={}; prefixes={(-1,):('root',)}
    configs=list(dto.data['nodes'])
    if integration:
        game=next(n for n in dto.data['processing_nodes']if n['role']=='game')
        configs.append({k:game[k]for k in ('role','path','positions','priority')}|{'kind':'ordinary'})
    by_position={tuple(n['positions']):n for n in configs}
    for node in configs:
        names=node['path'].split('/')[1:]
        for end in range(2,len(names)+1):prefixes[tuple(node['positions'][:end])]=tuple(names[:end])
    objects={(-1,):runtime.root}
    for pos in sorted((p for p in prefixes if len(p)>1),key=lambda p:(len(p),p)):
        parent=objects[pos[:-1]]
        while len(parent.children)<pos[-1]:
            gap=runtime.new_node('gap:'+str(pos[:-1])+':'+str(len(parent.children)), '__v8_gap_'+str(len(parent.children)))
            runtime.add_child(parent,gap)
        config=by_position.get(pos); name=prefixes[pos][-1]
        role=config['role'] if config else 'ancestor:'+ '/'.join(prefixes[pos])
        node=runtime.new_timer(role,name)if config and config['kind']=='timer'else runtime.new_node(role,name)
        runtime.add_child(parent,node);objects[pos]=node
        if config:
            runtime.set_priority(node,config['priority']); records[role]=node
            if config['kind']=='timer':
                runtime.configure_timer(node,config['one_shot'],config.get('process_mode',0));runtime.set_wait_time(node,_be_float(config['wait_time_bits']))
    ordinary=sorted((n for n in configs if n['kind']=='ordinary'),key=lambda n:(n['priority'],tuple(n['positions'])))
    return runtime,records,[n['role']for n in ordinary]


@dataclass
class TemporaryEntry:
    amount: int
    timeout: float
    item_id: str | None


class EngineFrameDriver(FrameDriver):
    """Only integration hooks; accepted finite phase/barrier algorithm is inherited."""
    def __init__(self,engine):
        self.engine=engine
        super().__init__(engine.timer_runtime,engine.runtime_inputs.data['frame_clock'],engine.runtime_roles['util'])

    def _util_physics(self,node,delta):
        if self.engine.integration_mode:self.engine._integration_callback('util',0,delta)
        super()._util_physics(node,delta)
        self.engine.util_time=self.util_time
        self.engine.runtime_trace.append(dict(kind='util_step',frame=self.engine.frame,util_time=self.util_time))

    def _util_idle(self,node,delta):
        if self.engine.integration_mode:self.engine._integration_callback('util',1,delta)
        super()._util_idle(node,delta)
        self.engine.runtime_trace.append(dict(kind='util_idle_step',frame=self.engine.frame,util_clock_time=self.util_clock_time))

    def snapshot(self):
        result=super().snapshot()
        result['model']=self.engine.snapshot()
        if self.engine.pure_combat_mode:
            result['business']=self.engine._pure_business_snapshot('final' if self.finalized else 'cleanup')
        elif self.engine.integration_mode:result['full_fx']=self.engine._integration_fx_snapshot()
        return result


@dataclass(frozen=True)
class Fixed60Passes:
    """Private immutable O(1) production capacity, not exogenous finite records."""
    def __len__(self):
        return SOURCE_KING_PASS_CAPACITY

    def __getitem__(self, index):
        if type(index) is not int:
            raise TypeError('source pass index requires strict INT, no slices/BOOL')
        if not 0 <= index < len(self):
            raise IndexError('source pass capacity exhausted')
        counter = index // 2 + 1
        return FramePass('physics' if index % 2 == 0 else 'idle', NATIVE_PHYSICS_DELTA, counter, counter)


def _source_king_bootstrap_clock():
    return dict(schema='phase105-exogenous-frame-clock/1', lineage='fresh_activate_idle_tail',
                environment=dict(physics_fps=60, scale_bits=_float_bits(1.0), paused=False),
                checkpoint=dict(phase='activate_items_idle_tail', physics_frame=0, idle_frame=0,
                    util_frame_counter=0, util_time_bits=_float_bits(0.0), util_clock_time_bits=_float_bits(0.0)),
                passes=[dict(kind='physics', delta_bits=_float_bits(NATIVE_PHYSICS_DELTA), physics_frame=1, idle_frame=1)])


class HeadlessKingFrameDriver(EngineFrameDriver):
    """Original dispatch/barrier with an internal bounded SOURCE pass view."""
    def __init__(self, engine):
        self.engine = engine
        FrameDriver.__init__(self, engine.timer_runtime, _source_king_bootstrap_clock(), engine.runtime_roles['util'])
        self.clock = replace(self.clock, passes=Fixed60Passes())

    def complete(self):
        if not self.finalized:
            raise ValueError('source King terminal barrier incomplete')
        return dict(status='SOURCE_KING_COMPUTED_TERMINAL_NOT_NATIVE_ACCEPTANCE',
                    post_cleanup=deepcopy(self.post_cleanup_snapshot), final=deepcopy(self.final_snapshot),
                    passes=deepcopy(self.pass_trace), passes_consumed=self.pass_index,
                    capacity=len(self.clock.passes))


class CombatEngine:
    def __init__(self, fixture, random_source, runtime):
        self.model_source_sha256 = assert_model_source_stable()
        self.fixture = deepcopy(fixture if fixture is not None else starter_fixture())
        validate_fixture(self.fixture)
        source_runtime = validate_runtime_inputs(runtime, self.fixture) if _source_king_profile(runtime) or _single_king_genuine_profile(runtime) or _pure441_profile(runtime) else None
        if _pure441_profile(runtime) and type(random_source) is not TapeRandom:
            raise ValueError('fixed441 pure candidate requires actual TapeRandom; no seed fallback')
        self.random = random_source if random_source is not None else SeededRandom(0)
        self.runtime_inputs = source_runtime if source_runtime is not None else validate_runtime_inputs(runtime, self.fixture)
        self.pure_combat_mode = _pure441_profile(self.runtime_inputs)
        self.pure_snapshots = []
        self.pure_api_trace = []
        self.physics_order = ["explicit_runtime_roles"]
        self.characters = {}
        self.items = {}
        self.side_items = {"P": [], "O": []}
        for side in self.fixture["sides"]:
            key = side["side"]
            self.characters[key] = CharacterState(key, float(side["hp"]), float(side["hp"]),
                                                    float(side["stamina"]), float(side["stamina"]),
                                                    base_max_stamina=5.0 if key == "P" else 0.0)
            for entry in side["items"]:
                item = ItemState(entry["instance_id"], entry["item_index"], key, occupied_cells(entry),
                                 transformed_cells(entry, "stars"), orientation=entry["f"],
                                 top_left=(entry["x"], entry["y"]), ordered_cells=ordered_occupied_cells(entry))
                self.items[item.instance_id] = item
                self.side_items[key].append(item)
        self.side_items["O"] = opponent_inventory_order(self.side_items["O"])
        self.affected_items_cache = self.new_caller_target_caches()
        self.steel_secondary_cache = self.new_steel_secondary_caches()
        self.preparation_order = list(self.runtime_inputs.prepare_order)
        self.events = []
        self.allocated_events = {}
        self.logging_mode = 1
        self.signal_queue = []
        self.event_num = -1
        self.time = 0.0
        self.elapsed = 0.0
        self.frame = 0
        self.prepared = False
        self.activated = False
        self.util_time = None
        self.runtime_trace = []
        self.pending_terminal = False
        self.ended = False
        self.finalized = False
        self.winner = None
        self.fatigue_counter = 0
        self.fatigue_start_left = 14.0
        self.fatigue_tick_left = None
        self.tick_left = {"P": 1.0, "O": 1.0}
        self.tick_counter = {"P": 0, "O": 0}
        self.diagnostics = []
        self.schedule_trace = []
        self.activation_listeners = {}
        self.lucky_listeners = {"P": [], "O": []}
        self.rage_listeners = {"P": [], "O": []}
        self.collar_targets = {}
        self.bag_inside_cache = {}
        self.bag_affected_inside_cache = {}
        self.histories = CombatHistories(self)
        self.timer_runtime, self.runtime_roles, self.ordinary_roles = build_runtime_scaffold(self.runtime_inputs)
        self.king_mode=_has_king(self.fixture)
        self.source_king_mode=_source_king_profile(self.runtime_inputs)
        self.integration_mode=_integration_domain(self.runtime_inputs.data)
        self.processing_inputs={n['role']:n for n in self.runtime_inputs.data.get('processing_nodes',[])}
        self.king_states={}
        self.invu_origins={'P':None,'O':None}
        self.invu_bubbles={'P':False,'O':False}
        if self.pure_combat_mode:
            for side, values in self.runtime_inputs.data['initial_characters'].items():
                self.characters[side].invulnerable = values['invulnerable']
                self.characters[side].buff_protect_stacks = values['buffProtectStacks']
                self.invu_origins[side] = values['invulnerabilityItem']
            self.king_states['P:12'] = dict(invuCharges=0, protectedBuffs=3.0, manaCost=4.0)
        elif self.king_mode:
            for identity,facts in self.runtime_inputs.data['king_particles'].items():
                self.king_states[identity]=dict(invuCharges=0,protectedBuffs=3.0,manaCost=4.0,crown=0,
                    visible=False,emitting=False,drag_visible=False,drag_emitting=False,
                    light_visible=True,light_modulate=[1.0,1.0,1.0,1.0],particle_facts=deepcopy(facts['activation']['getters']if self.integration_mode else facts))
        self._connect_runtime_callbacks()
        self.frame_driver=(HeadlessKingFrameDriver(self) if self.source_king_mode else EngineFrameDriver(self)) if self.king_mode else None
        if self.king_mode:
            for role in self.ordinary_roles:
                if role!='util':
                    node=self.runtime_roles[role]
                    self.timer_runtime.connect_ordinary(node,lambda node,delta,role=role:self._king_ordinary(role,delta),0)
                    active=self.processing_inputs[role]['ordinary_physics']if self.integration_mode else True
                    self.timer_runtime.set_ordinary_processing(node,active,0)
            if self.integration_mode:
                for role in self.ordinary_roles:
                    if role=='util':continue
                    if self.processing_inputs[role]['ordinary_idle']:
                        self.timer_runtime.connect_ordinary(self.runtime_roles[role],lambda node,delta,role=role:self._source_noninterfering_callback(role,1,delta),1)
                        self.timer_runtime.set_ordinary_processing(self.runtime_roles[role],True,1)
        if self.pure_combat_mode:
            self._validate_pure441_constructed()
            self.pure_snapshots.append(self._pure_business_snapshot('constructed_off_clock'))

    def _validate_pure441_constructed(self):
        data = self.runtime_inputs.data
        for side, values in data['initial_characters'].items():
            char = self.characters[side]
            if (char.invulnerable is not values['invulnerable'] or self.invu_origins[side] != values['invulnerabilityItem']
                    or char.buff_protect_stacks != values['buffProtectStacks']):
                raise ValueError('constructed character differs from supported441 values')
        for identity, values in data['initial_items'].items():
            item = self.items[identity]
            if (_float_bits(item.last_activation_time) != values['lastActivationTime_bits']
                    or _float_bits(item.last_trigger_time) != values['lastTriggerTime_bits']
                    or item.activations_this_frame != values['activationsThisFrame']
                    or item.triggers_this_frame != values['triggersThisFrame']
                    or (not self.prepared and item.cache_prepared) or values['dragged'] or values['moveback_running']):
                raise ValueError('constructed emitted item scalar mismatch')
        for role, initial in data['timer_initial'].items():
            _assert_pure441_timer(self.runtime_roles[role], initial)
        if self.random.position != 0 or self.random.audit:
            raise ValueError('fixed441 constructor may not consume activation Tape')

    def _validate_pure441_prepared(self):
        self._validate_pure441_constructed()
        if not self.prepared or self.king_states['P:12']['invuCharges'] != self.items['P:12'].definition['charges']:
            raise ValueError('pure King prepare business state mismatch')

    def _pure_business_snapshot(self, stage):
        off_clock = stage in ('constructed_off_clock', 'prepare_off_clock')
        d = getattr(self, 'frame_driver', None)
        clock = None if off_clock else dict(phase=d.phase, physics_frame=d.physics_frame,
            idle_frame=d.idle_frame, util_time_bits=_float_bits(d.util_time),
            util_clock_time_bits=_float_bits(d.util_clock_time), util_frame_counter=d.util_frame_counter,
            passes_consumed=d.pass_index, ending=d.ending, cleaned=d.cleaned, finalized=d.finalized,
            physics_signals_remaining=d.physics_signals_remaining)
        timers = {r:dict(public=self._public_timer(n),private_left_bits=_float_bits(n.private_left),processing=n.processing)
                  for r,n in self.runtime_roles.items() if isinstance(n,TimerRecord)}
        items = {identity:dict(lastActivationTime_bits=_float_bits(item.last_activation_time),
                    lastTriggerTime_bits=_float_bits(item.last_trigger_time),activationsThisFrame=item.activations_this_frame,
                    triggersThisFrame=item.triggers_this_frame,cache_prepared=item.cache_prepared,consumed=item.consumed,
                    iterationCooldown_bits=_float_bits(item.iteration_cooldown),triggerTime_bits=_float_bits(item.trigger_time),
                    speedScale_bits=_float_bits(item.speed_scale),goobert_activations=item.goobert_activations,potion_full=item.potion_full)
                 for identity,item in self.items.items()}
        return dict(schema='phase443-business-snapshot/1',stage=stage,clock=clock,off_clock=off_clock,
            combat_time_bits=_float_bits(self.time),timers=timers,
            processing_nodes=[self._integration_node(n['role']) for n in self.runtime_inputs.data['processing_nodes']],
            characters={s:asdict(c) for s,c in self.characters.items()},items=items,
            model_current_target_cache={k:[i.instance_id for i in v] for k,v in self.affected_items_cache.items()},
            king=deepcopy(self.king_states),invu_origins=deepcopy(self.invu_origins),
            event_num=self.event_num,events=deepcopy(self.events),allocated_events=deepcopy(self.allocated_events),
            histories=self.histories.snapshot(),logging_mode=self.logging_mode,pending_signals=len(self.signal_queue),
            tape_position=self.random.position,tape_audit_length=len(self.random.audit))

    def _pure_api_before(self, role, operation, args):
        self.pure_api_trace.append(dict(edge='before',operation=operation,role=role,argc=len(args),
            args=[_pure441_variant(x) for x in args],state=self._full_timer(self.runtime_roles[role]),
            phase=self.frame_driver.phase,physics_frame=self.frame_driver.physics_frame,idle_frame=self.frame_driver.idle_frame))

    def _pure_api_after(self, role, operation, args, helper_status):
        self.pure_api_trace.append(dict(edge='after',operation=operation,role=role,argc=len(args),
            args=[_pure441_variant(x) for x in args],state=self._full_timer(self.runtime_roles[role]),
            helper_status=helper_status,native_return_semantics=dict(typed={'type':'null'},basis='SOURCE_VOID_NOT_SAMPLED'),
            phase=self.frame_driver.phase,physics_frame=self.frame_driver.physics_frame,idle_frame=self.frame_driver.idle_frame))

    def _set_source_processing(self,role,enabled,source):
        if not self.integration_mode:return
        node=self.runtime_roles[role];before=node.ordinary_physics
        self.timer_runtime.set_ordinary_processing(node,enabled,0)
        self.runtime_trace.append(dict(kind='source_processing',role=role,source=source,before=before,after=node.ordinary_physics))

    def _set_item_cooldown(self,item,enabled,source):
        item.cooldown_active=enabled
        self._set_source_processing('item:'+item.instance_id,enabled,source)

    def _integration_callback(self,role,mode,delta):
        d=self.frame_driver
        self.runtime_trace.append(dict(kind='source_callback',role=role,mode=mode,physics_frame=d.physics_frame,idle_frame=d.idle_frame,
            phase=d.phase,delta_bits=None if delta is None else _float_bits(delta),combat_time_bits=_float_bits(self.time),
            util_time_bits=_float_bits(d.util_time),util_clock_time_bits=_float_bits(d.util_clock_time)))

    def _source_noninterfering_callback(self,role,mode,delta):
        if not self.integration_mode or not(role=='game' or mode==1 and role.startswith('item:')):
            raise ValueError('unknown noninterference callback')
        self._integration_callback(role,mode,delta)
        if self.pure_combat_mode:
            self.diagnostics.append(dict(kind='pure_shared_callback_domain',role=role,mode=mode,
                scope='443 fixed shared Game/Item business and selected-call guard; external pre-run closure required'))
            return
        self.diagnostics.append(dict(kind='source_ui_noninterference',role=role,mode=mode,lemma='127-complete-zero-unsupported-ui-authority'))

    def _integration_node(self,role):
        row=deepcopy(self.processing_inputs[role])
        node=self.timer_runtime.root if role=='root_viewport'else self.runtime_roles.get(role)
        if node is not None:
            for key in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle'):row[key]=getattr(node,key)
            row['inside_tree']=node.inside_tree
        return row

    def _integration_aux_timer(self,role):
        x=self.runtime_inputs.data['inactive_auxiliaries'][role]
        return dict(node=self._integration_node(role),process_mode=x['process_mode'],wait_time_bits=x['wait_time_bits'],time_left_bits=_float_bits(0.),one_shot=x['one_shot'],autostart=False,paused=False,stopped=True)

    def _integration_timer(self,role):
        if role in AUX_ROLES:return self._integration_aux_timer(role)
        node=self.runtime_roles[role];rt=self.timer_runtime
        return dict(node=self._integration_node(role),process_mode=node.process_mode,wait_time_bits=_float_bits(node.wait_time),time_left_bits=_float_bits(rt.time_left(node)),one_shot=node.one_shot,autostart=node.autostart,paused=node.paused,stopped=rt.is_stopped(node))

    def _integration_fx_snapshot(self):
        d=self.frame_driver
        timers={role:self._integration_timer(role)for role,node in self.runtime_roles.items()if isinstance(node,TimerRecord)}
        timers.update({role:self._integration_aux_timer(role)for role in AUX_ROLES})
        particles={}
        for identity,state in self.king_states.items():
            particles[identity]=dict(activation=dict(state['particle_facts'],node=deepcopy(self.runtime_inputs.data['king_particles'][identity]['activation']['node']),visible=state['visible'],emitting=state['emitting']),drag=dict(self.runtime_inputs.data['king_particles'][identity]['drag']['getters'],node=deepcopy(self.runtime_inputs.data['king_particles'][identity]['drag']['node']),visible=state['drag_visible'],emitting=state['drag_emitting']),light_visible=state['light_visible'],light_modulate_bits=[_float_bits(x)for x in state['light_modulate']])
            # Initial getter dictionary also contains visible/emitting; runtime flags win.
            particles[identity]['activation'].update(visible=state['visible'],emitting=state['emitting'])
            particles[identity]['drag'].update(visible=state['drag_visible'],emitting=state['drag_emitting'])
        return dict(schema='phase134-complete-public-fx/1',root=self._integration_node('root_viewport'),timers=timers,particles=particles,
            physics_frame=d.physics_frame,idle_frame=d.idle_frame,util_time_bits=_float_bits(d.util_time),util_clock_time_bits=_float_bits(d.util_clock_time),util_frame_counter=d.util_frame_counter,
            is_in_physics_frame=d.phase.startswith('physics_')or d.phase.endswith('_physics'),
            private_timers={role:_float_bits(node.private_left)for role,node in self.runtime_roles.items()if isinstance(node,TimerRecord)}|{role:_float_bits(-1.)for role in AUX_ROLES},
            processing_nodes=[self._integration_node(n['role'])for n in self.runtime_inputs.data['processing_nodes']])


    def _connect_runtime_callbacks(self):
        for role, node in self.runtime_roles.items():
            if isinstance(node, TimerRecord):
                self.timer_runtime.connect_timeout(node, lambda timer, role=role: self._timer_timeout(role))

    def _public_timer(self, node):
        def primitive(value):
            if type(value) is list:return [primitive(v) for v in value]
            if type(value) is not dict:raise ValueError('unknown component primitive')
            kind=value.get('type')
            if kind=='float':return struct.unpack('<d',bytes.fromhex(value['binary64_le']))[0]
            if kind=='int':return int(value['decimal'])
            if kind in ('bool','string'):return value['value']
            raise ValueError('unknown component public field')
        return {key:primitive(value)for key,value in self.timer_runtime.timer_state(node).items()}

    def _timer_snapshot(self):
        return {role:self._public_timer(node)for role,node in self.runtime_roles.items()if isinstance(node,TimerRecord)}

    def _start_timer(self, role, *args):
        if len(args)>1:raise ValueError('Timer.start supports zero or one argument')
        duration=args[0] if args else 0.0
        if type(duration) not in (int,float):raise ValueError('Timer.start numeric Variant required')
        timer=self.runtime_roles[role]
        if self.pure_combat_mode:
            self._pure_api_before(role,'start',args)
        if self.king_mode:self.runtime_trace.append(dict(kind='api_full_before',api='start',role=role,state=self._full_timer(timer)))
        self.runtime_trace.append(dict(kind='start_before',role=role,argument=float(duration),util_time=self.util_time,frame=self.frame))
        result=self.timer_runtime.start(timer,float(duration))
        if self.pure_combat_mode:
            self._pure_api_after(role,'start',args,dict(ok=result.ok,error=result.error))
        if not result.ok:raise ValueError(result.error)
        self.runtime_trace.append(dict(kind='start_after',role=role,public=self._public_timer(timer),util_time=self.util_time,frame=self.frame))
        if self.king_mode:self.runtime_trace.append(dict(kind='api_full_after',api='start',role=role,state=self._full_timer(timer)))

    def _stop_timer(self, role):
        if self.pure_combat_mode:self._pure_api_before(role,'stop',())
        if self.king_mode:self.runtime_trace.append(dict(kind='api_full_before',api='stop',role=role,state=self._full_timer(self.runtime_roles[role])))
        self.timer_runtime.stop(self.runtime_roles[role])
        if self.pure_combat_mode:self._pure_api_after(role,'stop',(),None)
        self.runtime_trace.append(dict(kind='stop',role=role,public=self._public_timer(self.runtime_roles[role]),util_time=self.util_time,frame=self.frame))
        if self.king_mode:self.runtime_trace.append(dict(kind='api_full_after',api='stop',role=role,state=self._full_timer(self.runtime_roles[role])))

    def _timer_timeout(self, role):
        if self.integration_mode:self._integration_callback(role,self.runtime_roles[role].process_mode,None)
        self.runtime_trace.append(dict(kind='timeout_enter',role=role,frame=self.frame,util_time=self.util_time))
        if role.startswith('rage:'):self.end_battle_rage(role[-1])
        elif role.startswith('invu:'):self.invu_timeout(role[-1])
        elif role.startswith('king_buff:'):self.king_buff_timeout(self.items[role[len('king_buff:'):]])
        elif role.startswith('king_hide:'):self.king_states[role[len('king_hide:'):]]['visible']=False
        elif role.startswith('king_drag:'):raise ValueError('fresh no-drag timer cannot time out')
        elif role.startswith('buff:'):
            _,side,stack=role.split(':');self.buff_timeout(side,stack)
        elif role.startswith('particle:'):
            item=self.items[role[len('particle:'):]]
            if item.item_index==53:self.light_particle_timeout(item)
            else:self.carrot_particle_timeout(item)
        elif role.startswith('tick:'):
            side=role[-1];char=self.characters[side];self.mark_schedule('character_tick:'+side,0.0)
            if self.tick_counter[side]%2==0 and char.regeneration>0:self.heal(side,char.regeneration,102)
            elif self.tick_counter[side]%2==1 and char.poison>0:self.damage_nonitem(side,char.poison,108)
            self.tick_counter[side]+=1
        elif role=='fatigue:start':self._start_timer('fatigue:tick',3 if self.pure_combat_mode else 3.0)
        elif role=='fatigue:tick':
            self.fatigue_tick();self._start_timer('fatigue:tick',1 if self.pure_combat_mode else 1.0)
        else:raise ValueError('unknown Timer callback role')
        self.runtime_trace.append(dict(kind='timeout_exit',role=role,frame=self.frame,util_time=self.util_time))

    def _full_timer(self,node):
        return dict(public=self.timer_runtime.timer_state(node),private_left=timer_component.typed(node.private_left),
                    processing=timer_component.typed(node.processing))

    def _king_ordinary(self,role,delta):
        # Same source ordinary receiver bodies as the frozen physics path.
        if self.integration_mode:
            if role=='game':return self._source_noninterfering_callback(role,0,delta)
            self._integration_callback(role,0,delta)
        if role=='combat_timer':
            self.mark_schedule('timer',delta);self.time+=delta
        elif role.startswith('character:'):
            side=role[-1];char=self.characters[side];self.mark_schedule(role,delta)
            if char.stunned>0:
                char.stunned-=delta
                if char.stunned<=0:self.end_stun(side)
            char.stamina=max(0.0,min(char.max_stamina,char.stamina+char.stamina_regen*delta))
        elif role.startswith('item:'):
            item=self.items[role[len('item:'):]]
            if item.cooldown_active:
                self.mark_schedule(role,delta)
                if self.characters[item.side].stunned==0:
                    item.trigger_time-=delta*self.speed(item)
                    if item.trigger_time<=0:self.trigger(item)
        else:raise ValueError('unknown ordinary King domain role')

    def king_prepare(self,item):
        state=self.king_states[item.instance_id]
        # getGemsNoNull is empty by closed input contract. Socket support remains open.
        state['invuCharges']=int(item.definition['charges'])
        self.king_set_state(item,0)

    def king_set_state(self,item,state,next_event=False):
        if item.item_index!=262 or type(state)is not int or state not in (0,1,2):
            raise ValueError('King CrownState integer required')
        self.histories.item_state(item,state,next_event=next_event)
        if self.pure_combat_mode:return
        k=self.king_states[item.instance_id];k['crown']=state
        if state==1:
            self._stop_timer('king_hide:'+item.instance_id)
            k['visible']=True;k['emitting']=True
            k['light_modulate']=[f32(1.3),f32(1.3),f32(1.3),1.0];k['light_visible']=True
        else:
            if k['visible']:
                k['emitting']=False
                facts=k['particle_facts']
                duration=_be_float(facts['lifetime_bits'])*(1+(1-_be_float(facts['explosiveness_bits']))/_be_float(facts['speed_scale_bits']))
                self._start_timer('king_hide:'+item.instance_id,duration)
            if state==0:k['light_modulate']=[1.0,1.0,1.0,1.0];k['light_visible']=True
            else:k['light_visible']=False

    def king_effect(self,item):
        if item.item_index!=262:raise ValueError('King caller required')
        k=self.king_states[item.instance_id];character=self.characters[item.side]
        self.change_buff_protect_stacks(item.side,k['protectedBuffs'])
        self.heal(item.side,item.definition['heal'],item.instance_id)
        if k['invuCharges']>0 and not character.invulnerable and character.mana>=k['manaCost']:
            k['invuCharges']-=1
            self.king_set_state(item,1,True)
            event=self.make_invulnerable(item,item.definition['duration'])
            self._start_timer('king_buff:'+item.instance_id,item.definition['duration'])
            self.use_stack(item,item.side,'Mana',k['manaCost'],event['id'])
            self.runtime_trace.append(dict(kind='source_visual_pulse',item=item.instance_id,frame=self.frame,util_time=self.util_time))

    def make_invulnerable(self,item,duration):
        if item.item_index!=262 or duration!=1.5 or type(duration)is not float:
            raise ValueError('only default King makeInvulnerable caller admitted')
        side=item.side;char=self.characters[side]
        if char.invulnerable:raise ValueError('generic active invulnerability extension not admitted')
        self.invu_origins[side]=item.instance_id
        self._start_timer('invu:'+side,duration)
        char.invulnerable=True;self.invu_bubbles[side]=True
        pitch=self.random.randf_range('invulnerability_pitch:'+item.instance_id,1-0.1,1+0.1)
        self.runtime_trace.append(dict(kind='source_invu_sound_pitch',item=item.instance_id,pitch=pitch))
        event=self.emit(item.instance_id,'InvulnerableStart',{'duration':duration},target=0 if side=='P' else 1)
        self.histories.character(side,4,event_num=event['id'])
        return event

    def invu_timeout(self,side):
        self.characters[side].invulnerable=False
        event=self.emit(self.invu_origins[side],'InvulnerableEnd',target=0 if side=='P' else 1)
        self.histories.character(side,4,event_num=event['id'])
        self.invu_bubbles[side]=False

    def king_buff_timeout(self,item):
        self.king_set_state(item,0 if self.king_states[item.instance_id]['invuCharges']>0 else 2,True)

    def _ordered_stars(self,item,layer='stars'):
        if layer not in ('stars','secondary_stars'):raise ValueError('unknown source affected layer')
        body=list(item.definition['shape']);stars=list(item.definition.get(layer,()))
        for _ in range(item.orientation):body=[(-y,x)for x,y in body];stars=[(-y,x)for x,y in stars]
        minx=min(x for x,y in body);miny=min(y for x,y in body)
        return [(x-minx+item.top_left[0],y-miny+item.top_left[1])for x,y in stars]

    def _fresh_goobert_targets(self,item):
        result=[];seen=set()
        for cell in self._ordered_stars(item):
            for other in self.side_items[item.side]:
                if not other.definition['bag'] and cell in other.cells and other.can_activate and other.instance_id not in seen:
                    seen.add(other.instance_id);result.append(other)
        return result

    def give_stacks_temporary(self,item,side,stack,amount,duration,parent=None):
        if amount<=0:return None
        _,name=self._buff_record(side,stack)
        rounded=int(self._fraction_round(amount*item.buff_powers[EVENT_TYPES[name]]))
        return self.gain_stacks_temporary(side,name,rounded,duration,item,parent)

    def change_current_log_show_label(self,side,stack,amount,item=None,parent=None,timeout=False):
        char=self.characters[side];change=min(getattr(char,stack.lower()),amount)
        if change>0:
            setattr(char,stack.lower(),getattr(char,stack.lower())-change)
            if item is not None:
                self._stack_metric(item,side,stack,-change)
                return self.stack_event(item,side,stack,-change,parent,notify=True,timeout=timeout)
        return None

    def buff_timeout(self,side,stack):
        fields,name=self._buff_record(side,stack)
        index=fields['nextTemporaryTimeout'];entries=fields['temporaryStacks']
        if type(index)is not int or not 0<=index<len(entries):raise ValueError('unclosed native invalid temporary index')
        entry=entries[index]
        item=self.items[entry.item_id]if entry.item_id is not None else None
        self.change_current_log_show_label(side,name,entry.amount,item,timeout=True)
        index=fields['nextTemporaryTimeout']
        if not 0<=index<len(entries):raise ValueError('unclosed synchronous temporary-list mutation')
        entries.pop(index)
        if entries:
            earliest=float('inf');selected=-1
            for i,candidate in enumerate(entries):
                if candidate.timeout<earliest:earliest=candidate.timeout;selected=i
            fields['nextTemporaryTimeout']=selected
            delay=earliest-self.util_time
            if delay<=.01:self.buff_timeout(side,name)
            else:self._start_timer('buff:'+side+':'+name,delay)

    def _blood_effect_domain(self,item):
        if item.item_index!=54:raise ValueError('unsupported effect damage caller')
        for character in self.characters.values():
            if (character.crit_resistance!=0.0 or character.crit_resist_stacks!=0 or character.crit_tokens!=0
                    or character.healing_efficiency!=1.0 or character.unhealing_amount!=0.0):
                raise ValueError('unclosed effect critical/healing resource modifier')
        if getattr(item,'crit_tokens',0)!=0 or getattr(item,'crit_severity',2.0)!=2.0 or getattr(item,'bonus_damage_factor',1.0)!=1.0:
            raise ValueError('unclosed effect item modifier')

    def take_effect_damage(self,item,base_damage,parent=None):
        self._blood_effect_domain(item)
        attacker=self.characters[item.side]
        defender=self.characters['O' if item.side=='P' else 'P']
        modified=base_damage*(1.0+attacker.typed_damage_factors[2])
        if type(modified)not in (int,float) or not math.isfinite(modified) or not -(2**63)<=modified<2**63:
            raise ValueError('undefined source effect INT conversion')
        # DamageSource.updateEffect writes typed INT min/max, then takeDamage clones it.
        amount=int(modified)
        source=dict(origin=item.instance_id,types=[2],flags=41,minDamage=amount,maxDamage=amount,accuracy=100.0,critChancePercent=max(0.0,min(100.0,item.crit_chance)))
        result=dict(event=None,damageSource=source,damage=0,healthDamage=0,hit=False,critical=False,damageReduction=0)
        if defender.dead:return result
        self.attack_effect_count(item)  # Native call exists for Effect too; Util.flip consumes a draw even at default chance0.
        result['hit']=True
        damage=item.damage_range.draw(source['minDamage'],source['maxDamage'],self.random,'damage:'+item.instance_id)
        critical=False
        if source['critChancePercent']>0:
            critical=defender.critical.roll_percent(source['critChancePercent'],self.random,'critical:'+defender.side+':'+item.instance_id)
        if critical:
            defender.crit_resistance_rng.roll_percent(0.0,self.random,'crit_resistance:'+defender.side)
            damage*=2
        resistance=max(-10.0,min(1.0,defender.damage_resistance/100.0))
        damage=int(self._fraction_round(damage*(1.0-resistance)))
        # Effect does not subtract attack-only Character.damageReduction. No selected
        # pre_take_damage receiver accepts this non-melee source (source ledger).
        if defender.invulnerable:damage=0
        damage=max(0,damage)
        result['damage']=damage;result['critical']=critical
        blocked=min(defender.block,damage)
        self.remove_stack(None,defender.side,'Block',blocked)
        result['healthDamage']=damage-blocked
        defender.hp-=result['healthDamage']
        event=self.allocate_event(item.instance_id,'CriticalDamage' if critical else 'DealDamage',{'damage':damage},parent=parent)
        self.histories.character(defender.side,0);self.histories.stack(defender.side,100)
        item.damage+=damage;self.histories.item_metric(item,0,damage)
        result['event']=event
        self.emit_event(event)
        self.on_character_attacked(defender.side,True,[],event)
        self.on_character_damaged(defender.side,event)
        if defender.hp<=0:self.death(defender)
        # Effect flags41 exclude passive spikes/vampirism and own attack hooks.
        return result

    def steal_life(self,item,damage,lifesteal_factor=1.0,parent=None):
        self._blood_effect_domain(item)
        if type(lifesteal_factor)not in (int,float) or not math.isfinite(lifesteal_factor):raise ValueError('invalid lifesteal factor')
        result=self.take_effect_damage(item,damage,parent)
        # Item.heal has a typed INT amount BEFORE Character.heal rounds it.
        heal_amount=int(result['damage']*float(lifesteal_factor))
        event=result['event']
        self.heal(item.side,heal_amount,item.instance_id,event['id']if event is not None else None)
        return result

    def blood_effect(self,item):
        return self.steal_life(item,item.definition['effect_damage']+self.characters[item.side].vampirism,item.definition['lifesteal_factor'])

    def carrot_effect(self,item):
        self.set_item_state(item,True,next_event=True)
        self.cleanse_random_debuffs(item,4)
        self.give_stacks_temporary(item,item.side,'Empower',item.definition['empower'],item.definition['duration'])
        self._stop_timer('particle:'+item.instance_id)
        self._start_timer('particle:'+item.instance_id,item.definition['duration'])

    def carrot_particle_timeout(self,item):
        self.set_item_state(item,False)

    def light_effect(self,item):
        self.set_item_state(item,True,next_event=True)
        self.heal(item.side,item.definition['heal'],item.instance_id)
        self.give_stacks_temporary(item,"O" if item.side=="P" else "P",'Blind',item.definition['blind'],item.definition['duration'])
        self._stop_timer('particle:'+item.instance_id)
        self._start_timer('particle:'+item.instance_id,item.definition['duration'])

    def light_particle_timeout(self,item):
        self.set_item_state(item,False)

    def _runtime_projection(self):
        result = dict(mode=self.runtime_inputs.data['mode'],profile=self.runtime_inputs.data['profile_id'],
                    util_time=self.util_time,combat_time=self.time,activated=self.activated,
                    pending_terminal=self.pending_terminal,terminal_profile=self.runtime_inputs.data['terminal_profile'],
                    timers=self._timer_snapshot(),ordinary_order=list(self.ordinary_roles))
        if self.king_mode:
            d=self.frame_driver
            result.update(util_clock_time=d.util_clock_time,util_frame_counter=d.util_frame_counter,
                          phase=d.phase,passes_consumed=d.pass_index,physics_frame=d.physics_frame,idle_frame=d.idle_frame,
                          full_timers={r:self._full_timer(n) for r,n in self.runtime_roles.items() if isinstance(n,TimerRecord)},
                          king=deepcopy(self.king_states),invu_origins=deepcopy(self.invu_origins),**({} if self.pure_combat_mode else dict(invu_bubbles=deepcopy(self.invu_bubbles))))
        return result


    def mark_schedule(self, label, delta):
        self.schedule_trace.append(dict(frame=self.frame, label=label,
                                        delta_hex=struct.pack(">d", delta).hex(),
                                        timestamp_hex=struct.pack(">d", self.time).hex()))

    def allocate_event(self, origin, event_type, params=None, target=None, parent=None):
        """CombatLog.createEvent: ID/stamina histories change before any logging."""
        self.event_num += 1
        for side in ("P", "O"):
            self.histories.character(side, 2)
        event = dict(sequence=None, id=self.event_num, timestamp=self.time,
                     timestamp_hex=struct.pack(">d", self.time).hex(), parent=parent,
                     origin=origin, target=target, type=EVENT_TYPES[event_type],
                     params=dict(params or {}), snapshot=None)
        self.allocated_events[self.event_num] = event
        return event

    def emit(self, origin, event_type, params=None, target=None, parent=None, after_fight=False):
        event = self.allocate_event(origin, event_type, params, target, parent)
        self.emit_event(event, after_fight=after_fight)
        return event

    def set_logging_mode(self, mode):
        if type(mode) is not int or mode not in (0, 1, 2):
            raise ValueError("unknown EventBus logging mode")
        self.logging_mode = mode

    def emit_event(self, event, signal=None, after_fight=False):
        if self.logging_mode == 2:
            self.signal_queue.append((event, signal, after_fight))
        else:
            self._emit_and_log(event, signal, after_fight)

    def _emit_and_log(self, event, signal=None, after_fight=False):
        # logEvent does not rewind event_num to this queued event's ID.
        if event is not None and (not self.ended or after_fight):
            event["sequence"] = len(self.events)
            self.events.append(event)
        if signal is not None and not self.ended:
            side, stack_type, amount = signal
            if stack_type == "CharacterDamaged":
                self.on_character_damaged(side, event)
                return
            if stack_type in ("BattleRageStart", "BattleRageEnd"):
                self.on_battle_rage(side, stack_type == "BattleRageStart", event)
                return
            if stack_type == "Lucky":
                self.lucky_changed(side, amount)
            self.on_stack_changed(side, stack_type, amount, event)

    def flush_logging_queue(self):
        self.set_logging_mode(1)
        pending = self.signal_queue.copy()
        self.signal_queue.clear()
        for event, signal, after_fight in pending:
            self._emit_and_log(event, signal, after_fight)

    def adjust_cooldown(self, item):
        low = 0.975 if item.side == "O" and self.fixture["below_master"] else 0.95
        return item.definition["cooldown"] * self.random.randf_range(f"cooldown:{item.instance_id}", low, 1.05)

    def ruby_effect(self, item, with_reflect_stacks=True):
        if (self.items.get(getattr(item, 'instance_id', None)) is not item
                or item.item_index != 62 or type(with_reflect_stacks) is not bool):
            raise ValueError("owned Ruby caller and strict BOOL flag required")
        if with_reflect_stacks:
            self.change_debuff_reflection(item.side, item.definition["reflect_stacks"])
        self.give_stack(item, item.side, "Heat", item.definition["heat"])
        self.activate(item)

    def prepare_only(self):
        if self.prepared:
            raise ValueError("combat already prepared")
        for side, character in self.characters.items():
            bias = (-0.2 if side == "P" else 0.2) if self.fixture["below_master"] else 0.0
            character.accuracy.reset(bias)
            character.critical.reset(bias)
            character.crit_resistance_rng.reset()
            character.stun_resistance_rng.reset()
        for identity in self.preparation_order:
            bag = self.items[identity]
            if bag.double_attack_effect_chance != 0.0:
                raise ValueError("unsupported nonzero double attack effect modifier")
            if bag.item_index in (26, 67, 405, 129):
                inside = self.inside_items(bag)
                self.bag_inside_cache[identity] = inside
                if bag.item_index == 405:
                    self.bag_affected_inside_cache[identity] = [
                        item for item in inside if GAINED_STACK_FLAGS[item.item_index] & 254]
                elif bag.item_index == 129:
                    self.bag_affected_inside_cache[identity] = [item for item in inside if item.has_cooldown]
                    bag.rage_has_activated = False
                    self.rage_listeners[bag.side].append(identity)
                elif bag.item_index == 26:
                    self.bag_affected_inside_cache[identity] = [
                        item for item in inside if item.has_cooldown and not item.definition["bag"]]
                else:
                    self.bag_affected_inside_cache[identity] = [item for item in inside if item.can_damage]
            if bag.item_index == 39:
                if any(item.item_index == 286 for item in self.side_items[bag.side]):
                    raise ValueError("unsupported Acorn Ace extended stars and stamina modifier")
                self.collar_targets[identity] = self.affected_items(bag)
            if bag.item_index==262:self.king_prepare(bag)
            if bag.item_index in GOOBERT_IDS:
                if bag.double_activation_chance != 0.0:
                    raise ValueError("unsupported nonzero Goobert double activation modifier")
                bag.goobert_activations = 0
                bag.iteration_cooldown = float(bag.definition["activations_to_trigger"])
                bag.trigger_time = bag.iteration_cooldown
                self.histories.tooltip(bag, 9)
                for affected in self.affected_items(bag):
                    self.activation_listeners.setdefault(affected.instance_id, []).append(bag.instance_id)
            bag.cache_prepared = True
            bag.chance_rng.reset()
            bag.damage_range.acc = 0.0
            bag.spikes_given = 0
            if bag.item_index == 52:
                bag.steel_affected_weapons.extend(self.steel_secondary_cache[bag.instance_id])
            if bag.item_index in STATE_PARTICLE_IDS:
                self.set_item_state(bag, False)
            if bag.item_index == 14:
                bag.spear_block_removal = (bag.definition["block_per_empty_cell"]
                                          * self.empty_affected_cells(bag))
            if bag.item_index == 34:
                bag.boots_has_activated = False
            if bag.definition.get("potion"):
                self.set_item_state(bag, True)
            if bag.item_index == 67:
                inside = self.inside_items(bag)
                if inside:
                    self.lucky_listeners[bag.side].append((identity, inside, 3.0))
                for item in inside:
                    item.crit_chance += 12.0
                    self.histories.tooltip(item, 6)
            if bag.item_index == 351:
                self.change_buff_protection_chance(bag.side, bag.definition["chance"])
                for name in ("Blind", "Cold"):
                    self.change_resist_chance(bag.side, name, bag.definition["chance2"])
            if bag.item_index == 332:
                chance = bag.definition["chance"] + len(self.affected_items(bag)) * bag.definition["chance2"]
                for name in DEBUFF_TYPES:
                    self.change_reflect_chance(bag.side, name, chance)
            if bag.item_index == 374:
                self.change_debuff_protection_chance(bag.side, -bag.definition["chance"])
                bag.speed_scale += bag.definition["potion_speed"] * len(self.affected_items(bag))
                self.histories.tooltip(bag, 3)
                self.histories.tooltip(bag, 9)
            if bag.item_index == 405:
                for affected in self.bag_affected_inside_cache[identity]:
                    for name in range(101, 108):
                        self.change_amplification(affected, name, bag.definition["chance"])
            if bag.item_index == 39 and self.collar_targets[identity]:
                self.lucky_listeners[bag.side].append(
                    (identity, self.collar_targets[identity], bag.definition["crit_per_lucky"]))
            if bag.definition.get("food"):
                bag.speed_scale += 0.1 * len(self.affected_items(bag))
                self.histories.tooltip(bag, 3)
                self.histories.tooltip(bag, 9)
            if bag.item_index == 179:
                speed = 0.0
                for affected in self.affected_items(bag):
                    speed += bag.definition["spell_speed"] * (2 if affected.definition.get("ice") else 1)
                bag.speed_scale += speed
                self.histories.tooltip(bag, 3)
                self.histories.tooltip(bag, 9)
        self.prepared = True
        if self.pure_combat_mode:
            self._validate_pure441_prepared()
            self.pure_snapshots.append(self._pure_business_snapshot('prepare_off_clock'))

    def activate_from_checkpoint(self):
        if self.king_mode and not self.frame_driver.activated:
            if not self.prepared:raise ValueError('activate requires prepared combat')
            return self.frame_driver.activate(lambda driver:self.activate_from_checkpoint())
        if not self.prepared or self.activated:
            raise ValueError('activation requires prepared/unactivated')
        if self.pure_combat_mode:
            self._validate_pure441_prepared()
            self.pure_snapshots.append(self._pure_business_snapshot('pre_activate'))
        self.util_time = self.runtime_inputs.util_time
        for identity, fields in self.runtime_inputs.data['initial_items'].items():
            item = self.items[identity]
            item.last_activation_time = _be_float(fields['lastActivationTime_bits'])
            item.activations_this_frame = fields['activationsThisFrame']
            item.last_trigger_time = _be_float(fields['lastTriggerTime_bits'])
            item.triggers_this_frame = fields['triggersThisFrame']
        self.activated = True
        self._stop_timer('fatigue:start'); self._stop_timer('fatigue:tick')
        self._start_timer('fatigue:start', 14 if self.pure_combat_mode else 14.0)
        if self.integration_mode:
            self._set_source_processing('combat_timer',True,'CombatTimer.start')
            for side in ('P','O'):
                self._set_source_processing('character:'+side,True,'Character.combatStart')
                if self.pure_combat_mode:self._start_timer('tick:'+side)
                else:self._start_timer('tick:'+side,0.0)
        else:self._start_timer('tick:P', 0.0); self._start_timer('tick:O', 0.0)
        # ALL preCombatStart before ANY combatStart.
        for identity in self.preparation_order:
            item = self.items[identity]
            if item.has_cooldown:
                item.iteration_cooldown = self.adjust_cooldown(item)
                item.trigger_time = item.iteration_cooldown
                self._set_item_cooldown(item,True,'Item.activateCooldown')
                self.histories.tooltip(item, 9)
            if item.item_index == 2:
                self.add_bonus_damage(item, len(self.affected_items(item)))
            elif item.item_index == 17:
                self.change_debuff_resistance(item.side, 3)
            elif item.item_index == 62:
                self.change_debuff_reflection(item.side, item.definition["reflect_stacks"])
        for identity in self.preparation_order:
            item = self.items[identity]
            if item.item_index in (29, 82, 83, 84):
                if item.item_index in (29, 82, 84):
                    for affected in self.affected_items(item):
                        self.add_bonus_damage(affected, item.definition["start_damage"])
                if item.item_index == 83:
                    for affected in self.affected_items(item):
                        self.add_speed(affected, item.definition["start_speed"])
                elif item.item_index == 84:
                    for target in self.steel_secondary_cache[item.instance_id]:
                        self.add_speed(self.items[target], item.definition["start_speed"])
                self.activate(item)
            elif item.item_index == 351:
                for affected in self.affected_items(item):
                    self.add_bonus_damage(affected, item.definition["bonus_damage"])
                self.activate(item)
            elif item.item_index == 26:
                if any(other.item_index == 361 for other in self.side_items[item.side]):
                    raise ValueError("unsupported Bagtacular Fanny Pack modifier")
                total_speed = item.definition["bag_speed"]
                active = False
                for other in self.inside_items(item):
                    if other.has_cooldown and not other.definition["bag"]:
                        other.speed_scale += total_speed
                        self.histories.tooltip(other, 3)
                        self.histories.tooltip(other, 9)
                        active = True
                if active:
                    self.activate(item)
            elif item.item_index == 54:
                self.give_stack(item, item.side, "Vampirism", item.definition['vampirism'])
                self.activate(item)
            elif item.item_index == 28:
                self.give_stack(item, item.side, "Vampirism", 1)
                self.activate(item)
            elif item.item_index == 209:
                self.give_stack(item, item.side, "Heat", 2)
                self.activate(item)
            elif item.item_index == 62:
                self.ruby_effect(item, False)
            elif item.item_index == 50:
                self.health_to_block(item,item.definition["start_health"],item.definition["start_block"])
                self.give_stack(item,item.side,"Vampirism",item.definition["vampirism"])
                self.activate(item)
            elif item.item_index == 17:
                self.give_stack(item, item.side, "Block", 45)
                self.activate(item)
            elif item.item_index == 18:
                for affected in self.affected_items(item):
                    affected.speed_scale += 0.2
                    self.histories.tooltip(affected, 3)
                    self.histories.tooltip(affected, 9)
                self.activate(item)
            elif item.item_index == 48:
                self.give_stack(item, item.side, "Vampirism", 2)
                self.give_max_health(item, 20.0)
                self.activate(item)
            elif item.item_index == 24:
                self.give_lucky(item, 1)
                self.activate(item)
                item.consumed = True
            elif item.item_index in (7, 8, 20):
                side = item.side if item.item_index in (7, 8) else ("O" if item.side == "P" else "P")
                self.give_stack(item, side, {7: "Regeneration", 8: "Spikes", 20: "Blind"}[item.item_index],
                                2 if item.item_index == 7 else 1)
                self.activate(item)
                item.consumed = True
            elif item.item_index == 10:
                for affected in self.affected_items(item):
                    self.add_bonus_damage(affected, 1)
                self.activate(item)
        self.prepared = True

    def inside_items(self, bag):
        if not bag.definition["bag"]:
            raise ValueError("inside_items requires a Bag")
        cached = self.bag_inside_cache.get(bag.instance_id)
        if cached:
            return cached
        inside = []
        seen = set()
        for cell in bag.ordered_cells:
            for item in self.side_items[bag.side]:
                if not item.definition["bag"] and cell in item.cells:
                    if item.instance_id not in seen:
                        seen.add(item.instance_id)
                        inside.append(item)
                    break
        return inside

    def empty_affected_cells(self, item):
        """Inventory.isCellEmpty: bag coverage without an ordinary occupant."""
        bag_cells, filled_cells = set(), set()
        for other in self.side_items[item.side]:
            if other.definition["bag"]:
                bag_cells.update(other.cells)
            else:
                filled_cells.update(other.cells)
        return sum(cell in bag_cells and cell not in filled_cells for cell in item.stars)

    def new_caller_target_caches(self):
        """Item.addToInventory initial cell order, then item_added append order."""
        caches = {}
        for sequence in self.side_items.values():
            for position, item in enumerate(sequence):
                if item.item_index not in CACHED_AFFECTED_IDS:
                    continue
                def eligible(other):
                    if other.definition["bag"] or other is item:
                        return False
                    if item.definition.get("food"):
                        return other.definition.get("food", False) and other.item_index != item.item_index
                    if item.item_index in (29, 82, 84):
                        return other.item_index in EMPOWERABLE_WEAPON_IDS
                    if item.item_index in (18,83):
                        return other.has_cooldown
                    if item.item_index == 179:
                        return other.definition.get("spell", False)
                    if item.item_index == 351:
                        return other.can_damage and "min_damage" in other.definition
                    if item.item_index == 332:
                        return other.definition.get("holy", False)
                    if item.item_index in GOOBERT_IDS:
                        return other.can_activate
                    return other.definition.get("potion", False)
                if item.item_index in POTION_IDS:
                    # Source Potion world-UP endpoint; transformed_cells owns DOWN rule.
                    ordered_stars=list(item.stars)  # exactly one source point
                else:
                    rotated_shape = list(item.definition["shape"])
                    stars = list(item.definition["stars"])
                    for _ in range(item.orientation):
                        rotated_shape = [(-y, x) for x, y in rotated_shape]
                        stars = [(-y, x) for x, y in stars]
                    min_x = min(x for x, y in rotated_shape)
                    min_y = min(y for x, y in rotated_shape)
                    ordered_stars = [(x - min_x + item.top_left[0], y - min_y + item.top_left[1])
                                     for x, y in stars]
                targets = []
                seen = set()
                for cell in ordered_stars:
                    for other in sequence[:position]:
                        if not other.definition["bag"] and cell in other.cells:
                            if eligible(other) and other.instance_id not in seen:
                                targets.append(other)
                                seen.add(other.instance_id)
                            break
                for other in sequence[position + 1:]:
                    if eligible(other) and other.cells & item.stars and other.instance_id not in seen:
                        targets.append(other)
                        seen.add(other.instance_id)
                caches[item.instance_id] = targets
        return caches

    def new_steel_secondary_caches(self):
        """Steel/Crossblades secondary keys: initial cells, then additions."""
        caches={}
        for sequence in self.side_items.values():
            for position,item in enumerate(sequence):
                if item.item_index not in (52,84):continue
                def eligible(other):
                    return other.has_cooldown if item.item_index==84 else other.item_index in EMPOWERABLE_WEAPON_IDS
                cells=self._ordered_stars(item,'secondary_stars');targets=[];seen=set()
                for cell in cells:
                    for other in sequence[:position]:
                        if eligible(other) and cell in other.cells and other.instance_id not in seen:
                            targets.append(other.instance_id);seen.add(other.instance_id)
                affected=set(cells)
                for other in sequence[position+1:]:
                    if eligible(other) and other.cells&affected and other.instance_id not in seen:
                        targets.append(other.instance_id);seen.add(other.instance_id)
                caches[item.instance_id]=targets
        return caches

    def affected_items(self, item):
        if item.item_index in GOOBERT_IDS and not item.cache_prepared:
            return self._fresh_goobert_targets(item)
        if item.item_index in CACHED_AFFECTED_IDS:
            return self.affected_items_cache[item.instance_id]
        if item.item_index == 14:
            return []
        if item.item_index == 39:
            targets = []
            seen = set()
            for x, y in item.definition["stars"]:
                for _ in range(item.orientation):
                    x, y = -y, x
                cell = (x + item.top_left[0], y + item.top_left[1])
                for other in self.side_items[item.side]:
                    if not other.definition["bag"] and cell in other.cells:
                        if other.can_damage and other.instance_id not in seen:
                            seen.add(other.instance_id)
                            targets.append(other)
                        break
            return targets
        candidates = [other for other in self.side_items[item.side]
                      if other is not item and other.cells & item.stars and not other.definition["bag"]]
        if item.definition.get("food"):
            return [other for other in candidates if other.definition.get("food") and other.item_index != item.item_index]
        if item.definition.get("potion"):
            return [other for other in candidates if other.definition.get("potion")]
        if item.item_index == 179:
            return [other for other in candidates if other.definition.get("spell")]
        if item.item_index in GOOBERT_IDS:
            return [other for other in candidates if other.can_activate]
        if item.item_index == 2:
            return [other for other in candidates if other.definition.get("food")]
        if item.item_index == 18:
            return [other for other in candidates if other.has_cooldown]
        if item.item_index == 10:
            return [other for other in candidates if "min_damage" in other.definition]
        return candidates

    def add_speed(self, item, amount):
        item.speed_scale += amount
        self.histories.tooltip(item, 3)
        self.histories.tooltip(item, 9)

    def add_bonus_damage(self, item, amount):
        if amount:
            item.bonus_damage += amount
            self.histories.tooltip(item, 0)
            self.histories.tooltip(item, 1)

    def damage_bounds(self, item):
        lower = item.definition["min_damage"] + item.bonus_damage + item.varying_damage
        upper = item.definition["max_damage"] + item.bonus_damage + item.varying_damage + item.bonus_max_only
        # Every supported damage item is a Weapon with positive base minimum;
        # the native canBeEmpowered predicate applies to ranged weapons too.
        empower = self.characters[item.side].empower * self.characters[item.side].empower_damage
        def source_round(value):
            return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)
        return max(0, source_round(math.ceil(lower) + empower)), max(0, source_round(math.ceil(upper) + empower))

    def change_varying_damage(self, item, amount):
        if amount:
            item.varying_damage += amount
            self.histories.tooltip(item, 0)
            self.histories.tooltip(item, 1)

    def add_max_damage(self, item, amount):
        item.bonus_max_only += amount
        self.histories.tooltip(item, 1)

    def on_stack_changed(self, side, stack_type, amount, event):
        for identity in self.preparation_order:
            if self.ended:
                break
            item = self.items[identity]
            if item.side != side:
                continue
            if item.item_index == 27 and stack_type == "Spikes":
                self.change_varying_damage(item, float(amount))
            elif item.item_index == 28 and stack_type == "Vampirism":
                self.add_max_damage(item, amount)
            elif item.item_index in (37,46) and stack_type == "Block":
                if item.potion_full and self.characters[side].block>=item.definition["block_threshold"]:
                    self.consume_potion(item)
            elif item.item_index == 172 and stack_type == "Mana":
                self.on_mana_changed(item, amount, event)

    def on_mana_changed(self, potion, amount, event):
        if not potion.potion_full or amount >= 0:
            return
        origin = self.items.get(event["origin"])
        if origin is not None and origin.side == potion.side:
            self.consume_potion(potion, event["id"])

    def change_debuff_resistance(self, side, amount):
        self.characters[side].debuff_resist_stacks += amount
        self.histories.character(side, 8, next_event=True)

    def change_debuff_reflection(self, side, amount):
        self.characters[side].debuff_reflect_stacks += amount
        self.histories.character(side, 7, next_event=True)

    def give_max_health(self, item, amount):
        amount = float(self._fraction_round(amount))
        if amount <= 0:
            return
        self.histories.item_metric(item, 6, amount, next_event=True)
        char = self.characters[item.side]
        char.temporary_max_hp += amount
        char.hp += amount
        event = self.emit(item.instance_id, "TemporaryMaxHealth", dict(amount=amount))
        self.histories.character(item.side, 0)
        self.histories.character(item.side, 1)
        return event

    def _buff_record(self, side, stack_type):
        if type(stack_type) is int:
            name = STACK_NAMES_BY_TYPE[stack_type]
        else:
            name = stack_type
        if name not in STACK_NAMES_BY_TYPE.values():
            raise ValueError("unknown stack type")
        return self.characters[side].buff_fields[EVENT_TYPES[name]], name

    def change_resist_chance(self, side, stack_type, amount):
        fields, _ = self._buff_record(side, stack_type)
        fields["resistChancePercent"] += float(amount)

    def change_protection_chance(self, side, stack_type, amount):
        fields, _ = self._buff_record(side, stack_type)
        fields["cleanseProtectionChancePercent"] += float(amount)

    def change_buff_protection_chance(self, side, amount):
        for category in range(101, 108):
            self.change_protection_chance(side, category, amount)

    def change_debuff_protection_chance(self, side, amount):
        for category in range(108, 111):
            self.change_protection_chance(side, category, amount)

    def change_reflect_chance(self, side, stack_type, amount):
        fields, _ = self._buff_record(side, stack_type)
        fields["reflectChancePercent"] += float(amount)

    def change_resist_stacks(self, side, stack_type, amount):
        fields, _ = self._buff_record(side, stack_type)
        fields["resistStacks"] = int(max(0, fields["resistStacks"] + amount))

    def change_buff_protect_stacks(self, side, amount):
        self.characters[side].buff_protect_stacks += int(amount)

    def change_amplification(self, item, stack_type, amount):
        category = stack_type if type(stack_type) is int else EVENT_TYPES[stack_type]
        item.buff_amplification_chances[category] += float(amount)

    def give_buff_power(self, item, stack_type, power):
        category = stack_type if type(stack_type) is int else EVENT_TYPES[stack_type]
        item.buff_powers[category] += float(power)

    def _stack_metric(self, item, side, stack_type, change, used=False):
        if item is None:
            return
        is_player = side == "P"
        if change > 0:
            if stack_type in DEBUFF_TYPES:
                is_player = not is_player
            change_type = 0
        else:
            if not used and stack_type not in DEBUFF_TYPES:
                is_player = not is_player
            change_type = 4 if used else 2
        metric_side = "P" if is_player else "O"
        metric = 14 + (change_type + int(not is_player)) * 11 + EVENT_TYPES[stack_type] - 100
        self.histories.item_metric(item, metric, abs(change), side=metric_side, next_event=True)

    def stack_event(self, item, side, stack_type, amount, parent=None, reflected=False,
                    resisted=False, used=False, notify=False, protected=False, duration=None, timeout=False):
        params = dict(amount=amount, used=used, reflected=reflected)
        if duration is not None: params["duration"] = duration
        if timeout: params["timeout"] = True
        if resisted:
            params["resisted"] = True
        if protected:
            params["protected"] = True
        event = self.allocate_event(item.instance_id if item is not None else None, stack_type, params,
                                    target=0 if side == "P" else 1, parent=parent)
        self.histories.stack(side, EVENT_TYPES[stack_type])
        if stack_type in ("Lucky", "Blind"):
            for weapon in self.side_items[side]:
                if "min_damage" in weapon.definition:
                    self.histories.tooltip(weapon, 5)
        if stack_type == "Empower":
            for weapon in self.side_items[side]:
                if "min_damage" in weapon.definition:
                    self.histories.tooltip(weapon, 0)
                    self.histories.tooltip(weapon, 1)
        if stack_type in ("Heat", "Cold"):
            for active in self.side_items[side]:
                if active.has_cooldown:
                    self.histories.tooltip(active, 3)
                    self.histories.tooltip(active, 9)
        self.emit_event(event, (side, stack_type, amount) if notify else None)
        return event

    def _buff_roll(self, item, side, stack_type, branch, ordinal, chance):
        identity = item.instance_id if item is not None else "null"
        raw = self.random.randf_range(f"buff:{branch}:{side}:{identity}:{stack_type}:{ordinal}", 0.0, 100.0)
        return raw <= chance

    def character_gain_stacks(self, side, stack_type, amount, item=None, parent=None, reflect=False):
        # Original Character.gainStacks deliberately does not forward reflect.
        return self._gain_permanent_stacks(item, side, stack_type, int(amount), parent, reflect=False)

    def gain_stacks_temporary(self, side, stack_type, amount, duration, item=None, parent=None, reflect=False):
        if type(duration) not in (int,float) or not math.isfinite(duration):
            raise ValueError('invalid source duration')
        if duration>=0:
            carrot=(duration==8.0 and stack_type in ('Empower',106) and item is not None and item.item_index==168 and not reflect)
            light=(duration==3.0 and stack_type in ('Blind',109) and item is not None and item.item_index==53 and side!=item.side and not reflect)
            stone=(duration==4.0 and stack_type in ('Spikes',104) and item is not None and item.item_index==46 and side==item.side and not reflect)
            if not (carrot or light or stone):raise ValueError('unsupported temporary caller/type/duration')
        if duration>=0 and self.util_time is None:raise ValueError('temporary gain without clock checkpoint')
        return self._gain_stacks(item,side,stack_type,int(amount),parent,reflect,float(duration))

    def _gain_permanent_stacks(self,item,side,stack_type,amount,parent=None,reflect=False):
        return self._gain_stacks(item,side,stack_type,amount,parent,reflect,-1.0)

    def _gain_stacks(self,item,side,stack_type,amount,parent=None,reflect=False,duration=-1.0):
        amount = int(amount)  # Buff.gainTemporary's typed int parameter.
        fields, stack_type = self._buff_record(side, stack_type)
        event = None
        if amount > 0:
            character = self.characters[side]
            category = EVENT_TYPES[stack_type]
            name = stack_type.lower()
            resisted = 0
            chance = fields["resistChancePercent"]
            if item is not None and not reflect:
                chance -= item.buff_amplification_chances[category]
            if chance > 0:
                for index in range(amount):
                    if self._buff_roll(item, side, stack_type, "resist", index, chance):
                        resisted += 1
            elif chance < 0:
                for index in range(amount):
                    if self._buff_roll(item, side, stack_type, "amplify", index, -chance):
                        amount += 1
            left = amount - resisted
            reflected = 0
            if stack_type in DEBUFF_TYPES:
                if not reflect:
                    identity = item.instance_id if item is not None else "null"
                    for _ in range(amount):
                        if self.random.randf_range(f"reflect:{side}:{identity}:{stack_type}", 0.0, 100.0) <= fields["reflectChancePercent"]:
                            reflected += 1
                    left -= reflected
                    by_stacks = min(left, character.debuff_reflect_stacks) if left > 0 else 0
                    if by_stacks > 0:
                        reflected += by_stacks
                        left -= by_stacks
                        self.change_debuff_reflection(side, -by_stacks)
                    if reflected > 0:
                        amount -= reflected
                # Source allows negative left/min; do not clamp or normalize it.
                own_used = min(left, fields["resistStacks"])
                resisted += own_used
                left -= own_used
                fields["resistStacks"] -= own_used
                if left > 0:
                    shared_used = min(left, character.debuff_resist_stacks)
                    resisted += shared_used
                    self.change_debuff_resistance(side, -shared_used)
            if resisted > 0:
                amount -= resisted
                self.stack_event(item, side, stack_type, resisted, parent, reflect, resisted=True)
            if amount > 0:
                amount = int(min(amount, (100000 if stack_type == "Block" else 10000) - getattr(character, name)))
                if amount == 0:
                    return None  # Native cap return skips the later reflection recursion.
                setattr(character, name, getattr(character, name) + amount)
                if duration<0:
                    fields['permanentStacks']+=amount
                else:
                    timeout=self.util_time+duration
                    if not math.isfinite(timeout):raise ValueError('nonfinite temporary deadline')
                    entries=fields['temporaryStacks'];entries.append(TemporaryEntry(amount,timeout,item.instance_id if item else None))
                    role='buff:'+side+':'+stack_type;timer=self.runtime_roles[role]
                    if self.timer_runtime.is_stopped(timer):
                        self._start_timer(role,duration);fields['nextTemporaryTimeout']=0
                    elif duration<self.timer_runtime.time_left(timer):
                        self._stop_timer(role);self._start_timer(role,duration);fields['nextTemporaryTimeout']=len(entries)-1
                if item is not None:
                    self._stack_metric(item, side, stack_type, amount)
                    event = self.stack_event(item, side, stack_type, amount, parent, reflect, notify=True, duration=duration if duration>0 else None)
            if reflected > 0:
                self._gain_stacks(item, "O" if side == "P" else "P", stack_type,
                                  reflected, parent, True, duration)
        return event

    def remove_stack(self, item, side, stack_type, amount, parent=None, used=False):
        fields, stack_type = self._buff_record(side, stack_type)
        char = self.characters[side]
        name = stack_type.lower()
        current = getattr(char, name)
        amount = min(current, int(amount))
        if not used:
            protected = 0
            chance = fields["cleanseProtectionChancePercent"]
            if chance > 0:
                for index in range(amount):
                    if self._buff_roll(item, side, stack_type, "protect", index, chance):
                        protected += 1
            elif chance < 0:
                for index in range(amount):
                    if self._buff_roll(item, side, stack_type, "unprotect", index, -chance):
                        protected -= 1
            amount = max(0, min(current, amount - protected))
            if amount > 0 and fields["resistStacks"] > 0:
                by_stacks = min(amount, fields["resistStacks"])
                protected += by_stacks
                amount -= by_stacks
                fields["resistStacks"] -= by_stacks
            if stack_type not in DEBUFF_TYPES and stack_type != "Block" and amount > 0 and char.buff_protect_stacks > 0:
                by_stacks = min(amount, char.buff_protect_stacks)
                protected += by_stacks
                amount -= by_stacks
                char.buff_protect_stacks -= by_stacks
            if protected > 0:
                self.stack_event(item, side, stack_type, protected, parent, protected=True)
        if fields["permanentStacks"] >= amount:
            fields["permanentStacks"] -= amount
        else:
            remaining=amount-fields["permanentStacks"]
            fields["permanentStacks"]=0
            entries=fields['temporaryStacks']
            while remaining>0:
                if not entries:raise ValueError('unclosed inconsistent source temporary loss')
                farthest=0.0;selected=-1
                for index,entry in enumerate(entries):
                    if entry.timeout>farthest:farthest=entry.timeout;selected=index
                if selected<0:raise ValueError('unclosed native invalid farthest temporary index')
                entry=entries[selected]
                if entry.amount>remaining:
                    entry.amount-=remaining;remaining=0
                else:
                    remaining-=entry.amount;entries.pop(selected)
                    if not entries:self._stop_timer('buff:'+side+':'+stack_type)
        change = min(current, amount)
        if change > 0:
            setattr(char, name, current - change)
            if item is not None:
                self._stack_metric(item, side, stack_type, -change, used)
                return self.stack_event(item, side, stack_type, -change, parent, used=used, notify=True)
        return None

    def use_stack(self, item, side, stack_type, amount, parent=None):
        return self.remove_stack(item, side, stack_type, amount, parent, used=True)

    def try_use_mana(self, item, amount, parent=None):
        if self.characters[item.side].mana < amount:
            return None
        return self.use_stack(item, item.side, "Mana", amount, parent)

    def lucky_changed(self, side, amount):
        for identity, targets, coefficient in self.lucky_listeners.get(side, ()):
            if self.ended:
                break
            for item in targets:
                item.crit_chance += amount * coefficient
                self.histories.tooltip(item, 6)

    def lose_health(self, side, amount, item=None, parent=None):
        """Character.loseHealth: float HP, int event amount, synchronous signal."""
        character=self.characters[side]
        character.hp -= amount
        event=None
        if item is not None:
            event=self.allocate_event(item.instance_id,"LoseHealth",{"amount":int(-amount)},
                                      target=0 if side=="P" else 1,parent=parent)
            self.histories.character(side,0)
            self.emit_event(event,(side,"CharacterDamaged",event["params"]["amount"]))
        if character.hp<=0:
            self.death(character)
        return event

    def health_to_block(self, item, health, block, parent=None):
        """Item.healthToBlock: clamp before signal, then original-parent Block."""
        health=float(health)
        paid=min(health,self.characters[item.side].hp-1)
        if paid>0:
            self.lose_health(item.side,paid,item,parent)
            block=math.ceil((paid/health)*block)
            self.give_stack(item,item.side,"Block",block,parent)

    def give_stack(self, item, side, stack_type, amount, parent=None, reflected=False):
        if amount <= 0:
            return None
        _, name = self._buff_record(side, stack_type)
        if item is not None:
            value = amount * item.buff_powers[EVENT_TYPES[name]]
            amount = int(self._fraction_round(value))
        return self.character_gain_stacks(side, name, amount, item, parent, reflected)

    @staticmethod
    def _fraction_round(value):
        if not math.isfinite(value):
            raise ValueError("nonfinite fraction intermediate")
        fractional, integer = math.modf(abs(value))
        return math.copysign(integer + (1.0 if fractional >= 0.5 else 0.0), value)

    def get_stack_fraction(self, item, target, fraction, limit, operation="direct",
                           available_stacks=tuple(range(101, 108))):
        categories = tuple(available_stacks)
        if (categories != tuple(range(101, 108))
                or any(type(value) is not int for value in categories)
                or operation not in ("direct", "multiply", "remove", "steal")
                or target not in ("P", "O") or item is None
                or type(fraction) not in (int, float) or not math.isfinite(fraction)
                or type(limit) is not int or not -(2 ** 63) <= limit < 2 ** 63):
            raise ValueError("unsupported fixed-seven fraction inputs")
        fraction = float(fraction)  # Original typed float parameter.
        character = self.characters[target]
        unlimited = {}
        total = 0.0
        for category in categories:
            prior = getattr(character, self._stack_name(category).lower())
            if type(prior) is not int:
                raise ValueError("source stack must be an integer")
            with_bonus = prior * fraction
            unlimited[category] = with_bonus
            total += with_bonus
        rounded = self._fraction_round(total)
        if rounded == 0:
            return None
        to_give = float(min(limit, rounded))
        factor = to_give / rounded
        given, overflow = {}, {}
        total_given = 0
        for category, amount in unlimited.items():
            limited = amount * factor
            if not math.isfinite(limited) or not -(2 ** 63) <= limited < 2 ** 63:
                raise ValueError("undefined source int64 fraction conversion")
            guaranteed = int(limited)
            given[category] = guaranteed
            overflow[category] = limited - guaranteed
            total_given += guaranteed
        remaining = to_give - total_given  # Source real remainder, not int.
        order = list(overflow)
        context = f"fraction_shuffle:{item.instance_id}:{target}:{operation}"
        for ordinal, index in enumerate(range(6, 0, -1)):
            width = index + 1
            raw = self.random.global_u32(f"{context}:{ordinal}:{width}", context, ordinal, width)
            selected = raw % width
            order[selected], order[index] = order[index], order[selected]
        # Original strict comparator's fixed-seven <=16 insertion path.
        for position in range(1, len(order)):
            value, hole = order[position], position
            while hole > 0 and overflow[value] > overflow[order[hole - 1]]:
                order[hole] = order[hole - 1]
                hole -= 1
            order[hole] = value
        for category in order:
            if remaining == 0:
                break
            given[category] += 1
            remaining -= 1
        return given

    def multiply_buffs_limit(self, item, bonus, limit):
        given = self.get_stack_fraction(item, item.side, bonus, limit, "multiply")
        if given is None:
            return
        self.set_logging_mode(2)
        for category, amount in given.items():
            self.give_stack(item, item.side, category, amount)
        self.flush_logging_queue()

    def remove_buffs_fraction(self, item, fraction, limit, parent=None):
        target = "O" if item.side == "P" else "P"
        removed = self.get_stack_fraction(item, target, fraction, limit, "remove")
        if removed is None:
            return
        self.set_logging_mode(2)
        for category, amount in removed.items():
            self.remove_stack(item, target, category, amount, parent)
        self.flush_logging_queue()

    def steal_stack(self, item, category, amount, parent=None):
        target = "O" if item.side == "P" else "P"
        loss = self.remove_stack(item, target, category, amount, parent)
        return self.give_stack(item, item.side, category, amount,
                               loss["id"] if loss is not None else None)

    def steal_buffs_fraction(self, item, fraction, limit, parent=None):
        target = "O" if item.side == "P" else "P"
        stolen = self.get_stack_fraction(item, target, fraction, limit, "steal")
        if stolen is None:
            return
        self.set_logging_mode(2)
        for category, amount in stolen.items():
            self.steal_stack(item, category, amount, parent)
        self.flush_logging_queue()

    def _stack_picker_inputs(self, stack_types, count, target):
        if type(count) is not int:
            raise ValueError("stack selection count must be an integer")
        if target not in ("P", "O"):
            raise ValueError("stack selection target must be P or O")
        if type(stack_types) not in (tuple, list, range):
            raise ValueError("stack selection categories must be an ordered array")
        categories = list(stack_types)
        if any(type(value) is not int or value not in range(100, 111) for value in categories):
            raise ValueError("unknown stack category")
        return categories

    def _stack_name(self, category):
        return next(name for name, value in EVENT_TYPES.items() if value == category)

    def pick_random_stacks(self, item, stack_types, num_stacks, target, priority_stack=None):
        categories = self._stack_picker_inputs(stack_types, num_stacks, target)
        if priority_stack is not None and (type(priority_stack) is not int or priority_stack not in range(100, 111)):
            raise ValueError("unknown priority stack category")
        stacks = {}
        for category in categories:
            count = getattr(self.characters[target], self._stack_name(category).lower())
            if count > 0:
                stacks[category] = count
        picked = {}
        if priority_stack is not None:
            count = min(num_stacks, stacks.get(priority_stack, 0))
            if count > 0:
                picked[priority_stack] = count
                num_stacks -= count
                stacks[priority_stack] -= count
                if stacks[priority_stack] <= 0:
                    del stacks[priority_stack]
        for index in range(num_stacks):
            if stacks:
                keys = list(stacks)
                raw = self.random.randi_range(f"random_stack:{item.instance_id}:{target}:take:{index}", 0, len(keys) - 1)
                category = keys[raw]
                picked[category] = picked.get(category, 0) + 1
                stacks[category] -= 1
                if stacks[category] <= 0:
                    del stacks[category]
        return picked

    def pick_random_stacks_to_give(self, item, stack_types, num_stacks, target=None):
        target = item.side if target is None else target
        categories = self._stack_picker_inputs(stack_types, num_stacks, target)
        if num_stacks > 0 and not categories:
            raise ValueError("cannot give random stacks from an empty category array")
        picked = {}
        for index in range(num_stacks):
            raw = self.random.randi_range(f"random_stack:{item.instance_id}:{target}:give:{index}", 0, len(categories) - 1)
            category = categories[raw]
            picked[category] = picked.get(category, 0) + 1
        return picked

    def cleanse_random_debuffs(self, item, num_debuffs, parent=None):
        picked = self.pick_random_stacks(item, range(108, 111), num_debuffs, item.side)
        self.set_logging_mode(2)
        for category, count in picked.items():
            self.remove_stack(item, item.side, self._stack_name(category), count, parent)
        self.flush_logging_queue()

    def give_random_buffs(self, item, num_buffs, parent=None, available_buffs=range(101, 108), target=None):
        target = item.side if target is None else target
        picked = self.pick_random_stacks_to_give(item, available_buffs, num_buffs, target)
        self.set_logging_mode(2)
        for category, count in picked.items():
            self.give_stack(item, target, self._stack_name(category), count, parent)
        self.flush_logging_queue()

    def use_random_buffs(self, item, num_buffs, parent=None, available_buffs=range(101, 108)):
        picked = self.pick_random_stacks(item, available_buffs, num_buffs, item.side)
        if not picked:
            return None
        events = []
        self.set_logging_mode(2)
        for category, count in picked.items():
            events.append(self.use_stack(item, item.side, self._stack_name(category), count, parent))
        self.flush_logging_queue()
        return events

    def inflict_random_debuffs(self, item, num_debuffs, parent=None, available_debuffs=range(108, 111)):
        target = "O" if item.side == "P" else "P"
        picked = self.pick_random_stacks_to_give(item, available_debuffs, num_debuffs, target)
        self.set_logging_mode(2)
        for category, count in picked.items():
            self.give_stack(item, target, self._stack_name(category), count, parent)
        self.flush_logging_queue()

    def remove_random_buffs(self, item, num_buffs, parent=None):
        target = "O" if item.side == "P" else "P"
        picked = self.pick_random_stacks(item, range(101, 108), num_buffs, target)
        self.set_logging_mode(2)
        for category, count in picked.items():
            self.remove_stack(item, target, self._stack_name(category), count, parent)
        self.flush_logging_queue()

    def steal_random_buff(self, item, num_buffs, parent=None, possible_buffs=range(101, 108), priority_buff=None):
        target = "O" if item.side == "P" else "P"
        picked = self.pick_random_stacks(item, possible_buffs, num_buffs, target, priority_buff)
        self.set_logging_mode(2)
        for category, count in picked.items():
            name = self._stack_name(category)
            self.remove_stack(item, target, name, count, parent)
            self.give_stack(item, item.side, name, count, parent)
        self.flush_logging_queue()

    def give_lucky(self, item, amount, parent=None):
        return self.give_stack(item, item.side, "Lucky", amount, parent)

    def heal(self, side, amount, origin, parent=None):
        amount = float(self._fraction_round(amount))
        character = self.characters[side]
        maximum = character.max_hp + character.temporary_max_hp
        overheal = max(0.0, amount - (maximum - character.hp))
        character.hp = min(maximum, character.hp + amount)
        if origin in self.items:
            self.items[origin].healing += amount
            self.items[origin].overheal += overheal
        event = self.emit(origin, "Health", {"amount": int(amount)}, target=0 if side == "P" else 1, parent=parent)
        self.histories.character(side, 0)
        if origin in self.items:
            self.histories.item_metric(self.items[origin], 1, float(amount))
            self.histories.item_metric(self.items[origin], 2, overheal)
        else:
            self.histories.metric(side, 1, origin, amount)
            self.histories.metric(side, 2, origin, overheal)
        self.on_character_healed(side, event)
        return event

    def on_character_healed(self, side, event):
        for identity in self.preparation_order:
            if self.ended:
                break
            item = self.items[identity]
            if item.side != side and item.item_index == 36 and item.potion_full:
                self.on_opponent_heal(item, event)

    def on_opponent_heal(self, item, event):
        if not item.potion_full:
            return
        self.set_item_state(item, False, next_event=True)
        self.trigger_potion(item, event["id"])
        affected = self.affected_items(item)
        if affected:
            self.trigger_potion(affected[0], event["id"])
        self.activate(item)

    def give_stamina(self, item, amount=1.0, parent=None):
        character = self.characters[item.side]
        character.stamina = max(0.0, min(character.max_stamina, character.stamina + amount))
        event = self.emit(item.instance_id, "Stamina", {"stamina": math.floor(amount * 10) / 10.0},
                         target=0 if item.side == "P" else 1, parent=parent)
        self.histories.item_metric(item, 8, float(amount))
        return event

    def activate(self, item):
        if self.util_time is None:
            raise ValueError('activation has no explicit clock')
        if self.util_time > item.last_activation_time:
            item.activations_this_frame = 1
            item.last_activation_time = self.util_time
        else:
            item.activations_this_frame += 1
        if item.activations_this_frame > 3:
            return
        if not self.ended:
            event = None
            if not item.definition["bag"]:
                event = self.emit(item.instance_id, "Activation")
                for receiver in self.activation_listeners.get(item.instance_id, ()):
                    if self.ended:
                        break
                    self.on_goobert_item_activated(self.items[receiver], event)
                item.activations += 1
                self.histories.item_metric(item, 4)
            if item.has_cooldown:
                self.histories.tooltip(item, 9, event_num=event["id"] if event is not None else None)

    def on_goobert_item_activated(self, item, event):
        if item.double_activation_chance != 0.0:
            raise ValueError("unsupported nonzero Goobert double activation modifier")
        item.goobert_activations += 1
        threshold = item.definition["activations_to_trigger"]
        if item.goobert_activations == threshold:
            item.goobert_activations = 0
            if item.item_index==262:
                self.king_effect(item)
            elif item.item_index in BUFF_GOOBERT_IDS:
                self.special_goobert_effect(item)
            elif item.item_index in RAINBOW_GOOBERT_IDS:
                self.rainbow_effect(item)
            elif item.item_index == 54:
                self.blood_effect(item)
            elif item.item_index == 168:
                self.carrot_effect(item)
            elif item.item_index == 53:
                self.light_effect(item)
            elif item.item_index == 52:
                for identity in item.steel_affected_weapons:
                    self.add_bonus_damage(self.items[identity],item.definition['damage_each'])
                # Source gave_block has no receivers in the explicit51 domain.
                self.give_stack(item,item.side,'Block',item.definition['block'])
            elif item.item_index == 400:
                if self.characters[item.side].lucky>=item.definition['lucky_threshold']:
                    self.give_stack(item,item.side,'Regeneration',item.definition['regeneration'])
                else:self.give_stack(item,item.side,'Lucky',item.definition['lucky_amount'])
            elif item.item_index == 468:
                if self.characters[item.side].stamina<item.definition['stamina_threshold']:
                    if self.characters[item.side].allow_stamina_overflow:
                        raise ValueError('unclosed Toast stamina-overflow helper domain')
                    self.give_stamina(item,item.definition['stamina_gain'])
                else:self.give_stack(item,item.side,'Regeneration',item.definition['regeneration'])
            else:
                self.heal(item.side, item.definition["heal"], item.instance_id)
                if item.item_index == 38:
                    self.give_stack(item,"O" if item.side=="P" else "P","Poison",item.definition["poison"])
                elif item.item_index == 205:
                    self.give_stack(item,item.side,"Heat",item.definition["heat"])
            self.activate(item)
        # Read after synchronous effects: another Goobert can reenter this one.
        item.trigger_time = float(threshold - item.goobert_activations)
        self.histories.tooltip(item, 9, event_num=event["id"])

    def get_most_stacks(self, target, available_stacks=range(101, 108)):
        categories = self._stack_picker_inputs(available_stacks, 0, target)
        if any(category not in range(101, 108) for category in categories):
            raise ValueError("most-buff helper admits buff categories101..107 only")
        values = {}
        for category in categories:
            value = getattr(self.characters[target], self._stack_name(category).lower())
            if type(value) is not int or value < 0:
                raise ValueError("invalid most-buff state outside nonnegative default domain")
            values[category] = value
        picked = []
        maximum = 0
        for category, value in values.items():
            if value == maximum:
                picked.append(category)
            elif value > maximum:
                picked = [category]
                maximum = value
        return picked

    def give_most_buffs(self, item, num_buffs, parent=None, available_buffs=range(101, 108)):
        if type(num_buffs) not in (int, float) or not math.isfinite(num_buffs):
            raise ValueError("most-buff amount must be a finite source number")
        picked = self.get_most_stacks(item.side, available_buffs)
        if not picked:
            raise ValueError("empty most-buff candidate selection has no admitted source index")
        index = self.random.randi_range(f"most_buff:{item.instance_id}:{item.side}", 0, len(picked) - 1)
        self.give_stack(item, item.side, picked[index], num_buffs, parent)

    def special_goobert_effect(self, item):
        identity = item.item_index
        if identity not in BUFF_GOOBERT_IDS:
            raise ValueError("unsupported four-item Goobert caller")
        definition = item.definition
        if identity in (204, 220) and self.characters[item.side].temporary_max_health_gain != 1.0:
            raise ValueError("nondefault temporaryMaxHealthGain outside new caller domain")
        if identity in (220, 416):
            self.give_stack(item, item.side, "Block", definition["block"])
        if identity in (204, 220):
            self.give_max_health(item, definition["max_health"])
        else:
            self.heal(item.side, definition["heal"], item.instance_id)
        if identity in (220, 416):
            self.give_stack(item, item.side, "Vampirism", definition["vampirism"])
        if identity in (204, 220):
            # giveRandomBuffs has a typed int count in the original source.
            self.give_random_buffs(item, int(definition["random_buffs"]))
        else:
            self.give_most_buffs(item, definition["most_buffs"])
        if identity in (220, 416):
            self.give_stack(item, "O" if item.side == "P" else "P", "Blind", definition["blind"])
            for affected in self.affected_items(item):
                if affected.item_index in EMPOWERABLE_WEAPON_IDS:
                    self.add_bonus_damage(affected, definition["damage_each"])

    def rainbow_effect(self, item):
        if item.item_index not in RAINBOW_GOOBERT_IDS:
            raise ValueError("unsupported Rainbow caller")
        definition = item.definition
        self.give_stack(item, item.side, "Block", definition["block"])
        self.heal(item.side, definition["heal"], item.instance_id)
        # Engineer's source gives stamina BEFORE Vampirism and Regeneration.
        if item.item_index == 469:
            self.give_stamina(item, definition["stamina_gain"])
        self.give_stack(item, item.side, "Vampirism", definition["vampirism"])
        if item.item_index == 169:
            self.give_stack(item, item.side, "Empower", definition["empower"])
        elif item.item_index == 219:
            self.give_stack(item, item.side, "Heat", definition["heat"])
        elif item.item_index in (401, 469):
            self.give_stack(item, item.side, "Regeneration", definition["regeneration"])
        target = "O" if item.side == "P" else "P"
        self.give_stack(item, target, "Blind", definition["blind"])
        if item.item_index == 74:
            self.give_stack(item, target, "Poison", definition["poison"])
        for affected in self.affected_items(item):
            if affected.item_index in EMPOWERABLE_WEAPON_IDS:
                self.add_bonus_damage(affected, definition["damage_each"])

    def roll_item_chance(self, item, secondary=False):
        suffix = "secondary" if secondary else "primary"
        chance = item.definition.get("chance2" if secondary else "chance", 0.0)
        return item.chance_rng.roll_percent(chance, self.random, f"item_chance:{item.instance_id}:{suffix}")

    def drain_stamina(self, item, amount, parent=None):
        side = "O" if item.side == "P" else "P"
        character = self.characters[side]
        drained = min(character.stamina, amount)
        character.stamina -= drained
        event = self.emit(item.instance_id, "DrainStamina",
                          {"stamina": math.floor(drained * 10) / 10.0},
                          target=0 if side == "P" else 1, parent=parent)
        self.histories.item_metric(item, 11, drained)
        return event

    def extra_attack(self, item, parent=None):
        """Dagger.onStun's attack callback, without cooldown or stamina payment."""
        if item.item_index not in (15, 30):
            raise ValueError("only Dagger stun callbacks are implemented")
        return self.weapon_attack(item, parent)

    def weapon_attack(self, item, parent=None):
        event = self.attack(item, parent)
        self.activate(item)
        if item.item_index == 3 and item.broom_bonus_damage:
            self.add_bonus_damage(item, -item.broom_bonus_damage)
            item.broom_bonus_damage = 0
        return event

    def stun(self, side, duration, item, parent=None):
        character = self.characters[side]
        # No supported item changes default stunResistance=0. BalancedRng
        # returns false at that boundary without a random draw or state change.
        character.stun_resistance_rng.roll_percent(0.0, self.random, f"stun_resistance:{side}")
        character.stunned = max(character.stunned, duration)
        event = self.emit(item.instance_id, "Stun", {"duration": duration},
                          target=0 if side == "P" else 1, parent=parent)
        for identity in self.preparation_order:
            if self.ended:
                break
            dagger = self.items[identity]
            if dagger.side != side and dagger.item_index in (15, 30):
                self.extra_attack(dagger, event["id"])
        self.histories.character(side, 5, event_num=event["id"])
        return event

    def end_stun(self, side):
        self.characters[side].stunned = 0.0
        self.histories.character(side, 5, next_event=True)

    def set_item_state(self, item, full, next_event=False):
        if type(full) is not bool or not (item.definition.get("potion") or item.item_index in STATE_PARTICLE_IDS):
            raise ValueError("only potion and source-qualified Goobert boolean states are implemented")
        self.histories.item_state(item, full, next_event=next_event)
        if item.definition.get("potion"):
            item.potion_full = full

    def trigger_potion(self, item, parent=None):
        if item.item_index == 36:
            self.give_stack(item, "O" if item.side == "P" else "P", "Poison", 3, parent)
            self.give_stack(item, item.side, "Poison", 1, parent)
        elif item.item_index in (19,35):
            self.heal(item.side,item.definition.get("heal",12),item.instance_id,parent)
            self.remove_stack(item,item.side,"Poison",item.definition.get("cleanse_poison",4),parent)
            if item.item_index==35:
                self.give_stack(item,item.side,"Regeneration",item.definition["regeneration"],parent)
        elif item.item_index in (37,46):
            self.health_to_block(item,item.definition["health_cost"],item.definition["converted_block"],parent)
            if item.item_index==46:
                self.give_stacks_temporary(item,item.side,"Spikes",item.definition["spikes"],item.definition["duration"],parent)
        elif item.item_index == 172:
            self.give_stack(item, item.side, "Mana", item.definition["mana"], parent)
            self.give_max_health(item, item.definition["max_health"])
        else:
            raise ValueError("unsupported potion")

    def consume_potion(self, item, parent=None, with_activate=True):
        if not item.potion_full:
            return
        self.set_item_state(item, False, next_event=True)
        self.trigger_potion(item, parent)
        affected = self.affected_items(item)
        if affected:
            self.trigger_potion(affected[0])
        if with_activate:
            self.activate(item)

    def on_character_attacked(self, side, hit, matched_shields, event):
        for identity in self.preparation_order:
            if self.ended:
                break
            item = self.items[identity]
            if item.side != side:
                continue
            if item in matched_shields:
                self.shield_after_attack([item], event)
            elif item.item_index == 3 and not hit:
                self.add_bonus_damage(item, 2)
                item.broom_bonus_damage += 2

    def is_battle_raging(self, side):
        if not hasattr(self, 'runtime_roles') or 'rage:' + side not in self.runtime_roles:
            return False
        return not self.timer_runtime.is_stopped(self.runtime_roles['rage:' + side])

    def start_battle_rage(self, item, duration, parent=None, apply_bonus=True):
        if item.instance_id not in self.rage_listeners[item.side] or type(apply_bonus) is not bool:
            raise ValueError('only prepared source BerserkerBag caller admitted')
        if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
            raise ValueError('positive finite source rage duration required')
        full_duration = float(duration) + (self.characters[item.side].battle_rage_bonus_duration if apply_bonus else 0.0)
        if not math.isfinite(full_duration) or full_duration <= 0 or f32(full_duration) <= 0:
            raise ValueError('invalid source rage duration')
        self._start_timer('rage:' + item.side, full_duration)
        event = self.allocate_event(item.instance_id, 'BattleRageStart', {'duration': full_duration}, parent=parent)
        self.emit_event(event, (item.side, 'BattleRageStart', None))
        self.histories.character(item.side, 6, event_num=event['id'])
        return event

    def end_battle_rage(self, side):
        self._stop_timer('rage:' + side)
        event = self.allocate_event(22, 'BattleRageEnd', target=0 if side == 'P' else 1)
        self.emit_event(event, (side, 'BattleRageEnd', None))
        self.histories.character(side, 6, event_num=event['id'])
        return event

    def on_battle_rage(self, side, started, event):
        for identity in self.rage_listeners[side]:
            if self.ended:
                break
            bag = self.items[identity]
            sign = 1.0 if started else -1.0
            self.characters[side].damage_resistance += sign * bag.definition['damage_resistance']
            self.histories.character(side, 15)
            for item in self.inside_items(bag):
                if item.has_cooldown:
                    item.speed_scale += sign * bag.definition['rage_speed']
                    self.histories.tooltip(item, 3)
                    self.histories.tooltip(item, 9)

    def _damage_after_resistance(self, damage, defender, attack=False):
        resistance = max(-10.0, min(1.0, defender.damage_resistance / 100.0))
        result = int(self._fraction_round(damage * (1.0 - resistance)))
        if attack:
            result -= defender.damage_reduction
        return result

    def on_character_damaged(self, side, event):
        for identity in self.preparation_order:
            if self.ended:
                break
            item = self.items[identity]
            if item.side != side:
                continue
            char = self.characters[side]
            if item.item_index == 129 and not item.rage_has_activated:
                if char.hp / (char.max_hp + char.temporary_max_hp) < item.definition['health_threshold']:
                    item.rage_has_activated = True
                    self.start_battle_rage(item, item.definition['rage_duration'], event['id'])
                    self.activate(item)
            elif item.item_index == 34 and not item.boots_has_activated:
                if char.hp / (char.max_hp + char.temporary_max_hp) < item.definition["health_threshold"]:
                    item.boots_has_activated = True
                    self.give_stack(item, side, "Lucky", item.definition["lucky"], event["id"])
                    self.give_stack(item, side, "Empower", item.definition["empower"], event["id"])
                    self.give_stack(item, side, "Block", item.definition["block"], event["id"])
                    self.activate(item)
                    item.consumed = True
            elif item.item_index in (19,35,172) and item.potion_full:
                if char.hp / (char.max_hp + char.temporary_max_hp) < item.definition.get("health_threshold", 0.5):
                    self.consume_potion(item, event["id"])

    def on_item_dealt_damage(self, item, hit, event):
        if hit and item.item_index == 233 and self.roll_item_chance(item):
            self.give_stack(item, item.side, "Spikes", 1, event["id"])
        if hit and item.item_index in (3, 12) and self.roll_item_chance(item):
            side = "O" if item.side == "P" else "P"
            if item.item_index == 3:
                self.give_stack(item, side, "Blind", 1, event["id"])
            else:
                self.stun(side, 0.5, item, event["id"])

    def shield_before_damage(self, defender_side, damage):
        reduction = 0
        matched = []
        for identity in self.preparation_order:
            item = self.items[identity]
            if self.ended:
                break
            if item.side != defender_side or not item.definition.get("shield"):
                continue
            if not self.roll_item_chance(item):
                continue
            amount = item.definition["damage_block"]
            # Native min(float amount, integer remainder) returns a real,
            # including zero; the first 0.0 changes an initial int0 history.
            self.histories.item_metric(item, 5, float(min(amount, max(0, damage - reduction))))
            reduction += int(amount)
            matched.append(item)
            if item.item_index == 16 and item.spikes_given < 5:
                item.spikes_given += 1
                self.give_stack(item, item.side, "Spikes", 1)
        return max(0, damage - reduction), matched

    def shield_after_attack(self, matched, event):
        for item in matched:
            if self.ended:
                break
            self.drain_stamina(item, 0.3, event["id"])
            self.activate(item)

    def speed(self, item):
        char = self.characters[item.side]
        modifier = item.speed_scale + (char.heat - char.cold) * 0.02
        return max(0.1, min(10.0, 1.0 + modifier if modifier >= 0 else 1.0 / (1.0 - modifier)))

    def trigger(self, item):
        item.iteration_cooldown = self.adjust_cooldown(item)
        item.trigger_time += item.iteration_cooldown
        char = self.characters[item.side]
        if item.item_index == 50:
            self.health_to_block(item,item.definition["health_cost"],item.definition["converted_block"])
            self.activate(item)
            return
        if item.item_index == 332:
            self.multiply_buffs_limit(item, item.definition["buff_factor"], item.definition["buff_limit"])
            self._set_item_cooldown(item,False,'Item.deactivateCooldown')
            self.activate(item)
            item.consumed = True
            return
        if item.item_index == 374:
            self.cleanse_random_debuffs(item, item.definition["cleanse_count"])
            self.heal(item.side, item.definition["heal"], item.instance_id)
            self.activate(item)
            return
        if item.item_index == 124:
            self.cleanse_random_debuffs(item, 1)
            if char.lucky >= item.definition["lucky_threshold"] and self.roll_item_chance(item):
                self.give_stack(item, item.side, "Empower", item.definition["empower"])
            self.activate(item)
            return
        if item.item_index == 117:
            self.give_stack(item, item.side, "Heat", item.definition["heat"])
            self.heal(item.side, item.definition["heal"], item.instance_id)
            if char.heat >= item.definition["heat_threshold"]:
                self.cleanse_random_debuffs(item, 1)
            self.activate(item)
            return
        if item.item_index == 6:
            self.give_stack(item, item.side, "Block", 3)
            if self.roll_item_chance(item):
                self.remove_stack(item, "O" if item.side == "P" else "P", "Vampirism", 1)
            self.activate(item)
            return
        if item.item_index == 5:
            self.heal(item.side, 4, item.instance_id)
            self.give_stamina(item)
            self.activate(item)
            return
        if item.item_index == 22:
            if char.mana < 10:
                self.give_stack(item, item.side, "Mana", 1)
            else:
                self.give_lucky(item, 1)
            self.activate(item)
            return
        if item.item_index == 21:
            self.give_stack(item, "O" if item.side == "P" else "P", "Poison", item.definition["poison"])
            self.activate(item)
            return
        if item.item_index == 179:
            used = self.try_use_mana(item, item.definition["mana_cost"])
            if used is not None:
                self.give_stack(item, "O" if item.side == "P" else "P", "Cold",
                                item.definition["cold"], used["id"])
            self.activate(item)
            return
        if item.item_index == 0 and item.ammunition < 1:
            return
        cost = item.definition["stamina"]
        if char.stamina < cost:
            item.out_of_stamina += 1
            self.histories.item_metric(item, 7, next_event=True)
            self.emit(item.instance_id, "OutofStamina", target=0 if item.side == "P" else 1)
            self.histories.tooltip(item, 9)
            return
        char.stamina = max(0.0, char.stamina - cost)
        self.histories.item_metric(item, 12, float(cost), next_event=True)
        if item.item_index == 0:
            item.ammunition -= 1
        if item.item_index == 83:
            # Source pays stamina once, then two complete damage/activation calls.
            # Neither an ended fight nor a dead second target cancels the caller.
            self.attack(item)
            self.activate(item)
            self.attack(item)
            self.activate(item)
        elif item.item_index == 0:
            self.attack(item)
            if item.ammunition == 0:
                self._set_item_cooldown(item,False,'Item.deactivateCooldown')
            self.activate(item)
            if item.ammunition == 0:
                item.consumed = True
        else:
            self.weapon_attack(item)

    def pre_item_damage(self, item, hit):
        """Execute one native early override; return its temporary damage."""
        defender_side = "O" if item.side == "P" else "P"
        if hit:
            if item.item_index == 84:
                self.add_bonus_damage(item, item.definition["growth_damage"])
                self.add_speed(item, item.definition["growth_speed"])
            elif item.item_index == 27:
                self.give_stack(item, item.side, "Spikes", 1)
            elif item.item_index == 28 and self.characters[item.side].regeneration >= 1:
                used = self.use_stack(item, item.side, "Regeneration", 1)
                self.give_stack(item, item.side, "Vampirism", 1, used["id"])
            elif item.item_index == 30:
                self.give_stack(item, defender_side, "Poison", 2)
            elif item.item_index == 234 and self.roll_item_chance(item):
                # Accuracy has already been decided; current crit is refreshed below.
                self.give_lucky(item, 1)
            elif item.item_index == 235 and self.roll_item_chance(item):
                # Game.getDebuffs() is all three categories, including absent ones.
                choice = self.random.randi_range(f"shortbow_debuff:{item.instance_id}", 0, 2)
                self.give_stack(item, defender_side, "Poison", item.definition["poison"] + int(choice == 0))
                if choice != 0:
                    self.give_stack(item, defender_side, ("Poison", "Blind", "Cold")[choice], 1)
            elif item.item_index in (208, 209) and self.roll_item_chance(item):
                self.add_bonus_damage(item, 1)
        # MagicStaff's early callback runs even on miss. Its temporary damage
        # belongs to this DamageResult; only the permanent bonus changes RNG bounds.
        if item.item_index != 32:
            return 0
        if self.try_use_mana(item, item.definition["mana_cost"]) is None:
            return 0
        self.add_bonus_damage(item, item.definition["permanent_damage"])
        return item.definition["temporary_damage"]

    def attack_effect_count(self, item):
        """The native default-zero flip still draws and succeeds at raw zero."""
        if item.double_attack_effect_chance != 0.0:
            raise ValueError("unsupported nonzero double attack effect modifier")
        raw = self.random.randf(f"double_attack_effect:{item.instance_id}")
        return 1 + int(raw <= item.double_attack_effect_chance)

    def late_item_damage(self, item, defender_side):
        """One hit-only late override, even when shield reduction leaves zero."""
        if item.item_index == 0:
            amount = 4
        elif item.item_index == 14:
            amount = item.spear_block_removal
        else:
            return
        removed = self.remove_stack(item, defender_side, "Block", amount)
        if removed:
            actual = -removed["params"]["amount"]
            item.damage += actual
            self.histories.item_metric(item, 0, actual)

    def attack(self, item, parent=None):
        attacker = self.characters[item.side]
        defender = self.characters["O" if item.side == "P" else "P"]
        if defender.dead:
            return None
        effect_count = self.attack_effect_count(item)
        hit = defender.accuracy.roll_percent(item.definition["accuracy"] + (attacker.lucky - attacker.blind) * 5,
                                             self.random, f"accuracy:{defender.side}:{item.instance_id}")
        # Native common early signal is emitted once; these are the own hooks.
        # No supported descriptor subscribes to that common signal.
        extra_damage = 0
        for _ in range(effect_count):
            extra_damage += self.pre_item_damage(item, hit)
        damage, critical = 0, False
        matched_shields = []
        if hit:
            low, high = self.damage_bounds(item)
            damage = extra_damage + item.damage_range.draw(low, high, self.random, f"damage:{item.instance_id}")
            if item.crit_chance > 0:
                critical = defender.critical.roll_percent(min(100.0, max(0.0, item.crit_chance)),
                                                          self.random, f"critical:{defender.side}:{item.instance_id}")
            if critical:
                damage *= 2
            damage = self._damage_after_resistance(damage, defender, attack=True)
            if defender.invulnerable:
                damage = 0
            if not item.definition.get("ranged"):
                damage, matched_shields = self.shield_before_damage(defender.side, damage)
            damage = max(0, damage)
            # Likewise, common late signal is once; only own hooks repeat.
            for _ in range(effect_count):
                self.late_item_damage(item, defender.side)
            blocked = min(defender.block, damage)
            self.remove_stack(None, defender.side, "Block", blocked)
            defender.hp -= damage - blocked
            event = self.emit(item.instance_id, "CriticalDamage" if critical else "DealDamage",
                              {"damage": damage}, parent=parent)
            self.histories.character(defender.side, 0)
            self.histories.stack(defender.side, 100)
            item.damage += damage
            self.histories.item_metric(item, 0, damage)
        else:
            item.misses += 1
            event = self.emit(item.instance_id, "MissedAttack", parent=parent)
            self.histories.item_metric(item, 3)
        self.on_character_attacked(defender.side, hit, matched_shields, event)
        self.on_character_damaged(defender.side, event)
        for _ in range(effect_count):
            self.on_item_dealt_damage(item, hit, event)
        if defender.hp <= 0:
            self.death(defender)
        if hit and damage > 0 and defender.spikes > 0 and not item.definition.get("ranged"):
            self.damage_nonitem(attacker.side, min(defender.spikes, damage), 104, event["id"])
        if hit and damage > 0 and attacker.vampirism > 0 and not item.definition.get("ranged"):
            self.heal(attacker.side, min(attacker.vampirism, damage), 103, event["id"])
        return event

    def death(self, character):
        character.dead = True
        if not self.ended:
            self.ended = True
            self.winner = "P" if self.characters["O"].hp <= 0 else "O"
            self.pending_terminal = True
            if self.king_mode:self.frame_driver.request_end(lambda driver:self.finish())

    def fatigue_tick(self):
        self.mark_schedule("fatigue_tick", 0.0)
        self.fatigue_counter += 1 + math.floor((0.1 if self.time < 60.0 else 0.2) * self.fatigue_counter)
        for side in ("O", "P"):
            self.damage_nonitem(side, self.fatigue_counter, 99)

    def damage_nonitem(self, side, amount, origin, parent=None):
        character = self.characters[side]
        if character.dead:
            return None
        # Even a fixed native DamageSource range invokes randi_range.
        label = {99: "fatigue", 104: "spikes", 108: "poison"}[origin]
        damage = self.random.randi_range(f"{label}:{side}", amount, amount)
        damage = self._damage_after_resistance(damage, character)
        if character.invulnerable:
            damage = 0
        damage = max(0, damage)
        blocked = min(character.block, damage)
        self.remove_stack(None, side, "Block", blocked)
        character.hp -= damage - blocked
        event = self.emit(origin, "DealDamage", {"damage": damage}, target=0 if side == "O" else 1, parent=parent)
        self.histories.character(side, 0)
        self.histories.stack(side, 100)
        self.histories.metric("P" if side == "O" else "O", 0, origin, damage)
        self.on_character_damaged(side, event)
        if character.hp <= 0:
            self.death(character)
        return event

    def step(self, delta=NATIVE_PHYSICS_DELTA):
        if self.king_mode:
            if type(delta)is not float or delta!=NATIVE_PHYSICS_DELTA:raise ValueError('King delta comes from sealed frame clock')
            if not self.prepared:self.prepare_only()
            if not self.activated:self.activate_from_checkpoint()
            d=self.frame_driver
            if d.finalized:raise ValueError('King terminal barrier already finalized')
            if d.pass_index<len(d.clock.passes) and d.clock.passes[d.pass_index].kind=='physics':
                self.frame+=1;self.elapsed+=d.clock.passes[d.pass_index].delta
            return d.step()
        if not self.prepared:self.prepare_only()
        if not self.activated:self.activate_from_checkpoint()
        if self.finalized:raise ValueError('combat already finalized')
        if type(delta)is not float or delta!=NATIVE_PHYSICS_DELTA:raise ValueError('only fixed60 promoted-f32 delta admitted')
        self.frame+=1;self.elapsed+=delta
        self.timer_runtime.dispatch_internal(delta)
        for role in self.ordinary_roles:
            if role=='util':
                self.util_time+=delta
                if not math.isfinite(self.util_time):raise ValueError('clock overflow')
                self.runtime_trace.append(dict(kind='util_step',frame=self.frame,util_time=self.util_time))
            elif role=='combat_timer':
                self.mark_schedule('timer',delta);self.time+=delta
            elif role.startswith('character:'):
                side=role[-1];char=self.characters[side];self.mark_schedule(role,delta)
                if char.stunned>0:
                    char.stunned-=delta
                    if char.stunned<=0:self.end_stun(side)
                char.stamina=max(0.0,min(char.max_stamina,char.stamina+char.stamina_regen*delta))
            elif role.startswith('item:'):
                item=self.items[role[len('item:'):]]
                if item.cooldown_active:
                    self.mark_schedule(role,delta)
                    if self.characters[item.side].stunned==0:
                        item.trigger_time-=delta*self.speed(item)
                        if item.trigger_time<=0:self.trigger(item)
        if self.pending_terminal:self.finish()

    def finish(self):
        if not self.ended or self.finalized:
            raise ValueError("finish requires an unfinalized ended combat")
        code = "Win" if self.winner == "P" else "Loss"
        self.emit(EVENT_TYPES[code], code, after_fight=True)
        # Game's deferred cleanup clears EventBus before Item.combatEnd.
        self.activation_listeners.clear()
        self.lucky_listeners.clear()
        self.rage_listeners.clear()
        self.pre_cleanup_hp = {side: char.hp for side, char in self.characters.items()}
        for side in ('P', 'O'):
            if self.integration_mode:self._set_source_processing('character:'+side,False,'Character.combatEnd')
            self._stop_timer('tick:' + side)
            for category in range(100, 111):
                name = STACK_NAMES_BY_TYPE[category]
                self._stop_timer('buff:' + side + ':' + name)
                self.characters[side].buff_fields[category]['temporaryStacks'].clear()
            if 'rage:' + side in self.runtime_roles:self._stop_timer('rage:' + side)
            if self.integration_mode:
                for name in ('battleRageTimer','autoRageTimer'):
                    role='aux:'+side+':'+name
                    if self.pure_combat_mode:self._stop_timer(role)
                    else:self.runtime_trace.append(dict(kind='inactive_aux_stop',role=role,source='Character.combatEnd',before=self._integration_aux_timer(role),after=self._integration_aux_timer(role)))
            if self.king_mode:self._stop_timer('invu:'+side)
        self.fatigue_counter = 0
        self._stop_timer('fatigue:start')
        self._stop_timer('fatigue:tick')
        self.fatigue_start_left = None
        self.fatigue_tick_left = None
        if self.integration_mode:self._set_source_processing('combat_timer',False,'CombatTimer.combatEnd')
        for side, character in self.characters.items():
            character.hp = max(1.0, character.hp) if side == self.winner else 0.0
        for item in self.side_items['P'] + self.side_items['O']:
            self._set_item_cooldown(item,False,'Item.combatEnd')
            if item.item_index == 0:
                item.ammunition = 1
            if item.item_index in STATE_PARTICLE_IDS:
                self._stop_timer('particle:' + item.instance_id)
            if item.item_index == 52:
                item.steel_affected_weapons.clear()
            if item.item_index == 262:self._stop_timer('king_buff:'+item.instance_id)
        if self.king_mode and not self.integration_mode:
            for role in self.ordinary_roles:
                if role!='util':self.timer_runtime.set_ordinary_processing(self.runtime_roles[role],False,0)
        self.pending_terminal=False
        self.finalized = True

    def snapshot(self):
        item_states = {}
        for identity, item in self.items.items():
            item_states[identity] = asdict(item)
            item_states[identity]["cells"] = sorted(item.cells)
            item_states[identity]["stars"] = sorted(item.stars)
            item_states[identity]["physics_processing"] = item.cooldown_active and not self.finalized
            item_states[identity]["owner_type"] = 1 if item.side == "P" else 3
        characters = {side: asdict(c) for side, c in self.characters.items()}
        for side, character in characters.items():
            character["battle_raging"] = self.is_battle_raging(side)
            character["physics_processing"] = self.activated and not self.finalized
        first_result = 0 if self.winner == "P" else 1 if self.winner == "O" else 3
        game = dict(curMode=1, curClass=self.fixture["sides"][0]["character_class"], curRound=2 if self.finalized else 1,
                    wins=int(self.winner == "P"), losses=int(self.winner == "O"),
                    tries=5 - int(self.winner == "O"), survivalMode=False,
                    fightEnded=self.ended, roundResults=[first_result] + [3] * 17,
                    ropeSpeedups={}, cubeAdvanced={}, sandbagActive=False,
                    numTimesOutOfStamina=sum(item.out_of_stamina for item in self.side_items["P"]))
        return dict(runtime=self._runtime_projection(), winner=self.winner, round=2 if self.finalized else 1, timestamp=self.time,
                    game=game, characters=characters, native_rule_state=native_rule_state(self),
                    items=item_states, pre_cleanup_hp=getattr(self, "pre_cleanup_hp", None),
                    fatigue_counter=self.fatigue_counter, time_advance=0.0,
                    event_bus=dict(logging_mode=self.logging_mode, pending_signal_count=len(self.signal_queue), connection_count=0) if self.finalized else None)

    def event_references(self):
        references = {}
        def visit(identity, visiting):
            if identity is None or str(identity) in references:
                return
            if identity in visiting:
                raise ValueError("cyclic independently generated event parent")
            event = self.allocated_events[identity]
            visit(event["parent"], visiting | {identity})
            references[str(identity)] = {key: deepcopy(value) for key, value in event.items() if key != "sequence"}
        for event in self.events:
            visit(event["parent"], set())
        return references

    def result(self):
        if self.king_mode:
            if not self.frame_driver.finalized:raise ValueError('King source terminal barrier incomplete')
            if self.source_king_mode:self.frame_driver.complete()
            else:self.frame_driver.run()  # Finite records still require exact exhaustion.
        if not self.finalized:
            raise ValueError("combat is not complete")
        if assert_model_source_stable() != self.model_source_sha256:
            raise ValueError("model_source_changed_during_run")
        result = dict(schema=1, implementation="native_replay_v8_independent_slice",
                    model_package="native_replay_v8", observer_version=observer_label(self.runtime_inputs.data),
                    comparison_status="NOT_EVALUATED", random_alignment=self.random.alignment,
                    model_source_sha256=dict(self.model_source_sha256),
                    fixture=deepcopy(self.fixture), events=deepcopy(self.events),
                    event_references=self.event_references(), histories=self.histories.snapshot(),
                    final=self.snapshot(),
                    random_inputs=deepcopy(self.random.audit),
                    scheduling=dict(physics_order=self.physics_order, preparation_order=self.preparation_order,
                                    frames=self.frame, elapsed=self.elapsed, status="requires_native_trace_validation"),
                    schedule_trace=deepcopy(self.schedule_trace), runtime_trace=deepcopy(self.runtime_trace),
                    allocated_events=deepcopy(self.allocated_events),
                    coverage=dict(items=list(CATALOG), unknown=["full_game", "native_UI_RNG", "unimplemented_callback_paths",
                                                               "gems", "retail_equivalence"]))
        if self.king_mode:
            result['king_terminal']=dict(post_cleanup=deepcopy(self.frame_driver.post_cleanup_snapshot),
                                        final=deepcopy(self.frame_driver.final_snapshot),
                                        passes=deepcopy(self.frame_driver.pass_trace))
        if self.pure_combat_mode:
            result['pure_combat_diagnostics'] = dict(schema='phase443-same-instance-business/1',
                contract=deepcopy(PURE441_CONTRACT), snapshots=deepcopy(self.pure_snapshots),
                post_cleanup=deepcopy(self.frame_driver.post_cleanup_snapshot['business']),
                final=deepcopy(self.frame_driver.final_snapshot['business']),
                api=deepcopy(self.pure_api_trace), callbacks=[deepcopy(x) for x in self.runtime_trace if x.get('kind')=='source_callback'],
                tape_position=self.random.position, tape_records=len(self.random.records),
                comparison_status='NOT_EVALUATED', pre_run_closure='External launcher responsibility; not a gameplay certificate')
        return result

    @staticmethod
    def _source_king_budget(max_seconds):
        if (type(max_seconds) not in (int, float) or not math.isfinite(max_seconds)
                or not 0 < max_seconds <= SOURCE_KING_MAX_SECONDS):
            raise ValueError('source King absolute positive finite budget <=120 required')
        return float(max_seconds)

    def _source_king_quantum(self, max_seconds=SOURCE_KING_MAX_SECONDS):
        budget = self._source_king_budget(max_seconds)
        if not self.source_king_mode:
            raise ValueError('SOURCE King quantum requires exact production profile')
        if not self.prepared:self.prepare_only()
        if not self.activated:self.activate_from_checkpoint()
        driver = self.frame_driver
        if driver.finalized:return False
        if driver._stepping or driver.pass_index % 2:
            raise ValueError('public source King quantum requires a complete physics/idle boundary')
        if not self.ended and (self.elapsed >= budget or driver.pass_index // 2 >= SOURCE_KING_QUANTA):
            raise TimeoutError('source King budget exhausted before rule end')
        self.step()
        if not driver.finalized:self.step()
        return not driver.finalized

    def _run_source_king(self, max_seconds, delta):
        budget = self._source_king_budget(max_seconds)
        if type(delta) is not float or delta != NATIVE_PHYSICS_DELTA:
            raise ValueError('source King uses fixed60 promoted-f32 delta')
        while not self.frame_driver.finalized:
            self._source_king_quantum(budget)
        return self.result()

    def run(self, max_seconds=120.0, delta=NATIVE_PHYSICS_DELTA):
        if self.source_king_mode:
            return self._run_source_king(max_seconds, delta)
        if not self.prepared:
            self.prepare_only()
        if not self.activated:
            self.activate_from_checkpoint()
        while not (self.frame_driver.finalized if self.king_mode else self.finalized):
            if self.elapsed >= max_seconds:
                raise TimeoutError(f"native_replay combat exceeded {max_seconds} seconds")
            self.step(delta)
        return self.result()


#355 actual finite runtime: private defaults never come from outcome observations.
def _single_king_genuine_profile(runtime):
    data = runtime.data if isinstance(runtime, RuntimeDTO) else runtime
    return type(data) is dict and data.get('profile_id') == SINGLE_KING_GENUINE_PROFILE


def _validate_single_king_initials(data):
    zero = _float_bits(0.0)
    for fields in data['initial_items'].values():
        if any(fields[k] != zero for k in ('lastActivationTime_bits', 'lastTriggerTime_bits')):
            raise ValueError('single King fresh constructor limiter times required')
        if any(type(fields[k]) is not int or fields[k] != 0 for k in ('activationsThisFrame', 'triggersThisFrame')):
            raise ValueError('single King fresh constructor limiter counters required')


def _validate_single_king_topology(data, table):
    def child(role, parent, suffix):
        node, owner = table[role], table[parent]
        if (node['positions'] != owner['positions'] + suffix or node['priority'] != 0
                or not node['path'].startswith(owner['path'] + '/')):
            raise ValueError('single King SOURCE relative Timer topology ' + role)
    for side in ('P', 'O'):
        child('tick:' + side, 'character:' + side, [3])
        child('invu:' + side, 'character:' + side, [5])
    child('king_buff:P:12', 'item:P:12', [7])
    owner = table['item:P:12']
    parts = data['king_particles']['P:12']
    for kind, suffix, timer in (('activation', [8], 'king_hide:P:12'), ('drag', [1, 2], 'king_drag:P:12')):
        node = parts[kind]['node']
        if node['positions'] != owner['positions'] + suffix or not node['path'].startswith(owner['path'] + '/'):
            raise ValueError('single King SOURCE particle ancestry ' + kind)
        t = table[timer]
        if t['positions'] != node['positions'] + [0] or t['priority'] != 0:
            raise ValueError('single King ready-created Timer child0 ' + kind)

def _validate_single_king_processing_inputs(data,fixture):
    from .genuine import validate_single_king_ui_authority, validate_single_king_fixture
    authority=validate_single_king_ui_authority(data['ui_authority'])
    # No guessed flags or caller-supplied verified booleans: raw complete carrier is revalidated.
    if authority['unsupported']!=0:raise ValueError('NOT_ADMITTED: unsupported UI entry')
    required=set(_required_roles(fixture))|AUX_ROLES|{'root_viewport','game'}
    rows=data['processing_nodes']
    if type(rows)is not list or len(rows)!=len(required):raise ValueError('single King processing association roles')
    validate_single_king_fixture(fixture)
    table={};native_ids=set();paths=set();positions=set();prefixes={}
    for n in rows:
        _keys(n,NODE_INPUT_KEYS,'processing node')
        if n['role']not in required or n['role']in table or type(n['native_id'])is not str or re.fullmatch('[1-9][0-9]*',n['native_id'])is None or n['native_id']in native_ids:
            raise ValueError('processing identity/role')
        if n['inside_tree']is not True or type(n['path'])is not str or n['path']in paths or type(n['positions'])is not list or tuple(n['positions'])in positions:
            raise ValueError('processing actual path/index')
        names=n['path'].split('/')[1:]
        if not(n['path']=='/root' or n['path'].startswith('/root/')) or len(names)!=len(n['positions']) or n['positions'][0]!=-1 or any(type(x)is not int or not 0<=x<=4096 for x in n['positions'][1:]) or n['name']!=names[-1]:raise ValueError('processing node coordinates')
        if type(n['priority'])is not int or type(n['class'])is not str:raise ValueError('processing scalar types')
        for flag in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
            if type(n[flag])is not bool:raise ValueError('actual independent processing flags')
        for j in range(1,len(names)+1):
            key=tuple(n['positions'][:j]);value=tuple(names[:j])
            if key in prefixes and prefixes[key]!=value:raise ValueError('raw processing prefix conflict')
            prefixes[key]=value
        table[n['role']]=n;native_ids.add(n['native_id']);paths.add(n['path']);positions.add(tuple(n['positions']))
    root=table['root_viewport']
    if data['root_node']!=root or root['path']!='/root' or root['positions']!=[-1] or root['priority']!=0 or root['class']!='Viewport' or not root['internal_physics'] or root['ordinary_physics'] or root['ordinary_idle']:
        raise ValueError('unsupported actual root flags')
    for node in data['nodes']:
        actual=table[node['role']]
        if any(node[k]!=actual[k]for k in ('path','positions','priority')):raise ValueError('model/raw topology mismatch')
        if node['kind']=='timer' and actual['class']!='Timer':raise ValueError('Timer class')
    for role,n in table.items():
        if role=='root_viewport':continue
        if n['internal_physics'] or n['internal_idle']:raise ValueError('nonroot initial internal callback')
        flags=(n['ordinary_physics'],n['ordinary_idle'])
        expected=(True,True)if role in ('util','game')else (True,False)if role.startswith('character:')else (False,True)if role.startswith('item:')else(False,False)
        if flags!=expected:raise ValueError('unsupported initial ordinary membership '+role)
    _keys(data['inactive_auxiliaries'],AUX_ROLES,'inactive auxiliary table')
    for role,x in data['inactive_auxiliaries'].items():
        _keys(x,('source_lemma','lineage','wait_time_bits','one_shot','process_mode'),'auxiliary fact')
        if x['source_lemma']!=AUX_LEMMA or x['lineage']!='fresh_configured' or x['one_shot']is not True or type(x['process_mode'])is not int or x['process_mode']!=0 or table[role]['class']!='Timer':raise ValueError('source inactive auxiliary')
        wait=_be_float(x['wait_time_bits'])
        if wait<=0 or f32(wait)!=wait:raise ValueError('aux wait getter')
    for identity,parts in data['king_particles'].items():
        king=table['item:'+identity]
        binds=[r['payload']for r in data['ui_authority']if r['kind']=='bind' and r['payload']['item_id']==king['native_id']]
        if len(binds)!=1:raise ValueError('particle source binding')
        for kind,part in parts.items():
            n=part['node'];_keys(n,NODE_INPUT_KEYS,'actual particle node')
            timer=table[('king_hide:'if kind=='activation'else'king_drag:')+identity]
            if n['class']!='Particles2D' or n['role']is not None or n['native_id']!=binds[0][kind+'_id'] or timer['path'].rsplit('/',1)[0]!=n['path'] or timer['positions'][:-1]!=n['positions'] or n['name']!=n['path'].rsplit('/',1)[1] or n['inside_tree']is not True or type(n['priority'])is not int:
                raise ValueError('distinct actual particle identity')
            if n['native_id']in native_ids or any(n[k]is not False for k in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')):raise ValueError('continuous particle source inactive callback flags')
            native_ids.add(n['native_id'])
    first=data['ui_authority'][0];last=data['ui_authority'][-1];controls=last['payload']['controls']
    if controls['root_id']!=root['native_id'] or any(controls[k]!=root[k]for k in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle')):raise ValueError('UI/root flags disagree')
    roles=next(r['payload']for r in data['ui_authority']if r['kind']=='roles')
    for guard in roles['selected_guards']:
        node=table.get('item:'+guard['role'])
        if node is None or node['native_id']!=guard['item_id'] or guard['viewport_id']!=root['native_id']:raise ValueError('UI selected native association')
    clock=decode_clock(data['frame_clock'])
    if not(first['physics_frame']<=clock.physics_frame<=last['physics_frame'] and first['idle_frame']<=clock.idle_frame<=last['idle_frame']):raise ValueError('activation outside complete UI window')
    # Source UI footer is authority only: it never ends the model or configures pass consumption.
    _validate_single_king_topology(data, table)
    return table



#443 fixed14 DTO. These routines validate emitted state, never external proof flags.
def _pure441_profile(runtime):
    data = runtime.data if isinstance(runtime, RuntimeDTO) else runtime
    return type(data) is dict and data.get('profile_id') == PURE441_PROFILE


def _pure441_roles(fixture):
    roles = _required_roles(fixture)
    del roles['king_hide:P:12']
    del roles['king_drag:P:12']
    roles['game'] = 'ordinary'
    for side in ('P', 'O'):
        for name in ('battleRageTimer', 'autoRageTimer'):
            roles['aux:' + side + ':' + name] = 'timer'
    return roles


def _validate_pure441_runtime(data, fixture, original):
    validate_pure441_profile(data, fixture)
    _keys(data, ('schema','mode','profile_id','checkpoint','environment','nodes','timer_initial',
                 'initial_items','initial_characters','prepare_order','activate_order','terminal_profile',
                 'frame_clock','processing_nodes'), 'pure441 runtime14')
    _keys(data['environment'], ('fps','scale','paused'), 'pure environment')
    env = data['environment']
    if type(env['fps']) is not int or env['fps'] != 60 or type(env['scale']) is not float or env['scale'] != 1.0 or env['paused'] is not False:
        raise ValueError('pure441 fixed60 scale1 unpaused required')
    _keys(data['checkpoint'], ('util_time_bits','combat_time_bits','source_phase'), 'pure checkpoint')
    checkpoint = data['checkpoint']
    util_time = _be_float(checkpoint['util_time_bits'])
    if util_time < 0 or checkpoint['combat_time_bits'] != _float_bits(0.0) or checkpoint['source_phase'] != 'Core/Game.gd::activateItems:enter':
        raise ValueError('pure441 activation checkpoint')
    clock = decode_clock(data['frame_clock'])
    if _float_bits(clock.util_time) != checkpoint['util_time_bits']:
        raise ValueError('pure441 checkpoint/clock mismatch')
    ids = {i['instance_id'] for side in fixture['sides'] for i in side['items']}
    for field in ('prepare_order','activate_order'):
        order = data[field]
        if type(order) is not list or len(order) != 39 or any(type(i) is not str for i in order) or set(order) != ids:
            raise ValueError('pure441 exact39 item order')
    if data['prepare_order'] != data['activate_order']:
        raise ValueError('pure441 different prepare/activate order unsupported')
    _keys(data['initial_items'], ids, 'pure initial items')
    for values in data['initial_items'].values():
        _keys(values, ('lastActivationTime_bits','lastTriggerTime_bits','activationsThisFrame','triggersThisFrame','dragged','moveback_running','cache_fresh'), 'pure emitted item scalars')
        if any(values[k] != _float_bits(0.0) for k in ('lastActivationTime_bits','lastTriggerTime_bits')):
            raise ValueError('pure441 limiter bits differ from fixed input domain')
        if any(type(values[k]) is not int or values[k] != 0 for k in ('activationsThisFrame','triggersThisFrame')):
            raise ValueError('pure441 limiter integer domain')
        if values['dragged'] is not False or values['moveback_running'] is not False or values['cache_fresh'] is not True:
            raise ValueError('pure441 emitted drag/tween/cache predicate')
    _keys(data['initial_characters'], ('P','O'), 'pure initial characters')
    for values in data['initial_characters'].values():
        _keys(values, ('invulnerable','invulnerabilityItem','buffProtectStacks'), 'pure character fields')
        if values['invulnerable'] is not False or values['invulnerabilityItem'] is not None or type(values['buffProtectStacks']) is not int or values['buffProtectStacks'] != 0:
            raise ValueError('unsupported fixed441 character initial values')
    required = _pure441_roles(fixture)
    rows = data['processing_nodes']
    if type(rows) is not list or len(rows) != 78:
        raise ValueError('pure441 processing78 required')
    table, native_ids, paths, positions, prefixes = {}, set(), set(), set(), {}
    for node in rows:
        _keys(node, NODE_INPUT_KEYS, 'pure processing node')
        role = node['role']
        if type(role) is not str or role not in set(required) | {'root_viewport'} or role in table:
            raise ValueError('pure441 unknown/duplicate role')
        if type(node['native_id']) is not str or re.fullmatch('[1-9][0-9]*',node['native_id']) is None or node['native_id'] in native_ids:
            raise ValueError('pure441 native identity')
        if type(node['path']) is not str or not (node['path']=='/root' or node['path'].startswith('/root/')) or node['path'] in paths:
            raise ValueError('pure441 actual path')
        names, pos = node['path'].split('/')[1:], node['positions']
        if type(pos) is not list or len(pos) != len(names) or not pos or pos[0] != -1 or any(type(x) is not int for x in pos) or any(not 0 <= x <= 4096 for x in pos[1:]) or tuple(pos) in positions:
            raise ValueError('pure441 actual sparse coordinates')
        if node['name'] != names[-1] or type(node['priority']) is not int or not -(2**31) <= node['priority'] < 2**31 or type(node['class']) is not str or node['inside_tree'] is not True:
            raise ValueError('pure441 node scalar types')
        for flag in ('ordinary_physics','internal_physics','ordinary_idle','internal_idle'):
            if type(node[flag]) is not bool:raise ValueError('pure441 independent bool flags')
        for j in range(1,len(names)+1):
            prefix = tuple(pos[:j])
            if prefix in prefixes and prefixes[prefix] != tuple(names[:j]):raise ValueError('pure441 sparse prefix conflict')
            prefixes[prefix] = tuple(names[:j])
        if role == 'root_viewport':
            if node['path']!='/root' or pos!=[-1] or node['priority']!=0 or node['class']!='Viewport' or (node['ordinary_physics'],node['internal_physics'],node['ordinary_idle'],node['internal_idle']) != (False,True,False,False):
                raise ValueError('pure441 root flags')
        else:
            if node['internal_physics'] or node['internal_idle']:raise ValueError('pure441 initial native internal flags')
            expected = (True,True) if role in ('game','util') else (True,False) if role.startswith('character:') else (False,True) if role.startswith('item:') else (False,False)
            if (node['ordinary_physics'],node['ordinary_idle']) != expected:raise ValueError('pure441 initial ordinary memberships')
        table[role]=node;native_ids.add(node['native_id']);paths.add(node['path']);positions.add(tuple(pos))
    if set(table) != set(required)|{'root_viewport'}:raise ValueError('pure441 complete processing roles')
    configs = data['nodes']
    if type(configs) is not list or len(configs)!=77:raise ValueError('pure441 config77 required')
    seen=set()
    for config in configs:
        _keys(config, ('role','path','positions','priority','kind'), 'pure node config')
        role=config['role']
        if type(role) is not str or role not in required or role in seen or type(config['kind']) is not str or config['kind']!=required[role]:raise ValueError('pure441 node kind/role')
        actual=table[role]
        if type(config['positions']) is not list or any(type(x) is not int for x in config['positions']):raise ValueError('pure441 typed config positions')
        if any(type(config[k]) is not type(actual[k]) or config[k]!=actual[k] for k in ('path','positions','priority')):raise ValueError('pure441 raw/config topology')
        seen.add(role)
    timers={role for role,kind in required.items() if kind=='timer'}
    _keys(data['timer_initial'],timers,'pure33 timer values')
    if len(timers)!=33:raise ValueError('pure441 exact33 timers')
    for role, initial in data['timer_initial'].items():
        _keys(initial, ('wait_time_bits','one_shot','process_mode','autostart','paused','private_left_bits'), 'pure timer fields')
        wait=_be_float(initial['wait_time_bits'])
        if wait!=1.0 or f32(wait)!=wait or type(initial['one_shot']) is not bool or initial['one_shot'] != (not role.startswith('tick:')) or type(initial['process_mode']) is not int or initial['process_mode']!=0 or initial['autostart'] is not False or initial['paused'] is not False or initial['private_left_bits'] != _float_bits(-1.0) or table[role]['class']!='Timer':
            raise ValueError('pure441 unsupported typed Timer state/config')
    for side, child in (('P',7),('O',5)):
        timer,parent=table['invu:'+side],table['character:'+side]
        if timer['positions']!=parent['positions']+[child] or timer['path']!=parent['path']+'/InvulnerabilityTimer':raise ValueError('pure441 P7/O5 topology')
    if isinstance(original,RuntimeDTO) and (type(original.prepare_order) is not tuple or original.prepare_order!=tuple(data['prepare_order']) or type(original.util_time) is not float or _float_bits(original.util_time)!=checkpoint['util_time_bits']):
        raise ValueError('pure441 RuntimeDTO convenience mismatch')
    return RuntimeDTO(data,tuple(data['prepare_order']),util_time)


def _assert_pure441_timer(node, initial):
    if (not isinstance(node,TimerRecord) or _float_bits(node.wait_time)!=initial['wait_time_bits']
            or node.one_shot is not initial['one_shot'] or node.process_mode!=initial['process_mode']
            or node.autostart is not initial['autostart'] or node.paused is not initial['paused']
            or _float_bits(node.private_left)!=initial['private_left_bits'] or node.processing
            or node.internal_physics or node.internal_idle or node.ordinary_physics or node.ordinary_idle):
        raise ValueError('actual model Timer differs from supported initial state')


def _build_pure441_scaffold(dto):
    table={n['role']:n for n in dto.data['processing_nodes']}
    runtime=TimerRuntime(root_internal_idle=table['root_viewport']['internal_idle'])
    configs=dto.data['nodes'];by_position={tuple(n['positions']):n for n in configs};prefixes={(-1,):('root',)}
    for config in configs:
        names=config['path'].split('/')[1:]
        for end in range(2,len(names)+1):prefixes[tuple(config['positions'][:end])]=tuple(names[:end])
    objects,records={(-1,):runtime.root},{}
    for pos in sorted((p for p in prefixes if len(p)>1),key=lambda p:(len(p),p)):
        parent=objects[pos[:-1]]
        while len(parent.children)<pos[-1]:
            gap=runtime.new_node('gap:'+str(pos[:-1])+':'+str(len(parent.children)),'__v8_gap_'+str(len(parent.children)))
            runtime.add_child(parent,gap)
        config=by_position.get(pos);name=prefixes[pos][-1]
        role=config['role'] if config else 'ancestor:'+'/'.join(prefixes[pos])
        node=runtime.new_timer(role,name) if config and config['kind']=='timer' else runtime.new_node(role,name)
        runtime.add_child(parent,node);objects[pos]=node
        if config:
            runtime.set_priority(node,config['priority']);records[role]=node
            if config['kind']=='timer':
                initial=dto.data['timer_initial'][role]
                runtime.configure_timer(node,initial['one_shot'],initial['process_mode'])
                result=runtime.set_wait_time(node,_be_float(initial['wait_time_bits']))
                if not result.ok:raise ValueError(result.error)
                _assert_pure441_timer(node,initial)
    ordinary=sorted((n for n in configs if n['kind']=='ordinary'),key=lambda n:(n['priority'],tuple(n['positions'])))
    return runtime,records,[n['role'] for n in ordinary]


def _pure441_variant(value):
    if type(value) is int:return dict(type='int',decimal=str(value))
    if type(value) is float and math.isfinite(value):return dict(type='float',binary64_be=_float_bits(value))
    raise ValueError('pure Timer argument must retain finite INT/REAL Variant')
