extends Item
class_name Potion

export var potionColor: Color

const connectorScene = preload("res://Items/Animations/PotionConnector.tscn")
const drinkSound = preload("res://Assets/Sound/PotionDrink.wav")
const triggerSound = preload("res://Assets/Sound/PotionOpen.wav")

onready var fluid = $Icon / BottleOfBooze
onready var fluidGradientTex = fluid.material.get_shader_param("gradient")
onready var fluidGradient = fluidGradientTex.gradient.duplicate()
onready var baseFoaminess = fluid.baseFoaminess
onready var baseScroll = fluid.baseScroll
onready var baseLevel = fluid.levelModification

var fluidTween
var isFull: bool = true
var connector = null

func _ready() -> void :
	if connector == null:
		connector = connectorScene.instance()
		add_child(connector)
		
		$Icon / Flask1Overlay.use_parent_material = true
	



func prepare():
	NativeRandomObserver.entry("Items/Potion.gd::prepare", self, {})
	.prepare()
	setState(true)
	NativeRandomObserver.leave("Items/Potion.gd::prepare", self, null, "return_implicit")

func canAffect(item):
	return item.hasType(Type.Potion)

func isEmpty():
	return not isFull

func fill():
	isFull = true
	Util.killTween(fluidTween)
	fluidTween = create_tween()
	fluidTween.tween_property(fluid, "levelModification", 0.0, baseLevel + 0.5)

func empty():
	isFull = false
	Util.killTween(fluidTween)
	fluidTween = create_tween()
	fluidTween.tween_property(fluid, "levelModification", baseLevel - 1.0, baseLevel + 0.5)
	Sound.playSound(drinkSound)

func drink():
	setState(false, true)

func consumePotion(event = null, withActivate: bool = true):
	NativeRandomObserver.entry("Items/Potion.gd::consumePotion", self, {"event": event, "withActivate": withActivate})
	if isEmpty():
		var observer7_return_0 = null
		NativeRandomObserver.leave("Items/Potion.gd::consumePotion", self, observer7_return_0, "return_explicit")
		return
	
	drink()
	
	triggerPotion(event)
	
	var affected = getAffectedItems()
	if not affected.empty():
		affected[0].triggerPotion()
		affected[0].miniActivate()
	
	if withActivate:
		activate()
	NativeRandomObserver.leave("Items/Potion.gd::consumePotion", self, null, "return_implicit")

func onTriggerPotion(triggerEvent = null):
	pass

func triggerPotion(triggerEvent = null):
	NativeRandomObserver.entry("Items/Potion.gd::triggerPotion", self, {"triggerEvent": triggerEvent})
	onTriggerPotion(triggerEvent)
	playActivationAnimation()
	EventBus.emitSignal(self, "potion_triggered", [self])
	NativeRandomObserver.leave("Items/Potion.gd::triggerPotion", self, null, "return_implicit")

func onStateChanged(_isFull):
	if _isFull:
		fill()
	else:
		empty()
	
	isFull = _isFull

func activate(damageRes = null, playCombatAni = true, consume = false, 
	animationOverride = null, emitSignal: bool = true):
	NativeRandomObserver.entry("Items/Potion.gd::activate", self, {"damageRes": damageRes, "playCombatAni": playCombatAni, "consume": consume, "animationOverride": animationOverride, "emitSignal": emitSignal})
	
	.activate(damageRes, playCombatAni, consume, null)
	
	if emitSignal:
		EventBus.emitSignal(self, "potion_emptied", [self])
	NativeRandomObserver.leave("Items/Potion.gd::activate", self, null, "return_implicit")

func shopEntered(craft: bool):
	.shopEntered(craft)
	if not isFull:
		fill()

func getAffectedCellsAfterRotate_primary(rotatedCells) -> Array:
	
	
	
	
	if faceDirection == FaceDirection.DOWN:
		return [rotatedCells[1] + Vector2.UP]
	else:
		return [rotatedCells[0] + Vector2.UP]

func addToInventory(_inventory, _occupiedCells: Array, _placedByPlayer: bool):
	.addToInventory(_inventory, _occupiedCells, _placedByPlayer)
	updateConnector()

func onRemoveFromInventory():
	connector.disappear()
	connector.call_deferred("checkState")
	resetGradient()

func onFusingAsIngredient():
	connector.disappear()
	connector.call_deferred("checkState")
	resetGradient()

func onAffectedItemAdded(item, color: int):
	if color == Affected.Primary:
		updateConnector()

func onAffectedItemRemoved(item, color: int):
	if color == Affected.Primary:
		updateConnector()

func updateConnector():
	var affected = getAffectedItems()
	if not affected.empty():
		var affectedPoint = getAffectedPoints()[0]
		connector.global_position = affectedPoint
		connector.position.y += 40
		connector.global_rotation = 0
		
		connector.appear()
		connector.call_deferred("checkState")
		
		
		
		var otherColor = affected[0].potionColor
		var colorDifV = otherColor - potionColor
		var colorDif = abs(colorDifV.r) + abs(colorDifV.g) + abs(colorDifV.b)
		
		fluid.baseFoaminess = baseFoaminess + 0.2
		fluid.baseScroll = baseScroll + 0.01
		if colorDif > 0.5:
			var newGradient = fluidGradient.duplicate()
			for i in newGradient.get_point_count():
				var offset = newGradient.get_offset(i)
				var color = newGradient.get_color(i)
				
				if offset < 0.6:
					var brightness = color.gray()
					
					
					
					var newColor = color
					newColor.h = otherColor.h
					newColor.s = otherColor.s
					if brightness > 0.8:
						newColor += color * 0.8
					newColor.a = color.a
					
					newGradient.set_color(i, newColor)
				
			fluidGradientTex.gradient = newGradient
		
	else:
		connector.disappear()
		connector.call_deferred("checkState")
		resetGradient()

func resetGradient():
	fluidGradientTex.gradient = fluidGradient
	fluid.self_modulate = Color.white
	fluid.baseFoaminess = baseFoaminess
	fluid.baseScroll = baseScroll

func discard(discardGems = true):
	if pooled:
		resetGradient()
		connector.reset()
	.discard(discardGems)

func getStarPosition() -> Vector2:
	var cellSize = 2 * halfCellSize.x * global_scale.x
	if faceDirection == FaceDirection.UP or faceDirection == FaceDirection.DOWN:
		return global_position + Vector2(0, - 1.5 * cellSize)
	elif faceDirection == FaceDirection.RIGHT:
		return global_position + Vector2(0.5 * cellSize, - 1.0 * cellSize)
	else:
		return global_position + Vector2( - 0.5 * cellSize, - 1.0 * cellSize)




