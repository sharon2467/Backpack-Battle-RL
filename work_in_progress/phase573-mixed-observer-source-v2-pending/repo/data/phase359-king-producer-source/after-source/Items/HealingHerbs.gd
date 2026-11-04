extends Item

func onCombatStart():
	NativeRandomObserver.entry("Items/HealingHerbs.gd::onCombatStart", self, {})
	giveRegeneration(getP1())
	consume()
	NativeRandomObserver.leave("Items/HealingHerbs.gd::onCombatStart", self, null, "return_implicit")

