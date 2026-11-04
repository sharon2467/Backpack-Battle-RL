extends Goobert

onready var numBuffs: = int(getP("buffs"))

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/CupcakeGoobert.gd::doCooldownEffect", self, {})
	heal()
	giveMostBuffs(numBuffs)
	NativeRandomObserver.leave("Items/Exclusive/CupcakeGoobert.gd::doCooldownEffect", self, null, "return_implicit")

