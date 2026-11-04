# Phase541: repaired single strict-eight comparison

## 1. Requirements

Continue the unfinished case029 comparison using immutable539 adapter after independent540 Source/five-control acceptance. Keep original535 model, gate and output seal, original nine Expected identities, original526 strict-eight contract and536 failure unchanged. No model/Native rerun, original raw12 INPUT read, B2/UI extraction or old control replay. Preparation reads metadata and Source only; actual Expected payload access requires a separate Root release.

## 2. Design

Mechanically derive a new host from tests/phase536_independent_actual_compare.py. Change stage/output/self paths and adapter descriptor to539, use closed10 binding copied exactly from539 template, authenticate original measured gate descriptor/canonical hash plus537 provenance addendum, and pass that original gate explicitly into compare_decoded. Retain original source/input/seal/request/capsule membership checks and strict comparison implementation. Add authentication of actual540 acceptance and preserve reference to536 failure. No new comparison algorithm or normalized replacement outputs.

One later fresh Python -I -B process, cwd /tmp, 50-second internal / 60-second outer wall limit. The same535 raw model and gate are decoded, not regenerated. Each nine Expected payloads is hash-verified and decoded once for this attempt; prior536 attempt already read those nine once and failed during model projection before compare_projected. New attempt metadata must retain that distinction. First exception or business differences are sealed without retry or relaxed contract.

## 3. Realize

main performs the existing536 preflight and same-instance association checks, adds frozen540 result/final acceptance, checks binding.prepare_gate against the original output-seal entry and its canonical hash, and pins the provenance addendum. The pure adapter receives native_outputs, sealed_result, bundle, input_proof, sealed_prepare_gate, root_binding. Counter coverage adds validate_sapphire_gate_origin; no candidate source import. Existing audit allows only the nine approved Expected reads and Source readback after the Expected gate. Save before, comparison when available, result and owner in new data/phase541-case029-comparison-first-001.

All host modifications, source-owner/pins and exact argv are sealed before release. The inherited previous-control evidence is read only; no old controls execute. Expected descriptors remain opaque during preparation.

## 4. Acceptance Criteria / Tests

One compare_decoded and, only if projections complete, one compare_projected. Each eight-section first difference is reported verbatim; success requires all eight null. Record actual helper calls, source hashes, same output identity, nine payload read counts and preserved capture_complete=true/process_clean_exit=false. A projection error remains a projection error, not a Native mismatch or business PASS. No broader formal75/general-layout/native-seed admission follows automatically. This phase is source preparation until Root releases execution; compile-only is permitted and is not an adapter import.
