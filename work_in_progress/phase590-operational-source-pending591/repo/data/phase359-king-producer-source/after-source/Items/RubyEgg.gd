extends DragonEgg

onready var reflects: = int(getP1())
onready var heat: = int(getP3())

func onPreCombatStart():
	NativeRandomObserver.entry("Items/RubyEgg.gd::onPreCombatStart", self, {})
	giveReflectStacks(reflects)
	NativeRandomObserver.leave("Items/RubyEgg.gd::onPreCombatStart", self, null, "return_implicit")

func onCombatStart():
	NativeRandomObserver.entry("Items/RubyEgg.gd::onCombatStart", self, {})
	doCooldownEffect(false)
	NativeRandomObserver.leave("Items/RubyEgg.gd::onCombatStart", self, null, "return_implicit")

func doCooldownEffect(withReflectStacks: bool = true):
	NativeRandomObserver.entry("Items/RubyEgg.gd::doCooldownEffect", self, {"withReflectStacks": withReflectStacks})
	if withReflectStacks:
		giveReflectStacks(reflects)
	giveHeat(heat)
	activate()
	NativeRandomObserver.leave("Items/RubyEgg.gd::doCooldownEffect", self, null, "return_implicit")

