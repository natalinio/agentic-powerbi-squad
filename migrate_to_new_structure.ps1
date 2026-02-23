# =============================================================================
# Migration Script — Restructure SalesOverviewFYTD project
# =============================================================================
# Migrates from flat PBIP/ structure to project-based <ProjectName>/ structure
#
# Usage:
#   cd <repo_root>
#   .\migrate_to_new_structure.ps1
#
# Before running:
#   1. Close Power BI Desktop
#   2. Commit any pending changes to git
#   3. Run from the repository root folder
# =============================================================================

$ErrorActionPreference = "Stop"
$RepoRoot = Get-Location
$ProjectName = "SalesOverviewFYTD"

Write-Host ""
Write-Host ("=" * 65) -ForegroundColor Cyan
Write-Host "  REPOSITORY MIGRATION SCRIPT — $ProjectName" -ForegroundColor Cyan
Write-Host ("=" * 65) -ForegroundColor Cyan
Write-Host ""
Write-Host "  Source:  PBIP/" -ForegroundColor Yellow
Write-Host "  Target:  $ProjectName/" -ForegroundColor Green
Write-Host ""

# ─────────────────────────────────────────────────────────────────
# PRE-FLIGHT CHECKS
# ─────────────────────────────────────────────────────────────────

Write-Host "[Pre-flight] Verifying source structure..." -ForegroundColor White

$requiredPaths = @(
    "PBIP\$ProjectName.pbip",
    "PBIP\$ProjectName.SemanticModel",
    "PBIP\$ProjectName.Report",
    "PBIP\data",
    "PBIP\scripts\generate_mock_data.py",
    "PBIP\spec_sales_overview_fytd.md",
    "PBIP\$ProjectName\tests\tests_definition.json"
)

$missingPaths = @()
foreach ($p in $requiredPaths) {
    if (-not (Test-Path $p)) {
        $missingPaths += $p
    }
}

if ($missingPaths.Count -gt 0) {
    Write-Host ""
    Write-Host "  ERROR: Required source paths not found:" -ForegroundColor Red
    $missingPaths | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
    Write-Host ""
    Write-Host "  Make sure you are running this script from the repository root." -ForegroundColor Yellow
    exit 1
}

Write-Host "  All source paths verified." -ForegroundColor Green
Write-Host ""

# ─────────────────────────────────────────────────────────────────
# STEP 1: Create target directory structure
# ─────────────────────────────────────────────────────────────────

Write-Host "[1/8] Creating target directory structure..." -ForegroundColor White

$targetDirs = @(
    "$ProjectName\PBIP",
    "$ProjectName\data",
    "$ProjectName\scripts",
    "$ProjectName\tests",
    "$ProjectName\input"
)

foreach ($dir in $targetDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  + Created: $dir/" -ForegroundColor Green
    } else {
        Write-Host "  = Exists:  $dir/" -ForegroundColor DarkGray
    }
}

# ─────────────────────────────────────────────────────────────────
# STEP 2: Move Power BI Canvas files (.pbip, SemanticModel, Report)
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[2/8] Moving Power BI project files..." -ForegroundColor White

Move-Item "PBIP\$ProjectName.pbip" "$ProjectName\PBIP\" -Force
Write-Host "  > Moved: $ProjectName.pbip" -ForegroundColor Green

Move-Item "PBIP\$ProjectName.SemanticModel" "$ProjectName\PBIP\" -Force
Write-Host "  > Moved: $ProjectName.SemanticModel/" -ForegroundColor Green

Move-Item "PBIP\$ProjectName.Report" "$ProjectName\PBIP\" -Force
Write-Host "  > Moved: $ProjectName.Report/" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────────
# STEP 3: Move CSV data files
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[3/8] Moving CSV data files..." -ForegroundColor White

Get-ChildItem "PBIP\data\*.csv" | ForEach-Object {
    Move-Item $_.FullName "$ProjectName\data\" -Force
    Write-Host "  > Moved: $($_.Name)" -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────────
# STEP 4: Move specification file to input/
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[4/8] Moving specification file..." -ForegroundColor White

Move-Item "PBIP\spec_sales_overview_fytd.md" "$ProjectName\input\" -Force
Write-Host "  > Moved: spec_sales_overview_fytd.md -> input/" -ForegroundColor Green

# ─────────────────────────────────────────────────────────────────
# STEP 5: Move project scripts (generate_mock_data.py only)
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[5/8] Moving project scripts..." -ForegroundColor White

Move-Item "PBIP\scripts\generate_mock_data.py" "$ProjectName\scripts\" -Force
Write-Host "  > Moved: generate_mock_data.py -> scripts/" -ForegroundColor Green
Write-Host "  - Skipped: remove_tmdl_comments.py (superseded by .github/scripts/)" -ForegroundColor DarkGray

# ─────────────────────────────────────────────────────────────────
# STEP 6: Move test artifacts (keep only essential files)
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[6/8] Moving test artifacts..." -ForegroundColor White

$testFilesToMove = @(
    "tests_definition.json",
    "tests_definition.md",
    "tests_execution.md",
    "tests_execution_raw.json"
)

foreach ($file in $testFilesToMove) {
    $src = "PBIP\$ProjectName\tests\$file"
    if (Test-Path $src) {
        Move-Item $src "$ProjectName\tests\" -Force
        Write-Host "  > Moved: $file" -ForegroundColor Green
    } else {
        Write-Host "  ! Not found: $file" -ForegroundColor Yellow
    }
}

Write-Host "  - Skipped: run_tests.py (superseded by .github/scripts/run_tests.py)" -ForegroundColor DarkGray
Write-Host "  - Skipped: requirements.txt (superseded by root requirements.txt)" -ForegroundColor DarkGray
Write-Host "  - Skipped: README.md (will be recreated)" -ForegroundColor DarkGray

# ─────────────────────────────────────────────────────────────────
# STEP 7: Update path references in migrated files
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[7/8] Updating path references in migrated files..." -ForegroundColor White

# 7a. generate_mock_data.py — OUTPUT_DIR and print statements
$scriptFile = "$ProjectName\scripts\generate_mock_data.py"
if (Test-Path $scriptFile) {
    $content = Get-Content $scriptFile -Raw -Encoding UTF8
    $content = $content -replace 'OUTPUT_DIR = "PBIP/data"', "OUTPUT_DIR = `"$ProjectName/data`""
    $content = $content -replace 'Review generated CSV files in PBIP/data/', "Review generated CSV files in $ProjectName/data/"
    $content = $content -replace 'Open SalesOverviewFYTD\.pbip in Power BI Desktop', "Open $ProjectName/PBIP/SalesOverviewFYTD.pbip in Power BI Desktop"
    [System.IO.File]::WriteAllText((Resolve-Path $scriptFile).Path, $content, [System.Text.Encoding]::UTF8)
    Write-Host "  * Updated: generate_mock_data.py (OUTPUT_DIR, print paths)" -ForegroundColor Cyan
}

# 7b. tests_definition.json — specificationFile and CSV notes
$testDefFile = "$ProjectName\tests\tests_definition.json"
if (Test-Path $testDefFile) {
    $content = Get-Content $testDefFile -Raw -Encoding UTF8
    $content = $content -replace '"specificationFile": "PBIP/spec_sales_overview_fytd.md"', "`"specificationFile`": `"$ProjectName/input/spec_sales_overview_fytd.md`""
    $content = $content -replace 'PBIP/data/', "$ProjectName/data/"
    [System.IO.File]::WriteAllText((Resolve-Path $testDefFile).Path, $content, [System.Text.Encoding]::UTF8)
    Write-Host "  * Updated: tests_definition.json (specificationFile, CSV paths)" -ForegroundColor Cyan
}

# 7c. tests_definition.md — specification and data paths
$testDefMd = "$ProjectName\tests\tests_definition.md"
if (Test-Path $testDefMd) {
    $content = Get-Content $testDefMd -Raw -Encoding UTF8
    $content = $content -replace 'PBIP/spec_sales_overview_fytd\.md', "$ProjectName/input/spec_sales_overview_fytd.md"
    $content = $content -replace 'PBIP/data/', "$ProjectName/data/"
    $content = $content -replace 'PBIP\\SalesOverviewFYTD\\tests', "$ProjectName\tests"
    $content = $content -replace 'cd PBIP\\SalesOverviewFYTD\\tests', "cd $ProjectName\tests"
    [System.IO.File]::WriteAllText((Resolve-Path $testDefMd).Path, $content, [System.Text.Encoding]::UTF8)
    Write-Host "  * Updated: tests_definition.md (specification, data paths)" -ForegroundColor Cyan
}

# 7d. TMDL CSV partition paths (CRITICAL — absolute paths in M expressions)
$tmdlTablesDir = "$ProjectName\PBIP\$ProjectName.SemanticModel\definition\tables"
if (Test-Path $tmdlTablesDir) {
    Write-Host ""
    Write-Host "  Updating TMDL CSV partition paths..." -ForegroundColor White
    Get-ChildItem "$tmdlTablesDir\*.tmdl" | ForEach-Object {
        $content = Get-Content $_.FullName -Raw -Encoding UTF8
        if ($content -match '\\PBIP\\data\\') {
            $content = $content -replace '\\PBIP\\data\\', "\$ProjectName\data\"
            [System.IO.File]::WriteAllText($_.FullName, $content, [System.Text.Encoding]::UTF8)
            Write-Host "  * Updated TMDL: $($_.Name)" -ForegroundColor Cyan
        }
    }
}

# ─────────────────────────────────────────────────────────────────
# STEP 8: Clean up old PBIP/ folder
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "[8/8] Cleaning up old structure..." -ForegroundColor White

if (Test-Path "PBIP") {
    Remove-Item "PBIP" -Recurse -Force
    Write-Host "  - Removed: PBIP/ (old structure)" -ForegroundColor Green
}

# ─────────────────────────────────────────────────────────────────
# COMPLETION
# ─────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host ("=" * 65) -ForegroundColor Green
Write-Host "  MIGRATION COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host ("=" * 65) -ForegroundColor Green
Write-Host ""
Write-Host "  New project structure:" -ForegroundColor White
Write-Host "  $ProjectName/" -ForegroundColor Cyan
Write-Host "    +-- PBIP/" -ForegroundColor Cyan
Write-Host "    |   +-- SalesOverviewFYTD.pbip" -ForegroundColor Cyan
Write-Host "    |   +-- SalesOverviewFYTD.SemanticModel/" -ForegroundColor Cyan
Write-Host "    |   +-- SalesOverviewFYTD.Report/" -ForegroundColor Cyan
Write-Host "    +-- data/ (10 CSV files)" -ForegroundColor Cyan
Write-Host "    +-- scripts/generate_mock_data.py" -ForegroundColor Cyan
Write-Host "    +-- tests/ (test artifacts)" -ForegroundColor Cyan
Write-Host "    +-- input/spec_sales_overview_fytd.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor Yellow
Write-Host "    1. Open $ProjectName/PBIP/SalesOverviewFYTD.pbip in Power BI Desktop" -ForegroundColor White
Write-Host "    2. Verify model loads without errors (CSV paths updated in TMDL)" -ForegroundColor White
Write-Host "    3. Refresh all tables to confirm data loads" -ForegroundColor White
Write-Host "    4. Run tests: python .github/scripts/run_tests.py $ProjectName --port <port>" -ForegroundColor White
Write-Host "    5. Delete this migration script: Remove-Item migrate_to_new_structure.ps1" -ForegroundColor White
Write-Host ""
