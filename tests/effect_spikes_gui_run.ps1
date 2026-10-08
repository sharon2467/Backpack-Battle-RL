param([string]$RunId = (Get-Date -Format 'yyyyMMdd_HHmmss'))
$ErrorActionPreference = 'Stop'
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunId must contain only letters, digits, underscore or dash' }
$effectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$effectProject = Join-Path $effectRoot 'Backpack Battles'
$effectProjectFile = Join-Path $effectProject 'project.godot'
$effectCharacter = Join-Path $effectProject 'Core/Character.gd'
$effectSharedJson = Join-Path $effectRoot 'data/custom_opponent.json'
$effectTemp = Join-Path $effectProject 'tests/effect_spikes_gui_battle.gd'
$effectAppData = Join-Path $effectRoot ('data/effect_spikes_gui_appdata_' + $RunId)
$effectOut = Join-Path $effectRoot 'data/effect_spikes_gui_stdout.log'
$effectErr = Join-Path $effectRoot 'data/effect_spikes_gui_stderr.log'
if (Test-Path -LiteralPath $effectTemp) { throw 'Temporary test already exists' }
if (Test-Path -LiteralPath $effectAppData) { throw 'Isolated APPDATA already exists' }
$effectBackup = @{}
foreach ($effectPath in @($effectProjectFile,$effectCharacter,$effectSharedJson)) { $effectBackup[$effectPath] = [IO.File]::ReadAllBytes($effectPath) }
$effectOriginalHashes = @{}
foreach ($effectPath in $effectBackup.Keys) { $effectOriginalHashes[$effectPath] = (Get-FileHash -LiteralPath $effectPath -Algorithm SHA256).Hash }
$effectOriginalHashes | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $effectRoot 'data/effect_spikes_gui_original_hashes.json')
$effectPrevAppData = $env:APPDATA
try {
    New-Item -ItemType Directory -Path $effectAppData | Out-Null
    $env:APPDATA = $effectAppData
    if (-not (Test-Path -LiteralPath (Split-Path $effectTemp))) { New-Item -ItemType Directory -Path (Split-Path $effectTemp) | Out-Null }
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'effect_spikes_gui_battle.gd') -Destination $effectTemp
    Copy-Item -LiteralPath (Join-Path $effectRoot 'data/effect_spikes_gui_opponent.json') -Destination $effectSharedJson
    $effectText = [Text.Encoding]::UTF8.GetString($effectBackup[$effectProjectFile])
    $effectMarker = 'InputBlocker="*res://Interface/InputBlocker.tscn"'
    if (-not $effectText.Contains($effectMarker)) { throw 'autoload marker missing' }
    $effectText = $effectText.Replace($effectMarker, $effectMarker + "`nEffectSpikesGui=`"*res://tests/effect_spikes_gui_battle.gd`"")
    [IO.File]::WriteAllText($effectProjectFile,$effectText,(New-Object Text.UTF8Encoding $false))
    $effectText = [Text.Encoding]::UTF8.GetString($effectBackup[$effectCharacter])
    $effectNeedle = 'func applySpikes(damageRes: DamageResult):'
    $effectObservation = @'
func applySpikes(damageRes: DamageResult):
	var obs_source = damageRes.damageSource
	var obs_origin = "system"
	if obs_source.origin is Item:
		obs_origin = obs_source.origin.descriptor.identifier
	print("EFFECT_SPIKES_INPUT ", JSON.print({"defender":playerId,"event":damageRes.event.id,"parent":damageRes.event.parentEvent.id if damageRes.event.parentEvent else -1,"origin":obs_origin,"types":obs_source.types,"flags":obs_source.flags,"hit":damageRes.hit,"damage":damageRes.damage,"health_damage":damageRes.healthDamage,"spikes":getSpikes(),"melee_limit":meleeSpikesLimit,"ranged_limit":rangedSpikesLimit,"effect_limit":effectSpikesLimit,"can_trigger":damageRes.canTriggerSpikes()}))
'@
    if (-not $effectText.Contains($effectNeedle)) { throw 'applySpikes marker missing' }
    $effectText = $effectText.Replace($effectNeedle,$effectObservation.TrimEnd())
    $effectNeedle = "`t`tvar spikeDam = min(getSpikes(), round(damageRes.damage * spikesLimit))"
    if (-not $effectText.Contains($effectNeedle)) { throw 'spikeDam marker missing' }
    $effectText = $effectText.Replace($effectNeedle,$effectNeedle + "`n`t`tprint(`"EFFECT_SPIKES_FORMULA `", JSON.print({`"event`":damageRes.event.id,`"selected_limit`":spikesLimit,`"spike_damage`":spikeDam}))")
    [IO.File]::WriteAllText($effectCharacter,$effectText,(New-Object Text.UTF8Encoding $false))
    $effectProcess = Start-Process -FilePath 'E:\godotsteam\godotsteam.362.editor.win64.exe' -ArgumentList @('--path',('"' + $effectProject + '"')) -WindowStyle Normal -RedirectStandardOutput $effectOut -RedirectStandardError $effectErr -PassThru
    $effectProcess.Id | Set-Content (Join-Path $effectRoot 'data/effect_spikes_gui_pid.txt')
    try { $effectProcess | Wait-Process -Timeout 110 -ErrorAction Stop }
    catch { Stop-Process -Id $effectProcess.Id -ErrorAction SilentlyContinue; throw 'Own experiment process timed out' }
    $effectProcess.Refresh()
    if ($effectProcess.ExitCode -ne 0) { throw "Godot exit $($effectProcess.ExitCode)" }
    if (-not (Select-String -LiteralPath $effectOut -Pattern 'EFFECT_SPIKES_GUI_PASS' -Quiet)) { throw 'PASS marker missing' }
    $effectRows = @(Get-Content -LiteralPath $effectOut | Where-Object { $_.StartsWith('EFFECT_SPIKES_INPUT ') } | ForEach-Object { $_.Substring(20) | ConvertFrom-Json })
    $effectMatched = @()
    foreach ($effectRow in $effectRows) {
        if ($effectRow.types.Count -eq 1 -and $effectRow.types[0] -eq 2 -and $effectRow.flags -eq 63 -and $effectRow.hit -and $effectRow.damage -gt 0 -and $effectRow.spikes -gt 0 -and $effectRow.effect_limit -eq 0 -and $effectRow.melee_limit -eq 1) {
            foreach ($effectChild in $effectRows) {
                if ($effectChild.types.Count -eq 1 -and $effectChild.types[0] -eq 104 -and $effectChild.parent -eq $effectRow.event -and $effectChild.damage -eq [Math]::Min($effectRow.spikes,$effectRow.damage)) { $effectMatched += @{effect=$effectRow;spikes=$effectChild} }
            }
        }
    }
    if ($effectMatched.Count -eq 0) { throw 'No pure Effect event with matching actual Spikes child' }
    $effectMatched | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $effectRoot 'data/effect_spikes_gui_verified_pairs.json')
    Write-Output "EFFECT_SPIKES_EVENT_PAIRS_PASS count=$($effectMatched.Count)"
}
finally {
    $env:APPDATA = $effectPrevAppData
    foreach ($effectPath in $effectBackup.Keys) { [IO.File]::WriteAllBytes($effectPath,$effectBackup[$effectPath]) }
    if (Test-Path -LiteralPath $effectTemp) { Remove-Item -LiteralPath $effectTemp }
    foreach ($effectPath in $effectBackup.Keys) {
        $effectHash = (Get-FileHash -LiteralPath $effectPath -Algorithm SHA256).Hash
        if ($effectHash -ne $effectOriginalHashes[$effectPath]) { throw "Restoration hash mismatch: $effectPath" }
        Write-Output "EFFECT_SPIKES_RESTORED $effectPath $effectHash"
    }
}
