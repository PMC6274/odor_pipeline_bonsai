param(
    [Parameter(Position = 0)]
    [string]$Config = "experiments/example.yaml",

    [switch]$ValidateOnly,
    [switch]$OpenOnly,
    [switch]$NoEditor
)

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$configPath = [System.IO.Path]::GetFullPath((Join-Path $root $Config))
$workflowPath = Join-Path $root "3device1blank.bonsai"
$bonsaiPath = Join-Path $root ".bonsai/Bonsai.exe"
$yamlAssembly = Join-Path $root ".bonsai/Packages/YamlDotNet.16.3.0/lib/net47/YamlDotNet.dll"

foreach ($path in @($configPath, $workflowPath, $bonsaiPath, $yamlAssembly)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Required file not found: $path"
    }
}

Add-Type -Path $yamlAssembly
$yaml = [YamlDotNet.RepresentationModel.YamlStream]::new()
$reader = [System.IO.StreamReader]::new($configPath)
try { $yaml.Load($reader) } finally { $reader.Dispose() }

if ($yaml.Documents.Count -ne 1) { throw "The YAML file must contain exactly one document." }
$document = $yaml.Documents[0].RootNode
if ($document -isnot [YamlDotNet.RepresentationModel.YamlMappingNode]) {
    throw "The YAML document root must be a mapping."
}

function Get-Map($node, [string]$name) {
    $key = [YamlDotNet.RepresentationModel.YamlScalarNode]::new($name)
    if (-not $node.Children.ContainsKey($key)) { throw "Missing YAML section: $name" }
    $value = $node.Children[$key]
    if ($value -isnot [YamlDotNet.RepresentationModel.YamlMappingNode]) {
        throw "$name must be a YAML mapping."
    }
    Write-Output -NoEnumerate $value
}

function Get-Text($node, [string]$name, [bool]$allowEmpty = $false) {
    $key = [YamlDotNet.RepresentationModel.YamlScalarNode]::new($name)
    if (-not $node.Children.ContainsKey($key)) { throw "Missing YAML value: $name" }
    $value = $node.Children[$key].Value
    if (-not $allowEmpty -and [string]::IsNullOrWhiteSpace($value)) { throw "$name cannot be empty." }
    return [string]$value
}

function Get-Number($node, [string]$name) {
    $text = Get-Text $node $name
    $value = 0.0
    if (-not [double]::TryParse($text, [Globalization.NumberStyles]::Float,
        [Globalization.CultureInfo]::InvariantCulture, [ref]$value)) {
        throw "$name must be a number."
    }
    if ([double]::IsNaN($value) -or [double]::IsInfinity($value) -or $value -lt 0) {
        throw "$name must be a finite, non-negative number."
    }
    return $value
}

function Get-Flow($node, [string]$name) {
    $value = Get-Number $node $name
    if ($value -ne [math]::Floor($value) -or $value -gt 1000) {
        throw "$name must be an integer between 0 and 1000."
    }
    return [int]$value
}

function Get-PositiveInteger($node, [string]$name) {
    $value = Get-Number $node $name
    if ($value -ne [math]::Floor($value) -or $value -lt 1 -or $value -gt [int]::MaxValue) {
        throw "$name must be a positive integer."
    }
    return [int]$value
}

function ConvertTo-Duration([double]$seconds) {
    return [TimeSpan]::FromSeconds($seconds).ToString("c", [Globalization.CultureInfo]::InvariantCulture)
}

$metadata = Get-Map $document "Metadata"
$hardware = Get-Map $document "Hardware"
$controls = Get-Map $document "Controls"
$protocol = Get-Map $document "Protocol"
$output = Get-Map $document "Output"

$experimentId = Get-Text $metadata "ExperimentId"
$subjectId = Get-Text $metadata "SubjectId"
$operator = Get-Text $metadata "Operator"
$sessionStart = Get-Text $metadata "SessionStart"
$parsedStart = [DateTimeOffset]::MinValue
if (-not [DateTimeOffset]::TryParse($sessionStart, [ref]$parsedStart)) {
    throw "Metadata.SessionStart must be an ISO date-time."
}

$olfactometer1 = Get-Text $hardware "Olfactometer1Port"
$olfactometer2 = Get-Text $hardware "Olfactometer2Port"
$olfactometer3 = Get-Text $hardware "Olfactometer3Port"
$whiteRabbit = Get-Text $hardware "WhiteRabbitPort"
foreach ($port in @($olfactometer1, $olfactometer2, $olfactometer3, $whiteRabbit)) {
    if ($port -notmatch '^COM[0-9]+$') { throw "Invalid COM port: $port" }
}

$startFlowKey = Get-Text $controls "StartFlow"
$disableFlowKey = Get-Text $controls "DisableFlow"
$startPpsKey = Get-Text $controls "StartPps"
$endPpsKey = Get-Text $controls "EndPps"
$startExperimentKey = Get-Text $controls "StartExperiment"

$charge = Get-Number $protocol "ChargeSeconds"
$stimulusFile = Get-Text $protocol "StimulusFile"
$stimulusPath = if ([System.IO.Path]::IsPathRooted($stimulusFile)) {
    [System.IO.Path]::GetFullPath($stimulusFile)
} else {
    [System.IO.Path]::GetFullPath((Join-Path $root $stimulusFile))
}
if (-not (Test-Path -LiteralPath $stimulusPath -PathType Leaf)) {
    throw "Protocol.StimulusFile was not found: $stimulusPath"
}
$stimulusExpression = [System.IO.File]::ReadAllText($stimulusPath).Trim()
if ([string]::IsNullOrWhiteSpace($stimulusExpression)) {
    throw "Protocol.StimulusFile is empty: $stimulusPath"
}
$trialCount = Get-PositiveInteger $protocol "TrialCount"
$stimulusTrials = [regex]::Matches($stimulusExpression, '(?m)^\s*it\s*==\s*(\d+)')
if ($stimulusTrials.Count -ne $trialCount) {
    Write-Warning "Protocol.TrialCount is $trialCount, but StimulusFile contains $($stimulusTrials.Count) trial conditions. Bonsai will still use TrialCount=$trialCount."
}
$sequenceMismatch = $false
for ($index = 0; $index -lt $stimulusTrials.Count; $index++) {
    $expectedTrial = $index + 1
    if ([int]$stimulusTrials[$index].Groups[1].Value -ne $expectedTrial) {
        $sequenceMismatch = $true
        break
    }
}
if ($sequenceMismatch) {
    Write-Warning "StimulusFile trial conditions are not sequential from 1. Bonsai will still open; inspect Odor loop.Expression before running."
}
$delivery = Get-Number $protocol "DeliverySeconds"
$flush = Get-Number $protocol "FlushSeconds"
$recharge = Get-Number $protocol "RechargeSeconds"
$flowAdjustment = Get-Number $protocol "FlowAdjustmentSeconds"
$timeBeforeOdor = Get-Number $protocol "TimeBeforeOdorSeconds"
$isiMinimum = Get-Number $protocol "IsiMinimumSeconds"
$isiMaximum = Get-Number $protocol "IsiMaximumSeconds"
if ($isiMaximum -lt $isiMinimum) { throw "IsiMaximumSeconds must be greater than or equal to IsiMinimumSeconds." }

$mainFlow = Get-Flow $protocol "MainFlow"
$controlFlow = Get-Flow $protocol "ControlFlow"
$flushFlow = Get-Flow $protocol "FlushFlow"
$dataDirectory = Get-Text $output "DataDirectory"
$webhook = Get-Text $output "Webhook" $true

$properties = [ordered]@{
    "Define Device.Olfactometer1" = $olfactometer1
    "Define Device.Olfactometer2" = $olfactometer2
    "Define Device.Olfactometer3" = $olfactometer3
    "Define Device.WhiteRabbit" = $whiteRabbit
    "Initialize Device.main_flow" = $mainFlow
    "Initialize Device.contorl_flow" = $controlFlow
    "Initialize Device.fulsh_flow" = $flushFlow
    "Initialize Device.StartFlow" = $startFlowKey
    "Initialize Device.DisableFlow" = $disableFlowKey
    "Initialize Device.StartPPS" = $startPpsKey
    "Initialize Device.EndPPS" = $endPpsKey
    "Odor loop.Count" = $trialCount
    "Odor loop.Start_experiment" = $startExperimentKey
    "Odor loop.charge time" = ConvertTo-Duration $charge
    "Odor loop.EndV0Delay" = ConvertTo-Duration $delivery
    "Odor loop.flush_time" = ConvertTo-Duration $flush
    "Odor loop.recharge_t" = ConvertTo-Duration $recharge
    "Odor loop.FlowADJt" = ConvertTo-Duration $flowAdjustment
    "Odor loop.time_before_odor" = ConvertTo-Duration $timeBeforeOdor
    "Odor loop.ISI_low (s)" = $isiMinimum.ToString([Globalization.CultureInfo]::InvariantCulture)
    "Odor loop.ISI_high (s)" = $isiMaximum.ToString([Globalization.CultureInfo]::InvariantCulture)
    "Odor loop.webhook" = $webhook
    "Logging.Path" = $dataDirectory
}

Write-Host "Validated experiment '$experimentId' for subject '$subjectId' (operator: $operator)."
Write-Host "Configuration: $configPath"
Write-Host ("  Odor loop.Expression = {0} ({1} characters)" -f $stimulusPath, $stimulusExpression.Length)
$properties.GetEnumerator() | ForEach-Object {
    Write-Host ("  {0} = {1}" -f $_.Key, $_.Value)
}

if ($ValidateOnly) {
    Write-Host "Validation succeeded; Bonsai was not started."
    exit 0
}

$runtimeWorkflowPath = Join-Path $root "3device1blank.runtime.bonsai"
$workflowXml = [System.Xml.XmlDocument]::new()
$workflowXml.PreserveWhitespace = $true
$workflowXml.Load($workflowPath)
$namespaceManager = [System.Xml.XmlNamespaceManager]::new($workflowXml.NameTable)
$namespaceManager.AddNamespace("scr", "clr-namespace:Bonsai.Scripting.Expressions;assembly=Bonsai.Scripting.Expressions")
$namespaceManager.AddNamespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")
$expressionNode = $workflowXml.SelectSingleNode(
    '//*[@xsi:type="scr:ExpressionTransform"][scr:Name="9odor_block"]/scr:Expression',
    $namespaceManager
)
if ($null -eq $expressionNode) {
    throw "Could not find the 9odor_block expression in 3device1blank.bonsai."
}
$expressionNode.InnerText = $stimulusExpression
$workflowXml.Save($runtimeWorkflowPath)

$bonsaiArgs = @($runtimeWorkflowPath)
if ($NoEditor -and $OpenOnly) { throw "Use either -NoEditor or -OpenOnly, not both." }
if ($NoEditor) { $bonsaiArgs += "--no-editor" }
elseif (-not $OpenOnly) { $bonsaiArgs += "--start" }
foreach ($entry in $properties.GetEnumerator()) {
    $bonsaiArgs += "-p"
    $bonsaiArgs += ($entry.Key + "=" + $entry.Value)
}

try {
    & $bonsaiPath @bonsaiArgs
    $exitCode = $LASTEXITCODE
} finally {
    Remove-Item -LiteralPath $runtimeWorkflowPath -Force -ErrorAction SilentlyContinue
}
exit $exitCode
