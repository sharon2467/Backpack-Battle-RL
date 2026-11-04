extends "res://Items/StoneSkinPotion.gd"

onready var spikes: = int(getP("spikes"))

func onTriggerPotion(triggerEvent = null):
	NativeRandomObserver.entry("Items/StrongStoneSkinPotion.gd::onTriggerPotion", self, {"triggerEvent": triggerEvent})
	.onTriggerPotion(triggerEvent)
	giveStacksTemporary(character(), Game.EventType.Spikes, 
		spikes, getP_m("dur"), triggerEvent)
	NativeRandomObserver.leave("Items/StrongStoneSkinPotion.gd::onTriggerPotion", self, null, "return_implicit")

