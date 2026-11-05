extends Reference
class_name Buff

var type: int
var isBuff: bool
var character: Node2D
var current: int = 0
var permanentStacks: int = 0
var counter: Node2D


var resistChancePercent: float = 0.0
var resistStacks: int = 0

var reflectChancePercent: float = 0.0

var cleanseProtectionChancePercent: float = 0.0

var signalName: String
var timer: Timer
var temporaryStacks: Array
var nextTemporaryTimeout: int
var MAX_STACKS: int

func init(_type, _character, _counter = null, _signalName = ""):
	NativeRandomObserver.entry("Core/Buff.gd::init", self, {"_type": _type, "_character": _character, "_counter": _counter, "_signalName": _signalName})
	type = _type
	isBuff = Game.isBuff(type)
	character = _character
	counter = _counter
	signalName = _signalName
	
	timer = Timer.new()
	character.add_child(timer)
	timer.one_shot = true
	timer.process_mode = Timer.TIMER_PROCESS_PHYSICS
	timer.connect("timeout", self, "onTimeout")
	
	if type == Game.EventType.Block:
		MAX_STACKS = 100000
	else:
		MAX_STACKS = 10000
	
	var observer7_return_0 = self
	NativeRandomObserver.leave("Core/Buff.gd::init", self, observer7_return_0, "return_explicit")
	return observer7_return_0

func getStacks():
	return current

func setStacks(amount: int):
	current = amount
	counter.updateHud(current)

func reset():
	setStacks(0)
	resistStacks = 0
	resistChancePercent = 0.0
	cleanseProtectionChancePercent = 0.0
	reflectChancePercent = 0.0

func changeResistChance(chance):
	NativeRandomObserver.entry("Core/Buff.gd::changeResistChance", self, {"chance": chance})
	resistChancePercent += chance
	NativeRandomObserver.leave("Core/Buff.gd::changeResistChance", self, null, "return_implicit")

func changeResistStacks(amount):
	resistStacks = max(0, resistStacks + amount)

func changeCleanseProtectionChance(chance):
	NativeRandomObserver.entry("Core/Buff.gd::changeCleanseProtectionChance", self, {"chance": chance})
	cleanseProtectionChancePercent += chance
	NativeRandomObserver.leave("Core/Buff.gd::changeCleanseProtectionChance", self, null, "return_implicit")

func changeReflectChance(amount):
	NativeRandomObserver.entry("Core/Buff.gd::changeReflectChance", self, {"amount": amount})
	reflectChancePercent += amount
	NativeRandomObserver.leave("Core/Buff.gd::changeReflectChance", self, null, "return_implicit")

func gainStacks(amount: int, item = null, triggerEvent = null, 
	reflect: bool = false):
	
	return gainTemporary(amount, - 1, item, triggerEvent, reflect)

func gainTemporary(amount: int, duration: float, item = null, 
	triggerEvent = null, reflect: bool = false):
	NativeRandomObserver.entry("Core/Buff.gd::gainTemporary", self, {"amount": amount, "duration": duration, "item": item, "triggerEvent": triggerEvent, "reflect": reflect})
	
	var event = null
	
	if amount > 0:
		
		var resisted = 0
		var totalResistChance = resistChancePercent
		
		if item != null and not reflect:
			totalResistChance -= item.getAmplificationChancePercent(type)
			
		if totalResistChance > 0:
			for i in amount:
				if Util.flipPercent(totalResistChance, NativeRandomObserver.buff_label(character, item, type, "resist", i)):
					resisted += 1
		elif totalResistChance < 0:
			for i in amount:
				if Util.flipPercent( - totalResistChance, NativeRandomObserver.buff_label(character, item, type, "amplify", i)):
					amount += 1
		
		var left = amount - resisted
		
		var reflected = 0
		
		if not isBuff:
			
			if not reflect:
				for i in amount:
					if Util.flipPercent(reflectChancePercent, NativeRandomObserver.reflect_label(character, item, type)):
						reflected += 1
				
				left -= reflected
				
				var reflectedByStacks = 0
				if left > 0:
					reflectedByStacks = min(left, character.debuffReflectStacks)
				
				if reflectedByStacks > 0:
					
					reflected += reflectedByStacks
					left -= reflectedByStacks
					character.changeDebuffReflectStacks( - reflectedByStacks)
					
				
				if reflected > 0:
					amount -= reflected
					var target = character
					Util.spawnReflectLabel(type, target.randBuffLabelPos(), reflected)
				
			
			var ownStacksUsed = min(left, resistStacks)
			resisted += ownStacksUsed
			left -= ownStacksUsed
			resistStacks -= ownStacksUsed
			
			if left > 0:
				var characterStacksUsed = min(left, character.debuffResistStacks)
				resisted += characterStacksUsed
				character.changeDebuffResistStacks( - characterStacksUsed)
			
		if resisted > 0:
			amount -= resisted
			Util.spawnResistedLabel(type, character.randBuffLabelPos(), resisted)
			var resistedEvent = Game.combatLog.createEvent_StackResistOrNullify(type, 
						item, resisted, character.playerId, triggerEvent, reflect)
			EventBus.logEvent(resistedEvent)
			
		
		if amount > 0:
			amount = int(min(amount, MAX_STACKS - current))
			if amount == 0:
				var observer7_return_0 = null
				NativeRandomObserver.leave("Core/Buff.gd::gainTemporary", self, observer7_return_0, "return_explicit")
				return observer7_return_0
			
			current += amount
			counter.updateHud(current)
			
			if duration < 0:
				permanentStacks += amount
			else:
				var timeout = Util.time + duration
				var tempStacks = TemporaryStacks.new(amount, timeout, item)
				temporaryStacks.push_back(tempStacks)
				NativeRandomObserver.middle("Core/Buff.gd::gainTemporary", "temporary_append", self, { "entry": NativeRandomObserver.temporary(tempStacks, temporaryStacks.size() - 1), "buff": NativeRandomObserver.state(self, "buff"), "timer": NativeRandomObserver.timer_state(timer) })
				
				if timer.is_stopped():
					NativeRandomObserver.timer_before(timer, "start", [duration], "Core/Buff.gd::gainTemporary")
					timer.start(duration)
					NativeRandomObserver.timer_after(timer, "start", [duration], "Core/Buff.gd::gainTemporary")
					nextTemporaryTimeout = 0
				else:
					if duration < timer.get_time_left():
						NativeRandomObserver.timer_before(timer, "stop", [], "Core/Buff.gd::gainTemporary")
						timer.stop()
						NativeRandomObserver.timer_after(timer, "stop", [], "Core/Buff.gd::gainTemporary")
						NativeRandomObserver.timer_before(timer, "start", [duration], "Core/Buff.gd::gainTemporary")
						timer.start(duration)
						NativeRandomObserver.timer_after(timer, "start", [duration], "Core/Buff.gd::gainTemporary")
						nextTemporaryTimeout = temporaryStacks.size() - 1
			
			
			
			if item:
				var isPlayer = (character == Game.PLAYER)
				
				if not isBuff:
					isPlayer = not isPlayer
				
				item.stackChanged(type, amount, isPlayer)
				
				if duration <= 0:
					event = Game.combatLog.createEvent_Stack(type, item, 
						amount, character.playerId, triggerEvent, false, reflect)
				else:
					event = Game.combatLog.createEvent_StackTemporary(type, 
						item, amount, duration, character.playerId, triggerEvent, 
						reflect)
				
				var appliedToOpponent = (character != item.character())
				Util.spawnBuffLabel_item(type, item, amount, appliedToOpponent)
				
				EventBus.emitEvent(character, signalName, event, [event.getAmount(), event])
		
		if reflected > 0:
			character.opponent.gainStacksTemporary(type, reflected, duration, 
				item, triggerEvent, true)
		
	var observer7_return_1 = event
	NativeRandomObserver.leave("Core/Buff.gd::gainTemporary", self, observer7_return_1, "return_explicit")
	return observer7_return_1


func loseStacks(amount: int, item = null, triggerEvent = null, used = false):
	NativeRandomObserver.entry("Core/Buff.gd::loseStacks", self, {"amount": amount, "item": item, "triggerEvent": triggerEvent, "used": used})
	
	amount = min(current, amount)
	
	if not used:
		var protected = 0
		
		
		if cleanseProtectionChancePercent > 0:
			for i in amount:
				if Util.flipPercent(cleanseProtectionChancePercent, NativeRandomObserver.buff_label(character, item, type, "protect", i)):
					protected += 1
		
		elif cleanseProtectionChancePercent < 0:
			for i in amount:
				if Util.flipPercent( - cleanseProtectionChancePercent, NativeRandomObserver.buff_label(character, item, type, "unprotect", i)):
					protected -= 1
		
		amount -= protected
		amount = clamp(amount, 0, current)
		
		if amount > 0 and resistStacks > 0:
			var protectedByStacks = min(amount, resistStacks)
			protected += protectedByStacks
			amount -= protectedByStacks
			resistStacks -= protectedByStacks
		
		if (isBuff and 
			type != Game.EventType.Block and 
			amount > 0 and 
			character.buffProtectStacks > 0):
			
			var protectedByStacks = min(amount, character.buffProtectStacks)
			protected += protectedByStacks
			amount -= protectedByStacks
			character.buffProtectStacks -= protectedByStacks
		
		if protected > 0:
			Util.spawnProtectedLabel(type, character.randBuffLabelPos(), protected)
			var protectedEvent = Game.combatLog.createEvent_StackProtect(type, 
				item, protected, character.playerId, triggerEvent)
			EventBus.logEvent(protectedEvent)
	


	
	if permanentStacks >= amount:
		permanentStacks -= amount
	else:
		var tempToCleanse = amount - permanentStacks
		permanentStacks = 0
		
		while tempToCleanse > 0:
			if temporaryStacks.empty():
				print("current < cleanse amount")
				
				break
			
			
			var farthestTimeout = 0
			var farthestIndex = - 1
			for i in temporaryStacks.size():
				var stacks = temporaryStacks[i]
				if stacks.timeout > farthestTimeout:
					farthestTimeout = stacks.timeout
					farthestIndex = i
			
			var farthest = temporaryStacks[farthestIndex]
			if farthest.amount > tempToCleanse:
				farthest.amount -= tempToCleanse
				tempToCleanse = 0
				
			else:
				tempToCleanse -= farthest.amount
				temporaryStacks.remove(farthestIndex)
				
				
				if temporaryStacks.empty():
					
					NativeRandomObserver.timer_before(timer, "stop", [], "Core/Buff.gd::loseStacks")
					timer.stop()
					NativeRandomObserver.timer_after(timer, "stop", [], "Core/Buff.gd::loseStacks")
	
	var observer7_return_0 = changeCurrentLogShowLabel(false, amount, item, triggerEvent, used)
	NativeRandomObserver.leave("Core/Buff.gd::loseStacks", self, observer7_return_0, "return_explicit")
	return observer7_return_0


func changeCurrentLogShowLabel(isTimeout: bool, amount: int, 
	item = null, triggerEvent = null, used: bool = false):
	NativeRandomObserver.entry("Core/Buff.gd::changeCurrentLogShowLabel", self, {"isTimeout": isTimeout, "amount": amount, "item": item, "triggerEvent": triggerEvent, "used": used})
		
	var change = min(current, amount)

	if change > 0:
		current -= change
		counter.updateHud(current)
		
		
		
		if item:
			var isPlayer = (character == Game.PLAYER)
			if not used:
				if isBuff:
					isPlayer = not isPlayer
			
			item.stackChanged(type, - change, isPlayer, used)
			
			var event
			if isTimeout:
				event = Game.combatLog.createEvent_StackTimeout(type, item, - change, character.playerId, triggerEvent)
			else:
				event = Game.combatLog.createEvent_Stack(type, item, - change, character.playerId, triggerEvent, used)
				
			EventBus.emitEvent(character, signalName, event, [event.getAmount(), event])
			
			var appliedToOpponent = (character != item.character())
			Util.spawnBuffLabel_item(type, item, - change, appliedToOpponent)
			
			var observer7_return_0 = event
			NativeRandomObserver.leave("Core/Buff.gd::changeCurrentLogShowLabel", self, observer7_return_0, "return_explicit")
			return observer7_return_0
	
	var observer7_return_1 = null
	NativeRandomObserver.leave("Core/Buff.gd::changeCurrentLogShowLabel", self, observer7_return_1, "return_explicit")
	return observer7_return_1

func onTimeout():
	NativeRandomObserver.entry("Core/Buff.gd::onTimeout", self, {})
	var timedOutStacks: TemporaryStacks = temporaryStacks[nextTemporaryTimeout]
	changeCurrentLogShowLabel(true, timedOutStacks.amount, timedOutStacks.item)
	temporaryStacks.remove(nextTemporaryTimeout)
	NativeRandomObserver.middle("Core/Buff.gd::onTimeout", "temporary_remove", self, { "buff": NativeRandomObserver.state(self, "buff"), "timer": NativeRandomObserver.timer_state(timer) })
	
	
	
	
	
	if not temporaryStacks.empty():
		var earliestTimeout = INF
		var earliestIndex = - 1
		for i in temporaryStacks.size():
			var stacks = temporaryStacks[i]
			if stacks.timeout < earliestTimeout:
				earliestTimeout = stacks.timeout
				earliestIndex = i
				
		nextTemporaryTimeout = earliestIndex
		var delay = earliestTimeout - Util.time
		if delay <= 0.01:
			onTimeout()
		else:
			NativeRandomObserver.timer_before(timer, "start", [delay], "Core/Buff.gd::onTimeout")
			timer.start(delay)
			NativeRandomObserver.timer_after(timer, "start", [delay], "Core/Buff.gd::onTimeout")
	NativeRandomObserver.leave("Core/Buff.gd::onTimeout", self, null, "return_implicit")

func combatEnd():
	NativeRandomObserver.entry("Core/Buff.gd::combatEnd", self, {})
	NativeRandomObserver.timer_before(timer, "stop", [], "Core/Buff.gd::combatEnd")
	timer.stop()
	NativeRandomObserver.timer_after(timer, "stop", [], "Core/Buff.gd::combatEnd")
	temporaryStacks.clear()
	NativeRandomObserver.leave("Core/Buff.gd::combatEnd", self, null, "return_implicit")

class TemporaryStacks extends Reference:
	var amount: int
	var timeout: float
	var item: Item
	
	func _init(_amount, _timeout, _item = null):
		NativeRandomObserver.entry("Core/Buff.gd::TemporaryStacks._init", self, {"_amount": _amount, "_timeout": _timeout, "_item": _item})
		amount = _amount
		timeout = _timeout
		item = _item
		NativeRandomObserver.leave("Core/Buff.gd::TemporaryStacks._init", self, null, "return_implicit")

