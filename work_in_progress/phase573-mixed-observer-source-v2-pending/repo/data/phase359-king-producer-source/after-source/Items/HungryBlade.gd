extends Weapon

const activationParticles = preload("res://Items/Particles/HungryBladeActivationParticles.tscn")

onready var vampirism: = int(getP1())
onready var regenNeeded: = int(getP2())
onready var vampirismForRegen: = int(getP3())

func onPrepare():
	NativeRandomObserver.entry("Items/HungryBlade.gd::onPrepare", self, {})
	connectForCombat(character(), "character_vampirism_changed", "onVampirismChanged")
	NativeRandomObserver.leave("Items/HungryBlade.gd::onPrepare", self, null, "return_implicit")

func onCombatStart():
	NativeRandomObserver.entry("Items/HungryBlade.gd::onCombatStart", self, {})
	giveVampirism(vampirism)
	activate(null, false, false, ActivationAni.Jump)
	NativeRandomObserver.leave("Items/HungryBlade.gd::onCombatStart", self, null, "return_implicit")

func onVampirismChanged(amount, _event):
	NativeRandomObserver.entry("Items/HungryBlade.gd::onVampirismChanged", self, {"amount": amount, "_event": _event})
	addMaxDamage(amount)
	NativeRandomObserver.leave("Items/HungryBlade.gd::onVampirismChanged", self, null, "return_implicit")

func onPreDealDamage_early(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/HungryBlade.gd::onPreDealDamage_early", self, {"damageRes": damageRes})
	if damageRes.hasHit():
		var numRegen = character().getRegeneration()
		if numRegen >= regenNeeded:
			var event = useRegeneration(regenNeeded)
			giveVampirism(vampirismForRegen, event)
			ObjectPool.particleOneShot(activationParticles, sprite)
	NativeRandomObserver.leave("Items/HungryBlade.gd::onPreDealDamage_early", self, null, "return_implicit")

