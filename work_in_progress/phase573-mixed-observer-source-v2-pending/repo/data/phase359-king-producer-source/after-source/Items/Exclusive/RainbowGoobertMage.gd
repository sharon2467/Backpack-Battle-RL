extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/RainbowGoobertMage.gd::doCooldownEffect", self, {})
	giveBlock()
	heal()
	giveVampirism(getP3())
	giveMostBuffs(getP4())
	inflictBlind(getP5())
	
	for item in getAffectedItems():
		if item.canBeEmpowered():
			item.addBonusDamage(getP6())
	NativeRandomObserver.leave("Items/Exclusive/RainbowGoobertMage.gd::doCooldownEffect", self, null, "return_implicit")

