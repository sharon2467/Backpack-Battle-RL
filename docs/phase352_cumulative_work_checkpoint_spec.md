# 352 当前工程累计工作检查点（保存工具SOURCE）

## 1. Requirements

将已完成的King SOURCE/组件/未来预封计划按实际状态保存到同一公开新分支，不晋级King、不改master、不购买。旧348稳定检查点及其原件保留，新保存仍不依赖旧云文件，全部失败/半成品按实际cut保留。

## 2. Design

复用原stdlib restore.py与十个固定大归档。把旧小progress348 payload与本轮phase>=348当前源/证据合为一个累计小ZIP，替换完整索引中的progress来源标签；当前manifest始终十基础+一个累计progress，不产生顺序补丁执行链。旧小分片留在Git/history并记录identity，原工程ZIP/原版大归档不动。SOURCE与业务状态以当前六说明/机器state为准。

## 3. Realize

builder先核当前pub MANIFEST精确identity和旧progress archive，读取旧小ZIP全部payload，覆盖本轮canonical15/六说明及repo data/docs/tests/tools中phase>=348真实文件（拒symlink/pycache），保留旧小payload中未被修改的叶。执行前应让所有活动写入方停在SOURCE或结果封口边界；每叶前后SHA确保stablecut。只合并文件，不运行候选/模型/原版。新ZIP全成员CRC/SHA、凭据模式扫描；48MiB分片；保存旧manifest/index/validation到history。完整logical index覆盖当前目的地并重绑累计archive，其它十archive/links守恒，计数重算。输出收据在归档后，不自证远端或恢复成功。

远端push后从只用GitHub数据的独立clone读取新manifest/parts，实际恢复到独立新目录；旧已验证恢复测试重复叶只可精确hash确认后释放，保留收据与raw输出，原live/checkpoints/失败不删。restore全逻辑SHA及active双读回后用无battle入口checker，并读取新增King各owner；不因保存重跑科学。

## 4. Acceptance Criteria / Tests

SOURCE审、实际归档/完整index材料审分离；当前总archive数仍11，旧10descriptor字节不变，累计progress无所需旧云文件。所有当前代码、失败、实际验收与未执行计划明确；source/actual/HIT不混淆。新模型或native次数0，Git远端commit/tree实读通过，最小same-host active恢复通过（非freshOS/full历史物理）。保存遇错保留现场，不能把本地建包当远端已备份。额度暂停优先。
