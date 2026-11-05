# 649 — fixed-plan consumer slot bound repair

## 1. Requirements

Implement Root648SPEC and647finding1cadb76d0942b3008509cb4637d5274c16b6312637ca94d3b42a2f39edffe6e8.
Preserve644firsterror/partial, raw002, producer610/612/621, host/recovery and all
old code. Generate once into `data/phase649-consumer-slot-boundary-source` and
compile only three new modules. No imports/helpers/tests/build/model/Native/
Expected or pool operation. First generation error is sealed and stops.

## 2. Design / exact seam table

| Source | New isolated file | Allowed change |
|---|---|---|
|610schema208143B a33d2b90...|schema/phase649_consumer_schema.py|one function, three spans below|
|tests/phase621_input_bridge.py|tests/phase649_input_bridge.py|schema descriptor, fixed schema binding, closed selfpath|
|tests/phase621_mixed_tape_run.py|tests/phase649_mixed_tape_run.py|INPUT_SOURCE/CANDIDATE_CONTEXT/FIXED_INPUTS input-owner only|

C adapter/B2 stay exact existing621leaves. B580all15, initial578 and runtime14
ABI remain exact. Consumer schema retains VERSION/PROFILE and all110producer
types/fields. No new Native producer or hook.612receipt still means the old
producer110+oldschema Source/finite acceptance, not acceptance of649. A separate
consumer-repair provenance file records pending650; it is not a caller proof flag
or a new field in the closed runtime/context contract.

## 3. Realize

`tests/phase649_prepare_consumer_slot_boundary_source.py` reads Source/647/648
metadata only. Exact AST line/spans, unique replacements and full inverses.

Schema `_binding_validate_value(value,fixed_plan)`: immediately after existing
`_binding_same_source(fixed_plan,BINDING_FIXED_PLAN)`, add
`side_limits={side:sum(spec['side']==side for spec in BINDING_FIXED_PLAN)-1 for side in ('P','O')}`.
Trusted frozen plan yields P22/O5. Replace only upper argument19 of
`integer(row['input_slot'],0,19)` and `integer(row['inventory_encounter_index'],0,19)`
with `side_limits[side]`. All other statements exact: INT rejects BOOL; callerplan
must equal trusted plan; exactrole/slot/descriptor/UID/inventory/character/geometry
joins and final unsorted contiguous encounter order remain. All other schema
functions and module declarations exact; no whole-profile count increase.

A: SCHEMA_PIN and FIXED_SOURCE_BINDINGS.schema_module point to new actual schema;
authenticate_request only replaces its literal bridge selfpath. Keep load_schema
body exact because schema VERSION/PROFILE did not change. New context copies621
exactly except schema pointers and bridge Source pin; fixed producer tuple/owner/
612receipt, Source rules,14ABI and candidateB580/581identities remain. Freeze
inputowner only after actual schema/bridge/context/provenance exist. No actual
12pins are read or filled. Source-template models/Expected remain strictINT0.

C launcher: bind that real inputowner/context and matching FIXED_INPUTS member;
all functions exact. Clone17key request template with new launcher/inputowner
descriptors; actualbundle/proof/witness/acceptance/B2 remain null, authorization
false. Retain existing Ccontract and exact adapter/B2 descriptors. No Source
provenance loop: schema→bridge/context→inputowner→launcher→totalfreeze/owner.

Save per-file full inverse/diff/function census, trustedplan count proof,
Source provenance/closure/freeze/API. No foreign actual rows or Expected provide
bounds; this is a consumer correction to the fixed SOURCE plan.

## 4. Acceptance

Author compile/static only: schema changed function exactly_binding_validate_value;
remove the three recorded spans to recover entire610file. A changed function
only authenticate_request (selfpath); launcher no changed functions. All110sites,
stricttyped/identity/geometry/encounter/helpers and B580/initial unchanged. Independent
650 later tests binding29positive and strictnegative boundaries from648; those
are not run by author and not fullINPUT/model/Native acceptance. Only after650
and Root explicit release may a new request bind the same immutable12actualpins
and run one repaired INPUTbuild in a new output. Never recapture or alter644.
