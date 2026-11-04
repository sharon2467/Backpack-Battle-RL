extends Goobert

onready var empower = getP3()

onready var particleTimer = $ParticleTimer
onready var activationParticles = $EmpowerParticles

func onPrepare():
	NativeRandomObserver.entry("Items/CarrotGoobert.gd::onPrepare", self, {})
	setState(false)
	activationParticles.global_rotation = 0
	NativeRandomObserver.leave("Items/CarrotGoobert.gd::onPrepare", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/CarrotGoobert.gd::doCooldownEffect", self, {})
	setState(true, true)
	cleanseRandomDebuffs(getP2())
	var duration = getP_m("dur")
	giveStacksTemporary(character(), Game.EventType.Empower, 
		empower, duration)
	NativeRandomObserver.timer_before(particleTimer, "stop", [], "Items/CarrotGoobert.gd::doCooldownEffect")
	particleTimer.stop()
	NativeRandomObserver.timer_after(particleTimer, "stop", [], "Items/CarrotGoobert.gd::doCooldownEffect")
	NativeRandomObserver.timer_before(particleTimer, "start", [duration], "Items/CarrotGoobert.gd::doCooldownEffect")
	particleTimer.start(duration)
	NativeRandomObserver.timer_after(particleTimer, "start", [duration], "Items/CarrotGoobert.gd::doCooldownEffect")
	NativeRandomObserver.leave("Items/CarrotGoobert.gd::doCooldownEffect", self, null, "return_implicit")

func onCombatEnd():
	NativeRandomObserver.entry("Items/CarrotGoobert.gd::onCombatEnd", self, {})
	NativeRandomObserver.timer_before(particleTimer, "stop", [], "Items/CarrotGoobert.gd::onCombatEnd")
	particleTimer.stop()
	NativeRandomObserver.timer_after(particleTimer, "stop", [], "Items/CarrotGoobert.gd::onCombatEnd")
	NativeRandomObserver.leave("Items/CarrotGoobert.gd::onCombatEnd", self, null, "return_implicit")

func onParticleTimeout():
	NativeRandomObserver.entry("Items/CarrotGoobert.gd::onParticleTimeout", self, {})
	setState(false)
	NativeRandomObserver.leave("Items/CarrotGoobert.gd::onParticleTimeout", self, null, "return_implicit")

func onShopEntered():
	onStateChanged(false)

func onStateChanged(active):
	if active:
		activationParticles.activate()
	else:
		activationParticles.deactivate()
