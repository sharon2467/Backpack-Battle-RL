# Phase439 Timer64 independent static review — first finding

Reviewed module `tests/phase439_timer_initial_overlay.py`,24686 bytes,SHA256 `e64c7ba004bd058718907ab1115949c776bb199c59ee71d14c9659e1b2dc1e69`; owner SHA256 `5ec3260026771303feb5b3def12c8eacbc1c62272623228c2da88de72ff3c161`. Read its spec/context/receiver manifest/API, native review and G02 receipt bindings, existing scene construction and active observer getter code. No module import, control process, actual439 overlay or native execution occurred.

**PAUSE BEFORE FUNCTIONAL/ACTUAL EXECUTION: concrete external-animation pin gap.** This is a small Source-domain correction, not a counterexample observed in the saved runtime or a demand to audit all UI.

Core/Player.tscn:10-17 directly declares eight external Animation resources;1658-1667 installs them on the actual Character AnimationPlayer. The pinned Character `_ready` plays StartOnTitle for P, and other lifecycle methods use this animation player. Thus this is a named active receiver/owner route, not arbitrary unreferenced data. Current439 context pins815 .gd,19 .tscn scene leaves,Main.tscn and selected other sources, but none of these eight external .tres leaves.

The source validation verifies only its descriptor groups and the .gd set (module145-169). Altering an external animation's path/type/keys to write a child Timer process_mode or invoke a Node internal-flag setter would leave every current descriptor unchanged; the promised Source drift guard would miss it. No such file was modified and no exploit/control was executed. Current contents of all eight have been read: tracks are value tracks on visual position/visibility/emitting/scale/modulate/rotation properties; none targets Timer mode/flags/script or invokes a method. Their checked bytes support the intended bounded domain if pinned.

Minimum correction: preserve v1; add precisely these eight .tres descriptors to a new immutable context and source-owner, with the current finite no-Timer-writer finding, and include an external-animation hash-drift negative control. No need to reopen an unrelated resource forest. Main/Character/Opponent contain no direct ext_resource of type Animation in the finite lookup; their local tracks are already covered by their .tscn pins.

| CharacterClasses/Animations leaf | Current SHA256 |
| --- | --- |
| CombatToTitle.tres | cc358ffed6ff991e95ba295f686924ec32231b5bd90d0cc3df3f5086acefd330 |
| StartInCombat.tres | 7c17925415af5cf342d5b411d535daaa479921cd2b4de2aa3610ffa5cd18e774 |
| EnterCombatFromShop.tres | e7d6aaa2f5ed8776718fdc14f7a4e5ae9401a8fccd72245b3e99e21d879ba371 |
| StartInShop.tres | a8bd27bd2e8748ca7b39e6cb55fd84345a60aa8d1e31f494e26a25e9521c942a |
| StartOnTitle.tres | 06b107f22e8b5a88efaae10c9174e7d3a7f0bf21f06a81181bd1773a0d28e4b7 |
| RESET.tres | 2bbeef3edc3d1d86b21cc2e2b13fbf93dcfd481c382a15dccc1dd6f36d1659ef |
| EnterShopFromCombat.tres | 8e94bb8f9c8d6b730ffdfbcfd101475945706ef962cd1b9d7001b7e3fb906a8e |
| EnterShopFromTitle.tres | a1e62e47cd7abcd68bf26a0a660de0aa3c0a97067c95457193b271f0cbfae1fb |

Other inspected design points remain sound pending controls: exact438 canonical fingerprint protects10 earlier derivations/exclusions;64 target keys are explicit; all19 existing DIRECT public fields and refs are joined to raw same-cut snapshots; strict bool flags/int mode and global node identity checks reject malformed/aliased representations; Buff44 has full duplicate Timer/Character/stack joins; remaining20 use8 Character children plus2 Main fatigue children across two cuts. Observer node_state188-200 and timer_state202-208 invoke actual native getters on these source-closed plain Timer receivers. Scene bindings show no local Timer script and no Player/Opponent replacement of these child nodes.

G02 remains the accepted ordinary builtin native attribution domain, not arbitrary native-injection or bit-exact custom build proof. The current snapshot cannot detect an earlier illegal mode or external flag write; exclusion of those histories comes from the pinned finite Source domain. Public time_left/stopped remain consistency evidence only. The eight-resource gap prevents certifying that domain in this v1 adapter until corrected; it does not invalidate the kernel theorem.

438 accepted Character8 is not replayed or modified. The same omitted leaf-pin coverage is now disclosed as a limitation of its prior source-resource hash coverage; current finite inspection finds no added writer. This record does not relabel newly read .tres bytes as historical observations or reconstructed reports as archived originals. Root determines any historical receipt addendum. Current accepted baseline remains1289DIRECT+10SOURCE_DERIVED+64MISSING, with116 exclusions and King/fullschema/inputbuild/model gates unchanged.
