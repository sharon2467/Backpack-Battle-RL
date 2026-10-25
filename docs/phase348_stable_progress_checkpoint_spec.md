# 348 stable75自包含GitHub恢复更新

## 1. Requirements

保存348真实晋级与346独立包验收结果，不把新成果只留旧云。复用已验证GitHub原版/243/343/347固定材料，所有原件及旧commit保留。当前75与旧暂停68清晰区分；King349工作另候选，未完成不称准入。不得上传秘密/无关私人材料，不购买LFS、不动master/强推/PR。

## 2. Design

现有stdlib restore.py完全不改：新增一个小ZIP progress348归档、一个分片描述，逻辑清单按同一目标路径覆盖当前源/六文档与新证据，MANIFEST指向完整11归档。这是一次完整当前索引，不引入需要顺次执行的增量链；旧10归档仍字节相同。新用户只需clone与一次restore命令。历史档在GitHub旧commit和原归档保留。原代码脱敏政策沿原manifest。

## 3. Realize

- builder从真实canonical15、六living入口、348 docs/tests/tools/data、344真实rootprep/promotion/portable和346实际output选取原字节，加新的portable ZIP；排除pycache/symlink，所有路径安全、模式归一644/755，固定stablecut不跟随运行结果变化。每payload做密钥模式扫描，发现具体命中则阻断不打印秘密。
- 建ZIP后逐成员CRC/SHA；progress348对应logical行active=true，旧同路径行被当前行替换，其余行/10归档字节不变；覆盖计数从新索引重算，source/status明确75已提升且engine/RL未完成。旧独立验收记录保留为历史68验证。
- 新check_restored75.py只读恢复收据/当前state/15freeze及晋级、346实际owner证据；可选仅--help入口，不初始化/跑战斗或原版。不能把已有科学成功轨迹再跑一遍当新证据。
- 从远端fetch新commit到独立clone，远端parts/tree实际核；新的独立恢复目录用原restore.py真实active恢复与全逻辑hash遍历，help-only检查；不借旧云文件生成恢复数据。空间不足仅释放先前经GitHub恢复校验的重复物理文件，先保留其收据/原始验收输出，原工作区/checkpoints/错误现场绝不删。

## 4. Acceptance Criteria / Tests

所有新增payload扫描、ZIP CRC/SHA、新manifest/index一致；独立SOURCE/材料审查通过，最终push成功后readback branch/SHA/filetree。一次远端-only active实际恢复及全部逻辑哈希通过，当前15等324、正式75/King未准入、346owner28叶完整，help exit0且模型/原版0。明确same-host active而非freshOS/full物理恢复；旧云必要工程文件清单为空，OS依赖/被排除凭据沿旧说明。原版采集/成功模型不重跑；额度新暂停优先。
