extends Item

func onPreCombatStart():
	NativeRandomObserver.entry("Items/LeatherArmor.gd::onPreCombatStart", self, {})
	character().changeDebuffResistStacks(getP1())
	NativeRandomObserver.leave("Items/LeatherArmor.gd::onPreCombatStart", self, null, "return_implicit")

func onCombatStart():
	NativeRandomObserver.entry("Items/LeatherArmor.gd::onCombatStart", self, {})
	giveBlock()
	activate()
	NativeRandomObserver.leave("Items/LeatherArmor.gd::onCombatStart", self, null, "return_implicit")

