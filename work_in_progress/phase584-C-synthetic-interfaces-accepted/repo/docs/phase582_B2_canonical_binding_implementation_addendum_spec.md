# Phase582 B2 canonical binding implementation addendum

## 1. Requirements
Root explicitly approves only one missing B2 binding field: input_bundle_canonical_sha256. Keep frozen582 design immutable and preserve the original canonical bundle check. No actual C/helper/model/Native/Expected execution is authorized.

## 2. Design
B2 root_binding has5 keys instead of4: schema,input_bundle,input_proof,source_basis,input_bundle_canonical_sha256. Function remains4args. Model request remains17 keys and comparison binding20. A physical pretty-JSON descriptor SHA and canonical decoded bundle SHA are distinct authorities.

## 3. Realize
The new isolated B2 helper compares canonical(bundle) with the explicit fifth key while independently checking raw UI SHA/size and Root descriptor/source associations. No fallback to a physical descriptor or old029 constant. Root context descriptor is copied exactly from its actual binding.json, without normalizing its path representation. Record this one shape delta in Source API/contracts/inverse.

## 4. Acceptance
Independent583 must include a physical prettyJSON SHA != canonical SHA vector and verify correct canonical acceptance/wrong canonical rejection. This is an interface control, not actual Native/window acceptance. All other strict checks and no-execution boundaries remain.
