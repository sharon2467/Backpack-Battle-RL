extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/RainbowGoobertRanger.gd::doCooldownEffect", self, {})
	giveBlock()
	heal()
	giveVampirism(getP3())
	giveEmpower(getP4())
	inflictBlind(getP5())
	
	for item in getAffectedItems():
		if item.canBeEmpowered():
			item.addBonusDamage(getP6())
	NativeRandomObserver.leave("Items/RainbowGoobertRanger.gd::doCooldownEffect", self, null, "return_implicit")

