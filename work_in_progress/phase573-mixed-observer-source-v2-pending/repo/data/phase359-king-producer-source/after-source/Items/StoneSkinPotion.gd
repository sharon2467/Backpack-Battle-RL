extends Potion

func onTriggerPotion(triggerEvent = null):
	NativeRandomObserver.entry("Items/StoneSkinPotion.gd::onTriggerPotion", self, {"triggerEvent": triggerEvent})
	healthToBlock(getP2(), getBlock(), triggerEvent)
	NativeRandomObserver.leave("Items/StoneSkinPotion.gd::onTriggerPotion", self, null, "return_implicit")

func onPrepare():
	NativeRandomObserver.entry("Items/StoneSkinPotion.gd::onPrepare", self, {})
	connectForCombat(character(), "character_block_changed", "onBlockChanged")
	NativeRandomObserver.leave("Items/StoneSkinPotion.gd::onPrepare", self, null, "return_implicit")

func onBlockChanged(_amount, event):
	NativeRandomObserver.entry("Items/StoneSkinPotion.gd::onBlockChanged", self, {"_amount": _amount, "event": event})
	if isEmpty():
		var observer7_return_0 = null
		NativeRandomObserver.leave("Items/StoneSkinPotion.gd::onBlockChanged", self, observer7_return_0, "return_explicit")
		return
	
	if character().getBlock() >= getP1():
		
		consumePotion()
	NativeRandomObserver.leave("Items/StoneSkinPotion.gd::onBlockChanged", self, null, "return_implicit")

