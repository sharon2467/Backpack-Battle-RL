# Remote-clone recovery verification

Result: **PASS**. Machine-readable details are in [validation.json](validation.json).

The payload was first published in commit `72c1e07b902354d7bc877bc8a6ddea15285cb932`. A new directory was cloned over HTTPS from GitHub, with `--no-local`, no reference repository and no object alternates. The checker was fetched from the same remote at tested commit `e419220e09232d2fcce05d6d140618cc8c807aa6`. No old workspace checkpoint, source tree or cache supplied the recovery data.

| Check | Actual result |
| --- | --- |
| All 27 part hashes and 10 whole-archive identities | PASS |
| Complete logical index | 47,931 files / 10,308,632,695 bytes streamed and SHA verified |
| Actual active working-set recovery | 20,452 regular files / 1,459,591,303 bytes; two physical readback passes |
| Explicit runtime links | 18 safe relative links reconstructed and checked |
| Current formal runtime | All 15 source identities match; 68 admitted default items |
| Independent candidate FINAL evidence | All 300 owned files / 46,361,052 bytes match |
| Unfinished promotion files | All 4 owned files / 25,304 bytes match; still PARTIAL |
| Prepared future portable source | All 27 owned files / 636,097 bytes match; planned run still not performed |
| Restored Python CLI, seed 32001 | 681 events, 842 random inputs, 2340 frames, winner O |
| Full CLI output | 2,440,177 bytes; SHA `93c720f4d3162c85a1d00f148f14861554217abb0ea48a96fab93b83e34ce079`, byte-identical to the retained historical example |
| Python payload-read boundary | Recovered15/example + standard library + own output only; no blocked attempts or old-workspace payload reads |
| Restored official runtime | Version probe returns `3.6.2.stable.custom_build` |
| Development / original battles / training / promotion | Not resumed |

This is an **actual isolated-directory active restore on the existing host**, plus a complete archive/logical-hash traversal. It is not a full physical materialization of the 10.31GB history, and not a fresh-OS/cloud test. The occupied host had insufficient spare disk for another complete historical tree; `--profile full` is supplied for an empty destination with at least12GB free. No unapproved new cloud environment was created.

The engineering files and original offline materials required for continuation are all in this repository. The old-cloud-required file list for that supported continuation is **empty**. Host OS/system libraries remain a documented platform dependency; fixed runtime/dependency artifacts and official versioned sources are provided. Online service credentials are deliberately not restored.

Read [README.md](README.md) for the exact restore and entry-point commands, the documented two API redactions/two encrypted-copy exclusions, and the absolute-path relocation rules. Formal68 and unpromoted candidate75 remain accurately distinguished. The migration stays paused until the user explicitly resumes it.
