extends Goobert

const activationPulse = preload("res://Items/Animations/SmallBlindPulse.tscn")

onready var particleTimer = $ParticleTimer
onready var activationParticles = $ActivationParticles
onready var blindAmount = getP3()

func onPrepare():
	NativeRandomObserver.entry("Items/LightGoobert.gd::onPrepare", self, {})
	setState(false)
	NativeRandomObserver.leave("Items/LightGoobert.gd::onPrepare", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/LightGoobert.gd::doCooldownEffect", self, {})
	setState(true, true)
	heal()
	var duration = getP_m("dur_blind")
	giveStacksTemporary(opponent(), Game.EventType.Blind, 
		blindAmount, duration)
	NativeRandomObserver.timer_before(particleTimer, "stop", [], "Items/LightGoobert.gd::doCooldownEffect")
	particleTimer.stop()
	NativeRandomObserver.timer_after(particleTimer, "stop", [], "Items/LightGoobert.gd::doCooldownEffect")
	NativeRandomObserver.timer_before(particleTimer, "start", [duration], "Items/LightGoobert.gd::doCooldownEffect")
	particleTimer.start(duration)
	NativeRandomObserver.timer_after(particleTimer, "start", [duration], "Items/LightGoobert.gd::doCooldownEffect")
	Util.createPulse(activationPulse, self, global_position)
	NativeRandomObserver.leave("Items/LightGoobert.gd::doCooldownEffect", self, null, "return_implicit")

func onCombatEnd():
	NativeRandomObserver.entry("Items/LightGoobert.gd::onCombatEnd", self, {})
	NativeRandomObserver.timer_before(particleTimer, "stop", [], "Items/LightGoobert.gd::onCombatEnd")
	particleTimer.stop()
	NativeRandomObserver.timer_after(particleTimer, "stop", [], "Items/LightGoobert.gd::onCombatEnd")
	NativeRandomObserver.leave("Items/LightGoobert.gd::onCombatEnd", self, null, "return_implicit")

func onParticleTimeout():
	NativeRandomObserver.entry("Items/LightGoobert.gd::onParticleTimeout", self, {})
	setState(false)
	NativeRandomObserver.leave("Items/LightGoobert.gd::onParticleTimeout", self, null, "return_implicit")

func onShopEntered():
	onStateChanged(false)

func onStateChanged(active):
	if active:
		activationParticles.activate()
	else:
		activationParticles.deactivate()
		
