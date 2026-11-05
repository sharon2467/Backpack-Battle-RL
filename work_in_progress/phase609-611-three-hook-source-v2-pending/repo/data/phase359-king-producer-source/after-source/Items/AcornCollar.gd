extends RangerCollar

func canAffect(item):
	return item.canDamage()

func onPrepare():
	NativeRandomObserver.entry("Items/AcornCollar.gd::onPrepare", self, {})
	if not affectedItems.empty():
		connectForCombat(character(), "character_lucky_changed", "onLuckyChanged")
	NativeRandomObserver.leave("Items/AcornCollar.gd::onPrepare", self, null, "return_implicit")

func onLuckyChanged(amount, _event):
	NativeRandomObserver.entry("Items/AcornCollar.gd::onLuckyChanged", self, {"amount": amount, "_event": _event})
	for item in affectedItems:
		item.changeCritChancePercent(amount * getChance())
	NativeRandomObserver.leave("Items/AcornCollar.gd::onLuckyChanged", self, null, "return_implicit")

