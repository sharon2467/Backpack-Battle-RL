# Phase418 — Initial-only AutoHide partial recipe implementation

## 1. Requirements

Implement the smallest standalone stdlib projection accepted by417 B01–B07. Root supplied the actual417 review before implementation. Only Timer.private_left for king_hide:P:12 and king_drag:P:12 at pre_prepare/pre_activate is eligible for a conditional SOURCE rule. The other84 targets are unconditionally MISSING; KingBuff/invu have no enable switch. Existing411 remains1391 DIRECT/SUPPORTED plus88 MISSING/UNPROVEN, recipe0. The1371 documentary subset is distinct from1391. No genuine bundle, fullschema validation, King admission or356/361 gate opening occurs.

Author work is SOURCE generation, physical pins, compile and AST only. No import or call of this module; no old audit/SUT/schema/Engine/Model/FrameDriver/native; no actual raw carrier or EXPECTED read. Existing403–417 and original source bytes remain unchanged. Root and independent419 must separately accept this implementation and authorize ONE future actual projection. Neither this SPEC nor the intermediate419 SOURCE review is that authority.

## 2. Design

### Finite SOURCE rule

AutoHide._ready calls Timer.new, immediately records birth before one_shot/connect/add_child/hide. Accepted version-attributed Timer semantics initialize private countdown to binary64-1, processingfalse and autostartfalse. Native READY does not start a non-autostart Timer. Within the exact selected owner/resource domain, all relevant start/stop routes are counted before the fixture-bound gate. Stable birth/current Timer and owner IDs plus zero monotone lifetime starts/stops can support both checkpoints. Public zero/stopped/configuration checks corroborate the domain; they never independently initialize private-1. Nonzero aggregate count cannot locate a call after the earlier checkpoint, so both phases for that role remain MISSING.

The finite N3 addition is five baseline leaves (4559B): SquishySprite, SocketsNode and Highlight/MiniActivate_consumed/ItemsCrafted animations. Squishy.init schedules both call_deferred and Util.callDelayed ready_deferred. Both return to reset and sprite-local motion/scale; ordinary Sprite physics is not Timer internal processing. Util.callDelayed creates a separate SceneTreeTimer; capture_delayed ignores ready_deferred. Item.liesInStorage only reads ownerType/dragged. SocketsNode._ready changes its own scale. Animations have value tracks for Icon modulation/self_modulation or item scale, no method tracks or selected Timer properties. The exact additional two-leaf GemSocket scene/script binding shows plain var item=null without setget: Item.initSockets assignment invokes no script setter. No optional Gem callback or recursive resource expansion is part of this proof.

The local source rule is recorded in source-edge-list.json, with exact source pins. The real Root native-attribution proposal and real419 intermediate conclusion are referenced as evidence, not final permission. The disclosed native limitation remains: version-matched source and the same pinned runtime with finite numeric conformance, without bit-exact custom build reproduction or direct private countdown measurement. Final419 must explicitly accept G01/G02 for this exact source rule; absent either accepted disposition, affected rows remain MISSING. No caller Boolean supplies authority.

### Inputs, boundaries and authority

The only data objects are the frozen411 index and three descriptors copied from the spent411 release metadata: king-slot-bindings.json, observer7-lineage.jsonl and king-ui-authority.jsonl. context.json fixes all four exact paths/size/SHA. Author never opens the three actual files. SOURCE/control descriptors are enumerated separately; no metadata-path traversal discovers further inputs.

Slot bindings are one bounded JSON document. Match the source-fixed39 slots, strict typed item/index/geometry, unique item IDs/encounter positions, side Character and inventory consistency. Select P:12/King81679. The lineage semantic prefix requires strict increasing INT shared sequence below138 (gaps allowed), exact selected fresh scene/descriptor and Item._ready enter/return. At first sequence>=138, only its sequence envelope identifies the cut; its payload and all following bytes remain opaque. EOF is an explicit alternative cut. UI uses its independent strict contiguous INT sequence from0 through the FIRST roles/configure row. Initial open controls, generation1/nonpooled selected binding, exact owner IDs81718/81714 and their ready ancestry to King/root must join. A mismatching first roles cut rejects; no later convenient roles row is searched. Unknown/unsupported selected initial entry paths make that role MISSING.

The initial index supplies Timer81740/81732 birth, public configuration and monotone counters. Each inspected row retains original index/input_refs; checkpoint references bind phase to shared138/1231, line1/4, native owner and a node pointer. Facts references bind their exact role/field pointer. Cross-phase/cross-owner conflicts reject. A missing role edge blocks that role without deleting the other role's evidence. UI sequence is never ordered against shared sequence or used to prove later business behavior.

read_regular first checks canonical path components, every ancestor, no symlink, ordinary regular leaf/nlink1, size; then O_NOFOLLOW open/inode match, bounded raw reads, stable metadata and exact SHA. The complete small carrier is held as raw bytes for hashing; only prefix parsers decode selected initial content. No suffix schema, uniqueness, later-writer or business validity claim is made. No full old391 schema runs. Output directory and files are exclusively new, with strict readback through read_regular. Failures after reservation preserve first-error and partial output without repair/retry. Pre-reservation failures are reported to the invoking launcher, which must retain stderr/exit evidence.

The new Root release is fixed at data/phase418-root-initial-partial-projection-release/release.json, schema root418-initial-autohide-projection/1, action ONE_INITIAL_AUTOHIDE_PROJECTION. It binds source_owner/context, final source_review/review_owner, exact four data descriptors and fixed fresh output. Final review schema/status are independent419-autohide-partial-recipe-final-review/1 and INDEPENDENT419_AUTOHIDE_PARTIAL_RECIPE_SOURCE_AND_FUNCTIONAL_ACCEPTED_ROOT_PENDING with final_seal=true. Review must pin this source_owner, source-edge-list and the actual native attribution proposal. Its G01/G02 statuses must equal the accepted literals in the API. The intermediate419 schema/final_seal=false is rejected. Owned files use descriptor lists; no future hashes are fabricated.

Python interpreter/stdlib startup precedes module-level I/O checks. The launcher must externally pin the module/source owner before import/CLI execution. This module repeats source/control verification before reading data; it does not claim to police interpreter startup or arbitrary hostile Python code calling private objects. No old project imports are present.

## 3. Realize — actual function interfaces

Module: tests/phase418_initial_autohide_projection.py. api-contract.json enumerates actual AST signatures and line locations; no alternate wrapper/template implements the algorithm.

- require(condition, reason), integer(value, minimum), native_id(value), same(left,right): strict domain helpers; bool is never INT and equality preserves JSON numeric type spelling.
- strict_json(raw): UTF-8 strict, duplicate-key and nonfinite rejection, no coercion of typed source values.
- canonical_path(value), physical_path(path,leaf_regular), descriptor(value): validate path/descriptor shape and physical ancestry before reads.
- read_regular(value,cap,io): gate, O_NOFOLLOW, stable ordinary identity, bounded bytes, exact size/SHA and I/O ledger.
- target_keys(): fixed88 keys (35Timer roles×2 plus Character12/King6).
- load_initial_index(raw): strict1479 unique rows,1391 supported DIRECT and exactly88 MISSING; no fullschema claim. observed(index,field,phase,role) returns raw value/index/ref without constructing runtime objects.
- project_slots(raw,fixed_table): exact source-fixed slot/identity/domain projection. _skip_string/_skip_value/envelope_sequence inspect a top-level sequence without decoding payload. project_lineage(raw,slot,cutoff=138) validates only the initial prefix and selected provenance, recording an explicit cut.
- project_ui(raw): decode initial open through first roles/configure only; validate independent UI order, controls, selected scene/binding/ancestry; preserve per-role gaps.
- check_autohide_role(index,provenance,role): check identity, birth/public typed domain and zero counters; return conditional_input_match/gaps/evidence only, never actual_value or admission. Local synthetic success cannot be a Root receipt.
- _VerifiedGate.__init__(token,reasons,receipts): internal handoff constructed by verify_release, not a public proof flag. verify_release(release_descriptor,io) verifies actual final review/source closure and returns context, gate, release; no data is opened before this.
- derive_autohide_pair(index,provenance,gate): fixed88 delta rows; only four matching enabled rows can receive SOURCE_DERIVED/SUPPORTED/proof_complete=true and binary64 bff0000000000000. Others have no actual_value. Gates are independently accepted SOURCE plus actual input premises.
- save_new(path,value): exclusive0600 bounded JSON, fsync, strict raw readback.
- run(release_descriptor): reserve fixed output once, read exact four objects, project/derive/write initial-provenance.json and delta-report.json plus owned-files.json; retain first error. main(): required --release/--release-size/--release-sha256 and print compact result. No optional mode runs other roles or schemas.

Actual output status is PARTIAL_SOURCE_DERIVATION_PENDING_INDEPENDENT_ACTUAL_REVIEW or BLOCKED_INITIAL_SOURCE_GAPS; it reports0..4 conditional promotions,88-minus-count remaining, unchanged1391 and documentary1371, fullschema NOT_VALIDATED and no genuine bundle/King admission. A successful projection still requires independent actual evidence review.

## 4. Acceptance Criteria / Tests

Author: compile bytes without execution; parse AST and enumerate exact imports/signatures; verify finite source/context descriptors and old bytes; record0 module imports/functions/projections/capture/oldSUT/schema/Model/native. No author synthetic positive or actual carrier read.

419 independently owns these bounded checks, each mapped to417:

1. B01: wrong/spent Root release, mismatched source/context/review owner, intermediate review, absent G01/G02, arbitrary proof flags and fresh output. Module startup limitations remain explicit.
2. B02: increasing shared sequence with lawful gaps; first>=138 cut; EOF cut; duplicate/reversed/bool sequence; poisoned suffix is never decoded. Initial duplicate JSON keys reject.
3. B03: contiguous independent UI sequence, first roles mismatch, duplicate/missing open/bind/ready, missing controls/ancestry and independent ordering.
4. B04: exact slot/native/descriptor/Character/inventory/owner/Timer joins; duplicate/collision and wrong typed geometry reject.
5. B05: one complete role versus one missing role, cross-phase ID mismatch, nonzero/bool counters, wrong birth type/autostart/internal flags. No cross-role proof reuse and no localization of nonzero aggregate calls.
6. B06: path/link/hardlink/size/hash/readback/exclusive creation; hash covers suffix while prefix payload decoding stops. Slots remain a whole bounded document.
7. B07: functional helper synthetics cannot authorize real run; preserve first errors/no retry; all other84 disabled. Fullschema/genuine input/model/native remain closed.

After final419 and a separate genuine Root release, the independent role may perform ONE true projection and verify each actual promoted role/phase. Author stops after SOURCE owner sealing. No passed411 audit/native/capture batch is rerun.
