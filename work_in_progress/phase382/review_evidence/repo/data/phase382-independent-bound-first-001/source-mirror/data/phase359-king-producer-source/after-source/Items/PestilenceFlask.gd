extends Potion

func onTriggerPotion(triggerEvent = null):
	NativeRandomObserver.entry("Items/PestilenceFlask.gd::onTriggerPotion", self, {"triggerEvent": triggerEvent})
	inflictPoison(getP1(), triggerEvent)
	selfInflictPoison(getP2(), triggerEvent)
	NativeRandomObserver.leave("Items/PestilenceFlask.gd::onTriggerPotion", self, null, "return_implicit")

func onPrepare():
	NativeRandomObserver.entry("Items/PestilenceFlask.gd::onPrepare", self, {})
	connectForCombat(opponent(), "character_healed", "onOpponentHeal")
	NativeRandomObserver.leave("Items/PestilenceFlask.gd::onPrepare", self, null, "return_implicit")

func onOpponentHeal(_amount, event):
	NativeRandomObserver.entry("Items/PestilenceFlask.gd::onOpponentHeal", self, {"_amount": _amount, "event": event})
	if isEmpty():
		var observer7_return_0 = null
		NativeRandomObserver.leave("Items/PestilenceFlask.gd::onOpponentHeal", self, observer7_return_0, "return_explicit")
		return
	
	drink()
	
	triggerPotion(event)
	
	var affected = getAffectedItems()
	if not affected.empty():
		affected[0].triggerPotion(event)
		affected[0].miniActivate()
	
	activate()
	NativeRandomObserver.leave("Items/PestilenceFlask.gd::onOpponentHeal", self, null, "return_implicit")

