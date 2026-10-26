extends Node

enum LoggingMode{
	None = 0, 
	Instant = 1, 
	Delayed = 2
}
var loggingMode = LoggingMode.Instant
var signalQueue = []

var connections = {}
var signalIDs = {}

func setLoggingMode(mode: int):
	loggingMode = mode
	
func getLoggingMode():
	return loggingMode

func queueSignal(emitter: Node, signalName: String, event: CombatEvent, arguments = []):
	signalQueue.push_back([emitter, signalName, event, arguments])


func flushLoggingQueue():
	NativeRandomObserver.entry("Utility/EventBus.gd::flushLoggingQueue", self, {})
	setLoggingMode(LoggingMode.Instant)
	NativeRandomObserver.middle("Utility/EventBus.gd::flushLoggingQueue", "mode_instant", self, { "state": NativeRandomObserver.state(self, "event_bus") })
	
	var queueDuplicate = signalQueue.duplicate()
	NativeRandomObserver.middle("Utility/EventBus.gd::flushLoggingQueue", "queue_snapshot", self, { "queue_snapshot": queueDuplicate, "state": NativeRandomObserver.state(self, "event_bus") })
	signalQueue.clear()
	NativeRandomObserver.middle("Utility/EventBus.gd::flushLoggingQueue", "queue_clear", self, { "state": NativeRandomObserver.state(self, "event_bus") })
	
	for tuple in queueDuplicate:
		var emitter = tuple[0]
		var signalName = tuple[1]
		var event = tuple[2]
		var arguments = tuple[3]
		emitAndLog(emitter, signalName, event, arguments)
	NativeRandomObserver.leave("Utility/EventBus.gd::flushLoggingQueue", self, null, "return_implicit")

func emitSignal(emitter: Node, signalName: String, arguments = []):
	emitEvent(emitter, signalName, null, arguments)

func emitEvent(emitter: Node, signalName: String, event: CombatEvent, arguments = []):
	if loggingMode == LoggingMode.Delayed:
		queueSignal(emitter, signalName, event, arguments)
	else:
		emitAndLog(emitter, signalName, event, arguments)

func logEvent(event: CombatEvent):
	if loggingMode == LoggingMode.Delayed:
		queueSignal(null, "", event, [])
	else:
		emitAndLog(null, "", event, [])
		



func emitAndLog(emitter: Node, signalName: String, event: CombatEvent, arguments: Array):
	NativeRandomObserver.entry("Utility/EventBus.gd::emitAndLog", self, {"emitter": emitter, "signalName": signalName, "event": event, "arguments": arguments})
	if event != null:
		Game.combatLog.logEvent(event)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	if emitter == null or not signalName in signalIDs:
		var observer7_return_0 = null
		NativeRandomObserver.leave("Utility/EventBus.gd::emitAndLog", self, observer7_return_0, "return_explicit")
		return
	
	
	
	var signalID = signalIDs[signalName]
	var emissionID = getEmissionID(emitter, signalID)
	for funcRef in connections.get(emissionID, []):
		if Game.fightEnded:
			var observer7_return_1 = null
			NativeRandomObserver.leave("Utility/EventBus.gd::emitAndLog", self, observer7_return_1, "return_explicit")
			return
		
		NativeRandomObserver.middle("Utility/EventBus.gd::emitAndLog", "receiver_attempt", self, { "funcRefID": funcRef.get_instance_id(), "emissionID": emissionID, "event_id": event, "fightEnded": Game.fightEnded })
		funcRef.call_funcv(arguments)
		NativeRandomObserver.middle("Utility/EventBus.gd::emitAndLog", "receiver_return", self, { "funcRefID": funcRef.get_instance_id(), "emissionID": emissionID, "event_id": event, "fightEnded": Game.fightEnded })
	NativeRandomObserver.leave("Utility/EventBus.gd::emitAndLog", self, null, "return_implicit")

func connectEvent(emitter: Node, signalName: String, receiver: Node, method: String):
	NativeRandomObserver.entry("Utility/EventBus.gd::connectEvent", self, {"emitter": emitter, "signalName": signalName, "receiver": receiver, "method": method})
	if not signalName in signalIDs:
		signalIDs[signalName] = signalIDs.size()
	var signalID = signalIDs[signalName]
	
	var emissionID = getEmissionID(emitter, signalID)
	var funcRef = FuncRef.new()
	funcRef.set_function(method)
	funcRef.set_instance(receiver)


	Util.dictAppend(connections, emissionID, funcRef)
	NativeRandomObserver.middle("Utility/EventBus.gd::connectEvent", "registration", self, { "emitter": emitter, "signalName": signalName, "receiver": receiver, "method": method, "emissionID": emissionID, "funcRefID": funcRef.get_instance_id(), "insertion_index": connections[emissionID].size() - 1 })
	NativeRandomObserver.leave("Utility/EventBus.gd::connectEvent", self, null, "return_implicit")

func getEmissionID(emitter: Node, signalID: int) -> int:
	var ID = emitter.get_instance_id()
	
	ID += (signalID << 32)
	
	return ID









	

func disconnectAll():
	NativeRandomObserver.entry("Utility/EventBus.gd::disconnectAll", self, {})
	connections.clear()
	NativeRandomObserver.leave("Utility/EventBus.gd::disconnectAll", self, null, "return_implicit")

