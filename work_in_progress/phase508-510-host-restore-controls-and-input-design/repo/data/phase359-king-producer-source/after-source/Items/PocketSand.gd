extends Item

func onCombatStart():
	NativeRandomObserver.entry("Items/PocketSand.gd::onCombatStart", self, {})
	inflictBlind(getP1())
	consume()
	NativeRandomObserver.leave("Items/PocketSand.gd::onCombatStart", self, null, "return_implicit")

