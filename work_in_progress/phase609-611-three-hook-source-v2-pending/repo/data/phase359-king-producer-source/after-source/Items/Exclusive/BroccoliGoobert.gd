extends Goobert

onready var luck: = int(getP("luck"))
onready var luckNeeded: = int(getP("luckt"))
onready var regen: = int(getP("regen"))

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/BroccoliGoobert.gd::doCooldownEffect", self, {})
	if character().getLucky() >= luckNeeded:
		giveRegeneration(regen)
	else:
		giveLucky(luck)
	NativeRandomObserver.leave("Items/Exclusive/BroccoliGoobert.gd::doCooldownEffect", self, null, "return_implicit")

