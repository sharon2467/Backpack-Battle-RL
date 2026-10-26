# First-idle scheduling control triage

The frozen385capture has2288physics and286idle control rows, each idle preceded by8physics, with continuous frame counters. The Source producer/collector/schema require exactly twofuturephysics aftercleanup. This first Source/control diagnosis did not read the opaque cleanup stamp and preserved that uncertainty. It did not infer logging overhead or full input/model acceptance. Copy review_evidence/repo additively; the original failed capture stays invalid and no replay was run.
