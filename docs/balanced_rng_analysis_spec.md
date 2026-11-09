# 原版 Balanced RNG 统计评估 SPEC

## 1. Requirements（需求）

依据当前权威解包 `Backpack Battles/Utility/BalancedRandom.gd`、`BalancedRange.gd`、`Util.gd`，评估区间抽样和成功/失败检定能否回归标称期望，并展示相对独立随机抽样的分布变化。区分单次边际分布、序列相关性、固定次数累计结果分布，以及每场重置的短程行为。仅做分析，不修改游戏或现有模拟器。

用户故事：研究战斗模拟器时，需要知道这套随机算法是否保留伤害均值/成功率、是否仍能使用均匀分布/二项分布，以及在少量攻击与动态概率条件下的限制。

验收：提供源码证据、可复现脚本、原始汇总数据、静态科研图和中文结论；明确区分解析结论、数值证据与未进行的原引擎验证。

## 2. Design（设计）

采用一个独立 Python 分析脚本与一个验证脚本，不引入框架。使用用户指定 Python 3.11.9 和已安装 NumPy/SciPy/Matplotlib。文档放 `docs`，脚本/验证放 `tests`，实验数据和图片放 `data/balanced_rng_analysis`。

权威调用路径：`BalancedRng.rollPercent -> roll -> Util.flip`；区间采用 `BalancedRange.randIntRange`。`roll1/roll2` 不属于当前战斗调用路径。战斗前 `Character.prepare` / `Item.prepare` 重置状态；角色部分场景在 reset 后设 ±0.2 bias。

模型假设：底层独立均匀随机数；整数区间含两端；`Util.flip` 用 `u <= chance`，超过 1 必成功。Python 不复刻 Godot PRNG 的位序列。解析极限采用实数运算，有限精度/PRNG 端点影响说明边界。

### 数据与接口 / 每个函数的伪代码

1. `range_step(acc: ndarray, raw: ndarray, low: int, high: int) -> tuple[ndarray, ndarray]`
   - 状态为累计偏差 acc；输出为修正后的抽样和新状态。
   - 伪代码：先保存 `dif=raw-(low+high)/2`；若 acc>=1，减 `min(raw-low, int(acc))`；若 acc<=-1，加 `min(high-raw,int(abs(acc)))`；更新 acc 为旧 acc 减/加修正再加 dif。必须使用修正前 dif。
2. `roll_step(expected: ndarray, wins: ndarray, last: ndarray, target: ndarray|float, uniform: ndarray) -> tuple[ndarray, ndarray, ndarray, ndarray]`
   - 接口显式保存 expectedWins/wins/lastResult，避免改写源码浮点加法顺序。
   - 伪代码：边界 target<=0 / >=1 直接返回，不改状态；其余取 dif=expected-wins，按 ±0.3、balancedness=3 修正 chance；expected+=target；依上次结果和 0.4/0.6 阈值乘 0.5/2；用 uniform<=chance 检定并更新 last/wins。
3. `roll_probability(expected: float, wins: int, last: bool, target: float) -> float`
   - 伪代码：照 roll 的概率计算部分运算；将结果截在 [0,1]，返回转移概率；用于独立的有限步状态枚举验证。
4. `exact_roll_counts(target: float, steps: int, bias: float=0) -> ndarray`
   - 伪代码：分布初始为 `(wins=0,last=false):1`；逐步按 roll_probability 分裂成功/失败概率，合并相同状态；expected 每步以源码顺序加 target；最后按 wins 汇总。边界概率单独处理。
5. `range_stationary(width: int) -> dict`
   - 伪代码：从 acc=0 枚举可达状态与每个原始整数抽样的转移/输出；构造有限转移矩阵；解 πP=π、sumπ=1；计算输出 PMF、均值、方差、相邻协方差、状态支持与平衡方程残差。
6. `summarize(samples: ndarray) -> dict`
   - 伪代码：返回均值、总体标准差、均值标准误和 1%/50%/99% 分位数。
7. `run_experiments(output: Path) -> dict`
   - 伪代码：固定种子；整数宽度 0..10 做精确稳态，代表宽度做多条长序列复核；多个固定 p 长序列测均值/偏差/方差/一阶相关；reset 起步做有限次数成功数精确分布；±0.2 bias 对照；交替概率测全局及按 target 分组的成功率；保存 JSON 与 NPZ。
   - 长序列批量化，多条独立路径，不以同一路径相关样本的朴素标准误声称显著性。
8. `plot_results(results: dict, output: Path) -> None`
   - 伪代码：绘制区间单次 PMF、固定次数均值分布、成功次数 PMF、reset 累计均值、动态概率分组与 IID 对照；使用清晰图例保存 PNG/PDF。
9. `main() -> None`
   - 伪代码：创建输出目录，执行实验，序列化结果，生成图，打印简短关键数字。

验证文件 `tests/test_balanced_rng_analysis.py` 的每个函数：

10. `test_range_accounting_and_bounds() -> None`：遍历多种整数范围和输入轨迹，断言区间合法及 acc 等于输出累计偏差。
11. `test_range_stationary_solution() -> None`：断言稳态概率归一、非负、平衡残差小、均值等于区间中点；包括退化区间。
12. `test_roll_source_edges() -> None`：核验边界检定不更新状态、概率溢出必成功、±0.3 和 0.4/0.6 严格阈值、lastResult 修正。
13. `test_roll_exact_counts() -> None`：断言精确分布归一；p=0/1、首步 p=.25/.5/.75 结果符合源码；枚举结果与另一路径的概率计算一致。

独立符号交叉验证：`tests/balanced_rng_exact_check.wls` 不定义函数，直接用精确有理数构造 [0,4] 的转移/输出矩阵，解稳态质量、单次 PMF、方差与相邻相关系数，以本机已验证 Mathematica kernel 核对 Python 浮点解。

执行调整：Mathematica 两种命令行方式均未返回验证标记，不能计为通过。使用指定 Python 中已安装的 SymPy 1.13.1，在 `test_range_stationary_solution` 内用独立写出的有理数矩阵完成符号交叉验证；保留 `.wls` 供以后复核。

关键流程：源码阅读 → 本 SPEC → 解析恒等式/漂移 → 源码逐句转写 → 有限状态/有限步精确计算 → 多路径随机复核 → 图表与报告。

## 3. Tasks（任务拆解）

1. [x] 阅读知识库，定位原版、flip、调用处和 reset/bias。
2. [x] 写 SPEC，确认解释器及依赖。
3. [x] 实现最小分析脚本与源码语义验证。依赖 1–2。
4. [x] 推导区间守恒关系和检定偏差漂移。依赖 1。
5. [x] 运行精确计算与多路径实验，检验动态概率、重置和 bias。依赖 3–4。
6. [x] 渲染并检查图，写中文分析报告和结论。依赖 5。

结果：`docs/balanced_rng_analysis.md`；数据和 PNG/PDF 为 `data/balanced_rng_analysis/`；4 项验证全部通过，SymPy 有理数结果与 NumPy 稳态一致。Mathematica 未返回成功标记，未计为通过。未进行 Godot PRNG 位序列或运行轨迹验证。

## 4. Acceptance Criteria / Tests（验收标准）

- 所有分析实现通过上述语义验证，未修改已有战斗实现或用户工作区改动。
- 固定区间均值有解析守恒与有界状态解释；精确稳态输出 PMF 与随机复核相符。
- 固定概率的长期成功率有恢复漂移解释；有限步结果用精确分布给出，不把经验接近当成有限步严格无偏。
- 明确二值单次分布与成功总次数分布的区别；展示区间边际形状及累计分布、相关性。
- 报告初始化、重复 reset、共享状态/变化概率的适用边界，记录种子、样本量和来源哈希。
- 图片经过视觉检查，结果可由指定 Python 一条命令复现。

## 5. 证明补充（2026-10-10）

需求：补全原报告从“区间外向内漂移”到“指数矩一致有界、几乎必然及均方收敛”的推理，不用数值实验替代理论证明。

设计：仅补充数学文档，不增加函数或改动实现。以完整历史为条件定义实际成功概率 q_n；从源码取得两侧统一概率界，显式选取 δ、θ 和收缩系数 r；用指数函数的二阶余项建立递推；用 Markov 不等式与尾部事件的并集界证明几乎必然收敛，用指数矩控制二阶矩证明均方收敛。

任务：
1. [x] 重新核对 roll 的概率乘除、lastResult 修正和更新顺序。
2. [x] 写出明确的正漂移下界 δ，以及指数矩递推中的常数。
3. [x] 在报告第 7 节补全证明，并在聊天中给出自足推导。

验收：证明覆盖任意固定 0<p<1、有限初始 bias；明确理想独立均匀随机输入与实数运算假设；对几乎必然收敛的每个 ε 事件和均方误差给出实际界，而不是只引用 Lyapunov 术语。纯文档补充，无新增代码测试。
