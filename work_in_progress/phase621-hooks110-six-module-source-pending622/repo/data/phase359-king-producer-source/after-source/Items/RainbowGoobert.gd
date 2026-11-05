extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/RainbowGoobert.gd::doCooldownEffect", self, {})
	giveBlock()
	heal()
	giveVampirism(getP3())
	inflictBlind(getP4())
	inflictPoison(getP4())
	
	for item in getAffectedItems():
		if item.canBeEmpowered():
			item.addBonusDamage(getP5())
	NativeRandomObserver.leave("Items/RainbowGoobert.gd::doCooldownEffect", self, null, "return_implicit")

