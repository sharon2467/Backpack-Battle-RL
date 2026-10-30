extends Weapon

const thornParticlesScene = preload("res://Items/Exclusive/Particles/ThornShortbowParticles.tscn")

func onDealtDamage(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/Exclusive/ThornShortbow.gd::onDealtDamage", self, {"damageRes": damageRes})
	if damageRes.hasHit() and rollChance():
		giveSpikes(1, damageRes.event)
		ObjectPool.particleOneShot(thornParticlesScene, self)
	NativeRandomObserver.leave("Items/Exclusive/ThornShortbow.gd::onDealtDamage", self, null, "return_implicit")

