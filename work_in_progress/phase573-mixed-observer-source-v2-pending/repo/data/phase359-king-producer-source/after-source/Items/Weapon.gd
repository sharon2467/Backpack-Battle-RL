extends Item
class_name Weapon

func _ready() -> void :
	damageSource = DamageSource.new().setItem(self)

func attack(triggerEvent = null):
	NativeRandomObserver.entry("Items/Weapon.gd::attack", self, {"triggerEvent": triggerEvent})
	var res: DamageResult = dealDamage(triggerEvent)
	activate(res)
	NativeRandomObserver.leave("Items/Weapon.gd::attack", self, null, "return_implicit")

func doCooldownEffect():
	NativeRandomObserver.entry("Items/Weapon.gd::doCooldownEffect", self, {})
	if useStamina() == Character.StaminaResult.Sufficient:
		attack()
	NativeRandomObserver.leave("Items/Weapon.gd::doCooldownEffect", self, null, "return_implicit")

