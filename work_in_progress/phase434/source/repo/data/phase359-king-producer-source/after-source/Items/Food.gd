extends Item
class_name Food

func canAffect(item):
	return item.hasType(Type.Food) and item.descriptor != descriptor
	
func prepare():
	NativeRandomObserver.entry("Items/Food.gd::prepare", self, {})
	.prepare()
	addSpeed(getNumAffectedItems() * 0.1)
	NativeRandomObserver.leave("Items/Food.gd::prepare", self, null, "return_implicit")

