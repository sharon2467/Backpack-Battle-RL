extends Item

onready var buffFactor: = getP("buffs") / 100.0
onready var buffLimit: = int(getP("max"))

func canAffect(item):
	return item.hasType(Type.Holy)

func onPrepare():
	NativeRandomObserver.entry("Items/Exclusive/MagicMirror.gd::onPrepare", self, {})
	var totalChance = getChance() + getNumAffectedItems() * getChance2()
	character().changeAllDebuffsReflectChance(totalChance)
	NativeRandomObserver.leave("Items/Exclusive/MagicMirror.gd::onPrepare", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/MagicMirror.gd::doCooldownEffect", self, {})
	multiplyBuffsLimit(buffFactor, buffLimit)
	onAfterEffectFinished()
	NativeRandomObserver.leave("Items/Exclusive/MagicMirror.gd::doCooldownEffect", self, null, "return_implicit")

