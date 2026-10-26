# 380 payload preflight and partial-install recovery SOURCE implementation

## 1. Requirements

Implement accepted379 design in new380 files. Preserve all old frozen code/failures, standard15/current75,375Food107/owner guard/schema,370collector, dispatch/clock/RNG/17-key ABI, fixtures and35301/35302. SOURCE generation/text compile/AST/pins and saved-only map derivation permitted; no resolver/installer/recovery SUT calls, unit self-acceptance, probe/Godot/Game/livepool inventory/restore/READY/model/projection.

## 2. Design

New host exports `resolve_execute_payloads` and `verify_execute_payloads`. They bind75patch descriptors,3 artifact descriptors (collector from freeze.collector, config/marker from exact frozenDATA rows),3 case inputs, actual schema/source tuple and all necessary SOURCE/root/review driver descriptors. Labels are not interpreted as paths. Plan resolves the actual complete graph before any lease/reset; execute independently resolves and compares the same graph before lease. No copy is added at the old guessed SOURCE/collector.gd location. Runtime resource gate/READY/lease/budget remain separate and unchanged.

New storage clones363. All original functions except install retain exact AST/bytes. New source descriptor checking validates safe root/path, strict sizeINT/SHA, regular+nlink1 source and stable bytes. Direct `install` accepts artifact descriptors instead of Paths and invokes full source+artifact+target preflight itself before backup.mkdir. No caller boolean or host-only proof. Preflight retains finite immutable payload bytes for the old journal→atomicImage ordering, eliminating first source existence checks inside the backup loop.

Actual frozen install corpus is75patch+3artifact=78 payload destinations,807199B (from375 actual frozen descriptors/379 audit). Constants MAX_INSTALL_PAYLOADS=78/MAX_INSTALL_BYTES=807199 bound preload before reads; smaller tinyFS contracts remain testable. This is a SOURCE-corpus bound, not kernel aggregate quota. Driver metadata is checked by streaming descriptor validation, not included in install-byte preload. Targets retain strictTarget/image checks and source before identities; artifact existing preimages remain recorded from actual files. Before reset, plan validates sources; post-reset direct installer validates its target preimages—do not conflate the two phases.

New partial map handles only attempt04/reset-complete/install-journal-incomplete: savedcurrent==prior-reset.after; old026target==reset.before==previous-source inventory; receipt excludes atomic install writes and complete journal. Only absent sink+marker may be created, with individually bound reset-delete and old-after payload evidence. Numeric75rawbackups are verified prefix evidence, not a journal or oldtarget metadata. All changes/counts derive from actual saved manifests, stageddata and bundle. Old writers are reused; actual recovery still requires a real independent/root gate and remains failed until separate exact readback/commit.

## 3. Realize

- Storage `check_source_descriptor` streams exact/stable regular source identity. `read_source_payload` returns bounded immutable bytes. `preflight_install_payloads` validates every patch/artifact descriptor, expected total/count, safe unique destination and current target before state; returns complete todo. `install` calls preflight before backup creation, keeps complete-journal-before-write, original atomicImage/fsync/metadata flow. strictTarget/image/state/lease/reset/archive methods are mechanically conserved.
- Host resolver creates closed JSON descriptor graph and driver dedup requiring same-path identities to agree. Verifier rereads every descriptor and checks fixed destinations/limits. Plan records graph; execute compares a fresh graph and verification before lease/reset, uses exact case descriptors for copies, passes artifact descriptors to install and archives driver sources from that same graph. New Root/review/SOURCE/attempt05 bindings remain unapproved metadata.
- Saved-only map builder validates exact attempt04 receipt/overlay/current/oldtarget/reset/old73+marker/prefix75backup evidence; emits all changed/created files with before-null only on exact2 known missing paths. New helper independently rechecks that evidence, permits those absent targets through existing atomicImage, and preserves old restore/readback/commit logic. No forged preimages.json.
- SOURCE preparer derives host/storage/helper; records exact inverse/function exceptions, schema/collector/75 payload conservation, full saved map pins, new freeze/owner. No operational module import. Existing356/361/projector remain closed and untouched.

## 4. Acceptance Criteria / Tests

Author: text compile, exact AST/inverse, old owner/new owner readback, saved-only map CRC/SHA/metadata derivation. No semantic SUT calls or self FINAL.

Independent: public resolver succeeds with valid reused collector elsewhere and no SOURCE collector copy; missing/changed/unsafe/linked/badidentity payloads reject before host mutation. Direct installer bypassing host rejects every source/artifact defect before creating backup, retaining unchanged target bytes/metadata. Verify descriptor artifact API, all-source bounds and late target checks; no fake native capture.

Partial helper controls reject wrong reset/state/schema, unknown missing/extra, nonexistent journal fabricated as original, bad prefixbackups/mode/mtime/payload and premature READY. Positive may create only the two evidenced files, then full target readback with failed state retained. Actualpool restore and any newattempt require separate root execution gates.
