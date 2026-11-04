extends Potion

onready var healthThreshold = getP1() / 100.0

func onTriggerPotion(triggerEvent = null):
	NativeRandomObserver.entry("Items/HealthPotion.gd::onTriggerPotion", self, {"triggerEvent": triggerEvent})
	heal(getP_m("heal"), triggerEvent)
	cleansePoison(getP3(), triggerEvent)
	NativeRandomObserver.leave("Items/HealthPotion.gd::onTriggerPotion", self, null, "return_implicit")

func onPrepare():
	NativeRandomObserver.entry("Items/HealthPotion.gd::onPrepare", self, {})
	connectForCombat(character(), "character_damaged", "onDamaged")
	NativeRandomObserver.leave("Items/HealthPotion.gd::onPrepare", self, null, "return_implicit")

func onDamaged(_healthChange, event):
	NativeRandomObserver.entry("Items/HealthPotion.gd::onDamaged", self, {"_healthChange": _healthChange, "event": event})
	if isEmpty():
		var observer7_return_0 = null
		NativeRandomObserver.leave("Items/HealthPotion.gd::onDamaged", self, observer7_return_0, "return_explicit")
		return
	
	var relHealth = character().getRelativeHealth()
	if relHealth < healthThreshold:
		consumePotion(event)
	NativeRandomObserver.leave("Items/HealthPotion.gd::onDamaged", self, null, "return_implicit")

func getTriggerPriority() -> int:
	return Priority.High
