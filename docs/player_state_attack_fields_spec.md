# PlayerState 攻击结算字段补充

## 1. Requirements（需求）

用户要求直接补齐上一轮清单第 1 组的角色字段，包括攻击数值、尖刺/吸血比例上限和三份平衡随机状态。

- 新字段可通过 `PlayerState` 构造参数设置，默认值采用原版战斗准备后的值。
- 每个角色拥有独立的类型伤害加成字典和三份独立随机状态。
- 保持已有构造参数的位置和默认值，已有物品及初始化入口可继续运行。
- 本轮交付角色的数据字段。攻击结算、治疗、死亡、疲惫和随机判定的读取逻辑由后续流程修改接入；角色快照的现有输出格式继续沿用。

权威依据：`Backpack Battles/Core/Character.gd:55-97,349-399`；平衡随机的使用状态见 `Backpack Battles/Utility/BalancedRandom.gd:4-7,18-49,104-107`。

## 2. Design（设计）

### 2.1 数据模型

在 `battle_module_v1.py` 的现有 `PlayerState` dataclass 后追加以下字段，避免改变已有位置参数含义：

| 字段 | 类型 | 默认值 |
| --- | --- | --- |
| is_dead | bool | False |
| damage_resistance | float | 0.0 |
| damage_reduction | int | 0 |
| invulnerable | bool | False |
| dodge_stacks | int | 0 |
| crit_tokens | int | 0 |
| crit_resistance | float | 0.0 |
| crit_resist_stacks | int | 0 |
| bonus_fatigue_damage | int | 0 |
| healing_efficiency | float | 1.0 |
| unhealing_amount | float | 0.0 |
| empower_damage | float | 1.0 |
| typed_damage_factors | dict[str, float] | 八种伤害类型分别为 0.0 |
| melee_spikes_limit | float | 1.0 |
| ranged_spikes_limit | float | 0.0 |
| effect_spikes_limit | float | 0.0 |
| melee_vampirism_limit | float | 1.0 |
| ranged_vampirism_limit | float | 0.0 |
| accuracy_rng | BalancedRngState | 独立新状态 |
| crit_rng | BalancedRngState | 独立新状态 |
| crit_resistance_rng | BalancedRngState | 独立新状态 |

伤害类型键为 `melee`、`ranged`、`effect`、`self_damage`、`unhealing`、`spikes`、`poison`、`fatigue`。

用一个普通 dataclass `BalancedRngState` 保存原版 `roll` 使用的三项历史状态：`expected_wins: float = 0.0`、`wins: int = 0`、`last_result: bool = False`。初始值对应原版战斗准备时的 `reset()`。该类仅存状态，后续判定函数使用 `BattleState.rng` 抽样，不为每个字段另建随机数生成器，也不在角色构造时消耗随机数。

`typed_damage_factors` 与三份随机状态均使用 `default_factory`，不会在角色间共享对象。角色的 `damage_reduction` 与事件减伤分别保存；`bonus_fatigue_damage` 与已有递增值 `fatigue_damage` 分别保存。

### 2.2 具体接口与伪代码

#### BalancedRngState.__init__(self, expected_wins: float = 0.0, wins: int = 0, last_result: bool = False) -> None

由 dataclass 自动生成：

```text
保存 expected_wins、wins、last_result
不执行随机抽样
```

#### PlayerState.__init__(...) -> None

完整构造接口（dataclass 自动生成）：

```python
PlayerState(
    player_id: str | None = None,
    health: int = 0,
    max_health: int = 0,
    block: int = 0,
    fatigue_damage: int = 0,
    stamina: float = 0.0,
    max_stamina: float = 0.0,
    buffs: BuffSlot = <独立默认对象>,
    debuffs: DebuffSlot = <独立默认对象>,
    items: dict[str, BattleItem] = <独立空字典>,
    is_dead: bool = False,
    damage_resistance: float = 0.0,
    damage_reduction: int = 0,
    invulnerable: bool = False,
    dodge_stacks: int = 0,
    crit_tokens: int = 0,
    crit_resistance: float = 0.0,
    crit_resist_stacks: int = 0,
    bonus_fatigue_damage: int = 0,
    healing_efficiency: float = 1.0,
    unhealing_amount: float = 0.0,
    empower_damage: float = 1.0,
    typed_damage_factors: dict[str, float] = <独立默认字典>,
    melee_spikes_limit: float = 1.0,
    ranged_spikes_limit: float = 0.0,
    effect_spikes_limit: float = 0.0,
    melee_vampirism_limit: float = 1.0,
    ranged_vampirism_limit: float = 0.0,
    accuracy_rng: BalancedRngState = <独立默认状态>,
    crit_rng: BalancedRngState = <独立默认状态>,
    crit_resistance_rng: BalancedRngState = <独立默认状态>,
)
```

```text
按原有顺序保存旧参数
保存新增标量参数
未显式传入字典时调用字典默认工厂
未显式传入随机状态时，各自新建一个 BalancedRngState
沿用现有 __setattr__ 的生命扣除约束
```

#### PlayerState.typed_damage_factors 默认工厂 () -> dict[str, float]

```text
返回新字典
八个伤害类型键的值均为 0.0
```

流程为：`创建 PlayerState → 填充默认数值与独立状态 → 后续引擎读取/修改`。

## 3. Tasks（任务拆解）

- [x] T1：保存本 SPEC。
- [x] T2（依赖 T1）：加入 `BalancedRngState` 和全部 21 个字段。
- [x] T3（依赖 T2）：检查字段构造、默认值和角色间可变状态隔离；运行已有角色、初始化和快照相关测试。
- [x] T4（依赖 T3）：检查差异，记录验证结果。

## 4. Acceptance Criteria / Tests（验收标准）

- 清单中的 21 个字段全部存在，可通过构造参数覆盖。
- 八种伤害类型具有独立字典，三个判定各有独立状态，不同角色之间也不共享默认对象。
- 原有位置参数仍绑定相同字段，初始化入口无需迁移。
- 已有角色、战斗初始化和快照相关测试通过。
- 角色构造不消耗战斗 RNG；本轮新增字段尚未改变伤害判定行为。

## 5. 执行结果

- `battle_module_v1.py` 已加入全部 21 个字段和仅保存判定历史的 `BalancedRngState`。
- 使用用户指定的 Python 3.11 进行构造检查：旧位置参数含义、八种类型默认字典、同角色三个状态和不同角色之间的状态隔离均通过。
- 已有 `test_battle_module_v1.py`、`test_battle_initializer_v1.py`、`test_player_state_history_v1.py` 共 112 个测试通过。
- `git diff --check` 通过。
- 攻击/治疗结算与快照函数继续沿用已有实现，新增字段等待后续结算流程接入。
