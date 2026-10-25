extends Goobert

onready var staminaThreshold: = getP("staminat")
onready var stamina: = getP("stamina")
onready var regen: = int(getP("regen"))

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/ToastGoobert.gd::doCooldownEffect", self, {})
	if character().getCurrentStamina() < staminaThreshold:
		giveStamina(stamina)
	else:
		giveRegeneration(regen)
	NativeRandomObserver.leave("Items/Exclusive/ToastGoobert.gd::doCooldownEffect", self, null, "return_implicit")

