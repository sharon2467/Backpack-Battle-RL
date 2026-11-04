extends Item

onready var manaNeeded: = int(getP("mana"))
onready var cold: = int(getP("cold"))
onready var spellSpeed: = int(getP("speed")) / 100.0

func canAffect(item):
	return item.hasType(Type.Spell)

func onPrepare():
	NativeRandomObserver.entry("Items/Exclusive/BookofIce.gd::onPrepare", self, {})
	var speed = 0.0
	for item in getAffectedItems():
		if item.hasType(Type.Ice):
			speed += spellSpeed * 2
		else:
			speed += spellSpeed
	addSpeed(speed)
	NativeRandomObserver.leave("Items/Exclusive/BookofIce.gd::onPrepare", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/BookofIce.gd::doCooldownEffect", self, {})
	if character().getMana() >= manaNeeded:
		var event = useMana(manaNeeded)
		inflictCold(cold, event)
	activate()
	NativeRandomObserver.leave("Items/Exclusive/BookofIce.gd::doCooldownEffect", self, null, "return_implicit")

