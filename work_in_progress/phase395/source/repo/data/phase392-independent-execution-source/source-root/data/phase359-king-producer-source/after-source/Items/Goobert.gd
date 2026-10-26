extends Item
class_name Goobert

onready var goobertAnimation = $Icon / GoobertAnimation
onready var activationsToTrigger = getP1()

var activations: int


func logCooldown() -> bool:
	return true

func canAffect(item):
	return item.canActivate()

func prepare():
	NativeRandomObserver.entry("Items/Goobert.gd::prepare", self, {})
	activations = 0
	iterationCooldown = activationsToTrigger
	triggerTime = iterationCooldown
	Game.combatLog.snapshotItemTooltipStat(self, Stat.Cooldown)
	
	for item in getAffectedItems():
		connectForCombat(item, "activated", "onItemActivated")
	.prepare()
	NativeRandomObserver.leave("Items/Goobert.gd::prepare", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Goobert.gd::doCooldownEffect", self, {})
	heal()
	NativeRandomObserver.leave("Items/Goobert.gd::doCooldownEffect", self, null, "return_implicit")

func onItemActivated(event):
	NativeRandomObserver.entry("Items/Goobert.gd::onItemActivated", self, {"event": event})
	activations += 1
	
	if activations == getP1():
		activations = 0
		doCooldownEffect()
		activate()
		
		if doubleActivationChance > 0 and Util.flip(doubleActivationChance):
			doCooldownEffect()
			activate()
		
		showCooldownSmooth(activations / activationsToTrigger, true)
	else:
		showCooldownSmooth(activations / activationsToTrigger, false)
	
	triggerTime = activationsToTrigger - activations
	Game.combatLog.snapshotItemTooltipStat(self, Stat.Cooldown, null, false, event)
	NativeRandomObserver.leave("Items/Goobert.gd::onItemActivated", self, null, "return_implicit")

