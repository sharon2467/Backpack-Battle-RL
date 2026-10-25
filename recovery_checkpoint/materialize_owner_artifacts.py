"""Copy exact public historical artifacts needed by old owners; never execute them."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def no_links(path):
    path = Path(os.path.abspath(path))
    require(not any(p.is_symlink() for p in (path, *path.parents)), 'symlink ancestor')
    return path


def relative(name, prefix):
    require(type(name) is str and name.startswith(prefix), 'path prefix')
    path = PurePosixPath(name)
    require(not path.is_absolute() and path.as_posix() == name
            and all(p not in ('', '.', '..') for p in name.split('/'))
            and '\\' not in name and ':' not in name
            and not any(ord(c) < 32 or ord(c) == 127 for c in name), 'unsafe path')
    return name


def pin(path):
    path = no_links(path)
    require(path.is_file(), 'regular file required')
    with path.open('rb') as stream:
        return {'size': path.stat().st_size,
                'sha256': hashlib.file_digest(stream, 'sha256').hexdigest()}


def load_plan():
    manifest = json.loads((ROOT / 'MANIFEST.json').read_text())
    plan = json.loads((ROOT / 'owner-relocations.json').read_text())
    require(set(plan) == {'schema', 'artifacts'} and plan['schema'] == 'public-owner-artifact-relocations/1', 'plan schema')
    require(type(plan['artifacts']) is list and len(plan['artifacts']) == 1, 'bounded artifact count')
    known = {}
    for row in manifest['historical_progress_archives']:
        archive = row['archive']
        if len(archive['parts']) == 1:
            part = archive['parts'][0]
            identity = {k: archive[k] for k in ('size', 'sha256')}
            require({k: part[k] for k in identity} == identity, 'single part must equal whole archive')
            known[part['path']] = identity
    for row in plan['artifacts']:
        require(set(row) == {'historical_absolute', 'destination', 'source', 'identity'}, 'artifact fields')
        relative(row['source'], 'parts/')
        relative(row['destination'], 'workspace/checkpoints/')
        require(row['historical_absolute'] == '/' + row['destination'], 'historical path mapping')
        require(row['source'] in known and row['identity'] == known[row['source']], 'artifact not exact public whole archive')
        require(pin(ROOT / row['source']) == row['identity'], 'source part identity')
    return plan


def materialize(destination):
    destination = no_links(destination)
    require(destination.is_dir(), 'existing restored destination required')
    recovery_path = no_links(destination / 'RECOVERY-RECEIPT.json')
    recovery = json.loads(recovery_path.read_text())
    require(recovery['status'] == 'ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED', 'verified recovery required')
    manifest_pin = pin(ROOT / 'MANIFEST.json')
    require(recovery['manifest'] == manifest_pin, 'recovery and current manifest mismatch')
    plan_pin = pin(ROOT / 'owner-relocations.json')
    plan = load_plan()
    receipt = destination / 'OWNER-ARTIFACTS-RECEIPT.json'
    require(not os.path.lexists(receipt), 'artifact receipt already exists')
    for row in plan['artifacts']:
        output = no_links(destination / row['destination'])
        require(not os.path.lexists(output), 'artifact destination already exists')
    for row in plan['artifacts']:
        source = ROOT / row['source']
        output = no_links(destination / row['destination'])
        output.parent.mkdir(parents=True, exist_ok=True)
        no_links(output)
        with source.open('rb') as incoming, output.open('xb') as outgoing:
            for block in iter(lambda: incoming.read(1024 * 1024), b''):
                outgoing.write(block)
            outgoing.flush()
            os.fsync(outgoing.fileno())
        output.chmod(0o644)
        require(pin(output) == row['identity'] == pin(source), 'artifact/source readback mismatch')
    require(pin(ROOT / 'MANIFEST.json') == manifest_pin
            and pin(ROOT / 'owner-relocations.json') == plan_pin, 'contract changed during copy')
    result = {'schema': 'public-owner-artifact-materialization-receipt/1',
              'status': 'HISTORICAL_OWNER_ARTIFACTS_MATERIALIZED',
              'manifest': manifest_pin, 'relocations': plan_pin,
              'artifacts': plan['artifacts'], 'destination': str(destination),
              'old_cloud_files_used': [], 'models': 0, 'native': 0, 'training': 0}
    with receipt.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write('\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(materialize(args.destination), indent=2, sort_keys=True))
    except Exception as error:
        print(json.dumps({'status': 'OWNER_ARTIFACT_COPY_REJECTED', 'error': str(error),
                          'partial_output_preserved': True}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
