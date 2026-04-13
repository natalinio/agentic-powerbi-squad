param(
    [switch]$AsJson
)

$workspaceRoot = Join-Path $env:LOCALAPPDATA "Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"

if (-not (Test-Path $workspaceRoot)) {
    Write-Error "AnalysisServicesWorkspaces path not found: $workspaceRoot"
    exit 1
}

$portFiles = Get-ChildItem -Path $workspaceRoot -Recurse -Filter "msmdsrv.port.txt" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending

if (-not $portFiles -or $portFiles.Count -eq 0) {
    Write-Error "No msmdsrv.port.txt file found under $workspaceRoot"
    exit 1
}

$selected = $portFiles[0]
$rawPort = (Get-Content -Path $selected.FullName -ErrorAction Stop | Select-Object -First 1).Trim()
$normalizedPort = ($rawPort -replace "[^0-9]", "").Trim()

$port = 0
if ([string]::IsNullOrWhiteSpace($normalizedPort) -or -not [int]::TryParse($normalizedPort, [ref]$port)) {
    Write-Error "Invalid port value '$rawPort' in $($selected.FullName)"
    exit 1
}

$result = [PSCustomObject]@{
    port = $port
    portFile = $selected.FullName
    workspace = $selected.DirectoryName
    detectedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
}

if ($AsJson) {
    $result | ConvertTo-Json -Depth 4
} else {
    Write-Host "PORT=$($result.port)"
    Write-Host "PORT_FILE=$($result.portFile)"
    Write-Host "WORKSPACE=$($result.workspace)"
}
