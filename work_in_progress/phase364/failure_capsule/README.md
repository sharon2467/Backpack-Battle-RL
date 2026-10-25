# Restore this standalone failure capsule

Run from the GitHub clone after main archival354 restoration. RECOVERED is that existing restoration directory. The command checks ZIP/every296member before and after additive extraction, refuses differing files/links, runs no archived code and does not create a Game or modify a pool.

```sh
export RECOVERED=/absolute/path/to/NEW-recovered-directory
python3 -I -B -S - <<'PY'
from pathlib import Path, PurePosixPath
import hashlib, json, os, stat, zipfile
p = Path("work_in_progress/phase364/failure_capsule")
m = json.loads((p / "CAPSULE.json").read_text())
z = p / m["archive"]
assert z.stat().st_size == m["archive_size"]
assert hashlib.sha256(z.read_bytes()).hexdigest() == m["archive_sha256"]
root = Path(os.environ["RECOVERED"]).absolute() / "workspace/python-original-engine/repo"
assert root.is_dir() and root.resolve() == root
with zipfile.ZipFile(z) as archive:
    assert archive.testzip() is None
    infos = archive.infolist()
    assert len(infos) == len({i.filename for i in infos}) == m["file_count"]
    assert {i.filename for i in infos} == set(m["files"])
    for info in infos:
        name = info.filename
        rel = PurePosixPath(name)
        assert not rel.is_absolute() and str(rel) == name
        assert ".." not in rel.parts and rel.parts[:2] == ("data", "phase364-first-native-failure")
        assert not stat.S_ISLNK(info.external_attr >> 16)
        value = archive.read(info)
        want = m["files"][name]
        assert len(value) == want["size"] and hashlib.sha256(value).hexdigest() == want["sha256"]
        target = root.joinpath(*rel.parts)
        assert not any(q.is_symlink() for q in (target, *target.parents))
        if target.exists():
            assert target.is_file() and target.read_bytes() == value
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(value)
        assert target.read_bytes() == value
print("PASS failure-capsule296members; no code execution or pool changes")
PY
cp -rn work_in_progress/phase364/independent_diagnosis/repo/. "$RECOVERED/workspace/python-original-engine/repo/"
cp -rn work_in_progress/phase364/recovery_design/repo/. "$RECOVERED/workspace/python-original-engine/repo/"
```

The mainREADME supplement loop does not implicitly extract ZIPs. This capsule contains private-baseline identity metadata and an overlay; baseline credential sanitization remains explicit. This is not freshOS/private-credential-identical oracle recovery, READY or attempt02 authorization.
