extends Goobert

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/RainbowGoobertBerserker.gd::doCooldownEffect", self, {})
	giveBlock()
	giveMaxHealth()
	giveVampirism(getP3())
	giveRandomBuffs(getP4())
	inflictBlind(getP("blind"))
	
	for item in getAffectedItems():
		if item.canBeEmpowered():
			item.addBonusDamage(getP5())
	NativeRandomObserver.leave("Items/Exclusive/RainbowGoobertBerserker.gd::doCooldownEffect", self, null, "return_implicit")

