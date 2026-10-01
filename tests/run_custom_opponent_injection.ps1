param(
    [string]$TestScript = 'test_custom_opponent_injection.gd',
    [string]$ExpectedMarker = 'CUSTOM_OPPONENT_TEST_PASS'
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$project = Join-Path $root 'Backpack Battles'
$projectFile = Join-Path $project 'project.godot'
$sourceTest = Join-Path $PSScriptRoot $TestScript
$projectTests = Join-Path $project 'tests'
$temporaryTest = Join-Path $projectTests 'test_custom_opponent_injection.gd'
$godot = 'E:\godotsteam\godotsteam.362.editor.win64.exe'
$stdout = Join-Path $PSScriptRoot 'custom_opponent_godot_stdout.tmp'
$stderr = Join-Path $PSScriptRoot 'custom_opponent_godot_stderr.tmp'
$isolatedAppData = Join-Path $root 'data/.godot_test_appdata'
$invalidFixture = Join-Path $root 'data/custom_opponent_test_invalid.json'

if (-not (Test-Path -LiteralPath $godot)) { throw "GodotSteam not found: $godot" }
if (Get-Process godotsteam.362.editor.win64 -ErrorAction SilentlyContinue) {
    throw 'Close the running GodotSteam editor before this temporary project test.'
}
if (Test-Path -LiteralPath $temporaryTest) { throw "Temporary test path is occupied: $temporaryTest" }
if (Test-Path -LiteralPath $isolatedAppData) { throw "Isolated test data path is occupied: $isolatedAppData" }
if (Test-Path -LiteralPath $invalidFixture) { throw "Test fixture path is occupied: $invalidFixture" }
if (-not ([IO.Path]::GetFullPath($temporaryTest)).StartsWith(([IO.Path]::GetFullPath($project) + [IO.Path]::DirectorySeparatorChar), [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Temporary test path is outside the project.'
}

$original = [IO.File]::ReadAllBytes($projectFile)
$createdDirectory = -not (Test-Path -LiteralPath $projectTests)
$previousAppData = $env:APPDATA
try {
    New-Item -ItemType Directory -Path $isolatedAppData | Out-Null
    $env:APPDATA = $isolatedAppData
    if ($createdDirectory) { New-Item -ItemType Directory -Path $projectTests | Out-Null }
    Copy-Item -LiteralPath $sourceTest -Destination $temporaryTest
    $text = [Text.Encoding]::UTF8.GetString($original)
    $text = $text.Replace('config/name="Backpack Battles"', 'config/name="Backpack Battles Oracle Test"')
    $marker = 'InputBlocker="*res://Interface/InputBlocker.tscn"'
    if (-not $text.Contains($marker)) { throw 'Autoload insertion marker was not found.' }
    $text = $text.Replace($marker, $marker + "`nCustomOpponentTest=`"*res://tests/test_custom_opponent_injection.gd`"")
    [IO.File]::WriteAllText($projectFile, $text, (New-Object Text.UTF8Encoding $false))
    $process = Start-Process -FilePath $godot -ArgumentList @('--path', ('"' + $project + '"'), '--no-window') -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
    try { $process | Wait-Process -Timeout 120 -ErrorAction Stop }
    catch { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue; throw 'GodotSteam test timed out.' }
    $process.Refresh()
    Get-Content -LiteralPath $stdout -Tail 35
    Get-Content -LiteralPath $stderr -Tail 35
    if ($process.ExitCode -ne 0) { throw "GodotSteam test failed with exit code $($process.ExitCode)." }
    if (-not (Select-String -LiteralPath $stdout -Pattern $ExpectedMarker -Quiet)) { throw 'GodotSteam did not print the success marker.' }
}
finally {
    $env:APPDATA = $previousAppData
    [IO.File]::WriteAllBytes($projectFile, $original)
    if (Test-Path -LiteralPath $temporaryTest) { Remove-Item -LiteralPath $temporaryTest }
    if ($createdDirectory -and (Test-Path -LiteralPath $projectTests)) { Remove-Item -LiteralPath $projectTests }
    if (Test-Path -LiteralPath $invalidFixture) { Remove-Item -LiteralPath $invalidFixture }
    $resolvedData = [IO.Path]::GetFullPath($isolatedAppData)
    $dataRoot = [IO.Path]::GetFullPath((Join-Path $root 'data')) + [IO.Path]::DirectorySeparatorChar
    if (-not $resolvedData.StartsWith($dataRoot, [StringComparison]::OrdinalIgnoreCase)) { throw 'Test data cleanup path is outside data/.' }
    if (Test-Path -LiteralPath $isolatedAppData) { Remove-Item -LiteralPath $isolatedAppData -Recurse -Force }
    if (Test-Path -LiteralPath $stdout) { Remove-Item -LiteralPath $stdout }
    if (Test-Path -LiteralPath $stderr) { Remove-Item -LiteralPath $stderr }
}
