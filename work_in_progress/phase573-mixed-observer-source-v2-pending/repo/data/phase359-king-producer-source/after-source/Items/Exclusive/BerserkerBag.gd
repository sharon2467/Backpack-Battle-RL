extends Bag

onready var healthThreshold = getP("healtht") / 100.0 - 0.0001
onready var battleRageSpeed = getP("speed_rage") / 100.0
onready var damageResistance = getP("damresistance")
var activated = false

func canApplyEffect(toItem):
	return toItem.hasCooldown()

func onPrepare():
	NativeRandomObserver.entry("Items/Exclusive/BerserkerBag.gd::onPrepare", self, {})
	activated = false
	connectForCombat(character(), "character_damaged", "onDamaged")
	connectForCombat(character(), "battle_rage_started", "onBattleRageStarted")
	connectForCombat(character(), "battle_rage_ended", "onBattleRageEnded")
	NativeRandomObserver.leave("Items/Exclusive/BerserkerBag.gd::onPrepare", self, null, "return_implicit")

func onDamaged(_damage, event):
	NativeRandomObserver.entry("Items/Exclusive/BerserkerBag.gd::onDamaged", self, {"_damage": _damage, "event": event})
	if not activated:
		if character().getRelativeHealth() < healthThreshold:
			activated = true
			character().startBattleRage(self, getP_m("dur_rage"), event)
			activate()
	NativeRandomObserver.leave("Items/Exclusive/BerserkerBag.gd::onDamaged", self, null, "return_implicit")

func onBattleRageStarted(_event):
	NativeRandomObserver.entry("Items/Exclusive/BerserkerBag.gd::onBattleRageStarted", self, {"_event": _event})
	character().changeDamageResistance(damageResistance)
	for item in getItemsInside():
		if canApplyEffect(item):
			item.addSpeed(battleRageSpeed)
	NativeRandomObserver.leave("Items/Exclusive/BerserkerBag.gd::onBattleRageStarted", self, null, "return_implicit")

func onBattleRageEnded(_event):
	NativeRandomObserver.entry("Items/Exclusive/BerserkerBag.gd::onBattleRageEnded", self, {"_event": _event})
	character().changeDamageResistance( - damageResistance)
	for item in getItemsInside():
		if canApplyEffect(item):
			item.reduceSpeed(battleRageSpeed)
	NativeRandomObserver.leave("Items/Exclusive/BerserkerBag.gd::onBattleRageEnded", self, null, "return_implicit")

func getTriggerPriority() -> int:
	return Priority.High + 10
