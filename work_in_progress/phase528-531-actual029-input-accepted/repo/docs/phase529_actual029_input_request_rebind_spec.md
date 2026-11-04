# Phase529 repaired actual029 INPUT request metadata rebind

## 1. Requirements
Prepare only a new Root request for the unchanged actual029 INPUT carriers after528 Source repair. Preserve525 request and527 failed output. No raw INPUT/Expected reads or hashes, imports/schema/helper/build/model/Oracle calls, pool writes or Source changes.526 remains PAUSED.

## 2. Design
Follow frozen528 `root-request-rebinding-contract.json`: copy every525 request value exactly except `source_context`, which becomes actual528 context descriptor. Strict models_allowed/expected_allowed INT0 and all12 input_descriptors remain exactly equal, including path/size/SHA; canonical digest must equal the contract. Candidate request is not projection acceptance or build authorization.

## 3. Realize
Read only525 request and528 metadata/context. Verify old request descriptor equals rebinding contract; hash actual528 context and compare it with the contract. Build new seven-key request by copying the old JSON object and changing one field. Assert identical other six fields and canonical12descriptors digest. Save request, comparison receipt, complete command proposal and owner in `data/phase529-actual029-repaired-input-request`.

Command uses new `tests/phase528_input_bridge.py`, explicit new request size/SHA and new output `data/phase511-case029-actual-input-repaired-001`. Never reuse the existing failed output. Proposed argv is not invoked; default Source request remainsNone. No production Source edited or compiled.

## 4. Acceptance criteria
Exactly one field changed, seven request keys, twelve descriptors canonical and decoded-value equality with525, strictINT0s unchanged, context/bridge identities equal528 frozen metadata, new output absent. Descriptor-own artifacts, hand to Root, then idle. Independent528 acceptance and Root explicit actualbuild release remain prerequisites; no actual72/INPUT/B1/model/strict8 success asserted. Trusted<=30/userpause checkpoint/stop.
