extends Weapon

const activationParticles = preload("res://Items/Particles/ThornWhipActivationParticles.tscn")

func onPrepare():
	NativeRandomObserver.entry("Items/ThornWhip.gd::onPrepare", self, {})
	connectForCombat(character(), "character_spikes_changed", "onSpikesChanged")
	NativeRandomObserver.leave("Items/ThornWhip.gd::onPrepare", self, null, "return_implicit")

func onPreDealDamage_early(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/ThornWhip.gd::onPreDealDamage_early", self, {"damageRes": damageRes})
	if damageRes.hasHit():
		giveSpikes(1)
		ObjectPool.particleOneShot(activationParticles, sprite)
	NativeRandomObserver.leave("Items/ThornWhip.gd::onPreDealDamage_early", self, null, "return_implicit")

func onSpikesChanged(amount, _event):
	NativeRandomObserver.entry("Items/ThornWhip.gd::onSpikesChanged", self, {"amount": amount, "_event": _event})
	changeVaryingDamage(getP1() * amount)
	NativeRandomObserver.leave("Items/ThornWhip.gd::onSpikesChanged", self, null, "return_implicit")

