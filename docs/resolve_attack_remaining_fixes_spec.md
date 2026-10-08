# 伤害结算剩余问题修复 SPEC

日期：2026-10-07；修订及实施：2026-10-08。状态：已实现并通过 Python 回归。终局方案采用调度边界显式检查，不使用嵌套深度计数器。

## 1. Requirements（需求）

- 作为模拟器维护者，我需要普通攻击、Effect、荆棘、毒、疲劳和反治疗共享正确的受伤流程，且无物品来源也能正常结算。
- 修复本轮审查发现的入口缺失、属性缺失、旧接口调用、死亡时序、flags、取整和未接通字段；保留用户已修好的机制。
- 机制以当前 `Backpack Battles/` 解包源码为准，结合 `resolve_attack_damage_fields_audit.md` 和两份 GUI 实测报告。不改游戏源码、不扩展局外系统、不实现无关物品。
- 完成标准：以下函数契约落地，代表性战斗不再异常，关键阶段和边界结果与原版一致；不以旧测试全部通过代替源码一致性。

## 2. Design（设计）

沿用现有 dataclass、事件和直接函数调用；只增加必要的数值辅助函数，不引入新事件框架或伤害类层级。

数据约定：`BattleItem` 初始化 `damage_multiplier=1.0`、`crit_tokens=0`、伤害区间平衡累计值；伤害抗性继续使用百分数。`AttackEvent.source_item` 可空，角色身份直接取事件的 attacker/defender。类型默认 flags 在创建伤害源时应用，显式覆盖优先；不能在 resolve 中仅凭 Effect 类型重置 flags。默认表改用现有小写类型名及具名布尔字段。

实现补充：治疗沿用现有上下文模式，增加简单的 `HealingContext(BattleContext)` 数据类，仅保存 amount、overheal、log_handle，供治疗监听器读取并通过继承的 for_item 切换视角；不增加新事件框架。heal 接受 `source` 关键字参数以保留物品/再生/吸血日志来源。旧伤害日志 final_* 键保留为已结算伤害的兼容字段，不再按剩余生命裁剪；移除旧的扣血日志补全辅助函数，其职责由 resolve_attack 写入完整日志替代。

原版范围约定：武器攻击才按可强化条件加 Empower；物品攻击、预计算 Effect 和无物品伤害分别按其来源规则准备数值，避免给荆棘/毒/疲劳重复乘武器倍率。荆棘允许暴击。`can_activate_item` 控制响应物品的资格，不粗暴屏蔽全部受伤通知。

删除合并函数 `_apply_melee_hit_statuses`，拆成 `apply_spikes(event)` 和 `apply_vampirism(event)`；二者直接读取事件的结算总伤害 `pending_damage`，不再额外传递同一伤害值。荆棘在受击方死亡判定后处理；普通攻击调用路径在荆棘完全返回后处理吸血，然后进行来源 attacked 收尾。吸血调用资格还须对应原版 `Character.dealDamage` 路径，不能仅凭 Effect 的 flags 推断应调用吸血；直接 `takeDamage` 路径及 `Item.stealLife` 专用治疗不应额外获得普通吸血。两函数均不限制为近战、不检查终局提前退出、不抛结束信号。

```text
创建来源与 flags → 已死亡检查 → 命中/闪避 → early
→ 按来源准备伤害/额外疲劳 → 暴击与抵抗 → 抗性/攻击固定减伤/无敌
→ pre_take/事件减伤 → late → 护盾与生命提交
→ 受伤通知/onDealtDamage → 判定死亡并立即锁定胜负 → 荆棘
→ 返回攻击调用侧/吸血 → 来源 attacked（终局后不再派发监听器）
→ 返回物品或系统调用方并完成其直接后续代码 → 调度边界抛结束信号
```

死亡检查位于原版回调之后。首次 death 时立即锁定 winner，作为 fightEnded 的模拟器等价标志；不得等后续反伤、吸血完成后重算胜负。按原版正常战斗分支，在首次死亡通知时若 OPPONENT.health<=0 则 PLAYER 胜，否则 OPPONENT 胜；双方当时都不大于零也走 PLAYER 胜利分支。PLAYER/OPPONENT 沿用既有战斗角色映射，不以本次 attacker/defender 替代，不纳入原版调试强制胜负开关。

不引入深度计数器。`resolve_attack`、扣血、治疗、反伤/吸血、单次毒/疲劳/再生、物品效果及监听器内部均不调用 `stop_if_battle_ended`。这些函数即使造成死亡也正常返回，允许当前直接调用链完成；对已死亡目标的再次伤害仍由 is_dead 入口拦截，而不是按 winner 全局拒绝伤害。只有调度层在下列位置检查并抛出结束信号：

1. `step()` 的 try 内、恢复耐力之前。
2. `step()` 中每个顶层 `item.activate_item(context)` 返回后。
3. `_apply_system_triggers()` 中每一次独立再生、毒或疲劳调用返回后，包括双方疲劳两次调用之间；顺序保持“对手再生 → 对手毒 → 对手疲劳 → 玩家疲劳 → 玩家毒 → 玩家再生”，仅执行到期项目。再生也检查，因为可能引出反治疗。

`step()` 捕获 `_BattleFinishedSignal`、记录最后快照并返回 winner；不吞掉其他异常。直接调用结算器的测试仍能取得致死事件返回值；外部若自行调度多个动作，应在各完整动作返回后显式检查。

原版收尾边界依据：`Character.gd:648–653,482–487` 的死亡后荆棘/吸血；`Item.gd:5119–5123` 的专用吸血治疗；HoloFireLizard 的伤害后加热、LuckyBow 的后续攻击与状态清除、Stone 的消耗、`Item.trigger:4409–4416` 的双重激活判断均属直接代码，不能被异常提前截断。`activate_item()` 返回前应完成所实现物品对应的整次触发逻辑。此约定不要求新增尚未实现的物品。

终局后 EventBus 仍允许记录事件，但每个监听器调用前检查终局并停止后续派发；已经进入的监听器继续其直接代码。伤害来源的直接钩子不能仅因终局而被一并屏蔽。普通 `Item.activate()` 的激活日志/统计则有独立终局门控，模拟器 `emit_activation()` 应对应处理。依据 `EventBus.gd:56–96`、`Item.gd:4669–4721`、`Game.gd:3084–3127`；本次是源码核对，非新增 GUI 实测。

### 函数接口与伪代码

以下为本次计划新增或修改的具体函数；未列出的现有接口保持不变。

| 函数接口 | 实现伪代码 |
| --- | --- |
| `godot_round(value: float) -> int`（新增） | 非负用 floor(value+0.5)，负数用 ceil(value-0.5)；替换伤害和治疗流程中的 Python round。暴击整数赋值使用 int 截断，不调用此函数。 |
| `BattleItem.__init__(现有参数不变)` | 保留已有初始化；补倍率、暴击层数及 damage_range_acc=0；每个实例独立存储。 |
| `BattleState.canBeEmpowered(event: AttackEvent) -> bool`（新增） | 返回来源物品存在且符合原版“武器并可造成伤害”的条件；不能只看攻击类型，不能给无物品来源加 Empower。 |
| `make_attack_event(*, attacker, defender, source_item, attack_types, min_damage, max_damage, accuracy=100.0, flag_overrides=None, trigger_log_handle=None) -> AttackEvent`（新增） | 按原版来源构建路径选择默认 flags；覆盖显式 flags；返回现有 AttackEvent。普通物品的多类型优先级按 setItem；雷神之锤式 init 路径允许显式保留全部 flags。 |
| `AttackEffect.apply(context: BattleContext, attack_type: str) -> bool` | 保留伤害修饰和命中修饰；调用 make_attack_event；交给 resolve_attack；返回命中结果。不在此重复加 Empower。 |
| `BattleState.build_attack_reaction_context(item: BattleItem \| None, attack_phase: str, attack_event: AttackEvent) -> AttackReactionContext` | 校验阶段；直接以事件 attacker/defender 建立来源上下文，允许 item=None；监听物品仍通过现有 for_item 转成自身视角。同步上下文 item 的可空标注。 |
| `BattleState.resolve_attack(event: AttackEvent) -> AttackEvent` | 校验角色和重复结算；已死亡目标返回不命中、零伤害结果；按上图执行。不可闪避时 hit=True；物品层数须 item非空且>0，角色层数须>0；概率暴击成功仍消耗已有层数；先概率抗暴，失败再消耗抵抗层。无来源不访问物品；只对攻击应用固定减伤。事后回调完成后若受击者health<=0，设置is_dead并调用check_battle_end；继续荆棘/吸血及内部收尾，正常返回事件，不抛结束信号。 |
| `BattleState.commit_health_reduction(player: PlayerState, blocked_damage: int, health_damage: int) -> None` | 校验非负整数和护盾；只扣护盾与生命，不裁剪过量伤害，不设置死亡、不结束战斗、不返回旧 tuple。 |
| `BattleState.apply_spikes(event: AttackEvent) -> None` | 未命中、pending_damage<=0、can_be_spiked为假或defender荆棘层数<=0则返回；含ranged取defender.ranged_spikes_limit，否则取melee_spikes_limit；含effect再取max(所选上限,effect_spikes_limit)。damage=min(荆棘层数,godot_round(pending_damage×上限))；damage>0时交换攻守方，创建无物品spikes事件，允许护盾/暴击，禁止闪避/再次反伤/吸血/物品触发，关联原事件日志并调用resolve_attack。 |
| `BattleState.apply_vampirism(event: AttackEvent) -> None` | 未命中、pending_damage<=0、can_be_vampiric为假或attacker吸血层数<=0则返回；含ranged取attacker.ranged_vampirism_limit，否则取melee_vampirism_limit。amount=min(吸血层数,godot_round(pending_damage×上限))；amount>0则heal(attacker,amount,trigger_log_handle=event.log_handle)，由heal统一处理效率、日志及反治疗。不得使用仅扣生命的health_damage或扣到零为止的实际生命损失。 |
| `BattleState._apply_poison_tick(target: PlayerState) -> int` | 零层返回0；构造无物品 poison 事件，攻击方为对手；调用统一结算；返回事件 block_damage+health_damage；删除旧 log_handle 参数和 tuple 解包。 |
| `BattleState.inflict_fatigue(target: PlayerState, *, nightfall: bool) -> int` | 保留疲劳递增规则；构造无物品 fatigue 事件进入统一结算；resolve 在暴击/抗性之前加受击者 bonus_fatigue_damage；返回原接口定义的基础疲劳值，额外伤害不写回递增状态。 |
| `BattleState.heal(target: PlayerState, amount: float \| int, *, source: object="Healing", trigger_log_handle: LogHandle \| None=None) -> int` | 校验数值；amount=godot_round(amount×max(0,efficiency))；以source记录治疗量和实际恢复量，并用HealingContext发送治疗/过量治疗通知；即使满血也继续反治疗逻辑。按 ceil(amount×unhealing_amount×(1+unhealing类型因子)) 向对手发送反治疗事件，关联治疗日志且不重复乘类型倍率；返回实际恢复量。 |
| `HealEffect.apply(context: BattleContext) -> bool` | 调用 heal 并使用其统一治疗日志，移除重复日志；返回实际恢复量>0。 |
| `BattleState._apply_regeneration_tick(target: PlayerState) -> int` | 调用 heal(target,再生层数)；沿用调度；使用统一治疗记录，不重复记账。 |
| `OnAttackedTrigger.update(context: BattleContext) -> bool` | 保留阶段、命中、类型和概率条件；补 can_activate_item 资格判断；不在 emit_signal 层全局屏蔽通知。 |
| `BattleState.check_battle_end() -> None` | winner已设置则返回；尚无死亡标志则返回；在首次死亡通知处按上述PLAYER/OPPONENT规则锁定winner。不抛异常、不等待收尾、不按后来生命值重算。 |
| `BattleState.stop_if_battle_ended() -> None` | 仅检查winner是否非None；若是，抛_BattleFinishedSignal；否则返回。不检查生命、不重新判死亡、不调用check_battle_end。 |
| `BattleState.step()`（返回现有winner类型） | try内先stop检查，再恢复耐力；依次activate_item，每次返回后stop检查；随后推进帧/时间并调用_apply_system_triggers；捕获结束信号记录快照返回；正常结束同样记录快照。 |
| `BattleState._apply_system_triggers() -> None` | 保留到期判断、时间更新与现有顺序；每次调用单次再生/毒/疲劳函数后立即stop检查。不得只在整组系统结算结束后检查。 |
| `BattleState.emit_signal(emitter, signalName, event_context=None) -> None` | 保留既有派发方式；每个监听器调用前若winner非None则停止派发；已进入的监听器正常返回。保留应写入的战斗日志，不因终局全局禁用record_log。 |
| `BattleItem.emit_activation(context: BattleContext) -> None` | 保留上下文校验；若winner非None则返回；否则记录激活并派发，匹配原版activate的日志/统计门控。不能用此门控跳过run_effect中的其他直接收尾。 |

平衡随机继续使用现有状态对象，不将普通 random 当作等价实现：

| 函数接口 | 实现伪代码 |
| --- | --- |
| `BalancedRngState.reset() -> None`（新增） | expected_wins=0；wins=0；last_result=False；战斗准备使用原版 reset 后状态，不无条件加入构造偏置。 |
| `BalancedRngState.roll_percent(percent: float, rng) -> bool`（新增） | p=percent/100；边界0/1直接返回且不消耗随机；按 expected_wins-wins 与±0.3阈值调整概率，再按上一结果及0.4/0.6阈值修正；expected_wins+=p；抽样并更新 wins/last_result，逐句对应 BalancedRandom.roll。 |
| `BattleItem.roll_damage(min_damage: int, max_damage: int, rng) -> int`（新增） | 取整数随机值并保存其与区间中点的差；按 damage_range_acc 的整数部分补偿结果且不越界；最后累计原始差值，逐句对应 BalancedRange.randIntRange。 |
| `BattleState.prepareItems() -> None` | 保留既有物品准备；在战斗初始化阶段按源码重置三套角色 RNG 和物品区间累计值，禁止在每次攻击时重置。 |

命中、暴击、抗暴采用受击者对应 RNG；物品区间使用物品状态，无物品区间保持普通整数随机。验证的是原版算法和随机消耗条件，不承诺 Python 与 Godot 相同 seed 产生同一序列。

当前无段位/大厅模式输入，准备时采用reset后的零偏置；原版低于大师或大厅模式会给双方命中/暴击RNG额外±0.2偏置（Character.gd:299–310），不在本次引入这些局外模式配置。现有武器的可强化资格使用AttackEffect的基础min_damage，而非增减伤后的事件数值，避免降至零伤害后错误失去Empower。尚未实现的Lifesteal标签武器需在导入时补对应资格，不以当前事件伤害猜测标签。

## 3. Tasks（任务拆解）

1. **T1 基础修复**：补函数/属性、可空上下文、取整辅助、毒伤调用契约；先让普通攻击和无来源事件运行。
2. **T2 结算规则**（依赖 T1）：落实 flags、来源数值边界、暴击；将_apply_melee_hit_statuses拆为apply_spikes和apply_vampirism并替换旧调用，保持荆棘先于吸血且符合原版调用路径；死亡时锁定胜负，仅在上述调度边界插入stop检查；补逐监听器及激活日志终局门控，保留已有正确修复。
3. **T3 系统伤害与治疗**（依赖 T2）：毒/疲劳接入统一流程；接入额外疲劳、反治疗及统一治疗日志。
4. **T4 随机一致性**（依赖 T1）：移植平衡概率与区间算法，核对初始化、归属及随机消耗次数。
5. **T5 回归与证据**（依赖 T2–T4）：测试放 tests；必要的对照数据放 data；更新既有测试中已废弃的字段和职责断言，记录实际结果。

## 4. Acceptance Criteria / Tests（验收标准）

- 普通攻击、无来源且可暴击伤害、首次毒 tick、疲劳 tick 均无异常；缺失接口和属性问题消失。
- 0%暴击且零层不暴击；100%概率暴击仍消耗已有物品/角色层数；抗暴概率优先于抵抗层数；荆棘可消耗角色暴击层。
- 普通 Effect 不反伤/吸血；显式全 flags 的纯 Effect 按近战反伤上限；远程及混合类型遵守原版优先级；禁用物品触发时不触发对应物品响应。
- 分别验证apply_spikes和apply_vampirism的开关、角色归属和总伤害口径；全额护盾吸收仍按总伤害计算；荆棘递归完整返回后才吸血；直接takeDamage路径不因允许吸血的flags而误调用普通吸血。旧合并函数及其调用全部移除。
- 抗性单位、仅攻击固定减伤、无敌、2.5取整、非整数暴击倍率、负倍率、分数吸血上限和负治疗效率覆盖边界。
- 毒/疲劳接受共同减伤规则；额外疲劳不污染下一次基础疲劳；满血治疗仍可反治疗，且类型倍率只应用一次。
- 回调可观察到正确的死亡时序；首次死亡立即锁定胜负，后来反伤/吸血不改结果；死亡目标不再承伤，双方首次通知时生命都不大于零按原版PLAYER胜处理。
- 致死resolve_attack正常返回；其调用方直接收尾仍执行，包括已有对应逻辑的专用治疗、状态清除和消耗；当前监听器能返回，但之后的监听器不再派发。终局后保留应有伤害/治疗日志，不新增普通激活日志。
- step入口能拒绝已结束战斗；致死物品完整返回后下一物品不执行；致死系统tick完整返回后下一tick不执行，分别覆盖双方疲劳之间、再生引出反治疗的边界。结束信号由step捕获，记录最后快照；普通程序异常继续暴露。实现不含嵌套深度计数器，底层结算不调用stop。
- 日志关联正确、不重复治疗记录；最终UI生命钳制属于原版deferred清理，不写回伤害量，也不用于重新裁定胜负。
- 平衡随机以固定输入随机流对照原版逐步状态，包括0/100%边界和区间累计补偿；现有相关测试和新增行为测试通过。
- 现有 GUI 实测结论作为回归依据；遇到静态源码无法裁决的死亡顺序或数值转换，再做最小 Godot 实验，不宣称未执行的验证已通过。

## 5. 实施与验证记录（2026-10-08）

- 已完成T1–T5，修改battle_module_v1.py、item_effects_v1.py、item_factory_registry_v1.py、item_triggers_v1.py；未修改原版Godot源码或custom opponent。
- 新增tests/test_damage_pipeline_spec.py的27项行为测试：覆盖暴击/抗暴、flags、无来源、两类反应、取整、系统伤害、治疗/反治疗、死亡时序、调度边界和原版平衡随机固定输入轨迹。
- 更新旧测试的过量伤害、随机消耗、事件减伤、上下文视角与终局断言；删除3项针对已移除扣血日志补全接口的测试，以统一伤害日志及父事件关联测试覆盖现行行为。致死测试仍验证结果和收尾，不通过跳过测试规避差异。
- 使用指定Python 3.11解释器运行unittest discover：524项，0 failures，0 errors。结果保存在data/damage_fix_test_results.txt。
- 本次未重新运行Godot GUI。既有两项GUI实测作为机制依据；本次验证不等同于完整游戏逐帧轨迹一致，也不包含最终UI生命钳制或尚未导入物品的全部专属逻辑。
