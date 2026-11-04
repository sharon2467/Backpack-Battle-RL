extends Weapon

func canAffect(item):
	return item.canBeEmpowered()

func onCombatStart():
	NativeRandomObserver.entry("Items/HeroSword.gd::onCombatStart", self, {})
	for item in getAffectedItems():
		item.addBonusDamage(getP1())
	activate(null, false, false, ActivationAni.Jump)
	NativeRandomObserver.leave("Items/HeroSword.gd::onCombatStart", self, null, "return_implicit")

