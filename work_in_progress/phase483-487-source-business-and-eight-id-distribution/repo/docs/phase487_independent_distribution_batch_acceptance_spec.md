# Requirements

Independently accept only the 486 distribution of exact482v2 fifteen-source experimental code and one limited two-job positive batch smoke run. Do not repeat483,478,484, old controls or individual battle runs. No native, Expected, capture or pool operations. Formal75/general King/native admission stays unchanged. The two seeds are fixed by Root before outcomes: A48701 and B48702.

# Design

Static gate: verify the frozen486 owner/manifest, exact correspondence of all15 runtime files to482v2, and conservation of the old four public examples plus verifier from484. Review README/lineage for the accepted478 fixed native case versus fresh Source limits and the preserved483 first budget error. New eight-ID layout equals the presealed483 job's layout; mixed jobs contain that layout first and the old public King-Basic seven-ID example second, with exact identity/order/types/geometry and the two prescribed seeds. max_seconds is simulated combat seconds per job, not a wall timeout.

Wait for Root's publication and independent HTTPS-clone HEAD/manifest SHA. Do not run from the live staging package or before that release. On that exact clone, execute the existing read-only package verifier once with Root's trusted manifest SHA. Then a fresh independent wrapper calls run_batch exactly once with two jobs, keep_results=True and max_seconds=120.0. The outer wrapper has a20-second wall ceiling for batch execution, separate from simulated time. No extra CLIhelp or individual run is needed.

The wrapper imports only the published15-source package and stdlib, disables bytecode and records actual module paths. Boundary wrappers count initialize, constructor, prepare, logical activation entries, Battle.run/Engine.run, and production provider creation without whole-process profiling. Observe the actual instances/providers created by the batch; retain references only for read-only post-call checks. Never replace RNG providers, advance instances again, or call run/step/result to obtain a second result.

# Realize

1. Static source review: check package manifest lists every payload and source15 exact approved hashes; old examples/verifier exact; compare new jobs structurally and with canonical SHA to the independently presealed expected-job identities. No candidate import or model call.
2. Release binding: save exact remote HEAD, package/manifest/source hashes, verifier command and batch wrapper/pins/owner before execution. Remote source must remain untouched. Any stale/mismatched identity blocks execution.
3. Invoke verifier once. Save stdout/stderr/status and stop on failure.
4. Invoke a fresh wrapper once. Read the frozen jobs once; retain an independent deep copy. Record perf_counter, self process CPU time and Linux resource.getrusage(RUSAGE_SELF).ru_maxrss before/after the call. Optional /proc/self/status RSS reading is confined to this own wrapper and recorded as available/unavailable; no global process audit. Execute only run_batch(jobs,max_seconds=120.0,keep_results=True).
5. Verify ordered two records: index0/1, seed48701/48702, statusCOMPLETED, full result present, profileA source-headless-king-mirror-poison-fixed60/1 and profileB source-headless-king-basic-goobert-fixed60/1. Each final terminal barrier, winner consistency and Source RNG state/audit must agree with its own retained instance. Verify full two-stream provenance and distinct instance/provider ownership without asserting numerical streams cannot coincidentally match. Preserve full result/events/history/audit/terminal and original input values. No second model call is used for verification.
6. Verify source/input bytes after, seal complete result and diagnostics. On the first exception, TIME_BUDGET status, missing result, or invariant failure, preserve available records and actual counts and stop without fixing/retrying or changing seeds/layout. A real timeout has no fabricated result/winner.

Upper bounds: one read-only verifier process, one mixed run_batch call, two successful constructors/prepares/logical initial activations, two natural run attempts and at most two complete battles. The internal activation method may enter twice per instance through the existing driver; report actual entries separately. Expected game RNG and FrameDriver activity belongs to those two new jobs only. No synthetic component invocation or prior test replay.

# Acceptance Criteria / Tests

All static identities and labels hold; verifier succeeds; two new jobs complete in requested order with correct profile, genuine Source provider, intact terminal/RNG/audit and unchanged inputs/source. Report batch wall seconds, two-job throughput (2 divided by batch wall time), CPU time and process RSS high-water measurement with units. A peak includes interpreter/imports and retained results; before/after high-water difference is not per-job memory. Report run/output serialization timings separately if measured, never substitute simulated combat duration for wall throughput.

This is a two-sample mixed-profile package smoke check, not a throughput benchmark, RL training environment certification, cross-process determinism test, or native seed/distribution equivalence. Natural branch HIT/NOT_HIT is descriptive only and does not justify rerunning or tuning input. Publication acceptance does not erase483's first simulated-budget failure or enlarge formal/native support. Until486freeze and Root's remote release are provided, execution remains blocked by phase sequencing and all new run counts are zero.
