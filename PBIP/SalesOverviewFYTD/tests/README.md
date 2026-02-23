# Functional Tests — Sales Overview FYTD

This folder contains automated functional tests for the Sales Overview FYTD semantic model.

## Files

- **`tests_definition.json`**: Test cases definition with DAX queries, expected behaviors, and validation methods
- **`run_tests.py`**: Python script to execute DAX queries against local Power BI Desktop Analysis Services
- **`tests_execution.md`**: Test execution report with results, recommendations, and pass/fail status
- **`tests_execution_raw.json`**: Raw test results in JSON format (machine-readable)
- **`requirements.txt`**: Python dependencies for test execution

## How to Run Tests

### Prerequisites
1. **Power BI Desktop** must be OPEN with `SalesOverviewFYTD.pbip` loaded
2. **Model loaded successfully** (no errors or warnings)
3. **Python 3.10+** installed
4. **Virtual environment** activated (recommended)

### Step 1: Install Dependencies
```powershell
cd PBIP\SalesOverviewFYTD\tests
pip install -r requirements.txt
```

**Important**: The script uses **pythonnet** to call Microsoft ADOMD.NET libraries (Analysis Services native client). This requires:
- **Power BI Desktop installed** (provides Microsoft.AnalysisServices.AdomdClient.dll)
- **.NET Framework 4.7.2+** (typically pre-installed on Windows)

### Step 2: Detect Analysis Services Port
The script will auto-detect the local Analysis Services workspace. If auto-detection fails, you can manually specify the port:

```powershell
# Find workspace folder
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces"

# Read port from msmdsrv.port.txt
Get-Content "$env:LOCALAPPDATA\Microsoft\Power BI Desktop\AnalysisServicesWorkspaces\<WorkspaceID>\msmdsrv.port.txt"
```

### Step 3: Run Tests
```powershell
python run_tests.py
```

#### Optional: Specify port manually
```powershell
python run_tests.py --port 12345
```

### Step 4: Review Results
Open `tests_execution.md` to see detailed test results with recommendations.

## Test Execution Frequency

- **Initial validation**: After Step 6 (Quality Review) completion
- **Regression testing**: After any DAX measure modification
- **Pre-deployment**: Before publishing model to Power BI Service
- **CI/CD integration**: Automated testing on every commit (optional)

## Troubleshooting

### Error: "Cannot connect to Analysis Services"
**Solution**: Verify Power BI Desktop is open and model is loaded. Check Analysis Services workspace is active.

### Error: "Module 'clr' not found" or "No module named 'clr'"
**Solution**: Install dependencies: `pip install -r requirements.txt`  
**Note**: `clr` is provided by `pythonnet` package. If installation fails, try: `pip install --upgrade pythonnet`

### Error: "Failed to load ADOMD.NET assembly" or "Could not load file or assembly 'Microsoft.AnalysisServices.AdomdClient'"
**Solution**: This assembly is provided by Power BI Desktop. Verify:
1. Power BI Desktop is installed (check `C:\Program Files\Microsoft Power BI Desktop\bin\`)
2. The `Microsoft.AnalysisServices.AdomdClient.dll` file exists in that folder
3. If Power BI Desktop is installed but DLL not found, try reinstalling Power BI Desktop

### Error: "Query execution timeout"
**Solution**: Increase timeout in `run_tests.py` (default 30 seconds). Check model performance.

### Error: "Test results differ from expected"
**Solution**: Review `tests_execution.md` for specific failures and recommendations. Apply fixes to DAX measures as suggested.

## Contact

For issues or questions about functional testing, refer to:
- Skill documentation: `.github/skills/07-functional-testing.md`
- DAX optimization: `.github/references/dax-optimization-framework.md`
- BPA rules: `.github/references/bpa-rules-reference.md`
