extends Food

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Carrot.gd::doCooldownEffect", self, {})
	cleanseRandomDebuffs(1)
	
	if character().getLucky() >= getP2():
		if rollChance():
			giveEmpower(1)
	activate()
	NativeRandomObserver.leave("Items/Carrot.gd::doCooldownEffect", self, null, "return_implicit")

