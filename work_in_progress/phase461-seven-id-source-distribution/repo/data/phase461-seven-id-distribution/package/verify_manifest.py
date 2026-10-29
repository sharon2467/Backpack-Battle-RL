"""Read-only package byte verifier. Never imports or executes battle modules."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys

SOURCE_PATHS = ('godot_pcg_integer.py', 'headless.py', 'native_replay_v7/__init__.py', 'native_replay_v7/frame_driver.py', 'native_replay_v7/timer_runtime.py', 'native_replay_v8/__init__.py', 'native_replay_v8/__main__.py', 'native_replay_v8/compare.py', 'native_replay_v8/engine.py', 'native_replay_v8/genuine.py', 'native_replay_v8/histories.py', 'native_replay_v8/observed.py', 'native_replay_v8/randomness.py', 'native_replay_v8/state.py', 'original_rng.py')
MANIFEST_SCHEMA = 'experimental-source-king-package-manifest/1'
FILE_CAP = 8 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate manifest key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite manifest value: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def _read_regular(root, relative):
    require(type(relative) is str and relative and '\\' not in relative, 'relative POSIX file path required')
    parts = PurePosixPath(relative).parts
    require(not PurePosixPath(relative).is_absolute() and '..' not in parts
            and str(PurePosixPath(relative)) == relative and relative != '.', 'unsafe manifest path')
    directory_flags = os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0) | getattr(os, 'O_NOFOLLOW', 0)
    descriptors = []
    file_descriptor = None
    try:
        require(not stat.S_ISLNK(os.lstat(root).st_mode), 'package root must not be a symlink')
        descriptors.append(os.open(root, directory_flags))
        for part in parts[:-1]:
            before = os.stat(part, dir_fd=descriptors[-1], follow_symlinks=False)
            require(stat.S_ISDIR(before.st_mode) and not stat.S_ISLNK(before.st_mode), 'ordinary package directory required')
            descriptors.append(os.open(part, directory_flags, dir_fd=descriptors[-1]))
        before = os.stat(parts[-1], dir_fd=descriptors[-1], follow_symlinks=False)
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= FILE_CAP,
                'ordinary single-link bounded payload required: ' + relative)
        file_descriptor = os.open(parts[-1], os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0), dir_fd=descriptors[-1])
        identity = lambda value: (value.st_dev, value.st_ino, value.st_mode, value.st_nlink,
                                  value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        require(identity(before) == identity(os.fstat(file_descriptor)), 'payload changed at open')
        chunks = []
        size = 0
        while True:
            chunk = os.read(file_descriptor, 65536)
            if not chunk:
                break
            size += len(chunk)
            require(size <= FILE_CAP, 'payload grew past cap')
            chunks.append(chunk)
        after = os.stat(parts[-1], dir_fd=descriptors[-1], follow_symlinks=False)
        require(identity(before) == identity(os.fstat(file_descriptor)) == identity(after), 'payload changed during read')
        return b''.join(chunks)
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def verify(root, manifest_sha256=None):
    root = Path(root).absolute()
    raw = _read_regular(root, 'manifest.json')
    actual_manifest_sha = hashlib.sha256(raw).hexdigest()
    if manifest_sha256 is not None:
        require(type(manifest_sha256) is str and re.fullmatch('[0-9a-f]{64}', manifest_sha256) is not None,
                'external manifest SHA256 must be64 lowercase hex')
        require(actual_manifest_sha == manifest_sha256, 'manifest SHA256 mismatch')
    manifest = _strict_json(raw)
    require(type(manifest) is dict and manifest.get('schema') == MANIFEST_SCHEMA, 'manifest schema')
    require(type(manifest.get('source_file_count')) is int and manifest['source_file_count'] == 15, 'exact15 Source count')
    require(type(manifest.get('files')) is list, 'manifest file array')
    seen = set()
    sources = set()
    for row in manifest['files']:
        require(type(row) is dict and set(row) == {'path', 'kind', 'size', 'sha256'}, 'manifest record fields')
        require(type(row['path']) is str and row['path'] not in seen and row['path'] != 'manifest.json', 'duplicate/self payload')
        require(row['kind'] in ('source', 'documentation', 'example', 'lineage', 'verifier'), 'payload kind')
        require(type(row['size']) is int and 0 <= row['size'] <= FILE_CAP, 'payload size')
        require(type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']) is not None, 'payload SHA256')
        payload = _read_regular(root, row['path'])
        require(len(payload) == row['size'] and hashlib.sha256(payload).hexdigest() == row['sha256'], 'payload mismatch: ' + row['path'])
        seen.add(row['path'])
        if row['kind'] == 'source':
            sources.add(row['path'])
    require(sources == set(SOURCE_PATHS) and len(sources) == 15, 'exact15 Source membership')
    require(_read_regular(root, 'manifest.json') == raw, 'manifest changed during verification')
    return dict(status='VERIFIED_LISTED_PACKAGE_BYTES', files=len(seen), source_files=15,
                manifest_sha256=actual_manifest_sha, battle_modules_imported=0, battle_calls=0)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).absolute().parent)
    parser.add_argument('--manifest-sha256')
    arguments = parser.parse_args()
    try:
        result = verify(arguments.root, arguments.manifest_sha256)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps(dict(status='FAIL', error=str(error))), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
