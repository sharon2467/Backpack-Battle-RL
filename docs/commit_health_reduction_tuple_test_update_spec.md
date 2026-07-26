# `commit_health_reduction` 二元返回值测试更新简短 SPEC

状态：已实现（2026-07-26）；只更新测试契约，未修改生产代码。  
日期：2026-07-26。

## 1. Requirements（需求）

以当前生产接口为准：

```python
BattleState.commit_health_reduction(
    player: PlayerState,
    blocked_damage: int,
    health_damage: int,
) -> tuple[int, int]
```

返回值依次为：

```python
(final_blocked_damage, final_health_damage)
```

测试不得继续把返回值解释为两项之和。致命扣血仍在返回前抛出
`_BattleFinishedSignal`，该测试不变。

## 2. Design（设计）

只修改当前失败的四个测试：

| 测试 | 新断言 |
| --- | --- |
| `test_commit_health_reduction_updates_block_and_health` | 返回 `(2, 4)` |
| `test_commit_health_reduction_returns_block_only_and_health_only` | 分别返回 `(2, 0)`、`(0, 4)` |
| `test_poison_tick_consumes_block_before_health` | `_apply_poison_tick()` 透传 `(2, 3)` |
| `test_melee_statuses_use_commit_returned_final_damage` | 测试替身对防守方返回 `(0, 2)`，验证 resolver 把二元组求和后传给近战状态结算 |

不修改 `commit_health_reduction()`、`resolve_attack()`、
`_apply_poison_tick()` 或其他生产函数。

## 3. Realize（逐测试修改）

### `tests/test_battle_module_v1.py`

```text
updates_block_and_health:
    接收 damage_parts
    断言 damage_parts == (2, 4)
    保留 Block/Health/胜负断言

returns_block_only_and_health_only:
    block-only 断言 (2, 0)
    health-only 断言 (0, 4)

poison_tick_consumes_block_before_health:
    断言返回 (2, 3)
    保留最终 Block=0、Health=7
```

### `tests/test_attack_resolution_v1.py`

`AdjustedFinalDamageBattleState.commit_health_reduction()` 仍先调用
`super()` 完成真实状态提交；当目标为防守方时，测试替身返回 `(0, 2)`，其余目标
原样返回基类二元组。这样 `resolve_attack()` 得到的最终伤害为 `0 + 2`，测试继续
验证 Spikes 与 Vampirism 使用 2，而不是原始 7。

## 4. Tasks（任务）

1. 更新三个 `test_battle_module_v1.py` 断言。
2. 更新攻击测试替身的返回值。
3. 运行完整测试套件，要求全部通过。

## 5. Acceptance Criteria / Tests（验收）

- 四个原失败测试通过。
- 完整测试套件通过。
- `git diff` 中没有本任务造成的生产代码修改。

## 6. 实现结果

- 四个目标测试全部通过。
- 完整测试套件共 436 项，全部通过。
