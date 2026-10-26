extends "res://Items/HealthPotion.gd"

func onTriggerPotion(triggerEvent = null):
	NativeRandomObserver.entry("Items/StrongHealthPotion.gd::onTriggerPotion", self, {"triggerEvent": triggerEvent})
	.onTriggerPotion(triggerEvent)
	giveRegeneration(getP4(), triggerEvent)
	NativeRandomObserver.leave("Items/StrongHealthPotion.gd::onTriggerPotion", self, null, "return_implicit")

func getTriggerPriority() -> int:
	return Priority.High + 1
