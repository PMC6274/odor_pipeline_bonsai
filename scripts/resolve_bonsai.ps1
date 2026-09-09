function Resolve-BonsaiExecutable {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [string]$BonsaiExe
    )

    if ([string]::IsNullOrWhiteSpace($BonsaiExe)) {
        $BonsaiExe = $env:ODOR_BONSAI_EXE
    }
    if ([string]::IsNullOrWhiteSpace($BonsaiExe)) {
        $BonsaiExe = Join-Path $ProjectRoot '.bonsai/Bonsai.exe'
    }
    $BonsaiExe = [Environment]::ExpandEnvironmentVariables($BonsaiExe)
    if (-not [IO.Path]::IsPathRooted($BonsaiExe)) {
        $BonsaiExe = Join-Path $ProjectRoot $BonsaiExe
    }
    $BonsaiExe = [IO.Path]::GetFullPath($BonsaiExe)
    if (-not (Test-Path -LiteralPath $BonsaiExe -PathType Leaf)) {
        throw @"
Bonsai installation not found: $BonsaiExe
The Git repository does not include Bonsai.exe or its Packages folder.
Copy the complete .bonsai folder from the working PC into:
  $ProjectRoot
The executable should then be: $(Join-Path $ProjectRoot '.bonsai/Bonsai.exe')
Alternatively, set ODOR_BONSAI_EXE to an existing Bonsai.exe, or pass -BonsaiExe
to run_experiment.ps1. That installation must contain this project's packages.
See docs/DEPLOYMENT.md. Copying only Bonsai.exe is not sufficient.
"@
    }
    return $BonsaiExe
}
