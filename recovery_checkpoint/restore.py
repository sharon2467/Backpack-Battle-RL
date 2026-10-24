"""Restore a pinned GitHub checkpoint; never execute checkpoint contents."""
from pathlib import Path, PurePosixPath
from contextlib import contextmanager, ExitStack
import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tarfile
import tempfile
import zipfile

CHUNK = 1024 * 1024
ROOT = Path(__file__).absolute().parent
FIELDS = {'path', 'size', 'sha256', 'archive', 'member', 'mode', 'active'}
FORMATS = {'compact_zip_tar_xz', 'zip', 'tar_xz'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe_name(name):
    require(type(name) is str and bool(name), 'nonempty relative path required')
    require(not any(ord(c) < 32 or ord(c) == 127 for c in name), 'control character in path')
    require('\\' not in name and ':' not in name, 'unsafe path character')
    p = PurePosixPath(name)
    require(not p.is_absolute() and p.as_posix() == name
            and all(c not in ('', '.', '..') for c in name.split('/')), 'noncanonical relative path')
    return name


def no_links(path):
    path = Path(os.path.abspath(path))
    for p in (path, *path.parents):
        require(not p.is_symlink(), 'symlink filesystem ancestor: ' + str(p))
    return path


def regular(path):
    path = no_links(path)
    require(path.is_file() and stat.S_ISREG(path.stat().st_mode), 'regular input required: ' + str(path))
    return path


def digest(stream):
    h, size = hashlib.sha256(), 0
    while block := stream.read(CHUNK):
        h.update(block)
        size += len(block)
    return {'size': size, 'sha256': h.hexdigest()}


def pin(path):
    with regular(path).open('rb') as stream:
        return digest(stream)


def identity(value):
    require(type(value) is dict and type(value.get('size')) is int and value['size'] >= 0,
            'strict nonnegative INT size required')
    require(type(value.get('sha256')) is str and re.fullmatch('[0-9a-f]{64}', value['sha256']),
            'lowercase SHA256 required')
    return {k: value[k] for k in ('size', 'sha256')}


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def decode(raw):
    def nonfinite(value):
        raise ValueError('nonfinite JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=nonfinite)


def source_path(name):
    return regular(ROOT / safe_name(name))


def link_target(path, target):
    require(type(target) is str and target and not target.startswith('/')
            and '\\' not in target and ':' not in target
            and not any(ord(c) < 32 or ord(c) == 127 for c in target), 'unsafe link target')
    parts = list(PurePosixPath(path).parent.parts)
    for part in target.split('/'):
        require(part != '', 'empty link target component')
        if part == '..':
            require(parts, 'link escapes destination')
            parts.pop()
        elif part != '.':
            parts.append(part)
    name = '/'.join(parts)
    require(name.startswith('workspace/'), 'runtime link target outside workspace tree')
    return safe_name(name)


def load_contract():
    no_links(ROOT)
    manifest_path = regular(ROOT / 'MANIFEST.json')
    raw = manifest_path.read_bytes()
    manifest = decode(raw)
    require(type(manifest) is dict and manifest.get('schema') == 'github-workspace-checkpoint/1',
            'checkpoint manifest schema')
    archives = manifest.get('archives')
    require(type(archives) is dict and archives, 'nonempty archives mapping')
    for label, archive in archives.items():
        require(type(label) is str and label and type(archive) is dict, 'archive descriptor')
        identity(archive)
        require(archive.get('format') in FORMATS, 'unknown archive format')
        require(type(archive.get('parts')) is list and archive['parts'], 'archive parts required')
        seen = set()
        for part in archive['parts']:
            require(type(part) is dict and set(part) == {'path', 'size', 'sha256'}, 'part descriptor fields')
            identity(part)
            name = safe_name(part['path'])
            require(name not in seen, 'repeated part in archive')
            seen.add(name)
            source_path(name)
        require(sum(p['size'] for p in archive['parts']) == archive['size'], 'part sizes do not total archive')
    index = manifest.get('logical_index')
    require(type(index) is dict and set(index) == {'path', 'size', 'sha256'}, 'logical index descriptor')
    identity(index)
    require(index['path'] == 'logical-files.jsonl', 'logical index filename')
    index_path = source_path(index['path'])
    require(pin(index_path) == identity(index), 'logical index identity mismatch')
    rows, paths, grouped = [], set(), {label: {} for label in archives}
    with index_path.open('rb') as stream:
        for line in stream:
            row = decode(line)
            require(type(row) is dict and set(row) == FIELDS, 'logical row exact fields')
            identity(row)
            name = safe_name(row['path'])
            require(name.startswith('workspace/') and name not in paths, 'duplicate or nonworkspace destination')
            require(type(row['mode']) is int and row['mode'] in (420, 493)
                    and type(row['active']) is bool, 'mode/active type')
            label = row['archive']
            require(type(label) is str and label in archives, 'unknown row archive')
            member = safe_name(row['member'])
            group = grouped[label].setdefault(member, [])
            require(not group or identity(group[0]) == identity(row), 'conflicting source member identities')
            group.append(row)
            paths.add(name)
            rows.append(row)
    require(rows and pin(index_path) == identity(index), 'empty or changed logical index')
    links = manifest.get('symlinks', [])
    require(type(links) is list, 'symlink whitelist list')
    link_paths = set()
    for link in links:
        require(type(link) is dict and set(link) == {'path', 'target', 'active'}, 'link descriptor fields')
        name = safe_name(link['path'])
        require(name.startswith('workspace/') and name not in paths and name not in link_paths,
                'duplicate link/file path')
        require(type(link['active']) is bool, 'link active type')
        # This whitelist describes runtime libraries only, never old project/pool links.
        require(not any('pool' in part.lower() or 'project' in part.lower()
                        for part in PurePosixPath(name).parts), 'project/pool links forbidden')
        link_target(name, link['target'])
        link_paths.add(name)
    all_paths = paths | link_paths
    for name in all_paths:
        require(not any(p.as_posix() in all_paths for p in PurePosixPath(name).parents
                        if p.as_posix() != '.'), 'file/link path is another entry ancestor')
    link_map = {r['path']: link_target(r['path'], r['target']) for r in links}
    for name, target in link_map.items():
        require(target in all_paths, 'unlisted link target')
        require(not any('pool' in part.lower() or 'project' in part.lower()
                        for part in PurePosixPath(target).parts), 'project/pool link target forbidden')
        seen = {name}
        while target in link_map:
            require(target not in seen, 'cyclic runtime link whitelist')
            seen.add(target)
            target = link_map[target]
        require(target in paths, 'link chain must end in a logical regular file')
    return manifest, rows, grouped, {'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


@contextmanager
def joined_archive(label, archive):
    with tempfile.TemporaryDirectory(prefix='github-checkpoint-') as temporary:
        joined = Path(temporary) / 'archive'
        whole, total = hashlib.sha256(), 0
        with joined.open('xb') as output:
            for part in archive['parts']:
                h, count = hashlib.sha256(), 0
                with source_path(part['path']).open('rb') as stream:
                    while block := stream.read(CHUNK):
                        count += len(block)
                        require(count <= part['size'], 'part exceeds declared size: ' + label)
                        h.update(block)
                        whole.update(block)
                        total += len(block)
                        output.write(block)
                require({'size': count, 'sha256': h.hexdigest()} == identity(part), 'part identity mismatch: ' + label)
        require({'size': total, 'sha256': whole.hexdigest()} == identity(archive), 'whole archive mismatch: ' + label)
        yield joined


def consume(stream, size, member, expected, selected, destination, materialized):
    references = expected.get(member, [])
    require(not references or all(r['size'] == size for r in references), 'member advertised size mismatch: ' + member)
    h, count = hashlib.sha256(), 0
    with ExitStack() as stack:
        sinks = []
        for row in references:
            if row['path'] in selected and destination is not None:
                path = no_links(destination / row['path'])
                path.parent.mkdir(parents=True, exist_ok=True)
                no_links(path)
                sinks.append(stack.enter_context(path.open('xb')))
        while block := stream.read(CHUNK):
            count += len(block)
            require(count <= size, 'member exceeds advertised size')
            h.update(block)
            for sink in sinks:
                sink.write(block)
        value = {'size': count, 'sha256': h.hexdigest()}
        require(count == size, 'truncated member: ' + member)
        for row in references:
            require(value == identity(row), 'logical file SHA mismatch: ' + row['path'])
            if row['path'] in selected and destination is not None:
                materialized[row['path']] = identity(row)
        for sink in sinks:
            sink.flush()
            os.fsync(sink.fileno())


def tar_members(stream, mode, expected, selected, destination, materialized):
    seen = set()
    with tarfile.open(fileobj=stream, mode=mode) as archive:
        for member in archive:
            name = member.name.rstrip('/') if member.isdir() else member.name
            safe_name(name)
            require(name not in seen, 'duplicate tar member: ' + name)
            seen.add(name)
            if member.isdir():
                require(name not in expected, 'logical member is directory')
                continue
            require(member.isfile(), 'archive links/special files are not restored')
            with archive.extractfile(member) as source:
                consume(source, member.size, name, expected, selected, destination, materialized)
    require(set(expected) <= seen, 'logical members missing from tar')
    return len(seen)


def scan_archive(path, archive, expected, selected, destination, materialized):
    if archive['format'] == 'tar_xz':
        with path.open('rb') as stream:
            return tar_members(stream, 'r|xz', expected, selected, destination, materialized)
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        require(len(infos) == len({i.filename for i in infos}), 'duplicate ZIP members')
        for info in infos:
            require(info.filename == info.orig_filename and not info.flag_bits & 1, 'normalized/encrypted ZIP member')
            safe_name(info.filename.rstrip('/') if info.is_dir() else info.filename)
            kind = stat.S_IFMT(info.external_attr >> 16)
            require(kind in (0, stat.S_IFREG, stat.S_IFDIR), 'ZIP link/special member')
        if archive['format'] == 'compact_zip_tar_xz':
            require(set(z.namelist()) == {'HANDOVER-README.md', 'HANDOVER-INDEX.json', 'HANDOVER-MANIFEST.json',
                                         'restore_handover.py', 'PAYLOAD.tar.xz'}, 'compact exact five members')
            # Outer support and complete compressed payload CRC are verified independently.
            for info in infos:
                with z.open(info) as stream:
                    require(digest(stream)['size'] == info.file_size, 'compact outer member size')
            with z.open('PAYLOAD.tar.xz') as stream:
                return tar_members(stream, 'r|xz', expected, selected, destination, materialized)
        seen = set()
        for info in infos:
            name = info.filename.rstrip('/') if info.is_dir() else info.filename
            seen.add(name)
            if info.is_dir():
                require(name not in expected, 'logical member is ZIP directory')
                with z.open(info) as stream:
                    require(digest(stream)['size'] == 0, 'nonempty ZIP directory')
                continue
            with z.open(info) as stream:
                consume(stream, info.file_size, name, expected, selected, destination, materialized)
        require(set(expected) <= seen, 'logical members missing from ZIP')
        return len(seen)


def restore(destination, profile, verify_only):
    destination = no_links(destination)
    require(not os.path.lexists(destination), 'destination must be new; partial output is never overwritten')
    require(destination.parent.is_dir(), 'destination parent must already exist')
    manifest, rows, grouped, manifest_pin = load_contract()
    selected = {r['path'] for r in rows if profile == 'full' or r['active']}
    selected_links = [r for r in manifest.get('symlinks', []) if profile == 'full' or r['active']]
    selected_names = selected | {r['path'] for r in selected_links}
    for row in selected_links:
        require(link_target(row['path'], row['target']) in selected_names, 'link target excluded by profile')
    if not verify_only:
        destination.mkdir()
    materialized, archives_checked = {}, {}
    for label, archive in manifest['archives'].items():
        with joined_archive(label, archive) as joined:
            count = scan_archive(joined, archive, grouped[label], selected,
                                 None if verify_only else destination, materialized)
        archives_checked[label] = {'identity': identity(archive), 'members_read': count}
    if not verify_only:
        require(set(materialized) == selected, 'physical output set mismatch')
        row_map = {r['path']: r for r in rows}
        for name, want in materialized.items():
            path = destination / name
            require(pin(path) == want, 'first physical readback mismatch')
            path.chmod(row_map[name]['mode'])
        for name, want in materialized.items():
            path = destination / name
            require(pin(path) == want and stat.S_IMODE(path.stat().st_mode) == row_map[name]['mode'],
                    'second physical readback/mode mismatch')
        for link in selected_links:
            path = no_links(destination / link['path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            no_links(path)
            require(not os.path.lexists(path), 'link destination exists')
            path.symlink_to(link['target'])
        for link in selected_links:
            path = destination / link['path']
            require(path.is_symlink() and os.readlink(path) == link['target'], 'link readback mismatch')
            resolved = path.resolve(strict=True)
            require(resolved.is_relative_to(destination) and resolved.is_file(), 'link cycle/dangling/outside target')
    receipt = dict(schema='github-workspace-checkpoint-receipt/1', status='ALL_ARCHIVES_AND_LOGICAL_FILES_VERIFIED',
                   profile=profile, verify_only=verify_only, full_physical_restore=profile == 'full' and not verify_only,
                   fresh_OS_verified=False, manifest=manifest_pin, logical_index=manifest['logical_index'],
                   verified_logical_files=len(rows), verified_logical_bytes=sum(r['size'] for r in rows),
                   archives=archives_checked, physical_files=len(materialized),
                   physical_bytes=sum(v['size'] for v in materialized.values()),
                   physical_readback_passes=0 if verify_only else 2,
                   symlinks_materialized=0 if verify_only else len(selected_links),
                   destination=str(destination), relocation_map={'/workspace': str(destination / 'workspace')},
                   checkpoint_state={k: manifest[k] for k in ('state', 'status', 'formal_production', 'candidate_status')
                                     if k in manifest}, checkpoint_contents_executed=0, models=0, native=0, training=0)
    require(pin(ROOT / 'MANIFEST.json') == manifest_pin, 'manifest changed during restoration')
    require(pin(source_path(manifest['logical_index']['path'])) == identity(manifest['logical_index']),
            'logical index changed during restoration')
    if not verify_only:
        with (destination / 'RECOVERY-RECEIPT.json').open('x') as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--profile', choices=('full', 'active'), default='full')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(restore(args.destination, args.profile, args.verify_only), indent=2, sort_keys=True))
    except Exception as error:
        print(json.dumps(dict(status='INCOMPLETE_RECOVERY_REJECTED', error=str(error),
                              partial_destination_preserved=True, checkpoint_contents_executed=0)), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
