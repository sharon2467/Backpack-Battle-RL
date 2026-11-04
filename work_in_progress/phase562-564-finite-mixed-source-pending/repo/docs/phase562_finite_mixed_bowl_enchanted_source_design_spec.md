# Phase562 — finite162+385+231 Source integration design

## 1. Requirements

Design only from accepted558 exact15 Source (portable560 copies those bytes). Permit the already implemented Bowl162, Enchanted Weapons385 and Wolpertinger231 families to coexist in a finite explicit Source layout. Add no item/API/registry entry, modifier framework or caller allowlist. Catalog remains84/formal75. No implementation, compilation, candidate/helper import, test/model, Expected, Native, UI, pool or old battle execution. Existing single-caller/absent-caller domains, Source/packages and all evidence remain immutable in this design.

Target implementation is **one engine file changed, fourteen files exact** (within Root's at-most-two-file limit). All existing business/prepare/cache/modifier/trigger/attack/Activation/queue/history/Timer/FrameDriver/RNG bodies remain byte-exact. Only fixed admission constants and the two existing fixture validators need change if the independent563 review accepts the closures below.

## 2. Design — actual predicate and interaction closure

### Finite branch, not general combination admission

When both162 and385 occur anywhere in the complete fixture, use the fixed union12 `{1,5,11,14,22,32,162,164,231,233,234,385}`. Keep class0/default/noGems/noKing/no rage, at most one162 and one385 **per side**. The caller presence is computed from actual typed item entries, not a request BOOL. Callers may be same-side or opposing-side; each actual modifier remains same-side. A natural integration case must include231 and both callers; the admission set does not invent an additional mandatory-Wolper flag.

No162: preserve previous551/83-registry admission and385's nine-ID branch.162 alone: preserve its seven-ID branch.385 alone: preserve its nine-ID branch. Neither: preserve the accepted pre-caller admission. Current actual registry stays84 in every branch. Existing formal/CLI/batch/Squirrel/King gates and experimental API names stay. Unknown IDs/Whelps/Gooberts/other Skill modifiers are rejected, not classified false or admitted by membership in broad formal75.

### Newly crossed predicates are actually closed

Item.hasAttackEffect4126–4129 is the OR of has_method flags500–502 for own early/late/dealt overrides. Bowl162 extends Food→Item; Banana5 extends Food→Item; Squirrel164 extends ForestFriend→Item. Their complete direct parent chains contain none of those three overrides. Therefore **162/164/5 are false for385**, not merely unsupported defaults. Existing231 is likewise a Pet with no attack-effect override.385 extends Item, and CSV385 Type.Skill/empty extraTypes supplies no Pet/Food flag; its14-line script adds no types or own attack hook. Under the closed default descriptors it is **not a Bowl global Pet or Food-star target**. No dynamic type/script transformation, gems or custom resource override is part of this input domain.

| IDs | Pet for Bowl global | Food predicate category | Own attack effect for385 |
| --- | --- | --- | --- |
| 164,231 | true | false | false |
| 5,22,162 | false | true | false |
| 14,32,233,234 | false | false | true (already selected receiver proofs) |
| 1,11,385 | false | false | false |

Bowl's **global** actual inventory loop gives164/2310.2 double_activation_chance, regardless of stars. Its spatial Food cache gives speed only to5/22/different descriptor Food; same162 is excluded. Squirrel's Pet OR Food cache admits the same Pet/Food categories as before, and rejects the newly neighboring four weapons/385. Wolper remains Pet-only.385's existing ordered spatial cache admits only14/32/233/234 and ignores the newly permitted162/164/5. Existing geometry/self/bag/dedup and cell blocking algorithms already iterate real items and require no new rule; e.g. a Food occupying a Spear star blocks that cell in the existing empty-cell calculation rather than becoming an attack-effect receiver.

### Modifier lifecycle and real combined business chain

The actual558 validators/setters use **different sources and different real fields**:162/global-Pet→double_activation_chance0/.2;385/cached-four-weapons→double_attack_effect_chance0/.25. No item in this union receives both positive modifiers. Both own target/source identity, exact metadata and prepared-cache lifetime checks already exist. Each setter loop is callback/RNG-free, completes before its own expected check, and no generic check runs during partial current-source application. A Bowl-first/Skill-first/receiver-first preparation permutation cannot contaminate the other expected value. Later receiver prepare resets neither field. End-of-prepare checks and consumption guards remain observational; no value is supplied, repaired or clamped by admission.

The combined interaction is more than an allowlist change: existing162 random2 flush/385 least1/231 least3 can gain Mana and other own buffs, invoking231's actual registered beneficial listeners and live stamina regeneration/history. Magic Staff32's repeated early Mana use emits actual negative deltas, can exhaust Mana between its two own callbacks, and feeds the same231 listener while preserving null early-use parents and current global event_num. Repeated Spear removes Block, which is **excluded** from231 beneficial callback categories; do not misreport Block loss as Wolper feedback. Thorn's Spikes grants and Lucky's Lucky grants use their original own hook/parent/timing and can feed231. Banana stamina refill and Food speed change future eligibility/timing through existing character/cooldown code.

Bowl extra-Pet dispatch still runs complete first effect/Activation/pitch before its positive flip; success adds at most the second actual effect without extra cooldown adjustment.385 effect count still flips once before accuracy, repeats only the appropriate own hooks and retains the independent Shortbow item chance stream. Different labels/chronologies remain separate in one actual shared Source RNG audit; no duplicated/reused random return, sorted log or post-result alignment. Changed Mana/buff/stamina values may legitimately change subsequent primitive bounds/counts and callback branches. No fixed future count/winner/HIT is predicted.

All of these paths are already production code in558; their positive individual and shared state semantics were controlled in546/553/559 and fixed029 where applicable. This inspection found **no additional business algorithm gap in the selected union**, so implementing a new mixed kernel or rerunning those old cases would be unnecessary. New interaction controls and one new case are still required before claiming mixed Source acceptance.

## 3. Realize — minimum future delta

* Add one immutable `MIXED_BOWL_ENCHANTED_FIXTURE_IDS=frozenset({...12...})` constant. Keep existing BOWL_FIXTURE_IDS/ENCHANTED_FIXTURE_IDS and receiver constants exact; do not extend their standalone domains or Pet/Weapon predicates.
* `validate_bowl_fixture`: keep initial absent162 return and original single162 branch. Before that original branch, when actual entries also contain385, validate class0/all union12/maxone162 per side and return. No geometry/default/UID rules are bypassed: full validate_fixture already checks them. The other existing validator enforces maxone385.
* `validate_enchanted_fixture`: symmetric mixed branch only when actual162 also exists, class0/all union12/maxone385 per side; otherwise original branch/error behavior stays. Production full validate_fixture calls both, so both caller multiplicities are enforced even across sides. Direct tests of a single private validator must not mistake its own-caller bound for complete validation.
* No new public function, runtime flag, DTO field, synthetic profile, metadata entry or headless edit. Existing initialize_experimental_nonking already admits both catalog IDs into shared validation and will then accept the finite mixed shape. Legacy initialize/CLI/batch/Squirrel/King remain exact. Catalog84 does not change.
* All other fifteen-file Source bytes/functions are conserved. The future Source assembly should record exact old branch slices/inverse and every unmodified function, compile-only/freeze/owner before independent controls. A real new discrepancy from563 or those controls must be reported rather than hidden by a weaker predicate.

## 4. Acceptance, bounded cost and evidence limits

Independent563 first reviews only this Source design/pins. Later propose at most eight presealed directed groups: (1) all newly crossed predicates and cache target sets/order, spatial Food versus global Pet, unaffected opposite side; (2) same-side/opposite-side caller presence, typed union12, duplicates/class/gems/unknown rejection, and unchanged standalone/absent gates; (3) representative preparation permutations, both fields0/.2/.25 and no resets/partial observation; (4) Bowl random2 flush and Skill/Wolper least gains into actual231 listener/current histories, excluding Block/debuff; (5) repeated Magic Staff use/exhaustion after a controlled gain, exact negative feedback and original parent/metric order; (6) Thorn/Lucky independent own rolls and positive feedback plus Spear Block loss without false231 feedback; (7) one mixed Pet trigger with real pitch→extra roll→effect and shared primitive order, existing limiter/ended/speed-ledger semantics conserved; (8) no counter/geometry/registry inflation, unchanged Source output snapshots/Timer/ordinary order and old-gate finite checks. Use actual production helpers with predeclared synthetic prestates, not a second expected algorithm or full old battles.

At most one new Source layout/seed, fixed before execution, includes162+385+231 plus selected Food/Pet/weapon representatives in actual cells. Report separate natural HIT/NOT_HIT for both modifiers, Mana/use→regen, extra Pet feedback and speed budget; components cover missing natural distinctions. No seed tuning/Expected input filling, no546/553/559 repeat. Code cost: one fixed constant and two short admission branches, expected one changed file/fourteen exact, no runtime dependency. No new Source package is necessary until acceptance.

Existing record029 does not contain162/231/385 and cannot provide this layout's identities, clocks/caches or primitive returns. Individual Source evidence is not a new joint Native record or all-layout proof. Future representative Original capture may benefit from this union, but requires separate acquisition/canAdd/resource/space and actual lawful INPUT/observer/caller/initial/clock bindings, then sealed model before strict comparison. No install/capture/cleanup is authorized here; last known disk remains below5905580032 and a future attempt requires its own fresh gate. Native seed law, arbitrary receiver combinations/overlapping callers and all75×modifier coverage remain unclaimed.
