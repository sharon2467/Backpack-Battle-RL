extends Particles2D

var timer

func _ready() -> void :
	NativeRandomObserver.ui_ready(self)
	NativeRandomObserver.entry("Utility/AutoHideParticles.gd::_ready", self, {})
	timer = Timer.new()
	NativeRandomObserver.timer_birth(timer, self, "AutoHide.Timer.new")
	timer.one_shot = true
	timer.connect("timeout", self, "timeout")
	add_child(timer)
	hide()
	NativeRandomObserver.leave("Utility/AutoHideParticles.gd::_ready", self, null, "return_implicit")

func activate():
	var observer359_ui_token = NativeRandomObserver.ui_entry("Utility/AutoHideParticles.gd::activate", self, {})
	NativeRandomObserver.entry("Utility/AutoHideParticles.gd::activate", self, {})
	NativeRandomObserver.timer_before(timer, "stop", [], "Utility/AutoHideParticles.gd::activate")
	timer.stop()
	NativeRandomObserver.timer_after(timer, "stop", [], "Utility/AutoHideParticles.gd::activate")
	
	
	show()
	
	if one_shot:
		restart()
		startTimer()
	else:
		emitting = true
	NativeRandomObserver.leave("Utility/AutoHideParticles.gd::activate", self, null, "return_implicit")
	NativeRandomObserver.ui_leave(observer359_ui_token, "Utility/AutoHideParticles.gd::activate", self)

func deactivate():
	var observer359_ui_token = NativeRandomObserver.ui_entry("Utility/AutoHideParticles.gd::deactivate", self, {})
	NativeRandomObserver.entry("Utility/AutoHideParticles.gd::deactivate", self, {})
	if visible:
		emitting = false
		startTimer()
	NativeRandomObserver.leave("Utility/AutoHideParticles.gd::deactivate", self, null, "return_implicit")
	NativeRandomObserver.ui_leave(observer359_ui_token, "Utility/AutoHideParticles.gd::deactivate", self)

func startTimer():
	var observer359_ui_token = NativeRandomObserver.ui_entry("Utility/AutoHideParticles.gd::startTimer", self, {})
	NativeRandomObserver.entry("Utility/AutoHideParticles.gd::startTimer", self, {})
	var observer359_timer_arg_2 = lifetime * (1 + (1 - explosiveness) / speed_scale)
	NativeRandomObserver.timer_before(timer, "start", [observer359_timer_arg_2], "Utility/AutoHideParticles.gd::startTimer")
	timer.start(observer359_timer_arg_2)
	NativeRandomObserver.timer_after(timer, "start", [observer359_timer_arg_2], "Utility/AutoHideParticles.gd::startTimer")
	NativeRandomObserver.leave("Utility/AutoHideParticles.gd::startTimer", self, null, "return_implicit")
	NativeRandomObserver.ui_leave(observer359_ui_token, "Utility/AutoHideParticles.gd::startTimer", self)

func timeout():
	NativeRandomObserver.entry("Utility/AutoHideParticles.gd::timeout", self, {})
	hide()
	NativeRandomObserver.leave("Utility/AutoHideParticles.gd::timeout", self, null, "return_implicit")

func instantClear():
	var observer359_ui_token = NativeRandomObserver.ui_entry("Utility/AutoHideParticles.gd::instantClear", self, {})
	NativeRandomObserver.entry("Utility/AutoHideParticles.gd::instantClear", self, {})
	NativeRandomObserver.timer_before(timer, "stop", [], "Utility/AutoHideParticles.gd::instantClear")
	timer.stop()
	NativeRandomObserver.timer_after(timer, "stop", [], "Utility/AutoHideParticles.gd::instantClear")
	restart()
	emitting = false
	hide()
	NativeRandomObserver.leave("Utility/AutoHideParticles.gd::instantClear", self, null, "return_implicit")
	NativeRandomObserver.ui_leave(observer359_ui_token, "Utility/AutoHideParticles.gd::instantClear", self)

