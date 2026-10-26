extends Potion

onready var healthThreshold: = getP1() / 100.0 - 0.0001


func onTriggerPotion(event = null):
	NativeRandomObserver.entry("Items/ManaPotion.gd::onTriggerPotion", self, {"event": event})
	giveMana(getP2(), event)
	
	giveMaxHealth()
	NativeRandomObserver.leave("Items/ManaPotion.gd::onTriggerPotion", self, null, "return_implicit")

func onPrepare():
	NativeRandomObserver.entry("Items/ManaPotion.gd::onPrepare", self, {})
	
	connectForCombat(character(), "character_mana_changed", "onManaChanged")
	connectForCombat(character(), "character_damaged", "onDamaged")
	NativeRandomObserver.leave("Items/ManaPotion.gd::onPrepare", self, null, "return_implicit")

func onDamaged(_healthChange, event):
	NativeRandomObserver.entry("Items/ManaPotion.gd::onDamaged", self, {"_healthChange": _healthChange, "event": event})
	if isEmpty():
		var observer7_return_0 = null
		NativeRandomObserver.leave("Items/ManaPotion.gd::onDamaged", self, observer7_return_0, "return_explicit")
		return
	
	var relHealth = character().getRelativeHealth()
	if relHealth < healthThreshold:
		consumePotion(event)
	NativeRandomObserver.leave("Items/ManaPotion.gd::onDamaged", self, null, "return_implicit")

func onManaChanged(amount, event):
	NativeRandomObserver.entry("Items/ManaPotion.gd::onManaChanged", self, {"amount": amount, "event": event})
	if isEmpty():
		var observer7_return_0 = null
		NativeRandomObserver.leave("Items/ManaPotion.gd::onManaChanged", self, observer7_return_0, "return_explicit")
		return
	
	if (amount < 0 and 
		event.getOrigin() is Item and 
		event.getOrigin().character() == character()):
			consumePotion(event)
	NativeRandomObserver.leave("Items/ManaPotion.gd::onManaChanged", self, null, "return_implicit")

