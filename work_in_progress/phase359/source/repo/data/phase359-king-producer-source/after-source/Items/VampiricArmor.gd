extends Item

func onCombatStart():
	NativeRandomObserver.entry("Items/VampiricArmor.gd::onCombatStart", self, {})
	healthToBlock(getP1(), getBlock())
	giveVampirism(getP2())
	activate()
	NativeRandomObserver.leave("Items/VampiricArmor.gd::onCombatStart", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/VampiricArmor.gd::doCooldownEffect", self, {})
	healthToBlock(getP3(), getP4())
	activate()
	NativeRandomObserver.leave("Items/VampiricArmor.gd::doCooldownEffect", self, null, "return_implicit")

