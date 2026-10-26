extends Item

func canAffect(item):
	return item.canBeEmpowered()

func onPrepare():
	NativeRandomObserver.entry("Items/Exclusive/ShepherdsCrook.gd::onPrepare", self, {})
	character().changeBuffProtectionChance(getChance())
	character().changeResistChance(Game.EventType.Blind, getChance2())
	character().changeResistChance(Game.EventType.Cold, getChance2())
	NativeRandomObserver.leave("Items/Exclusive/ShepherdsCrook.gd::onPrepare", self, null, "return_implicit")

func onCombatStart():
	NativeRandomObserver.entry("Items/Exclusive/ShepherdsCrook.gd::onCombatStart", self, {})
	for item in getAffectedItems():
		item.addBonusDamage(getP1())
	activate()
	NativeRandomObserver.leave("Items/Exclusive/ShepherdsCrook.gd::onCombatStart", self, null, "return_implicit")

