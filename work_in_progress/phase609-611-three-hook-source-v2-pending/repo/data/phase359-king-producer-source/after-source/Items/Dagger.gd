extends Weapon
class_name Dagger

func prepare():
	.prepare()
	connectForCombat(opponent(), "character_stunned", "onStun")

func onStun(triggerEvent):
	NativeRandomObserver.entry("Items/Dagger.gd::onStun", self, {"triggerEvent": triggerEvent})
	attack(triggerEvent)
	NativeRandomObserver.leave("Items/Dagger.gd::onStun", self, null, "return_implicit")

