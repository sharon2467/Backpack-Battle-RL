extends Weapon

const stunParticles = preload("res://Items/Particles/StunParticles.tscn")

func onDealtDamage(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/Hammer.gd::onDealtDamage", self, {"damageRes": damageRes})
	if damageRes.hasHit() and rollChance():
		stun(getP_m("dur_stun"), damageRes.event)
		var particles = ObjectPool.particleOneShot(stunParticles, sprite)
		particles.position = Vector2(175, - 144)
	NativeRandomObserver.leave("Items/Hammer.gd::onDealtDamage", self, null, "return_implicit")

func onFusingAsCatalystFinished():
	.onFusingAsCatalystFinished()
	playActivationAnimation()
