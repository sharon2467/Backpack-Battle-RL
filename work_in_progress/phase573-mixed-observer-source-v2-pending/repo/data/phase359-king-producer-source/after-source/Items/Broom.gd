extends Weapon

const blindParticles = preload("res://Items/Particles/DirtParticles.tscn")

onready var bonusDamPerMiss = int(getP1())

var broomBonusDam = 0
var onMissReadyTime = 0.0

func onPrepare():
	NativeRandomObserver.entry("Items/Broom.gd::onPrepare", self, {})
	connectForCombat(character(), "character_attacked", "onAttacked")
	NativeRandomObserver.leave("Items/Broom.gd::onPrepare", self, null, "return_implicit")

func onAttacked(damageRes):
	NativeRandomObserver.entry("Items/Broom.gd::onAttacked", self, {"damageRes": damageRes})
	if not damageRes.hasHit():
		addBonusDamage(bonusDamPerMiss)
		broomBonusDam += bonusDamPerMiss
	NativeRandomObserver.leave("Items/Broom.gd::onAttacked", self, null, "return_implicit")

func attack(event = null):
	NativeRandomObserver.entry("Items/Broom.gd::attack", self, {"event": event})
	.attack(event)
	if broomBonusDam != 0:
		reduceBonusDamage(broomBonusDam, false)
		broomBonusDam = 0
	NativeRandomObserver.leave("Items/Broom.gd::attack", self, null, "return_implicit")

func onDealtDamage(damageRes):
	NativeRandomObserver.entry("Items/Broom.gd::onDealtDamage", self, {"damageRes": damageRes})
	if damageRes.hasHit():
		if rollChance():
			inflictBlind(1, damageRes.event)
			var particles = ObjectPool.particleOneShot(blindParticles, sprite)
			particles.position = Vector2(0, 230)
			particles.global_rotation = 0
	NativeRandomObserver.leave("Items/Broom.gd::onDealtDamage", self, null, "return_implicit")

func onShopEntered():
	broomBonusDam = 0
