extends Item

onready var cleanses: = int(getP("debuffs"))
onready var potionSpeed: = getP("speed") / 100.0

func canAffect(item):
	return item.hasType(Type.Potion)

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/Shelly.gd::doCooldownEffect", self, {})
	cleanseRandomDebuffs(cleanses)
	heal()
	activate()
	NativeRandomObserver.leave("Items/Exclusive/Shelly.gd::doCooldownEffect", self, null, "return_implicit")

func onPrepare():
	NativeRandomObserver.entry("Items/Exclusive/Shelly.gd::onPrepare", self, {})
	character().changeDebuffProtectionChance( - getChance())
	addSpeed(potionSpeed * getNumAffectedItems())
	NativeRandomObserver.leave("Items/Exclusive/Shelly.gd::onPrepare", self, null, "return_implicit")

func getTriggerPriority() -> int:
	return Priority.High
