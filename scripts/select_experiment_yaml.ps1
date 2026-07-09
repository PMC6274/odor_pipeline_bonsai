param(
    [Parameter(Position = 0)]
    [string]$InitialDirectory = ""
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Application]::EnableVisualStyles()

if ([string]::IsNullOrWhiteSpace($InitialDirectory) -or -not (Test-Path -LiteralPath $InitialDirectory -PathType Container)) {
    $InitialDirectory = [Environment]::GetFolderPath("MyDocuments")
}

$dialog = [System.Windows.Forms.OpenFileDialog]::new()
$dialog.Title = "Select experiment YAML"
$dialog.InitialDirectory = [System.IO.Path]::GetFullPath($InitialDirectory)
$dialog.Filter = "YAML files (*.yaml;*.yml)|*.yaml;*.yml|All files (*.*)|*.*"
$dialog.Multiselect = $false

if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
    Write-Output $dialog.FileName
}
