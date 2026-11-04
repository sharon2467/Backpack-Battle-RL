extends Item

func onCombatStart():
	NativeRandomObserver.entry("Items/BloodAmulet.gd::onCombatStart", self, {})
	giveVampirism(getP1())
	giveMaxHealth()
	activate()
	NativeRandomObserver.leave("Items/BloodAmulet.gd::onCombatStart", self, null, "return_implicit")

