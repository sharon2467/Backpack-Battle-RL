"""Compile-only392 draft. No391 implementation is bound or executable here."""

from pathlib import PurePosixPath


PHASE = "phase392-compile-only-firsteligible-runner-draft/1"
EXECUTION_DENIED = "DRAFT_ONLY_WAIT391_FREEZE_AND_NEW_ROOT_EXECUTION_GATE"
REQUIRED_BINDINGS = (
    "collector", "schema_module", "active_source_tuple", "native_source_origin",
)
API_TARGETS = {
    "terminal_evidence": {
        "module": "phase391_king_observer_schema",
        "function": "validate_terminal_evidence",
        "provisional_signature": "(endpoint, ClockSchedule, cleanup)",
        "unbound": "ClockSchedule constructor/types, exact endpoint/caps/source descriptor",
    },
    "terminal_receipt": {
        "module": "phase391_king_observer_schema",
        "function": "validate_terminal_receipt",
        "provisional_signature": "(endpoint, clock, receipt, control, validation)",
        "unbound": "actual closed receipt/control/validation keys and real consumer pins",
    },
    "terminal_diagnostics": {
        "module": "phase391_king_observer_schema",
        "function": "validate_terminal_diagnostics",
        "provisional_signature": "(rows) -> finalcontrol",
        "unbound": "actual record framing/caps, closed row fields and typed finalcontrol",
    },
    "host_file_boundary": {
        "module": "UNBOUND_REAL_HOST_FROM_FREEZE",
        "function": "read_terminal_expected_controls",
        "provisional_signature": "(source_root, freeze, capture) -> proof",
        "unbound": "real host path, exact control filenames/bytecaps and permissions",
        "rule": "Call real host boundary; no injected validator or schema-only substitute",
    },
    "host_metadata_consumer": {
        "module": "UNBOUND_REAL_HOST_FROM_FREEZE",
        "function": "collect_capture_metadata",
        "provisional_signature": "UNBOUND",
        "unbound": "actual caller signature and delegation to the same public receipt join",
    },
}


def strict_descriptor(row):
    """Pure descriptor syntax only; this does not establish actual file safety."""
    if type(row) is not dict:
        raise ValueError("descriptor must be a dictionary")
    if not all(key in row for key in ("path", "size", "sha256")):
        raise ValueError("missing source descriptor identity")
    path, size, digest = row["path"], row["size"], row["sha256"]
    if type(path) is not str or not path or "\\" in path or "\x00" in path:
        raise ValueError("unsafe source descriptor path")
    pure = PurePosixPath(path)
    if pure.is_absolute() or pure.as_posix() != path or any(
        part in (".", "..") for part in path.split("/")
    ):
        raise ValueError("source descriptor must be canonical repo-relative")
    if type(size) is not int or size < 0:
        raise ValueError("source descriptor size requires strictINT")
    if type(digest) is not str or len(digest) != 64 or any(
        char not in "0123456789abcdef" for char in digest
    ):
        raise ValueError("source descriptor requires lowercase SHA256")
    return {"path": path, "size": size, "sha256": digest}


def source_read_descriptors(
    freeze_files, actual_bindings, source_owner_files,
    *, freeze_descriptor, source_owner_descriptor, executing_checker_descriptor,
):
    """Future exact union, including origins and self; no filesystem operations."""
    if type(actual_bindings) is not dict or set(actual_bindings) != set(REQUIRED_BINDINGS):
        raise ValueError("all four actual SOURCE bindings must be resolved from freeze")
    if type(freeze_files) is not list or type(source_owner_files) is not list:
        raise ValueError("full frozen file and source-owner lists required")
    rows = list(freeze_files) + [actual_bindings[key] for key in REQUIRED_BINDINGS]
    rows += list(source_owner_files)
    rows += [freeze_descriptor, source_owner_descriptor, executing_checker_descriptor]
    result = {}
    for row in rows:
        item = strict_descriptor(row)
        previous = result.get(item["path"])
        if previous is not None and previous != item:
            raise ValueError("conflicting descriptor for " + item["path"])
        result[item["path"]] = item
    return [result[path] for path in sorted(result)]


def fixture_references(contract):
    """Notation references only: no ClockSchedule, full carrier or API input."""
    if type(contract) is not dict:
        raise ValueError("frozen392 contract required")
    cases = contract["cases"]
    if [row["id"] for row in cases] != ["C%02d" % i for i in range(1, 33)]:
        raise ValueError("logical obligations must remain exactly C01..C32")
    baselines = contract["baseline_notation_only"]
    if any(len(value["rows_notation"]) > 32 for value in baselines.values()):
        raise ValueError("synthetic clock exceeds32 rows")
    return [
        {
            "id": row["id"],
            "baseline_reference": row["baseline"],
            "mutation_reference": row["concrete_input_or_mutation"],
            "expected_reference": row["expected_outcome"],
            "planned_layer": row["planned_layer"],
            "input_materialization": "NOT_IMPLEMENTED_BEFORE_ACTUAL391_API_FREEZE",
        }
        for row in cases
    ]


def execution_plan(contract):
    """Return a nonexecuting future outline; never return acceptance or proof."""
    return {
        "status": EXECUTION_DENIED,
        "fixture_references": fixture_references(contract),
        "public_API_targets": API_TARGETS,
        "ordered_future_steps": [
            "Verify actual freeze/source-owner/actual bindings/self descriptors before import",
            "Independently inspect391 delta and aggregate finite SOURCE blockers",
            "Bind real signatures/caps/keys/tuple and freeze a new executable contract",
            "Audit exact SOURCE closure; expected/control file access separately released",
            "Call real new public schema/join APIs only on honest bounded SOURCE units",
            "Test actual host file-boundary API if fully representable; otherwise mark OPEN",
            "Do not replace host path with injected validator or a fake full12 positive",
            "Only if separately released: at most one exact empty-project language process",
            "Joint-seal actual first results before interpretation; preserve first failure",
        ],
        "forbidden": [
            "current_execution", "unsealed391_reads", "whole_repo_read_grant",
            "actual_pool", "original_Game", "fake_native_or_capture_marker",
            "candidate_Engine_RNG_model", "projection", "oracle_terminal_model_input",
        ],
    }


def main():
    raise SystemExit(EXECUTION_DENIED)


if __name__ == "__main__":
    main()
