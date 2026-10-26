extends Item

onready var bonusSpeed: = getP1() / 100

func canAffect(item):
	return item.hasCooldown()
	
func onCombatStart():
	NativeRandomObserver.entry("Items/GlovesofHaste.gd::onCombatStart", self, {})
	for item in getAffectedItems():
		item.addSpeed(bonusSpeed)
	activate()
	NativeRandomObserver.leave("Items/GlovesofHaste.gd::onCombatStart", self, null, "return_implicit")

