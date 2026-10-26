extends Weapon

const poisonParticlesScene = preload("res://Items/Exclusive/Particles/PoisonShortbowParticles.tscn")

onready var poison: int = getP1()

func onPreDealDamage_early(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/Exclusive/PoisonShortbow.gd::onPreDealDamage_early", self, {"damageRes": damageRes})
	if damageRes.hasHit() and rollChance():
		var randomDebuff = Util.pickRandomElement(Game.getDebuffs(), NativeRandomObserver.shortbow_debuff_label(self))
		if randomDebuff == Game.EventType.Poison:
			inflictPoison(poison + 1)
		else:
			inflictPoison(poison)
			giveStacks(opponent(), randomDebuff, 1)
		ObjectPool.particleOneShot(poisonParticlesScene, self)
	NativeRandomObserver.leave("Items/Exclusive/PoisonShortbow.gd::onPreDealDamage_early", self, null, "return_implicit")

