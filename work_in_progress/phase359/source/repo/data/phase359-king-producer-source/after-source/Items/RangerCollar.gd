extends Item
class_name RangerCollar

onready var acornAceDescriptor = ItemBook.getDescriptor("Acorn Ace")

var affectedItems

func prepare():
	NativeRandomObserver.entry("Items/RangerCollar.gd::prepare", self, {})
	affectedItems = getAffectedItems()
	var numAces = countAllInInventoryOfType(acornAceDescriptor)
	if numAces > 0:
		var staminaReduction = numAces * - acornAceDescriptor.getP("stamina")
		for item in affectedItems:
			item.changeStaminaFactor(staminaReduction)
	.prepare()
	NativeRandomObserver.leave("Items/RangerCollar.gd::prepare", self, null, "return_implicit")

