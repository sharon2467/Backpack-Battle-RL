extends Goobert

const activationPulse = preload("res://Items/Animations/BookOfLightActivationPulse.tscn")

onready var protectedBuffs = getP("buffs")
onready var manaCost = getP("mana")
onready var activationParticles = $ActivationParticles
onready var buffTimer = $BuffTimer
onready var light = $Icon / CircleLight

var invuCharges: int

enum CrownState{
	Inactive, 
	Active, 
	Used
}

func prepare():
	NativeRandomObserver.entry("Items/Exclusive/KingGoobert.gd::prepare", self, {})
	var gemPower = getP("gempower") / 100.0
	for gem in getGemsNoNull():
		gem.changeGemPower(gemPower)
	
	invuCharges = getP("charges")
	setState(CrownState.Inactive)
	.prepare()
	NativeRandomObserver.leave("Items/Exclusive/KingGoobert.gd::prepare", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Exclusive/KingGoobert.gd::doCooldownEffect", self, {})
	character().changeBuffProtectStacks(protectedBuffs)
	heal()
	if invuCharges > 0 and character().isVulnerable() and checkMana(manaCost):
		invuCharges -= 1
		setState(CrownState.Active, true)
		var invuDur = getP_m("dur_invu")
		var event = character().makeInvulnerable(invuDur, self)
		var observer359_timer_arg_9 = invuDur
		NativeRandomObserver.timer_before(buffTimer, "start", [observer359_timer_arg_9], "Items/Exclusive/KingGoobert.gd::doCooldownEffect")
		buffTimer.start(observer359_timer_arg_9)
		NativeRandomObserver.timer_after(buffTimer, "start", [observer359_timer_arg_9], "Items/Exclusive/KingGoobert.gd::doCooldownEffect")
		useMana(manaCost, event)
		Util.createPulse(activationPulse, self, global_position)
	NativeRandomObserver.leave("Items/Exclusive/KingGoobert.gd::doCooldownEffect", self, null, "return_implicit")

func buffEnded():
	NativeRandomObserver.entry("Items/Exclusive/KingGoobert.gd::buffEnded", self, {})
	if invuCharges > 0:
		setState(CrownState.Inactive, true)
	else:
		setState(CrownState.Used, true)
	NativeRandomObserver.leave("Items/Exclusive/KingGoobert.gd::buffEnded", self, null, "return_implicit")

func onCombatEnd():
	NativeRandomObserver.entry("Items/Exclusive/KingGoobert.gd::onCombatEnd", self, {})
	NativeRandomObserver.timer_before(buffTimer, "stop", [], "Items/Exclusive/KingGoobert.gd::onCombatEnd")
	buffTimer.stop()
	NativeRandomObserver.timer_after(buffTimer, "stop", [], "Items/Exclusive/KingGoobert.gd::onCombatEnd")
	NativeRandomObserver.leave("Items/Exclusive/KingGoobert.gd::onCombatEnd", self, null, "return_implicit")

func onShopEntered():
	onStateChanged(CrownState.Inactive)

func onStateChanged(_crownState):
	NativeRandomObserver.entry("Items/Exclusive/KingGoobert.gd::onStateChanged", self, {"_crownState": _crownState})
	if _crownState == CrownState.Inactive:
		activationParticles.deactivate()
		light.self_modulate = Color.white
		light.show()
	
	elif _crownState == CrownState.Active:
		activationParticles.activate()
		light.self_modulate = Color(1.3, 1.3, 1.3, 1)
		light.show()
	
	else:
		activationParticles.deactivate()
		light.hide()
	NativeRandomObserver.leave("Items/Exclusive/KingGoobert.gd::onStateChanged", self, null, "return_implicit")

