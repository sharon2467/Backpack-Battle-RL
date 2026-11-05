extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/PoisonGoobert.gd::doCooldownEffect", self, {})
	heal()
	inflictPoison(getP3())
	NativeRandomObserver.leave("Items/PoisonGoobert.gd::doCooldownEffect", self, null, "return_implicit")

