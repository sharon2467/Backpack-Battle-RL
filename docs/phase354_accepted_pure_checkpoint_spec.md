# 354 固定单King pure独立验收后的累计检查点

## 1. Requirements

将351固定四轨迹首次独立通过的SOURCE、实际检查、负控及失败诊断纳入同一GitHub恢复分支。正式75与King未准入保持；完整引擎/RL未完成。保留352远端恢复回执及所有原件，不新跑模型或原版。

## 2. Design

复用已独立审核、未修改的352累计builder；当前十基础归档和链接不变，新增一个替代当前progress的累计ZIP及完整索引。旧progress分片与manifest/index/validation历史保留，无顺序脚本链。351实施、独立测试均须完成封口才取cut。

## 3. Realize

更新六当前说明与机器状态，记录351完整pure已接受以及未命中的自然分支。精确绑定当前352 manifest SHA、builder SHA，按phase354唯一新名执行。新ZIP逐成员CRC/SHA、前后源稳定性和凭据模式检查；独立材料检查后push，不改master/不强推/不PR。远端读取完整tree与清单。实际恢复只从独立GitHub clone获得输入，校验全逻辑档案并物化active；只做入口help与owner读回，不重跑科学。释放空间仅限已有可靠远端验证且再次逐叶hash确认的恢复测试重复payload，保留原始输出与receipt。

材料审发现旧352 material owner引用绝对保存ZIP；原字节已在public历史单分片。保持当前cut/archive/index不变，另在GitHub恢复入口显式增加owner-relocations.json与stdlib materialize_owner_artifacts.py。映射必须由保留历史descriptor的single-part whole-archive size/SHA证明，目标限定新恢复目录workspace/checkpoints，不可覆盖/穿越链接；复制前后与读回校验并另出receipt。主restore不改。新helper必须独立SOURCE审和有效拒绝控件后，才从远端执行；owner读回仅按该白名单重定位绝对路径，不访问旧云路径。该恢复入口补充在公开仓库直接提供，区别于原已封599成员cut。

## 4. Acceptance Criteria / Tests

351实际review、owner、source freeze、12负控与四raw均完整；King仍未生产准入，353为SOURCE计划，新原版采集0。累计检查点不依赖旧云文件。远端实际commit/树、全部逻辑SHA、active双读回及help/新owner检查通过后才声明恢复成功，明确same-host而非freshOS/full物理历史。遇保存或验收错误保留首错并只修相应工具，不能为其重跑成功战斗。
