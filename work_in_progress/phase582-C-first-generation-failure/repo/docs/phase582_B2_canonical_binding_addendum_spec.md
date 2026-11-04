# C B2 canonical identity supplement

## 1. Requirements
Preserve the old B2 input-bundle canonical SHA check. A physical pretty-JSON descriptor SHA is a different identity and cannot replace it.

## 2. Design
Only the B2 root_binding dict gains the fifth key input_bundle_canonical_sha256. The helper still takes four arguments;17-key model request and20-key comparison binding stay exact. Actual raw UI,Source,proof and ownership checks stay strict.

## 3. Realize
New C Source reads the explicit required canonical hash and compares canonical(bundle) to it, in addition to existing physical/raw provenance. No default, optional key or I/O-verified BOOL. Keep frozen582 design unchanged and record this added interface in actual patch/census and contracts.

## 4. Acceptance
Independent583 includes a physical-pretty SHA versus canonical SHA distinction and mismatch rejection as needed. Source generation/compile-only release is unchanged; no helper/model/Expected/Native execution is added. Current Source-generated input/output remains unbound until actual new observations and releases.
