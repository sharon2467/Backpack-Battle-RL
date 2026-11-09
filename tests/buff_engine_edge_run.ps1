param(
    [string]$RunId = (Get-Date -Format 'yyyyMMdd_HHmmss'),
    [ValidateSet('source_probe', 'smoke', 'negative_left', 'full_cap', 'cleanse_resistance')][string]$Mode = 'source_probe',
    [int]$TimeoutSeconds = 180,
    [ValidateSet('original', 'godotsteam')][string]$Engine = 'original',
    [switch]$TemporarilyHideInstalledPack,
    [switch]$EnableEditorStartupFeatures,
    [switch]$DisableSteamIntegration,
    [switch]$PreviewOnly
)
$ErrorActionPreference = 'Stop'

function Get-OracleSourceHashes([string[]]$Paths) {
    $result = @{}
    foreach ($path in $Paths) {
        $result[$path] = if (Test-Path -LiteralPath $path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash } else { 'MISSING' }
    }
    return $result
}

function Write-OracleUtf8([string]$Path, [string]$Text) {
    [IO.File]::WriteAllText($Path, $Text, [Text.UTF8Encoding]::new($false))
}

function Add-OracleObservation([string]$Text, [string]$Needle, [string]$Replacement) {
    $count = [regex]::Matches($Text, [regex]::Escape($Needle)).Count
    if ($count -ne 1) { throw "Observation marker must occur once, found $count : $Needle" }
    return $Text.Replace($Needle, $Replacement)
}

if ($RunId -notmatch '^[A-Za-z0-9_-]+$') { throw 'Invalid RunId' }
if (($Mode -eq 'cleanse_resistance' -or $PreviewOnly) -and ($Engine -ne 'godotsteam' -or $TemporarilyHideInstalledPack -or $EnableEditorStartupFeatures -or $DisableSteamIntegration)) { throw 'Cleanse experiment uses only GodotSteam without installation or feature adaptation switches' }
if ($PreviewOnly -and $Mode -ne 'cleanse_resistance') { throw 'PreviewOnly is limited to the cleanse experiment' }
if ($EnableEditorStartupFeatures -and ($Engine -ne 'original' -or $Mode -eq 'source_probe')) { throw 'Startup features require explicit original engine and a non-metadata mode' }
if ($DisableSteamIntegration -and -not $EnableEditorStartupFeatures) { throw 'Disabling Steam requires explicit startup feature adaptation' }
if ($TimeoutSeconds -lt 10 -or $TimeoutSeconds -gt 600) { throw 'TimeoutSeconds must be in 10..600' }
$oracleRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$oracleProject = (Resolve-Path (Join-Path $oracleRoot 'Backpack Battles')).Path
$oracleRun = Join-Path $oracleRoot ($(if ($Mode -eq 'cleanse_resistance') { 'data/buff_cleanse_resistance/' } else { 'data/buff_engine_edge/' }) + $RunId)
$oracleData = Join-Path $oracleRun 'data'
$oracleOriginalExe = 'E:/steam/steamapps/common/Backpack Battles/BackpackBattles.exe'
$oraclePack = 'E:/steam/steamapps/common/Backpack Battles/BackpackBattles.pck'
$oracleTemporaryPack = $oraclePack + '.codex_buff_edge_' + $RunId + '.disabled'
$oracleExe = if ($Engine -eq 'original') { $oracleOriginalExe } else { 'E:/godotsteam/godotsteam.362.editor.win64.exe' }
$oracleProjectFile = Join-Path $oracleProject 'project.godot'
$oracleBuffFile = Join-Path $oracleProject 'Core/Buff.gd'
$oracleJson = Join-Path $oracleRoot 'data/custom_opponent.json'
$oracleSharedPaths = @($oracleProjectFile, $oracleBuffFile, (Join-Path $oracleProject 'Core/Character.gd'), (Join-Path $oracleProject 'Core/Game.gd'), (Join-Path $oracleProject 'Utility/SteamHelper.gd'), (Join-Path $oracleProject 'Sheets/CSV/ItemData.csv'), (Join-Path $oracleProject 'Sheets/CSV/ItemData_e.csv'), $oracleJson, $oracleExe)
if ($Engine -eq 'original') { $oracleSharedPaths += $oraclePack }
if (Test-Path -LiteralPath $oracleRun) { throw "Evidence path already exists: $oracleRun" }
if ($TemporarilyHideInstalledPack) {
    if ($Engine -ne 'original') { throw 'PCK rename is only allowed with explicit original engine' }
    if (Get-Process -Name BackpackBattles -ErrorAction SilentlyContinue) { throw 'An existing game process is running; not touching the installation' }
    if (-not (Test-Path -LiteralPath $oraclePack) -or (Test-Path -LiteralPath $oracleTemporaryPack)) { throw 'PCK source missing or unique temporary name occupied; do not overwrite' }
    $oracleInstallation = (Resolve-Path -LiteralPath 'E:/steam/steamapps/common/Backpack Battles').Path
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($oracleTemporaryPack)), $oracleInstallation)) { throw 'Temporary package path is outside named installation directory' }
}
$oracleBefore = Get-OracleSourceHashes $oracleSharedPaths
if ($Engine -eq 'original' -and $oracleBefore[$oracleOriginalExe] -ne '4522A5F2B71FE2AA5F7F730A2BD71F66F4F8112609164BCEF39C110F047AD577') { throw 'Unexpected original executable SHA256' }
if ($Engine -eq 'godotsteam' -and $oracleBefore[$oracleExe] -ne '100B76E344A040D2CA50D1B4D03B097A259C35B32D5865043F33486A666EDA1C') { throw 'Unexpected selected GodotSteam executable SHA256' }
$oraclePreviousAppData = $env:APPDATA
$oraclePreviousLocalAppData = $env:LOCALAPPDATA
$oraclePreviousData = $env:BB_BUFF_EDGE_RUN_DATA
$oraclePreviousSha = $env:BB_BUFF_EDGE_EXPECTED_SHA
$oracleProcess = $null
$oracleBackups = @{}
$oracleWritten = @{}
$oracleResults = @()
$oraclePackMoved = $false
try {
    New-Item -ItemType Directory -Path $oracleData, (Join-Path $oracleRun 'original_bytes') | Out-Null
    Write-OracleUtf8 (Join-Path $oracleRun 'source_hashes_before.json') ($oracleBefore | ConvertTo-Json)
    if ($TemporarilyHideInstalledPack) {
        Write-OracleUtf8 (Join-Path $oracleRun 'package_move.json') (@{source=$oraclePack; temporary=$oracleTemporaryPack; before_sha256=$oracleBefore[$oraclePack]; state='before_move'} | ConvertTo-Json)
        Move-Item -LiteralPath $oraclePack -Destination $oracleTemporaryPack
        $oraclePackMoved = $true
        Write-OracleUtf8 (Join-Path $oracleRun 'package_move.json') (@{source=$oraclePack; temporary=$oracleTemporaryPack; before_sha256=$oracleBefore[$oraclePack]; state='temporarily_renamed'} | ConvertTo-Json)
        Write-Output 'BUFF_EDGE_INSTALLED_PCK_TEMPORARILY_RENAMED'
    }
    if ($Mode -ne 'source_probe') {
        foreach ($path in @($oracleProjectFile, $oracleBuffFile, $oracleJson)) {
            $oracleBackups[$path] = if (Test-Path -LiteralPath $path) { [IO.File]::ReadAllBytes($path) } else { $null }
            if ($null -ne $oracleBackups[$path]) { [IO.File]::WriteAllBytes((Join-Path $oracleRun ('original_bytes/' + [IO.Path]::GetFileName($path) + '.bin')), $oracleBackups[$path]) }
        }
        $oracleText = [IO.File]::ReadAllText($oracleProjectFile).Replace("`r`n", "`n")
        if ($EnableEditorStartupFeatures) {
            if ($oracleText.Contains('custom_features=')) { throw 'Existing custom_features need explicit merge review' }
            $oracleFeatures = if ($DisableSteamIntegration) { 'full_version,editor,disable_steam_integration' } else { 'full_version,editor' }
            $oracleText = Add-OracleObservation $oracleText 'config_version=4' ('config_version=4' + "`n`n" + '_custom_features="' + $oracleFeatures + '"')
        }
        $oracleAutoload = 'BuffEngineEdge="*' + (Join-Path $PSScriptRoot 'buff_engine_edge_battle.gd').Replace('\','/') + '"'
        $oracleText = Add-OracleObservation $oracleText 'ControllerIcons="*res://addons/controller_icons/ControllerIcons.gd"' ($oracleAutoload + "`n" + 'ControllerIcons="*res://addons/controller_icons/ControllerIcons.gd"')
        $oraclePreparedProject = if ($PreviewOnly) { Join-Path $oracleRun 'prepared_project.godot' } else { $oracleProjectFile }
        Write-OracleUtf8 $oraclePreparedProject $oracleText
        if (-not $PreviewOnly) { $oracleWritten[$oracleProjectFile] = (Get-FileHash -LiteralPath $oracleProjectFile -Algorithm SHA256).Hash }
        $oracleText = [IO.File]::ReadAllText($oracleBuffFile).Replace("`r`n", "`n")
        $oracleNeedle = "`tvar event = null`n`t`n`tif amount > 0:"
        $oracleReplacement = @'
	var event = null
	var oracle_call_id = BuffEngineEdge.new_call_id()
	BuffEngineEdge.observe("enter", oracle_call_id, self, {"request":amount,"duration":duration,"incoming_reflected":reflect,"source":item.descriptor.identifier if item != null else null,"trigger_parent":triggerEvent.id if triggerEvent != null else -1})
	
	if amount > 0:
'@
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle $oracleReplacement
        $oracleNeedle = "`t`tvar left = amount - resisted"
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle ($oracleNeedle + "`n`t`tBuffEngineEdge.observe(`"after_resist`", oracle_call_id, self, {`"amount`":amount,`"resisted`":resisted,`"left`":left})")
        $oracleNeedle = "`t`t`tvar ownStacksUsed = min(left, resistStacks)"
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle ("`t`t`tBuffEngineEdge.observe(`"before_own_resist`", oracle_call_id, self, {`"amount`":amount,`"resisted`":resisted,`"left`":left,`"reflected_count`":reflected})`n" + $oracleNeedle)
        $oracleNeedle = "`t`t`tresistStacks -= ownStacksUsed"
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle ($oracleNeedle + "`n`t`t`tBuffEngineEdge.observe(`"after_own_resist`", oracle_call_id, self, {`"amount`":amount,`"resisted`":resisted,`"left`":left,`"reflected_count`":reflected,`"own_stacks_used`":ownStacksUsed})")
        $oracleNeedle = "`t`t`tamount = int(min(amount, MAX_STACKS - current))"
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle ("`t`t`tBuffEngineEdge.observe(`"before_cap`", oracle_call_id, self, {`"amount`":amount,`"resisted`":resisted,`"reflected_count`":reflected})`n" + $oracleNeedle + "`n`t`t`tBuffEngineEdge.observe(`"after_cap`", oracle_call_id, self, {`"amount`":amount,`"resisted`":resisted,`"reflected_count`":reflected})")
        $oracleNeedle = "`t`t`tif amount == 0: return null"
        $oracleReplacement = @'
			if amount == 0:
				BuffEngineEdge.observe("cap_zero_return", oracle_call_id, self, {"amount":amount,"reflected_count":reflected})
				return null
'@
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle $oracleReplacement
        $oracleNeedle = "`t`tif reflected > 0:`n`t`t`tcharacter.opponent.gainStacksTemporary"
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle ("`t`tBuffEngineEdge.observe(`"before_reflect_dispatch`", oracle_call_id, self, {`"amount`":amount,`"reflected_count`":reflected,`"event_id`":event.id if event != null else -1})`n" + $oracleNeedle)
        $oracleNeedle = "`n`treturn event`n"
        $oracleText = Add-OracleObservation $oracleText $oracleNeedle ("`n`tBuffEngineEdge.observe(`"exit`", oracle_call_id, self, {`"event_id`":event.id if event != null else -1})" + $oracleNeedle)
        if ($Mode -eq 'cleanse_resistance') {
            $oracleNeedle = "`tamount = min(current, amount)"
            $oracleReplacement = @'
	var oracle_loss_call_id = BuffEngineEdge.new_call_id()
	BuffEngineEdge.observe("lose_enter", oracle_loss_call_id, self, {"request":amount,"used":used,"source":item.descriptor.identifier if item != null else null,"trigger_parent":triggerEvent.id if triggerEvent != null else -1})
	amount = min(current, amount)
	BuffEngineEdge.observe("lose_after_cap", oracle_loss_call_id, self, {"amount":amount})
'@
            $oracleText = Add-OracleObservation $oracleText $oracleNeedle $oracleReplacement
            $oracleNeedle = "`t`tamount = clamp(amount, 0, current)"
            $oracleText = Add-OracleObservation $oracleText $oracleNeedle ($oracleNeedle + "`n`t`tBuffEngineEdge.observe(`"lose_after_probability`", oracle_loss_call_id, self, {`"amount`":amount,`"protected`":protected})")
            $oracleNeedle = "`t`t`tresistStacks -= protectedByStacks"
            $oracleText = Add-OracleObservation $oracleText $oracleNeedle ($oracleNeedle + "`n`t`t`tBuffEngineEdge.observe(`"lose_after_type_resist`", oracle_loss_call_id, self, {`"amount`":amount,`"protected`":protected,`"protected_by_type`":protectedByStacks})")
            $oracleNeedle = "`t`tif protected > 0:"
            $oracleText = Add-OracleObservation $oracleText $oracleNeedle ("`t`tBuffEngineEdge.observe(`"lose_after_global_protect`", oracle_loss_call_id, self, {`"amount`":amount,`"protected`":protected})`n" + $oracleNeedle)
            $oracleNeedle = "`t`t`tEventBus.logEvent(protectedEvent)"
            $oracleText = Add-OracleObservation $oracleText $oracleNeedle ($oracleNeedle + "`n`t`t`tBuffEngineEdge.observe(`"lose_protect_event`", oracle_loss_call_id, self, {`"protected_event_id`":protectedEvent.id})")
            $oracleNeedle = "`treturn changeCurrentLogShowLabel(false, amount, item, triggerEvent, used)"
            $oracleReplacement = @'
	var oracle_loss_event = changeCurrentLogShowLabel(false, amount, item, triggerEvent, used)
	BuffEngineEdge.observe("lose_exit", oracle_loss_call_id, self, {"event_id":oracle_loss_event.id if oracle_loss_event != null else -1})
	return oracle_loss_event
'@
            $oracleText = Add-OracleObservation $oracleText $oracleNeedle $oracleReplacement
            $oracleNeedle = "`tvar change = min(current, amount)"
            $oracleText = Add-OracleObservation $oracleText $oracleNeedle ($oracleNeedle + "`n`tBuffEngineEdge.observe(`"lose_actual`", BuffEngineEdge.current_call_id(self), self, {`"actual`":change,`"timeout`":isTimeout})")
        }
        $oraclePreparedBuff = if ($PreviewOnly) { Join-Path $oracleRun 'prepared_Buff.gd' } else { $oracleBuffFile }
        Write-OracleUtf8 $oraclePreparedBuff $oracleText
        if (-not $PreviewOnly) { $oracleWritten[$oracleBuffFile] = (Get-FileHash -LiteralPath $oracleBuffFile -Algorithm SHA256).Hash }
        $oracleLocations = @(Select-String -LiteralPath $oraclePreparedBuff,$oraclePreparedProject -Pattern 'BuffEngineEdge|oracle_call_id|oracle_loss' | Select-Object Path,LineNumber,Line)
        Write-OracleUtf8 (Join-Path $oracleRun 'probe_locations.json') ($oracleLocations | ConvertTo-Json)
        $oracleDiff = & git -c core.autocrlf=false diff --no-index -- (Join-Path $oracleRun 'original_bytes/Buff.gd.bin') $oraclePreparedBuff
        Write-OracleUtf8 (Join-Path $oracleRun 'buff_observation.diff') ($oracleDiff -join "`n")
        $oracleDiff = & git -c core.autocrlf=false diff --no-index -- (Join-Path $oracleRun 'original_bytes/project.godot.bin') $oraclePreparedProject
        Write-OracleUtf8 (Join-Path $oracleRun 'autoload_observation.diff') ($oracleDiff -join "`n")
        if ($PreviewOnly) { Write-Output "BUFF_EDGE_PREVIEW_ONLY $oracleRun"; return }
    }
    $oracleCases = switch ($Mode) {
        'source_probe' { @(@{name='source_probe';mode='source_probe'}) }
        'smoke' { @(@{name='smoke';mode='smoke'}) }
        'full_cap' { @(@{name='full_cap';mode='full_cap'}) }
        'cleanse_resistance' { @(@{name='C_overlap';mode='cleanse_resistance';mirrors=$true},@{name='C_no_mirror';mode='cleanse_resistance';mirrors=$false}) }
        default { @(@{name='N_overlap';mode='negative_left';elephants=$true;mirrors=$true},@{name='R_resist_only';mode='negative_left';elephants=$true;mirrors=$false},@{name='F_reflect_only';mode='negative_left';elephants=$false;mirrors=$true}) }
    }
    if ($Mode -ne 'source_probe') {
        $oracleOpponentItems = @(@{item_index=11;x=0;y=0;f=0},@{item_index=20;x=0;y=0;f=0})
        if ($Mode -eq 'full_cap') {
            $oracleOpponentItems = @()
            foreach ($y in @(0,2,4)) { foreach ($x in @(0,2,4,6)) { $oracleOpponentItems += @{item_index=11;x=$x;y=$y;f=0} } }
            foreach ($x in 0..6) { $oracleOpponentItems += @{item_index=148;x=$x;y=0;f=0} }
            $oracleOpponentItems += @{item_index=332;x=7;y=0;f=0}
        }
        if ($Mode -eq 'cleanse_resistance') {
            $oracleOpponentItems = @()
            foreach ($y in @(0,2,4)) { foreach ($x in @(0,2,4,6)) { $oracleOpponentItems += @{item_index=11;x=$x;y=$y;f=0} } }
            foreach ($x in 0..6) { $oracleOpponentItems += @{item_index=148;x=$x;y=0;f=0} }
            $oracleOpponentItems += @{item_index=424;x=3;y=3;f=0}
        }
        $oracleOpponent = @{schema_version=1;game_version='1.1.8';class=0;health=25;stamina=5;items=$oracleOpponentItems}
        Write-OracleUtf8 $oracleJson ($oracleOpponent | ConvertTo-Json -Depth 8)
        $oracleWritten[$oracleJson] = (Get-FileHash -LiteralPath $oracleJson -Algorithm SHA256).Hash
        Write-OracleUtf8 (Join-Path $oracleData 'custom_opponent_input.json') ($oracleOpponent | ConvertTo-Json -Depth 8)
    }
    foreach ($oracleCase in $oracleCases) {
        $oracleCaseName = $oracleCase.name
        $oracleCase.expected_engine = $Engine
        $oracleCase.expected_exe_sha256 = $oracleBefore[$oracleExe]
        $oracleCase.original_buff_sha256 = $oracleBefore[$oracleBuffFile]
        Write-OracleUtf8 (Join-Path $oracleData 'case.json') ($oracleCase | ConvertTo-Json)
        Write-OracleUtf8 (Join-Path $oracleData ($oracleCaseName + '_case.json')) ($oracleCase | ConvertTo-Json)
        $oracleCaseAppData = Join-Path $oracleRun ('appdata/' + $oracleCaseName)
        $oracleCaseLocalData = Join-Path $oracleRun ('localappdata/' + $oracleCaseName)
        New-Item -ItemType Directory -Path $oracleCaseAppData,$oracleCaseLocalData -Force | Out-Null
        $env:APPDATA = $oracleCaseAppData
        $env:LOCALAPPDATA = $oracleCaseLocalData
        $env:BB_BUFF_EDGE_RUN_DATA = $oracleData
        $env:BB_BUFF_EDGE_EXPECTED_SHA = if ($Mode -eq 'source_probe') { $oracleBefore[$oracleBuffFile] } else { $oracleWritten[$oracleBuffFile] }
        $oracleStdout = Join-Path $oracleData ($oracleCaseName + '_stdout.log')
        $oracleStderr = Join-Path $oracleData ($oracleCaseName + '_stderr.log')
        $oracleArguments = @('--path',('"'+$oracleProject+'"'),'--windowed','--resolution','1280x720')
        if ($Mode -eq 'source_probe') { $oracleArguments += @('--script',('"'+(Join-Path $PSScriptRoot 'buff_engine_source_probe.gd')+'"')) }
        Write-Output "BUFF_EDGE_START $oracleCaseName engine=$Engine"
        $oracleStartedUtc = [DateTime]::UtcNow
        $oracleProcess = Start-Process -FilePath $oracleExe -WorkingDirectory $oracleProject -ArgumentList $oracleArguments -WindowStyle Hidden -RedirectStandardOutput $oracleStdout -RedirectStandardError $oracleStderr -PassThru
        Write-OracleUtf8 (Join-Path $oracleData ($oracleCaseName + '_process.json')) (@{pid=$oracleProcess.Id;exe=$oracleExe;engine=$Engine;working_directory=$oracleProject;arguments=$oracleArguments;runner_launch_utc=$oracleStartedUtc.ToString('o')} | ConvertTo-Json)
        if (-not $oracleProcess.WaitForExit($TimeoutSeconds * 1000)) { throw "Own experiment process timed out: $oracleCaseName PID=$($oracleProcess.Id)" }
        $oracleExitedUtc = [DateTime]::UtcNow
        $oracleProcess.Refresh()
        $oracleLines = @(Get-Content -LiteralPath $oracleStdout)
        $oracleLog = Get-ChildItem -LiteralPath $oracleCaseAppData -Filter godot.log -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($null -ne $oracleLog) {
            Copy-Item -LiteralPath $oracleLog.FullName -Destination (Join-Path $oracleData ($oracleCaseName + '_godot.log'))
            if (-not ($oracleLines | Where-Object { $_.StartsWith('BUFF_EDGE_') })) { $oracleLines = @(Get-Content -LiteralPath $oracleLog.FullName) }
        }
        Write-OracleUtf8 (Join-Path $oracleData ($oracleCaseName + '_exit.json')) (@{exit_code=$oracleProcess.ExitCode;runner_observed_exit_utc=$oracleExitedUtc.ToString('o');runner_elapsed_seconds=($oracleExitedUtc-$oracleStartedUtc).TotalSeconds} | ConvertTo-Json)
        $oracleMarker = if ($Mode -eq 'source_probe') { 'BUFF_EDGE_SOURCE_PASS' } else { 'BUFF_EDGE_PASS ' }
        if ($oracleProcess.ExitCode -ne 0 -or -not ($oracleLines | Where-Object { $_.StartsWith($oracleMarker) })) {
            $oracleLines | Select-Object -Last 20
            Get-Content -LiteralPath $oracleStderr -Tail 20
            throw "Case $oracleCaseName failed: exit=$($oracleProcess.ExitCode), inspect $oracleRun"
        }
        if ($Mode -eq 'source_probe' -or $Mode -eq 'smoke') {
            $oracleResults += @{case=$oracleCaseName;passed=$true;engine=$Engine;exit_code=$oracleProcess.ExitCode}
        } else {
            $oracleTrace = @($oracleLines | Where-Object { $_.StartsWith('BUFF_EDGE_TRACE ') } | ForEach-Object { $_.Substring(16) | ConvertFrom-Json })
            $oracleEvents = @($oracleLines | Where-Object { $_.StartsWith('BUFF_EDGE_EVENT ') } | ForEach-Object { $_.Substring(16) | ConvertFrom-Json })
            $oracleFinal = $oracleLines | Where-Object { $_.StartsWith('BUFF_EDGE_FINAL ') } | Select-Object -Last 1 | ForEach-Object { $_.Substring(16) | ConvertFrom-Json }
            if ($Mode -eq 'cleanse_resistance') {
                $oracleCleanseFinal = $oracleLines | Where-Object { $_.StartsWith('BUFF_EDGE_CLEANSE_FINAL ') } | Select-Object -Last 1 | ForEach-Object { $_.Substring(24) | ConvertFrom-Json }
                $oracleSuccess = $oracleTrace | Where-Object { $_.call_id -eq $oracleCleanseFinal.successful_lose_id -and $_.stage -eq 'lose_exit' } | Select-Object -First 1
                if ($null -eq $oracleSuccess -or $oracleSuccess.source -ne 'Wisdom Puppy' -or $oracleSuccess.target -ne 0 -or $oracleSuccess.type -ne 110 -or $oracleSuccess.used -or $oracleSuccess.initial_current -le 0 -or $oracleSuccess.initial_resist_stacks -ne 0 -or $oracleSuccess.actual -ne 1 -or $oracleSuccess.current -ne ($oracleSuccess.initial_current - 1)) { throw 'Missing natural Puppy cleanse with no typed resistance' }
                $oracleSuccessEvent = $oracleEvents | Where-Object { $_.id -eq $oracleSuccess.event_id -and $_.origin -eq 'Wisdom Puppy' -and $_.target -eq 0 -and $_.params.amount -eq -1 -and -not $_.params.protected -and -not $_.params.resisted -and -not $_.params.used } | Select-Object -First 1
                if ($null -eq $oracleSuccessEvent) { throw 'Natural cleanse lacks the actual negative native Cold event' }
                $oracleBlockedGain = $null
                $oracleBlockedLoss = $null
                $oracleProtectEvent = $null
                if ($oracleCase.mirrors) {
                    $oracleBlockedGain = $oracleTrace | Where-Object { $_.call_id -eq $oracleCleanseFinal.blocked_gain_id -and $_.stage -eq 'after_own_resist' } | Select-Object -First 1
                    $oracleGainBefore = $oracleTrace | Where-Object { $_.call_id -eq $oracleCleanseFinal.blocked_gain_id -and $_.stage -eq 'before_own_resist' } | Select-Object -First 1
                    $oracleBlockedLoss = $oracleTrace | Where-Object { $_.call_id -eq $oracleCleanseFinal.blocked_lose_id -and $_.stage -eq 'lose_exit' } | Select-Object -First 1
                    if ($null -eq $oracleBlockedGain -or $oracleBlockedGain.source -ne 'Snowmaster' -or $oracleBlockedGain.target -ne 0 -or $oracleBlockedGain.initial_current -le 0 -or $oracleBlockedGain.initial_resist_stacks -ne 0 -or $oracleBlockedGain.request -ne 1 -or $oracleGainBefore.left -ne -1 -or $oracleGainBefore.resisted -ne 1 -or $oracleGainBefore.reflected_count -ne 1 -or $oracleBlockedGain.own_stacks_used -ne -1 -or $oracleBlockedGain.resist_stacks -ne 1) { throw 'Missing natural already-Cold negative-left regeneration' }
                    if ($null -eq $oracleBlockedLoss -or $oracleBlockedLoss.source -ne 'Wisdom Puppy' -or $oracleBlockedLoss.target -ne 0 -or $oracleBlockedLoss.used -or $oracleBlockedLoss.initial_current -le 0 -or $oracleBlockedLoss.initial_resist_stacks -ne 1 -or $oracleBlockedLoss.protected_by_type -ne 1 -or $oracleBlockedLoss.protected -ne 1 -or $oracleBlockedLoss.actual -ne 0 -or $oracleBlockedLoss.current -ne $oracleBlockedLoss.initial_current -or $oracleBlockedLoss.resist_stacks -ne 0 -or $oracleBlockedLoss.event_id -ne -1) { throw 'Puppy did not consume the regenerated typed reserve and prevent its own cleanse' }
                    if ($oracleTrace | Where-Object { $_.target -eq 0 -and $_.type -eq 110 -and $_.stage -in @('enter','lose_enter') -and $_.call_id -gt $oracleBlockedGain.call_id -and $_.call_id -lt $oracleBlockedLoss.call_id }) { throw 'Another target Cold operation interrupted the claimed regeneration/cleanse chain' }
                    $oracleProtectEvent = $oracleEvents | Where-Object { $_.id -eq $oracleBlockedLoss.protected_event_id -and $_.origin -eq 'Wisdom Puppy' -and $_.target -eq 0 -and $_.params.protected -and $_.params.amount -eq 1 } | Select-Object -First 1
                    if ($null -eq $oracleProtectEvent) { throw 'Blocked cleanse lacks its real native Protect event' }
                    if (-not ($oracleEvents | Where-Object { $_.target -eq 0 -and $_.params.amount -gt 0 -and -not $_.params.protected -and -not $_.params.resisted -and $_.time -lt $oracleBlockedGain.combat_time })) { throw 'No actual positive Cold event preceded regeneration' }
                }
                if ($oracleFinal.player_damage_resistance -ne 105 -or $oracleFinal.opponent_damage_resistance -ne 105) { throw 'Natural Deer damage resistance changed' }
                $oracleResult = @{case=$oracleCaseName;passed=$true;engine=$Engine;regenerated_gain=$oracleBlockedGain;blocked_cleanse=$oracleBlockedLoss;protect_event=$oracleProtectEvent;successful_cleanse=$oracleSuccess;successful_event=$oracleSuccessEvent;final=$oracleCleanseFinal;native_cold_events=$oracleEvents;global_positive_inventory_tested=$false}
            } elseif ($Mode -eq 'full_cap') {
                $oracleNaturalPartial = @($oracleTrace | Where-Object { $_.stage -eq 'before_reflect_dispatch' -and $_.source -eq 'Gigawatz' -and $_.target -eq 1 -and $_.initial_current -lt 10000 -and $_.reflected_count -in @(1,2) })
                $oracleSuppressed = @($oracleTrace | Where-Object { $_.stage -eq 'cap_zero_return' -and $_.source -eq 'Gigawatz' -and $_.target -eq 1 -and $_.initial_current -eq 10000 -and $_.reflected_count -in @(1,2) })
                if ($oracleNaturalPartial.Count -eq 0 -or $oracleSuppressed.Count -eq 0 -or -not $oracleFinal.precap_partial -or -not $oracleFinal.cap_partial -or -not $oracleFinal.cap_full) { throw 'Full-cap observations incomplete' }
                foreach ($row in $oracleSuppressed) {
                    $capBefore = $oracleTrace | Where-Object { $_.call_id -eq $row.call_id -and $_.stage -eq 'before_cap' } | Select-Object -First 1
                    if ($null -eq $capBefore -or $row.request -ne 3 -or $capBefore.amount -ne (3 - $row.reflected_count) -or $capBefore.current -ne 10000 -or $capBefore.resist_chance -ne 0 -or $capBefore.reflect_chance -ne 20) { throw 'Suppressed call did not have the required positive pre-cap remainder' }
                    if ($oracleTrace | Where-Object { $_.stage -eq 'enter' -and $_.parent_call -eq $row.call_id }) { throw 'Suppressed full-cap call unexpectedly dispatched a child' }
                }
                $oraclePairs = @()
                foreach ($parentRow in @($oracleNaturalPartial) + @($oracleTrace | Where-Object { $_.stage -eq 'before_reflect_dispatch' -and $_.source -eq 'Hawk Rune' -and $_.target -eq 1 -and $_.initial_current -eq 10000 -and $_.reflected_count -eq 1 })) {
                    if (($parentRow.source -eq 'Gigawatz' -and $parentRow.request -ne 3) -or ($parentRow.source -eq 'Hawk Rune' -and $parentRow.request -ne 1)) { throw 'Natural source request amount differs from authoritative item parameters' }
                    foreach ($child in @($oracleTrace | Where-Object { $_.stage -eq 'enter' -and $_.parent_call -eq $parentRow.call_id -and $_.incoming_reflected -and $_.target -eq 0 })) {
                        $childEnd = $oracleTrace | Where-Object { $_.call_id -eq $child.call_id -and $_.stage -eq 'exit' } | Select-Object -First 1
                        $nativeEvent = $oracleEvents | Where-Object { $_.id -eq $childEnd.event_id -and $_.params.reflected -and $_.target -eq 0 -and $_.origin -eq $parentRow.source -and $_.params.amount -eq $parentRow.reflected_count } | Select-Object -First 1
                        if ($null -ne $nativeEvent) { $oraclePairs += @{parent=$parentRow;child=$child;native_event=$nativeEvent} }
                    }
                }
                if (-not ($oraclePairs | Where-Object { $_.parent.source -eq 'Gigawatz' }) -or -not ($oraclePairs | Where-Object { $_.parent.source -eq 'Hawk Rune' })) { throw 'Missing real native reflected-event pairs for the before-cap and full-reflection controls' }
                if ($oracleFinal.player_damage_resistance -ne 105 -or $oracleFinal.opponent_damage_resistance -ne 105 -or $oracleFinal.opponent_blind -ne 10000) { throw 'Natural full-cap/Deer conditions changed' }
                $oracleResult = @{case=$oracleCaseName;passed=$true;engine=$Engine;precap_partial=$oracleNaturalPartial;cap_partial=$oracleSuppressed;reflected_pairs=$oraclePairs;final=$oracleFinal;native_blind_events=$oracleEvents}
            } else {
                $oracleIncoming = $oracleTrace | Where-Object { $_.stage -eq 'enter' -and $_.type -eq 109 -and $_.target -eq 0 -and $_.source -eq 'Pocket Sand' -and -not $_.incoming_reflected } | Select-Object -First 1
                if ($null -eq $oracleIncoming) { throw "Missing natural Pocket Sand call: $oracleCaseName" }
                $oracleOwnBefore = $oracleTrace | Where-Object { $_.call_id -eq $oracleIncoming.call_id -and $_.stage -eq 'before_own_resist' } | Select-Object -First 1
                $oracleOwnAfter = $oracleTrace | Where-Object { $_.call_id -eq $oracleIncoming.call_id -and $_.stage -eq 'after_own_resist' } | Select-Object -First 1
                $oracleChildren = @($oracleTrace | Where-Object { $_.stage -eq 'enter' -and $_.parent_call -eq $oracleIncoming.call_id -and $_.incoming_reflected -and $_.target -eq 1 })
                if ($oracleCase.elephants -and [Math]::Abs($oracleIncoming.resist_chance - 120) -gt 0.001) { throw 'Natural rune resistance is not 120%' }
                if ($oracleCase.mirrors -and $oracleIncoming.reflect_chance -lt 100) { throw 'Natural reflection below 100%' }
                if (-not $oracleCase.elephants -and $oracleIncoming.resist_chance -ne 0) { throw 'Reflection control has nonzero resistance' }
                if (-not $oracleCase.mirrors -and $oracleIncoming.reflect_chance -ne 0) { throw 'Resistance control has nonzero reflection' }
                if ($oracleCaseName -eq 'N_overlap') {
                    if ($oracleOwnBefore.left -ne -1 -or $oracleOwnAfter.own_stacks_used -ne -1 -or $oracleOwnBefore.resist_stacks -ne 0 -or $oracleOwnAfter.resist_stacks -ne 1 -or $oracleChildren.Count -ne 1 -or $oracleFinal.player_blind_resist_stacks -ne 1) { throw 'Negative-left branch evidence did not match' }
                } elseif ($oracleOwnAfter.own_stacks_used -ne 0 -or $oracleFinal.player_blind_resist_stacks -ne 0) { throw 'Control increased dedicated resistance' }
                $oracleExpectedEnemyBlind = if ($oracleCase.mirrors) { 1 } else { 0 }
                if ($oracleFinal.player_blind -ne 0 -or $oracleFinal.opponent_blind -ne $oracleExpectedEnemyBlind) { throw 'Actual final Blind differs from branch' }
                $oracleSuccessful = @($oracleEvents | Where-Object { $_.params.amount -gt 0 -and -not $_.params.resisted -and -not $_.params.protected })
                $oracleReflectedEvents = @($oracleSuccessful | Where-Object { $_.origin -eq 'Pocket Sand' -and $_.target -eq 1 -and $_.params.reflected -and $_.params.amount -eq 1 })
                if ($oracleReflectedEvents.Count -ne $oracleExpectedEnemyBlind -or $oracleSuccessful.Count -ne $oracleExpectedEnemyBlind) { throw 'Native successful Blind event evidence differs from expectation' }
                $oracleResult = @{case=$oracleCaseName;passed=$true;engine=$Engine;incoming=$oracleIncoming;before_own=$oracleOwnBefore;after_own=$oracleOwnAfter;reflected_children=$oracleChildren;native_blind_events=$oracleEvents;final=$oracleFinal}
            }
            Write-OracleUtf8 (Join-Path $oracleData ($oracleCaseName + '_verified.json')) ($oracleResult | ConvertTo-Json -Depth 12)
            $oracleResults += $oracleResult
        }
        Write-Output "BUFF_EDGE_VERIFIED $oracleCaseName"
        $oracleProcess = $null
    }
    Write-OracleUtf8 (Join-Path $oracleRun 'results.json') ($oracleResults | ConvertTo-Json -Depth 12)
    Write-Output "BUFF_EDGE_RUN_PASS $oracleRun"
} finally {
    $oracleRestoreErrors = @()
    try {
        if ($null -ne $oracleProcess -and -not $oracleProcess.HasExited) { Stop-Process -Id $oracleProcess.Id -Force }
    } catch { $oracleRestoreErrors += "Own process stop error: $($_.Exception.Message)" }
    $env:APPDATA = $oraclePreviousAppData
    $env:LOCALAPPDATA = $oraclePreviousLocalAppData
    $env:BB_BUFF_EDGE_RUN_DATA = $oraclePreviousData
    $env:BB_BUFF_EDGE_EXPECTED_SHA = $oraclePreviousSha
    foreach ($path in $oracleWritten.Keys) {
        try {
            $currentHash = if (Test-Path -LiteralPath $path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash } else { 'MISSING' }
            if ($currentHash -ne $oracleWritten[$path]) { $oracleRestoreErrors += "Probe file concurrently changed, not overwriting: $path"; continue }
            if ($null -ne $oracleBackups[$path]) { [IO.File]::WriteAllBytes($path, $oracleBackups[$path]) } else { Remove-Item -LiteralPath $path }
        } catch { $oracleRestoreErrors += "Probe restoration error for $path : $($_.Exception.Message)" }
    }
    if ($oraclePackMoved) {
        try {
            if (Test-Path -LiteralPath $oraclePack) { throw 'Original package name was occupied during run; refusing overwrite' }
            if (-not (Test-Path -LiteralPath $oracleTemporaryPack)) { throw 'Owned temporary package is missing' }
            if ((Get-FileHash -LiteralPath $oracleTemporaryPack -Algorithm SHA256).Hash -ne $oracleBefore[$oraclePack]) { throw 'Owned temporary package hash changed; refusing move' }
            Move-Item -LiteralPath $oracleTemporaryPack -Destination $oraclePack
            if ((Get-FileHash -LiteralPath $oraclePack -Algorithm SHA256).Hash -ne $oracleBefore[$oraclePack]) { throw 'Restored package hash differs' }
            Write-OracleUtf8 (Join-Path $oracleRun 'package_move.json') (@{source=$oraclePack; temporary=$oracleTemporaryPack; before_sha256=$oracleBefore[$oraclePack]; after_sha256=(Get-FileHash -LiteralPath $oraclePack -Algorithm SHA256).Hash; state='restored'} | ConvertTo-Json)
            Write-Output 'BUFF_EDGE_INSTALLED_PCK_RESTORED'
        } catch { $oracleRestoreErrors += "Package restoration error: $($_.Exception.Message); source=$oraclePack temporary=$oracleTemporaryPack" }
    }
    $oracleAfter = Get-OracleSourceHashes $oracleSharedPaths
    if (Test-Path -LiteralPath $oracleRun) { Write-OracleUtf8 (Join-Path $oracleRun 'source_hashes_after.json') ($oracleAfter | ConvertTo-Json) }
    foreach ($path in $oracleSharedPaths) { if ($oracleAfter[$path] -ne $oracleBefore[$path]) { $oracleRestoreErrors += "Restoration/install hash mismatch: $path" } }
    if (Test-Path -LiteralPath $oracleRun) { Write-OracleUtf8 (Join-Path $oracleRun 'restoration.json') (@{unchanged=($oracleRestoreErrors.Count -eq 0); errors=$oracleRestoreErrors; before=$oracleBefore; after=$oracleAfter} | ConvertTo-Json -Depth 5) }
    if ($oracleRestoreErrors.Count -gt 0) { throw ($oracleRestoreErrors -join "`n") }
    Write-Output 'BUFF_EDGE_SHARED_AND_INSTALL_HASHES_UNCHANGED'
}
