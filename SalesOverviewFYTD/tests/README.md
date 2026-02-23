# Functional Tests — Sales Overview FYTD

This folder contains automated functional tests for the Sales Overview FYTD semantic model.

## Files

- **`tests_definition.json`**: Test cases definition with DAX queries, expected behaviors, and validation methods
- **`tests_definition.md`**: Human-readable test guide with manual validation steps
- **`tests_execution.md`**: Test execution report with results and pass/fail status
- **`tests_execution_raw.json`**: Raw test results in JSON format (machine-readable)

## How to Run Tests

### Prerequisites
1. **Power BI Desktop** must be OPEN with `SalesOverviewFYTD/PBIP/SalesOverviewFYTD.pbip` loaded
2. **Model loaded successfully** (no errors or warnings)
3. **Python 3.10+** installed with virtual environment activated
4. **Dependencies installed**: `pip install -r requirements.txt` (from repo root)

### Step 1: Activate Virtual Environment
```powershell
cd <repo_root>
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Important**: The universal test runner uses **pythonnet** to call Microsoft ADOMD.NET libraries. This requires:
- **Power BI Desktop installed** (provides `Microsoft.AnalysisServices.AdomdClient.dll`)
- **.NET Framework 4.7.2+** (typically pre-installed on Windows)

### Step 2: Detect Analysis Services Port
The test runner auto-detects the local Analysis Services workspace. If auto-detection fails:

```powershell
# Find workspace folder
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"

# Read port from msmdsrv.port.txt
Get-Content "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\<WorkspaceID>\msmdsrv.port.txt"
```

### Step 3: Run Tests (Universal Runner)
```powershell
# From repo root — auto-detect port
python .github/scripts/run_tests.py SalesOverviewFYTD

# With explicit port
python .github/scripts/run_tests.py SalesOverviewFYTD --port 65518

# With verbose output
python .github/scripts/run_tests.py SalesOverviewFYTD --verbose
```

### Step 4: Review Results
Open `SalesOverviewFYTD/tests/tests_execution.md` to see detailed test results with recommendations.

## Test Execution Frequency

- **Initial validation**: After Step 6 (Quality Review) completion
- **Regression testing**: After any DAX measure modification
- **Pre-deployment**: Before publishing model to Power BI Service

## Troubleshooting

### Error: "Cannot connect to Analysis Services"
**Solution**: Verify Power BI Desktop is open and model is loaded. Check Analysis Services workspace is active.

### Error: "Module 'clr' not found"
**Solution**: Install dependencies: `pip install -r requirements.txt` (from repo root)

### Error: "Failed to load ADOMD.NET assembly"
**Solution**: Verify Power BI Desktop is installed:
1. Check `C:\Program Files\Microsoft Power BI Desktop\bin\`
2. Verify `Microsoft.AnalysisServices.AdomdClient.dll` or `Microsoft.PowerBI.AdomdClient.dll` exists

### Error: "Project folder not found"
**Solution**: Make sure you run the test runner from the repository root, not from the tests/ folder.

## References

- Skill documentation: `.github/skills/07-functional-testing.md`
- DAX optimization: `.github/references/dax-optimization-framework.md`
- BPA rules: `.github/references/bpa-rules-reference.md`
