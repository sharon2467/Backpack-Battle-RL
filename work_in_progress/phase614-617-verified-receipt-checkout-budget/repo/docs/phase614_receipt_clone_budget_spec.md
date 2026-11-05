# Phase614 — reclaim verified receipt-clone checkout duplicates

## 1. Requirements
Prepare headroom before another long operation without touching live Source,the fixed pool,original resources,checkpoint ZIPs orunique evidence. Only narrow the sparse checkout of the existing independent Git receipt clone. Preserve its Git objects andremote branch/history.

## 2. Design
Current independent clone HEAD must equal verified2059ab3 andbe clean withnoalternates. For every older archive proposed for removal,verify its FILES payloads byactualSHA256 and verify Git can return the identical bytes fromcurrentHEAD. Keep latest repair Source/acceptance,actual failure/recovery archives,runtime package andrecovery entry files. No working file without a manifest orwithuntracked content is eligible.

## 3. Realize
Record exact current patterns,HEAD,oldarchive names/file hashes andrestorable Git blobs in a new proof. An independent judge reviews the precise proposed sparse change. Only then use Git's existing sparse-checkout interface to omit those old paths;do not recursive-delete orprune object storage. Preserve originals/publication staging andall Git refs. Save before/after space andcheck clean HEAD,retained manifests andoldblob recoverability. No engine,test,oracle,fullcheckpoint restore ornew environment.

## 4. Acceptance
All omitted payloads must be exact duplicates recoverable byte-for-byte fromretained Git objects;no unknown/untracked file is removed. Active roles must not use those oldcheckout paths. Currentruntime/currentfailure/currentrecovery/latestSource stay materialized. Sparse omissions are reversible withGit;they are not deletion ofremote backups. Report actual spacegain andremeasure atfuturestartup;do not lower5905580032B gate.
