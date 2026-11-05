extends Item

onready var healthThreshold: = getP1() / 100.0 - 0.0001
var hasActivated: bool

func onPrepare():
	NativeRandomObserver.entry("Items/LeatherBoots.gd::onPrepare", self, {})
	hasActivated = false
	connectForCombat(character(), "character_damaged", "onDamaged")
	NativeRandomObserver.leave("Items/LeatherBoots.gd::onPrepare", self, null, "return_implicit")

func onDamaged(_damage, event):
	NativeRandomObserver.entry("Items/LeatherBoots.gd::onDamaged", self, {"_damage": _damage, "event": event})
	if hasActivated:
		var observer7_return_0 = null
		NativeRandomObserver.leave("Items/LeatherBoots.gd::onDamaged", self, observer7_return_0, "return_explicit")
		return
	
	var relHealth = character().getRelativeHealth()
	if relHealth < healthThreshold:
		hasActivated = true
		giveLucky(getP2(), event)
		giveEmpower(getP3(), event)
		giveBlock(getBlock(), true, event)
		consume()
	NativeRandomObserver.leave("Items/LeatherBoots.gd::onDamaged", self, null, "return_implicit")

func getTriggerPriority() -> int:
	return Priority.High + 2
