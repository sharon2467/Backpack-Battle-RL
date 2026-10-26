extends Goobert

var affectedWeapons = []

func canAffect_secondary(item):
	return item.canBeEmpowered()

func onPrepare():
	NativeRandomObserver.entry("Items/SteelGoobert.gd::onPrepare", self, {})
	for item in getAffectedItems(Affected.Secondary):
		affectedWeapons.push_back(item)
	NativeRandomObserver.leave("Items/SteelGoobert.gd::onPrepare", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/SteelGoobert.gd::doCooldownEffect", self, {})
	for item in affectedWeapons:
		item.addBonusDamage(getP2())
	giveBlock()
	NativeRandomObserver.leave("Items/SteelGoobert.gd::doCooldownEffect", self, null, "return_implicit")

func onCombatEnd():
	NativeRandomObserver.entry("Items/SteelGoobert.gd::onCombatEnd", self, {})
	affectedWeapons.clear()
	NativeRandomObserver.leave("Items/SteelGoobert.gd::onCombatEnd", self, null, "return_implicit")

