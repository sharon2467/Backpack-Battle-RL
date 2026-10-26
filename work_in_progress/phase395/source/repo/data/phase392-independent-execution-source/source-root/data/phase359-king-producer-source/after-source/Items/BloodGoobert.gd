extends Goobert

onready var dam: = getP("dam")
onready var vampirism: = int(getP("vampirism"))

func onCombatStart():
	NativeRandomObserver.entry("Items/BloodGoobert.gd::onCombatStart", self, {})
	giveVampirism(vampirism)
	activate()
	NativeRandomObserver.leave("Items/BloodGoobert.gd::onCombatStart", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/BloodGoobert.gd::doCooldownEffect", self, {})
	stealLife(dam + character().getVampirism(), getP_m("lifesteal") / 100.0)
	NativeRandomObserver.leave("Items/BloodGoobert.gd::doCooldownEffect", self, null, "return_implicit")

