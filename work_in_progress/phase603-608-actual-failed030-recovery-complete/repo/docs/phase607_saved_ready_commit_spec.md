# Phase607 — separate saved READY state commit

## 1. Requirements
After605 actual files restoration and606 independent full physical readback PASS,restore only the exact saved pre-busy state bytes/mode/mtime. Preserve the genuine failed state andall run/evidence artifacts. No newOriginal,model,source change orphysical regression run.

## 2. Design
The independent reader already compared baseline/project/staged/priorbundle/driver andretained/preimages under the original exclusive lock. Its two process checks report no readable active matches,with24 inspection gaps andno global completeness claim. This commit relies on that accepted task-scoped check,settled owned process groups andno other active role writing this pool;it does not remove orweaken any check. Reacquire the same ordinary lock,verify failedstate identity+mode+mtime andreadback/source/request identities,then atomically replace state fromthe actual controls image0.

## 3. Realize
Verify606 final/actual reader result/owners,605 result,actualcontrols manifest andsaved0. Require currentstate still246B/SHA698998f49b9bbe4dba03693016c3b35aca6d7a7129278aa187a77ba5ad7bc6ed andmetadata fixed601 authority. Require saved0 ready/run actual027,hash/mode/mtime equalcontrols. Under exclusive `.lock`,recheck,create a unique adjacent temporary file,write+fsync,chmod/utime tosaved values,recheck failedpreimage,replace andfsync pooldirectory. Record single state write. Tiny stable physical readback must match saved image;independent judge then reads that actualstate. No PENDING fabrication orrepeatfullinventory.

## 4. Acceptance
Exact saved READY bytes4243B/SHAe92ce49332709fe5cf71665b8add0f2ee47acaff4a04c5318f9d06ff0a543431,mode0600,mtime1793007805399408434 andrun027 must be restored. Source/evidence unchanged. Unknown/newwriter oridentity mismatch stops before replace;preserve error andtemporary image. This is pool recovery only,not Original030 capture acceptance orsupport promotion.
