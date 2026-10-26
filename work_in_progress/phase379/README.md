# Complete execute-payload preflight and known-partial recovery design

The proposed repair uses one descriptor-resolved payload graph in plan and execute, including the correctly reused collector. Every source payload is read/hash/type/link checked before lease/reset. The direct installer independently validates all patch/artifact sources and current targets before creating any backup; existing strict-target/atomic-image/write ordering stays intact.

The partial failed state has exactly two known old-target paths absent, with reset deletion and real old-payload proof. A new recovery schema must preserve the missing journal and validate actual failed/target/reset/raw-prefix evidence; it must not weaken arbitrary path checks or reuse a completed-install map.

Copy design/repo additively after main restoration. This is a four-section design/SOURCE audit, not implementation or independent runtime acceptance. Source380 and concrete helper controls remain separate.
