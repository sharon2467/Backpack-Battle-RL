param(
    [string]$RunId = (Get-Date -Format 'yyyyMMdd_HHmmss'),
    [string[]]$Cases = @('all'),
    [int]$RepeatCount = 3,
    [int]$TimeoutSeconds = 120,
    [switch]$PreviewOnly,
    [double]$EqualDuration = 0.2
)
$ErrorActionPreference = 'Stop'

function Get-T0Hashes([string[]]$Paths) {
    $values = @{}
    foreach ($path in $Paths) { $values[$path] = if (Test-Path -LiteralPath $path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash } else { 'MISSING' } }
    return $values
}
function Write-T0Utf8([string]$Path, [string]$Text) {
    [IO.File]::WriteAllText($Path, $Text, [Text.UTF8Encoding]::new($false))
}
function Add-T0Observation([string]$Text, [string]$Needle, [string]$Replacement) {
    $count = [regex]::Matches($Text, [regex]::Escape($Needle)).Count
    if ($count -ne 1) { throw "Expected exactly one observation marker, found $count : $Needle" }
    return $Text.Replace($Needle, $Replacement)
}

if ($RunId -notmatch '^[A-Za-z0-9_-]+$' -or $RepeatCount -lt 1 -or $RepeatCount -gt 5 -or $TimeoutSeconds -lt 20 -or $TimeoutSeconds -gt 300) { throw 'Invalid run parameters' }
if ([double]::IsNaN($EqualDuration) -or [double]::IsInfinity($EqualDuration) -or $EqualDuration -le 0 -or $EqualDuration -gt 1) { throw 'Invalid equal-duration input' }
$t0Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$t0Project = (Resolve-Path (Join-Path $t0Root 'Backpack Battles')).Path
$t0Run = Join-Path $t0Root ('data/buff_stage2_t0/' + $RunId)
$t0Exe = 'E:/godotsteam/godotsteam.362.editor.win64.exe'
$t0Json = Join-Path $t0Root 'data/custom_opponent.json'
$t0ProjectFile = Join-Path $t0Project 'project.godot'
$t0BuffFile = Join-Path $t0Project 'Core/Buff.gd'
$t0CharacterFile = Join-Path $t0Project 'Core/Character.gd'
$t0ItemFile = Join-Path $t0Project 'Items/Item.gd'
$t0Changed = @($t0ProjectFile,$t0BuffFile,$t0CharacterFile,$t0ItemFile,$t0Json)
$t0Paths = @($t0ProjectFile,$t0BuffFile,$t0CharacterFile,$t0ItemFile,(Join-Path $t0Project 'Core/Game.gd'),(Join-Path $t0Project 'Utility/SteamHelper.gd'),(Join-Path $t0Project 'Sheets/CSV/ItemData.csv'),(Join-Path $t0Project 'Sheets/CSV/ItemData_e.csv'),$t0Json,$t0Exe)
$t0Names = @('smoke','zero_fresh','zero_reused','zero_running','equal_forward','equal_reverse','tolerance_inside','tolerance_outside','cross_start_forward','cross_start_reverse','phase_physics','phase_deferred','reentry_use','reentry_lose','reentry_gain','stale_far_first','stale_early_first','cap_expiry','reset_controlled','lifecycle_natural')
if ($Cases -contains 'all') { $Cases = $t0Names | Where-Object { $_ -ne 'smoke' } }
if (@($Cases | Where-Object { $_ -notin $t0Names }).Count) { throw 'Unknown case' }
if (Test-Path -LiteralPath $t0Run) { throw 'Evidence directory already exists' }
if (Get-Process -Name 'godotsteam.362.editor.win64' -ErrorAction SilentlyContinue) { throw 'Existing user GodotSteam process: refusing temporary source changes' }
$t0Before = Get-T0Hashes $t0Paths
if ($t0Before[$t0Exe] -ne '100B76E344A040D2CA50D1B4D03B097A259C35B32D5865043F33486A666EDA1C') { throw 'Selected engine fingerprint mismatch' }
$t0Backups = @{}
$t0Written = @{}
$t0Prepared = @{}
$t0Process = $null
$t0Results = @()
$t0PreviousEnv = @{}
foreach ($name in @('APPDATA','LOCALAPPDATA','BB_BUFF_T0_RUN_DATA')) { $t0PreviousEnv[$name] = [Environment]::GetEnvironmentVariable($name,'Process') }
try {
    New-Item -ItemType Directory -Path $t0Run,(Join-Path $t0Run 'original_bytes'),(Join-Path $t0Run 'prepared') | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $t0Run 'test_scripts') | Out-Null
    Copy-Item -LiteralPath $PSCommandPath,(Join-Path $PSScriptRoot 'buff_stage2_t0_battle.gd') -Destination (Join-Path $t0Run 'test_scripts')
    Write-T0Utf8 (Join-Path $t0Run 'test_scripts_sha256.json') ((Get-T0Hashes @($PSCommandPath,(Join-Path $PSScriptRoot 'buff_stage2_t0_battle.gd'))) | ConvertTo-Json)
    Write-T0Utf8 (Join-Path $t0Run 'source_hashes_before.json') ($t0Before | ConvertTo-Json)
    foreach ($path in $t0Changed) {
        $t0Backups[$path] = if (Test-Path -LiteralPath $path) { [IO.File]::ReadAllBytes($path) } else { $null }
        if ($null -ne $t0Backups[$path]) { [IO.File]::WriteAllBytes((Join-Path $t0Run ('original_bytes/' + [IO.Path]::GetFileName($path) + '.bin')), $t0Backups[$path]) }
    }
    $t0Text = [IO.File]::ReadAllText($t0ProjectFile).Replace("`r`n","`n")
    $t0Autoload = 'T0Probe="*' + (Join-Path $PSScriptRoot 'buff_stage2_t0_battle.gd').Replace('\','/') + '"'
    $t0Prepared[$t0ProjectFile] = Add-T0Observation $t0Text 'ControllerIcons="*res://addons/controller_icons/ControllerIcons.gd"' ($t0Autoload + "`n" + 'ControllerIcons="*res://addons/controller_icons/ControllerIcons.gd"')

    # Work on one original function at a time. Only observation locals/reads are added.
    foreach ($t0Source in @($t0BuffFile,$t0CharacterFile,$t0ItemFile)) {
        $t0Text = [IO.File]::ReadAllText($t0Source).Replace("`r`n","`n")
        $t0Functions = if ($t0Source -eq $t0BuffFile) { @('gainTemporary','loseStacks','changeCurrentLogShowLabel','onTimeout','reset','combatEnd') } elseif ($t0Source -eq $t0CharacterFile) { @('combatStart','combatEnd','cleanse','onTick') } else { @('trigger') }
        foreach ($t0Function in $t0Functions) {
            $t0Pattern = '(?ms)^func ' + [regex]::Escape($t0Function) + '\(.*?(?=^(?:func |class |const |var |onready var |signal |enum )|\z)'
            $t0Match = [regex]::Match($t0Text,$t0Pattern)
            if (-not $t0Match.Success) { throw "Original function absent: $t0Function" }
            $t0Original = $t0Match.Value
            $t0Block = $t0Original
            $t0Kind = if ($t0Source -eq $t0BuffFile) { 'buff' } elseif ($t0Source -eq $t0CharacterFile) { 'character' } else { 'item' }
            $t0Label = $t0Kind + '_' + $t0Function
            $t0SignatureEnd = $t0Block.IndexOf(":`n") + 2
            if ($t0SignatureEnd -lt 2) { throw 'Function signature not recognized' }
            $t0Enter = "`tvar t0_call_id = T0Probe.new_call_id()`n`tT0Probe.observe(`"${t0Label}_enter`", t0_call_id, self)`n"
            $t0Block = $t0Block.Insert($t0SignatureEnd,$t0Enter)
            if ($t0Source -eq $t0BuffFile -and $t0Function -eq 'gainTemporary') {
                $t0Block = Add-T0Observation $t0Block "`tvar event = null" ("`tT0Probe.observe(`"gain_request`", t0_call_id, self, {`"request`":amount,`"duration`":duration,`"reflected_in`":reflect,`"source`":item.get_instance_id() if item != null else -1,`"parent`":triggerEvent.id if triggerEvent != null else -1})`n`tvar event = null")
                $t0Needle = "`t`tvar left = amount - resisted"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`tT0Probe.observe(`"gain_after_resist`",t0_call_id,self,{`"amount`":amount,`"resisted`":resisted,`"left`":left})")
                $t0Needle = "`t`t`tvar ownStacksUsed = min(left, resistStacks)"
                $t0Block = Add-T0Observation $t0Block $t0Needle ("`t`t`tT0Probe.observe(`"gain_after_reflect`",t0_call_id,self,{`"amount`":amount,`"resisted`":resisted,`"left`":left,`"reflected_count`":reflected})`n" + $t0Needle)
                $t0Needle = "`t`t`tamount = int(min(amount, MAX_STACKS - current))"
                $t0Block = Add-T0Observation $t0Block $t0Needle ("`t`t`tT0Probe.observe(`"gain_before_cap`",t0_call_id,self,{`"amount`":amount,`"reflected_count`":reflected})`n" + $t0Needle + "`n`t`t`tT0Probe.observe(`"gain_after_cap`",t0_call_id,self,{`"amount`":amount,`"reflected_count`":reflected})")
                $t0Block = Add-T0Observation $t0Block "`t`t`tif amount == 0: return null" "`t`t`tif amount == 0:`n`t`t`t`tT0Probe.observe(`"buff_gainTemporary_exit`",t0_call_id,self,{`"cap_zero`":true})`n`t`t`t`treturn null"
                $t0Needle = "`t`t`t`ttemporaryStacks.push_back(tempStacks)"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`t`t`tT0Probe.observe(`"gain_batch_added`",t0_call_id,self,{`"batch_id`":tempStacks.get_instance_id(),`"timeout`":timeout})")
                $t0Needle = "`t`t`t`t`tnextTemporaryTimeout = 0"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`t`t`t`tT0Probe.observe(`"gain_timer_stopped_start`",t0_call_id,self)")
                $t0Needle = "`t`t`t`t`t`tnextTemporaryTimeout = temporaryStacks.size() - 1"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`t`t`t`t`tT0Probe.observe(`"gain_timer_running_restart`",t0_call_id,self)")
                $t0Block = Add-T0Observation $t0Block "`treturn event" "`tT0Probe.observe(`"buff_gainTemporary_exit`",t0_call_id,self,{`"event_id`":event.id if event != null else -1})`n`treturn event"
            } elseif ($t0Source -eq $t0BuffFile -and $t0Function -eq 'loseStacks') {
                $t0Needle = "`tamount = min(current, amount)"
                $t0Block = Add-T0Observation $t0Block $t0Needle ("`tT0Probe.observe(`"lose_request`",t0_call_id,self,{`"request`":amount,`"used`":used,`"source`":item.get_instance_id() if item != null else -1,`"parent`":triggerEvent.id if triggerEvent != null else -1})`n" + $t0Needle)
                $t0Needle = "`t`t`tvar farthest = temporaryStacks[farthestIndex]"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`t`tT0Probe.observe(`"lose_selected_batch`",t0_call_id,self,{`"selected_index`":farthestIndex,`"batch_id`":farthest.get_instance_id(),`"remaining_request`":tempToCleanse})")
                $t0Needle = "`treturn changeCurrentLogShowLabel(false, amount, item, triggerEvent, used)"
                $t0Block = Add-T0Observation $t0Block $t0Needle "`tvar t0_event = changeCurrentLogShowLabel(false,amount,item,triggerEvent,used)`n`tT0Probe.observe(`"buff_loseStacks_exit`",t0_call_id,self,{`"event_id`":t0_event.id if t0_event != null else -1})`n`treturn t0_event"
            } elseif ($t0Source -eq $t0BuffFile -and $t0Function -eq 'changeCurrentLogShowLabel') {
                $t0Needle = "`tvar change = min(current, amount)"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`tT0Probe.observe(`"change_actual`",t0_call_id,self,{`"actual`":change,`"requested`":amount,`"timeout`":isTimeout,`"used`":used,`"source`":item.get_instance_id() if item != null else -1,`"parent`":triggerEvent.id if triggerEvent != null else -1})")
                $t0Needle = "`t`tcurrent -= change"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`tT0Probe.observe(`"change_committed`",t0_call_id,self,{`"actual`":change,`"timeout`":isTimeout})")
                $t0Needle = "`t`t`tEventBus.emitEvent(character, signalName, event, [event.getAmount(), event])"
                $t0Block = Add-T0Observation $t0Block $t0Needle ("`t`t`tT0Probe.observe(`"change_before_signal`",t0_call_id,self,{`"event_id`":event.id,`"actual`":change,`"timeout`":isTimeout})`n" + $t0Needle)
                $t0Block = Add-T0Observation $t0Block "`t`t`treturn event" "`t`t`tT0Probe.observe(`"buff_changeCurrentLogShowLabel_exit`",t0_call_id,self,{`"event_id`":event.id})`n`t`t`treturn event"
                $t0Block = Add-T0Observation $t0Block "`treturn null" "`tT0Probe.observe(`"buff_changeCurrentLogShowLabel_exit`",t0_call_id,self,{`"event_id`":-1})`n`treturn null"
            } elseif ($t0Source -eq $t0BuffFile -and $t0Function -eq 'onTimeout') {
                $t0Needle = "`tvar timedOutStacks: TemporaryStacks = temporaryStacks[nextTemporaryTimeout]"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`tT0Probe.observe(`"timeout_selected`",t0_call_id,self,{`"batch_id`":timedOutStacks.get_instance_id(),`"selected_amount`":timedOutStacks.amount,`"selected_timeout`":timedOutStacks.timeout,`"source`":timedOutStacks.item.get_instance_id() if timedOutStacks.item != null else -1})")
                $t0Needle = "`ttemporaryStacks.remove(nextTemporaryTimeout)"
                $t0Block = Add-T0Observation $t0Block $t0Needle ("`tT0Probe.observe(`"timeout_before_remove`",t0_call_id,self,{`"selected_batch`":timedOutStacks.get_instance_id()})`n" + $t0Needle + "`n`tT0Probe.observe(`"timeout_after_remove`",t0_call_id,self)")
                $t0Needle = "`t`tvar delay = earliestTimeout - Util.time"
                $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`tT0Probe.observe(`"timeout_delay`",t0_call_id,self,{`"delay`":delay,`"earliest`":earliestTimeout,`"recursive`":delay <= 0.01})")
                $t0Block = $t0Block.TrimEnd() + "`n`tT0Probe.observe(`"buff_onTimeout_exit`",t0_call_id,self)`n`n"
            } else {
                if ($t0Source -eq $t0CharacterFile -and $t0Function -eq 'onTick') {
                    foreach ($t0Metric in @('regen','poison')) {
                        $t0Needle = if ($t0Metric -eq 'regen') { "`t`tvar regen = getRegeneration()" } else { "`t`tvar poison = getPoison()" }
                        $t0Block = Add-T0Observation $t0Block $t0Needle ($t0Needle + "`n`t`tT0Probe.observe(`"tick_read_${t0Metric}`",t0_call_id,self,{`"value`":$t0Metric})")
                    }
                }
                $t0Block = $t0Block.TrimEnd() + "`n`tT0Probe.observe(`"${t0Label}_exit`",t0_call_id,self)`n`n"
            }
            $t0Text = Add-T0Observation $t0Text $t0Original $t0Block
        }
        $t0Prepared[$t0Source] = $t0Text
    }
    foreach ($path in $t0Prepared.Keys) {
        $t0PreparedPath = Join-Path $t0Run ('prepared/' + [IO.Path]::GetFileName($path))
        Write-T0Utf8 $t0PreparedPath $t0Prepared[$path]
        $t0Diff = & git -c core.autocrlf=false diff --no-index -- (Join-Path $t0Run ('original_bytes/' + [IO.Path]::GetFileName($path) + '.bin')) $t0PreparedPath
        Write-T0Utf8 (Join-Path $t0Run ([IO.Path]::GetFileName($path) + '.diff')) ($t0Diff -join "`n")
    }
    $t0Locations = @(Select-String -Path (Join-Path $t0Run 'prepared/*') -Pattern 'T0Probe|t0_call_id|t0_event' | Select-Object Path,LineNumber,Line)
    Write-T0Utf8 (Join-Path $t0Run 'probe_locations.json') ($t0Locations | ConvertTo-Json)
    if ($PreviewOnly) { Write-Output "BUFF_T0_PREVIEW $t0Run"; return }
    foreach ($path in $t0Prepared.Keys) { Write-T0Utf8 $path $t0Prepared[$path]; $t0Written[$path] = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash }
    $t0Plan = @()
    foreach ($caseName in $Cases) {
        $variants = if ($caseName -eq 'reentry_gain') { @('forward','reverse') } else { @('default') }
        $repetitions = if ($caseName -match '^(cross_start_|phase_)') { $RepeatCount } else { 1 }
        foreach ($variant in $variants) { foreach ($repeat in 1..$repetitions) { $t0Plan += @{name=$caseName;variant=$variant;repeat=$repeat;id=($caseName+'_'+$variant+'_'+$repeat)} } }
    }
    Write-T0Utf8 (Join-Path $t0Run 'execution_plan.json') ($t0Plan | ConvertTo-Json)
    foreach ($t0Case in $t0Plan) {
        $t0CaseDir = Join-Path $t0Run $t0Case.id
        New-Item -ItemType Directory -Path $t0CaseDir,(Join-Path $t0CaseDir 'appdata'),(Join-Path $t0CaseDir 'localappdata') | Out-Null
        $t0Case.expected_exe_sha = $t0Before[$t0Exe]
        $t0Case.original_hashes = $t0Before
        $t0Case.observed_hashes = Get-T0Hashes @($t0BuffFile,$t0CharacterFile,$t0ItemFile)
        $t0Case.tolerance_b = if ($t0Case.name -eq 'tolerance_inside') { 0.125 } else { 0.16 }
        $t0Case.phase_offset = 0.0
        $t0Case.equal_duration = $EqualDuration
        Write-T0Utf8 (Join-Path $t0CaseDir 'case.json') ($t0Case | ConvertTo-Json -Depth 6)
        $t0OpponentItems = @()
        foreach ($y in @(0,2,4)) { foreach ($x in @(0,2,4,6)) { $t0OpponentItems += @{item_index=11;x=$x;y=$y;f=0} } }
        $t0Opponent = @{schema_version=1;game_version='1.1.8';class=0;health=25;stamina=5;items=$t0OpponentItems}
        Write-T0Utf8 $t0Json ($t0Opponent | ConvertTo-Json -Depth 6)
        $t0Written[$t0Json] = (Get-FileHash -LiteralPath $t0Json -Algorithm SHA256).Hash
        Write-T0Utf8 (Join-Path $t0CaseDir 'opponent_input.json') ($t0Opponent | ConvertTo-Json -Depth 6)
        $env:APPDATA = Join-Path $t0CaseDir 'appdata'
        $env:LOCALAPPDATA = Join-Path $t0CaseDir 'localappdata'
        $env:BB_BUFF_T0_RUN_DATA = $t0CaseDir
        $t0Started = [DateTime]::UtcNow
        $t0Args = @('--path',('"'+$t0Project+'"'),'--windowed','--resolution','1280x720')
        Write-Output "BUFF_T0_START $($t0Case.id)"
        try {
            $t0Process = Start-Process -FilePath $t0Exe -WorkingDirectory $t0Project -ArgumentList $t0Args -WindowStyle Hidden -RedirectStandardOutput (Join-Path $t0CaseDir 'stdout.log') -RedirectStandardError (Join-Path $t0CaseDir 'stderr.log') -PassThru
            Write-T0Utf8 (Join-Path $t0CaseDir 'process.json') (@{pid=$t0Process.Id;exe=$t0Exe;args=$t0Args;working_directory=$t0Project;started_utc=$t0Started.ToString('o')} | ConvertTo-Json)
            $t0TimedOut = -not $t0Process.WaitForExit($TimeoutSeconds*1000)
            if ($t0TimedOut -and -not $t0Process.HasExited) { Stop-Process -Id $t0Process.Id -Force; $t0Process.WaitForExit() }
            $t0Ended = [DateTime]::UtcNow
            $t0Process.Refresh()
            $t0Result = @{case=$t0Case.id;exit_code=$t0Process.ExitCode;timed_out=$t0TimedOut;ended_utc=$t0Ended.ToString('o');elapsed_seconds=($t0Ended-$t0Started).TotalSeconds}
            $t0NativeLog = Get-ChildItem -LiteralPath (Join-Path $t0CaseDir 'appdata') -Filter godot.log -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($null -ne $t0NativeLog) { Copy-Item -LiteralPath $t0NativeLog.FullName -Destination (Join-Path $t0CaseDir 'godot.log') }
            if (Test-Path -LiteralPath (Join-Path $t0CaseDir 'result.json')) { $t0Result.observation = Get-Content -LiteralPath (Join-Path $t0CaseDir 'result.json') -Raw | ConvertFrom-Json }
            $t0Result.stderr = Get-Content -LiteralPath (Join-Path $t0CaseDir 'stderr.log') -Raw
            Write-T0Utf8 (Join-Path $t0CaseDir 'process_result.json') ($t0Result | ConvertTo-Json -Depth 12)
            $t0Results += $t0Result
            Write-Output "BUFF_T0_DONE $($t0Case.id) exit=$($t0Process.ExitCode) timeout=$t0TimedOut"
        } catch {
            $t0Results += @{case=$t0Case.id;runner_error=$_.Exception.Message}
            Write-Output "BUFF_T0_CASE_ERROR $($t0Case.id) $($_.Exception.Message)"
        } finally {
            if ($null -ne $t0Process) { try { if (-not $t0Process.HasExited) { Stop-Process -Id $t0Process.Id -Force } } catch { Write-Output "BUFF_T0_STOP_ERROR $($_.Exception.Message)" } }
            $t0Process = $null
        }
        Write-T0Utf8 (Join-Path $t0Run 'results.json') ($t0Results | ConvertTo-Json -Depth 12)
    }
} finally {
    $t0RestoreErrors = @()
    try { if ($null -ne $t0Process -and -not $t0Process.HasExited) { Stop-Process -Id $t0Process.Id -Force } } catch { $t0RestoreErrors += $_.Exception.Message }
    foreach ($name in $t0PreviousEnv.Keys) { try { [Environment]::SetEnvironmentVariable($name,$t0PreviousEnv[$name],'Process') } catch { $t0RestoreErrors += $_.Exception.Message } }
    foreach ($path in $t0Written.Keys) {
        try {
            $currentHash = if (Test-Path -LiteralPath $path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash } else { 'MISSING' }
            if ($currentHash -ne $t0Written[$path]) { throw "Concurrent change, refusing overwrite: $path" }
            if ($null -eq $t0Backups[$path]) { Remove-Item -LiteralPath $path } else { [IO.File]::WriteAllBytes($path,$t0Backups[$path]) }
        } catch { $t0RestoreErrors += $_.Exception.Message }
    }
    $t0After = Get-T0Hashes $t0Paths
    foreach ($path in $t0Paths) { if ($t0After[$path] -ne $t0Before[$path]) { $t0RestoreErrors += "Hash mismatch: $path" } }
    if (Test-Path -LiteralPath $t0Run) { Write-T0Utf8 (Join-Path $t0Run 'restoration.json') (@{unchanged=($t0RestoreErrors.Count-eq 0);errors=$t0RestoreErrors;before=$t0Before;after=$t0After} | ConvertTo-Json -Depth 5) }
    if ($t0RestoreErrors.Count) { throw ($t0RestoreErrors -join "`n") }
    Write-Output 'BUFF_T0_SOURCES_RESTORED'
}
