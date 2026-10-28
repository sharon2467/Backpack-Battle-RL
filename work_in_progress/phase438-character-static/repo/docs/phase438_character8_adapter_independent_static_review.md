# Phase438 Character8 adapter independent static review

## Reviewed owner and decision

Static-only review of `tests/phase438_character_initial_overlay.py`, 20871 bytes, SHA256 `bb69dd1674929c892e60788f9cc269faf80710747e7921719dcf0eed17f32d7b`, owner `data/phase438-character-overlay-source/source-owner.json`,1355 bytes,SHA256 `c838f626bacb889b5b32028010cc38593e9e57fd62d9fd94dc50c81c87b12909`. Current source hashes were independently read. Read spec/API/context and original437 relevant metadata/8 targets/2 prior derivations. No module import, compile, function control, actual overlay, Oracle or old control was run by this reviewer.

**REQUEST SMALL REVISION before functional release.** Character8 Source theorem remains accepted. Three implementation/protocol points below need correction; none requires wider Source traversal or native collection. The new8 value construction itself is correct: line269 emits exactly `{"type":"bool","value":false}` or `{"type":"null"}`, not numeric zero, string false, null-with-value or a native reference.

## Findings

### 1. Exact437 pure-helper domain is not enforced

`validate_audit`144-173 validates counts, uniqueness, eight target identities and that the other64 missing rows have field_id Timer.private_left. It does not compare their complete identities/order, the full required identity set, prior-derived value shapes, or original excluded payloads against the fixed437 baseline. A concrete unexecuted counterexample is to change one non-target missing Timer.private_left row's side_or_role to a previously absent string; all counts and checked predicates remain true. Reordering rows is also accepted. A prior SOURCE_DERIVED actual_value can be changed to `{"type":"bool","value":0}` and pass163 because only presence is tested. Non-target comparisons278-280 merely preserve the supplied mutated input.

`run` does pin the complete original437 byte hash before parsing, so these counterexamples do **not** bypass the actual I/O entry as written. Nevertheless `project` is deliberately exported for direct pure-helper counterexample testing and the advertised exact-input contract is weaker than claimed. Minimal fix: add a literal expected canonical SHA256 of the entire original437 JSON to validate_audit, after useful structural checks, using canonical JSON serialization with allow_nan=False. This requires no runtime file read and makes both helper and run accept only the exact original typed payload/order/keyset. An exact ordered-key digest plus unchanged baseline payload digests would also work but adds complexity. Preserve raw-byte pinning in run. Then count-preserving foreign keys, ordering, old derivations and excluded mutations all reject.

This fixed-input fingerprint is an artifact identity guard, not a proof boolean and not a replacement for typed cut/ledger checks. New8 output shapes still deserve direct postcondition assertions in the positive control.

### 2. Historical full-reference counts change meaning

line275 changes full_reference_counts from original437 `DIRECT1391/SOURCE_DERIVED6/MISSING82` to `1391/14/74`. The arithmetic is consistent with applying eight changes to the original full counts, and line274 does preserve the original in a new field. The issue is meaning: the existing field was the reference accounting for the preserved earlier full artifact; no updated full artifact is emitted here, and the task promises retention of that prior reference.

Minimal fix: leave `full_reference_counts` and associated full-reference metadata exactly inherited. The actual required-row output counts become1289/10/64. If desired, add a clearly named `phase438_projected_full_counts` for1391/14/74 with explicit derived accounting semantics; it is optional and should not imply the excluded116 were admitted. Preserve original counts separately only if useful. Update spec/API accordingly.

### 3. Readback evidence must describe actual operations precisely

line320-321 really calls read_pinned for every before descriptor; that helper independently reopens/reads/hashes and checks fd/path identity. This is not a missing recheck. However line327 writes after=deepcopy(before), rather than the collected results from those actual calls. Minimal fix: initialize `after=[]`, pass it into those read_pinned calls, require before/after agreement and emit it as the list of successfully reverified descriptors. If filesystem timestamps/inodes are emitted, collect their actual observed values separately instead of labelling expected pin descriptors as stat metadata.

The input checkpoint file is read in full at312 and again by readback: all306081 bytes including six JSONL lines are physically read and hashed. Only lines1/4 are JSON-decoded at315. Therefore `postcleanup_reads:0` is ambiguous/misleading if read as physical I/O. State `parsed_checkpoint_lines:[1,4]`, `postcleanup_records_parsed:0`, and `checkpoint_hash_scope:entire_file`; record physical byte reads and number of passes if claiming counts. No postcleanup record values are parsed or used in inference. Amend spec's unqualified prohibition/read claim to this exact distinction. EXPECTED file reads remain zero.

## Other bounded checks

The literal context pin closes the actual source manifest; no source_closed boolean can authorize run. Input hashes are checked before project. Native source files are not dynamically executed. Ledger counters require exact int zero, excluding bool, missing, positive and negative values; identity binding joins known owners/timers, both snapshots and birth/current facts. Positive-start histories cannot pass the current ledger validator. Output updates only the8 explicit target keys; compare loops preserve all other supplied rows and exclusions. The newly added exact437 identity guard should make that preservation refer to the actual baseline as promised.

Source-derived values are constructed directly and consistently in row.actual_value and proof.changes. Existing two derivations are native private-left binary64 -1; exact-input identity should protect their prior type/payload. The output source_context is pin-linked evidence, not an assertion that all future captures share this domain. Buff44/Timer64 remain unmodified. Top-level profile still names the fixed437 profile while schema/status/rule identify the overlay; this is acceptable as lineage if documented, and is not an additional blocker.

## Updated minimal function control plan — not executed

After receiving revised immutable source owner and explicit Root release, run one bounded stdlib process under timeout15s. Import only this reviewed adapter, never invoke its run/main for the function batch, and never import old tests/helpers. Parse lawful input records1/4 and input facts solely to construct the pure-helper fixture. The result is a candidate function result, not an actual saved overlay or acceptance. Keep first failure and do not retry without diagnosis.

1. Positive project: exactly8 target rows change; exact ordered1363 keys persist; required counts1289/10/64; excluded116 and all1355 non-target rows—including old2 derivations—are canonically identical; historical full-reference metadata unchanged. Assert all4 bool values have exact keys type/value and `value is False`; all4 nulls have only type:null.
2. Exact-audit negative group: one unique non-target Timer role substitution with counts unchanged; swapped order of two valid non-target rows; malformed old SOURCE_DERIVED actual_value; excluded payload change. Each must reject. Also exercise duplicate target key and wrong classification/count to retain existing structural guards.
3. Ledger negative group: starts False/0.0/"0"/missing/-1/1; wrong ready kind; mismatched owner/timer; one alias P/O; malformed birth mode bool; current-vs-cut mismatch. Each must reject; original P reuse is accepted through whole-life lineage rather than an invented fresh flag.
4. Cut negative group: changed phase/site/sequence/subject; missing required node or duplicate role/nativeID; source-resource/Character/Timer disagreement; wrong fixed frame or malformed typed environment. Each must reject without producing output files.
5. Small standalone I/O helper controls in a dedicated new data temp directory, only if Root includes them in release: valid read_pinned returns data and appends verified descriptor; digest drift and symlink/hardlink reject; save_new cannot overwrite. Do not call run merely to exercise its rehash loop. Actual one-time run/readback accounting is checked only when separately released.

The abstract Timer/Character Source-transition control plan remains separately pending and does not authorize this adapter process. Keep current437 counts/formal75/King state unchanged until separate actual-output acceptance.
