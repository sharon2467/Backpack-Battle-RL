# Phase435 EMPTY preparation v2: two bounded harness repairs

## 1. Requirements

Preserve original sealed EMPTY preparation; create successor only. No native execution. Change only own-process-group cleanup and G09 first-error stability assertion.434Source/otherprojectfixtures/expected19subcases56calls unchanged.

## 2. Design

Finally always TERM the Popen start_new_session group even if leader exited, allow a short grace then KILL the same group. Bound cleanup to a19.5s launch-relative deadline beneath20s outer limit; do not claim unrelated processes/escaped sessions or all descendants reaped. Limited numeric/proc stat observations report only own pgrp/session live/zombie members. G09 checks codeNIL/primitive first latch after subsequent rawsnapshot error.

## 3. Realize

Copy only prior owned EMPTY fixture/evidence into unique v2 directory. Keep exact Source bodies and expected bytes; add bounded stat-observer/cleanup to launcher and primitive/code assertions to existing G09 ok expression. Compile launcher source without calling it. Seal identity/diff report and ordinary owner. No launch or oldcontrol replay.

## 4. Acceptance Criteria / Tests

Root independently reads successor owner before once execution release. Static inverse of two harness changes must recover previous launcher/G09 line; all otherprojectresources and expected byteidentical. Record runtimecleanup limited scope rather than universal reaping; Player inherited fixture is tested prospectively, Opponent not directly exercised.0native currently;6/82 unchanged.
