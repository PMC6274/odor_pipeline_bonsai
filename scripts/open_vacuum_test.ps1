param([string]$BonsaiExe)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
. (Join-Path $PSScriptRoot 'resolve_bonsai.ps1')
$executable = Resolve-BonsaiExecutable -ProjectRoot $root -BonsaiExe $BonsaiExe
& $executable (Join-Path $root 'tools/vacuum_test/bonsai_flow_control_demo.bonsai')
exit $LASTEXITCODE
