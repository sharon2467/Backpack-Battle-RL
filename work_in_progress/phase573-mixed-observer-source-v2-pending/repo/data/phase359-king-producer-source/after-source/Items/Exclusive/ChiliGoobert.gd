extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/ChiliGoobert.gd::doCooldownEffect", self, {})
	heal()
	giveHeat(getP3())
	NativeRandomObserver.leave("Items/Exclusive/ChiliGoobert.gd::doCooldownEffect", self, null, "return_implicit")

