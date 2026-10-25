# 362 写量策略裁定（SOURCE，不授执行）

root已明确授权 `bounded-writers-and-monitored-process/1`。用户要求预算检查和不重复Game，并未要求内核级数学硬配额。自有observer/collector writer严格cap；host PIPE控制stdout/stderr；后台user/cache写入显式隔离的XDG/TMPDIR，以50ms监控、未知root/异常cap中止、4GiB free floor和300s wall保护。启动重新核4GiB reserve+保守1.5GiB attempt。

必须记录 `POLLING_NOT_KERNEL_AGGREGATE_QUOTA`：后台总写量不是严格原子上界，轮询间可能超量；不得冒称kernel quota或凭当前5.7GiB永久PASS。合法cache root内新文件计入预算，不以未知文件名当attack；root越界、symlink、cap或I/O故障保partial、kill本次独立process group、停止写入，不清原件/不重试。

这取代本阶段尚未冻结实施稿中“必须先证明严格后台全局硬配额”的自设要求，不改已冻结19813B设计或359/360/361。不存在caller risk_accept/ready开关；仍须独立SOURCE验收和root真实精确config后才能执行。当前只源码，不修改HOME/平台安全配置、不运行。
