extends Item

func onCombatStart():
	NativeRandomObserver.entry("Items/WalrusTusk.gd::onCombatStart", self, {})
	giveSpikes(getP1())
	consume()
	NativeRandomObserver.leave("Items/WalrusTusk.gd::onCombatStart", self, null, "return_implicit")

