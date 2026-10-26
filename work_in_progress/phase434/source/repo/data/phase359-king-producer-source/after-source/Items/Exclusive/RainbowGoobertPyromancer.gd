extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/RainbowGoobertPyromancer.gd::doCooldownEffect", self, {})
	giveBlock()
	heal()
	giveVampirism(getP3())
	giveHeat(getP4())
	inflictBlind(getP("blind"))
	
	for item in getAffectedItems():
		if item.canBeEmpowered():
			item.addBonusDamage(getP5())
	NativeRandomObserver.leave("Items/Exclusive/RainbowGoobertPyromancer.gd::doCooldownEffect", self, null, "return_implicit")

