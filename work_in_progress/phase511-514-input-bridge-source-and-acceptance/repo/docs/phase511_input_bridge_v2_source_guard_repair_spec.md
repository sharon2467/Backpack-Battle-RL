# Phase511v2 Source guard repair and immutable reuse

## 1. Requirements

Root released the exact preparer-only repair. Preserve original511 first assembly failure and partial owner `e7d2be6ee724c2bc0d1f07f6c2d3acd0a0fef578e13f296f299614948fd38c1e`. Two generated modules already compiled but no schema/projector execution occurred. They remain byte-exact, including error names/input guards/all business projection code. Do not finish or overwrite original failure directory.

## 2. Design

New producer `tests/phase511_prepare_input_bridge_source_v2.py`, new output `data/phase511-input-bridge-source-v2`. Original modules remain at their existing paths and are explicitly reused. Their immutable ABI/branch-rule references intentionally point to original sealed leaves; new context/request/owner include those leaves and partialowner. No path rebinding inside modules, no new actual pins or success reinterpretation of assembly1.

## 3. Realize

Replace substring INPUT_PINS check with AST module top-level Assign/AnnAssign target Name INPUT_PINS absence. Keep the independent no import-time loader constraint. Check newly assembled module bytes equal the existing two sealed modules instead of writing them. New rules/context use original branch-rule/ABI descriptors, whose bytes are verified against partialowner; new output may retain copies as provenance but consumes only the exact original referenced leaves. Compile Source only, record reuse and cumulative two Source assemblies (first failedguard, second attempted). Complete owner includes old leaves/partialowner/baseSPEC and new metadata. First new error preserves and stops.

## 4. Acceptance Criteria / Tests

Both module SHA remain exactly original partial; typed/IO/Tape bodies remain Source470-conserved.0schema/projector imports/calls, model, Native record, baseline/pool/Expected reads. Actual Root request/cuts/UID/branch/cache remain unknown. Freeze goes to Root, no automatic512. Future actual build and same-instance business prepare gate remain independently required.
