extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/CheeseGoobert.gd::doCooldownEffect", self, {})
	giveMaxHealth()
	giveRandomBuffs(getP3())
	NativeRandomObserver.leave("Items/Exclusive/CheeseGoobert.gd::doCooldownEffect", self, null, "return_implicit")

