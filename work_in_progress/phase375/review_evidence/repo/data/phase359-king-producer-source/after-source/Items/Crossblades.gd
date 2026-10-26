extends Weapon

func canAffect(item):
	return item.canBeEmpowered()

func canAffect_secondary(item):
	return item.hasCooldown()

func onCombatStart():
	NativeRandomObserver.entry("Items/Crossblades.gd::onCombatStart", self, {})
	for item in getAffectedItems(Affected.Primary):
		item.addBonusDamage(getP1())
	
	for item in getAffectedItems(Affected.Secondary):
		item.addSpeed(getP2() / 100.0)
	
	activate(null, false)
	NativeRandomObserver.leave("Items/Crossblades.gd::onCombatStart", self, null, "return_implicit")

func onPreDealDamage_early(damageRes: DamageResult):
	NativeRandomObserver.entry("Items/Crossblades.gd::onPreDealDamage_early", self, {"damageRes": damageRes})
	if damageRes.hasHit():
		addBonusDamage(getP3())
		addSpeed(getP4() / 100.0)
	NativeRandomObserver.leave("Items/Crossblades.gd::onPreDealDamage_early", self, null, "return_implicit")

func getCraftingOffset(forDirection):
	match forDirection:
		FaceDirection.UP:
			return Vector2( - 1, 0)
		FaceDirection.DOWN:
			return Vector2( - 1, 0)
		FaceDirection.LEFT:
			return Vector2(0, - 1)
		FaceDirection.RIGHT:
			return Vector2(0, - 1)
