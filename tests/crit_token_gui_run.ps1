$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$project = Join-Path $root 'Backpack Battles'
$projectFile = Join-Path $project 'project.godot'
$characterFile = Join-Path $project 'Core/Character.gd'
$opponentFile = Join-Path $root 'data/custom_opponent.json'
$temporaryTest = Join-Path $project 'tests/crit_token_gui_battle.gd'
$isolated = Join-Path $root 'data/crit_token_gui_appdata'
$stdout = Join-Path $root 'data/crit_token_gui_stdout.log'
$stderr = Join-Path $root 'data/crit_token_gui_stderr.log'
if (Test-Path -LiteralPath $temporaryTest) { throw 'temporary test occupied' }
$originals = @{}
foreach($path in @($projectFile,$characterFile,$opponentFile)) {
    $originals[$path] = [IO.File]::ReadAllBytes($path)
    $backupName = if($path -eq $projectFile){'project'} elseif($path -eq $characterFile){'character'} else {'opponent'}
    [IO.File]::WriteAllBytes((Join-Path $root ('data/crit_token_gui_backup_' + $backupName + '.bin')), $originals[$path])
}
$previous = $env:APPDATA
$process = $null
try {
    New-Item -ItemType Directory -Path $isolated -Force | Out-Null
    $env:APPDATA = $isolated
    Copy-Item -LiteralPath (Join-Path $root 'data/crit_token_gui_opponent.json') -Destination $opponentFile
    New-Item -ItemType Directory -Path (Split-Path $temporaryTest) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'crit_token_gui_battle.gd') -Destination $temporaryTest
    $char = [Text.Encoding]::UTF8.GetString($originals[$characterFile]).Replace("`r`n","`n")
    $marker = "`t`t`tvar critical = false"
    $char = $char.Replace($marker,$marker + "`n`t`t`tprint(`"CRIT_BEFORE item=`", item.getName() if item != null else `"null`", `" item_tokens=`", item.getCritTokens() if item != null else -1, `" char_tokens=`", opponent.getCritTokens(), `" resistance=`", critResistance, `" resist_tokens=`", critResistStacks)")
    $marker = "`t`t`t`tcritical = true`n`t`t`t`n`t`t`tif not damageRes.critical and item != null"
    $char = $char.Replace($marker,"`t`t`t`tcritical = true`n`t`t`t`tprint(`"CRIT_NATURAL_SUCCESS item=`", item.getName() if item != null else `"null`", `" chance=`", critChancePercent)`n`t`t`t`n`t`t`tif not damageRes.critical and item != null")
    $marker = "`t`t`tif critical:`n"
    $char = $char.Replace($marker,"`t`t`tprint(`"CRIT_AFTER_TOKENS item=`", item.getName() if item != null else `"null`", `" chance=`", critChancePercent, `" item_tokens=`", item.getCritTokens() if item != null else -1, `" char_tokens=`", opponent.getCritTokens(), `" result_critical=`", damageRes.critical)`n" + $marker)
    $marker = "`t`tvar activeDmgResi ="
    $char = $char.Replace($marker,"`t`tprint(`"CRIT_FINAL item=`", item.getName() if item != null else `"null`", `" critical=`", damageRes.critical, `" damage=`", damageRes.damage, `" resistance=`", critResistance, `" resist_tokens=`", critResistStacks)`n" + $marker)
    [IO.File]::WriteAllText($characterFile,$char,(New-Object Text.UTF8Encoding $false))
    $text = [Text.Encoding]::UTF8.GetString($originals[$projectFile])
    $text = $text.Replace('config/name="Backpack Battles"','config/name="Backpack Battles Crit Token GUI"')
    $marker = 'InputBlocker="*res://Interface/InputBlocker.tscn"'
    if(-not $text.Contains($marker)){throw 'autoload marker missing'}
    $text = $text.Replace($marker,$marker + "`nCritTokenGui=`"*res://tests/crit_token_gui_battle.gd`"")
    [IO.File]::WriteAllText($projectFile,$text,(New-Object Text.UTF8Encoding $false))
    $process = Start-Process -FilePath 'E:\godotsteam\godotsteam.362.editor.win64.exe' -ArgumentList @('--path', ('"' + $project + '"'), '--resolution','1280x720') -WindowStyle Normal -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    $process.Id | Set-Content (Join-Path $root 'data/crit_token_gui_pid.txt')
    $process | Wait-Process -Timeout 110
    $process.Refresh()
    if(-not (Select-String -LiteralPath $stdout -Pattern 'CRIT_GUI_PASS' -Quiet)){throw 'pass marker missing'}
}
finally {
    if($null -ne $process -and -not $process.HasExited){Stop-Process -Id $process.Id -Force}
    $env:APPDATA = $previous
    foreach($path in $originals.Keys){[IO.File]::WriteAllBytes($path,$originals[$path])}
    if(Test-Path -LiteralPath $temporaryTest){Remove-Item -LiteralPath $temporaryTest}
    foreach($path in $originals.Keys){Get-FileHash -LiteralPath $path -Algorithm SHA256 | Select-Object Path,Hash}
}
