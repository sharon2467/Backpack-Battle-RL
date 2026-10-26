extends Weapon

const activationParticles = preload("res://Items/Particles/TorchActivationParticles.tscn")
onready var permDamBonus = getP2()

func onCombatStart():
	NativeRandomObserver.entry("Items/BurningTorch.gd::onCombatStart", self, {})
	giveHeat(getP1())
	activate(null, false)
	NativeRandomObserver.leave("Items/BurningTorch.gd::onCombatStart", self, null, "return_implicit")

func onPreDealDamage_early(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/BurningTorch.gd::onPreDealDamage_early", self, {"damageRes": damageRes})
	if damageRes.hasHit() and rollChance():
		addBonusDamage(permDamBonus)
		var particles = ObjectPool.particleOneShot(activationParticles, sprite)
		particles.scale = Vector2(1.2, 1.2)
	NativeRandomObserver.leave("Items/BurningTorch.gd::onPreDealDamage_early", self, null, "return_implicit")

