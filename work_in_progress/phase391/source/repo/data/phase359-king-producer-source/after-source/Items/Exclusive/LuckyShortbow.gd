extends Weapon

const luckyParticlesScene = preload("res://Items/Exclusive/Particles/LuckyShortbowParticles.tscn")

func onPreDealDamage_early(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/Exclusive/LuckyShortbow.gd::onPreDealDamage_early", self, {"damageRes": damageRes})
	if damageRes.hasHit() and rollChance():
		giveLucky(1)
		ObjectPool.particleOneShot(luckyParticlesScene, self)
	NativeRandomObserver.leave("Items/Exclusive/LuckyShortbow.gd::onPreDealDamage_early", self, null, "return_implicit")

