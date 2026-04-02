"""
Automated Functional Testing for Power BI Semantic Models (Universal Tool)

This script executes DAX queries against a local Power BI Desktop Analysis Services
workspace to validate measure calculations, time intelligence behavior, and edge cases.

It is project-agnostic: test definitions, data files, and outputs are resolved
from the project folder passed as argument.

Prerequisites:
- Power BI Desktop OPEN with PBIP project loaded
- Python 3.10+
- Dependencies installed: pip install -r requirements.txt

Usage:
    python .github/scripts/run_tests.py <ProjectName>
    python .github/scripts/run_tests.py <ProjectName> --port 65518
    python .github/scripts/run_tests.py <ProjectName> --verbose

Arguments:
    ProjectName: Name of the project folder (e.g., SalesOverviewFYTD)
                 Test definition: <ProjectName>/tests/tests_definition.json
                 Data folder:     <ProjectName>/data/
                 Output folder:   <ProjectName>/tests/
"""

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import pandas as pd
    import clr  # pythonnet - Python for .NET
except ImportError as e:
    print(f"❌ ERROR: Missing required dependency: {e}")
    print("Install dependencies: pip install -r requirements.txt")
    sys.exit(1)


# Resolve repository root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class AnalysisServicesDetector:
    """Detects local Power BI Desktop Analysis Services workspace"""

    @staticmethod
    def _resolve_port_file(workspace_dir: Path) -> Optional[Path]:
        """Resolve the Power BI Desktop port file for a workspace."""
        direct_port_file = workspace_dir / 'msmdsrv.port.txt'
        if direct_port_file.exists():
            return direct_port_file

        data_port_file = workspace_dir / 'Data' / 'msmdsrv.port.txt'
        if data_port_file.exists():
            return data_port_file

        nested_matches = sorted(workspace_dir.rglob('msmdsrv.port.txt'))
        if nested_matches:
            return nested_matches[0]

        return None

    @staticmethod
    def find_workspace_port() -> Optional[int]:
        """
        Auto-detect Analysis Services workspace port from Power BI Desktop

        Returns:
            int: Port number if found, None otherwise
        """
        localappdata = os.getenv('LOCALAPPDATA')
        workspaces_path = Path(localappdata) / 'Microsoft' / 'Power BI Desktop' / 'AnalysisServicesWorkspaces'

        if not workspaces_path.exists():
            return None

        # Find most recent workspace (largest timestamp folder)
        workspaces = [d for d in workspaces_path.iterdir() if d.is_dir()]
        if not workspaces:
            return None

        # Sort by modification time, get most recent
        most_recent = max(workspaces, key=lambda d: d.stat().st_mtime)

        # Power BI Desktop commonly stores the port file under the workspace Data folder.
        port_file = AnalysisServicesDetector._resolve_port_file(most_recent)
        if not port_file or not port_file.exists():
            return None

        try:
            port = int(port_file.read_text().strip())
            return port
        except (ValueError, IOError):
            return None


class DAXTestExecutor:
    """Executes DAX queries and validates results using ADOMD.NET"""

    def __init__(self, port: int, verbose: bool = False):
        self.port = port
        self.verbose = verbose
        self.conn = None
        self.model_name = None
        self._load_adomd_assembly()

    def _load_adomd_assembly(self):
        """Load ADOMD.NET assembly from Power BI Desktop"""
        try:
            # Possible Power BI Desktop installation paths
            pbi_paths = [
                r"C:\Program Files\Microsoft Power BI Desktop\bin",
                r"C:\Program Files (x86)\Microsoft Power BI Desktop\bin"
            ]

            # Power BI Desktop uses a proprietary wrapper: Microsoft.PowerBI.AdomdClient.dll
            # Standard ADOMD.NET: Microsoft.AnalysisServices.AdomdClient.dll
            dll_candidates = [
                "Microsoft.PowerBI.AdomdClient.dll",
                "Microsoft.AnalysisServices.AdomdClient.dll"
            ]

            dll_path = None
            dll_name = None

            # Search for ADOMD.NET DLL
            for base_path in pbi_paths:
                for candidate_dll in dll_candidates:
                    candidate_path = os.path.join(base_path, candidate_dll)
                    if os.path.exists(candidate_path):
                        dll_path = candidate_path
                        dll_name = candidate_dll
                        if self.verbose:
                            print(f"✅ Found ADOMD.NET assembly: {dll_path}")
                        break
                if dll_path:
                    break

            if not dll_path:
                raise FileNotFoundError(
                    f"Could not find ADOMD.NET client DLL in Power BI Desktop installation. "
                    f"Searched paths: {pbi_paths}\n"
                    f"Searched DLLs: {dll_candidates}\n"
                    f"Please verify Power BI Desktop is installed."
                )

            # Load assembly using full path
            clr.AddReference(dll_path)

            # Import ADOMD classes - try both namespaces
            global AdomdConnection, AdomdCommand
            try:
                # Power BI Desktop proprietary wrapper
                from Microsoft.PowerBI.AdomdClient import AdomdConnection, AdomdCommand
            except ImportError:
                # Standard ADOMD.NET
                from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand

            if self.verbose:
                print("✅ Loaded ADOMD.NET client library")

        except Exception as e:
            print(f"❌ Failed to load ADOMD.NET assembly: {e}")
            print("Make sure Power BI Desktop is installed.")
            raise

    def connect(self) -> bool:
        """Establish connection to Analysis Services using ADOMD.NET"""
        try:
            conn_str = f"Data Source=localhost:{self.port};"

            if self.verbose:
                print(f"🔌 Connecting to Analysis Services: localhost:{self.port} (ADOMD.NET)")

            self.conn = AdomdConnection(conn_str)
            self.conn.Open()

            # Verify connection works by running a simple DAX query
            try:
                cmd = self.conn.CreateCommand()
                cmd.CommandText = 'EVALUATE ROW("test", 1)'
                reader = cmd.ExecuteReader()
                reader.Close()
                if self.verbose:
                    print("✅ Connected to Analysis Services")
                return True
            except Exception as verify_err:
                print(f"❌ Connection opened but query verification failed: {verify_err}")
                return False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def execute_query(self, dax_query: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a DAX query and return results using ADOMD.NET"""
        if not self.conn:
            return {'success': False, 'error': 'Not connected to Analysis Services'}

        start_time = datetime.now()

        try:
            cmd = self.conn.CreateCommand()
            cmd.CommandText = dax_query
            cmd.CommandTimeout = timeout

            reader = cmd.ExecuteReader()

            # Get column names
            columns = [reader.GetName(i) for i in range(reader.FieldCount)]

            # Fetch all rows
            data = []
            while reader.Read():
                row_dict = {}
                for i in range(reader.FieldCount):
                    col_name = columns[i]
                    value = reader.GetValue(i)

                    # Convert .NET types to Python types
                    if value is None or str(value) == '':
                        row_dict[col_name] = None
                    elif hasattr(value, '__float__'):
                        row_dict[col_name] = float(value)
                    elif hasattr(value, '__int__'):
                        row_dict[col_name] = int(value)
                    else:
                        row_dict[col_name] = str(value)

                data.append(row_dict)

            reader.Close()

            execution_time = (datetime.now() - start_time).total_seconds()

            if self.verbose:
                print(f"  ⏱️  Query executed in {execution_time:.2f}s")

            return {
                'success': True,
                'data': data,
                'columns': columns,
                'row_count': len(data),
                'execution_time': execution_time,
                'error': None
            }

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return {
                'success': False,
                'data': None,
                'execution_time': execution_time,
                'error': str(e)
            }

    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.Close()


class CSVValidator:
    """Validates DAX results against CSV source data"""

    def __init__(self, data_folder: Path):
        self.data_folder = data_folder
        self.csv_cache = {}

    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV file with caching"""
        if filename not in self.csv_cache:
            filepath = self.data_folder / filename
            if not filepath.exists():
                raise FileNotFoundError(f"CSV file not found: {filepath}")
            self.csv_cache[filename] = pd.read_csv(filepath)
        return self.csv_cache[filename]

    def calculate_total(self, filename: str, column: str) -> float:
        """Calculate total for a numeric column in CSV"""
        df = self.load_csv(filename)
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in {filename}")
        return df[column].sum()


class TestAssertionEvaluator:
    """Evaluates test results against explicit or legacy test-plan assertions."""

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value

        text = str(value).strip()
        if text == '':
            return None

        lowered = text.lower()
        if lowered == 'true':
            return True
        if lowered == 'false':
            return False

        try:
            numeric_value = float(text)
            if math.isfinite(numeric_value):
                return numeric_value
        except ValueError:
            pass

        return text

    @staticmethod
    def _extract_scalar(data: Optional[List[Dict[str, Any]]]) -> Any:
        if not data or len(data) != 1:
            return None

        row = data[0]
        if len(row) != 1:
            return None

        return TestAssertionEvaluator._normalize_value(next(iter(row.values())))

    @staticmethod
    def _extract_row(data: Optional[List[Dict[str, Any]]]) -> Optional[Dict[str, Any]]:
        if not data or len(data) != 1:
            return None

        return {
            key.strip('[]'): TestAssertionEvaluator._normalize_value(value)
            for key, value in data[0].items()
        }

    @staticmethod
    def _parse_tolerance(pass_threshold: str) -> Optional[float]:
        match = re.search(r'Absolute delta <\s*([0-9.]+)', pass_threshold or '')
        if not match:
            return None
        return float(match.group(1))

    @staticmethod
    def _safe_float(text: str) -> float:
        return float(text.rstrip('.,;: '))

    @staticmethod
    def _parse_expected_scalar(test: Dict[str, Any]) -> Any:
        if 'expectedValue' in test:
            return test.get('expectedValue')

        expected_behavior = test.get('expectedBehavior', '')
        pass_threshold = test.get('passThreshold', '')

        if pass_threshold == 'Result is BLANK':
            return None

        if pass_threshold == 'Exact boolean match':
            if 'TRUE' in expected_behavior.upper():
                return True
            if 'FALSE' in expected_behavior.upper():
                return False

        if pass_threshold == 'Exact string match':
            label_match = re.search(r'Returns\s+([^\.]+?)(?:\s+because|\.|$)', expected_behavior)
            if label_match:
                return label_match.group(1).strip()

        numeric_match = re.search(r'Expected value:\s*([-0-9.]+)', expected_behavior)
        if numeric_match:
            return TestAssertionEvaluator._safe_float(numeric_match.group(1))

        returns_match = re.search(r'returns\s+([-0-9.]+)', expected_behavior, flags=re.IGNORECASE)
        if returns_match:
            return TestAssertionEvaluator._safe_float(returns_match.group(1))

        if 'no prior-year rows' in expected_behavior.lower():
            return None

        return None

    @staticmethod
    def _parse_expected_row(test: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if 'expectedRow' in test:
            return test.get('expectedRow')

        expected_behavior = test.get('expectedBehavior', '')
        if 'SalesActual' in expected_behavior and 'BudgetActual' in expected_behavior:
            sales_match = re.search(r'SalesActual\s*=\s*([-0-9.]+)', expected_behavior)
            budget_match = re.search(r'BudgetActual\s*=\s*([-0-9.]+)', expected_behavior)
            if sales_match and budget_match:
                return {
                    'SalesActual': TestAssertionEvaluator._safe_float(sales_match.group(1)),
                    'BudgetActual': TestAssertionEvaluator._safe_float(budget_match.group(1))
                }

        return None

    @staticmethod
    def _resolve_assertion_type(test: Dict[str, Any]) -> str:
        if 'assertionType' in test:
            return test['assertionType']

        pass_threshold = test.get('passThreshold', '')
        expected_behavior = test.get('expectedBehavior', '')

        if pass_threshold == 'Result is BLANK':
            return 'blank'
        if pass_threshold == 'Exact string match':
            return 'exact'
        if pass_threshold == 'Exact boolean match':
            return 'exact'
        if pass_threshold == 'Exact match':
            return 'exact'
        if 'for both values' in pass_threshold:
            return 'row_numeric_tolerance'
        if pass_threshold.startswith('Absolute delta <'):
            return 'numeric_tolerance'
        if 'no prior-year rows' in expected_behavior.lower():
            return 'blank'

        return 'execution_only'

    @staticmethod
    def evaluate(test: Dict[str, Any], query_result: Dict[str, Any]) -> Dict[str, Any]:
        if not query_result['success']:
            return {
                'status': 'FAIL',
                'actualValue': None,
                'expectedValue': None,
                'delta': None,
                'assertionType': 'query_error',
                'assertionMessage': query_result.get('error') or 'Query execution failed.',
                'recommendation': 'Fix the DAX query or required model objects before re-running the test.'
            }

        assertion_type = TestAssertionEvaluator._resolve_assertion_type(test)
        tolerance = test.get('tolerance', TestAssertionEvaluator._parse_tolerance(test.get('passThreshold', '')))
        actual_scalar = TestAssertionEvaluator._extract_scalar(query_result.get('data'))
        actual_row = TestAssertionEvaluator._extract_row(query_result.get('data'))
        expected_scalar = TestAssertionEvaluator._normalize_value(TestAssertionEvaluator._parse_expected_scalar(test))
        expected_row = TestAssertionEvaluator._parse_expected_row(test)

        if assertion_type == 'blank':
            passed = actual_scalar is None
            return {
                'status': 'PASS' if passed else 'FAIL',
                'actualValue': actual_scalar,
                'expectedValue': None,
                'delta': None,
                'assertionType': assertion_type,
                'assertionMessage': 'Expected BLANK result.' if passed else f'Expected BLANK but got {actual_scalar!r}.',
                'recommendation': None if passed else 'Re-check the filter context and DIVIDE/BLANK propagation for this measure.'
            }

        if assertion_type == 'numeric_tolerance':
            if actual_scalar is None or expected_scalar is None:
                return {
                    'status': 'FAIL',
                    'actualValue': actual_scalar,
                    'expectedValue': expected_scalar,
                    'delta': None,
                    'assertionType': assertion_type,
                    'assertionMessage': 'Numeric tolerance assertion requires scalar actual and expected values.',
                    'recommendation': 'Define an explicit expectedValue or adjust the DAX query to return a single scalar.'
                }

            delta = abs(float(actual_scalar) - float(expected_scalar))
            passed = delta < float(tolerance)
            return {
                'status': 'PASS' if passed else 'FAIL',
                'actualValue': actual_scalar,
                'expectedValue': expected_scalar,
                'delta': delta,
                'assertionType': assertion_type,
                'assertionMessage': f'Delta {delta:.6f} with tolerance {float(tolerance):.6f}.',
                'recommendation': None if passed else 'Investigate measure logic, filter context, or CSV expectation derivation.'
            }

        if assertion_type == 'row_numeric_tolerance':
            if not actual_row or not expected_row:
                return {
                    'status': 'FAIL',
                    'actualValue': actual_row,
                    'expectedValue': expected_row,
                    'delta': None,
                    'assertionType': assertion_type,
                    'assertionMessage': 'Row tolerance assertion requires a one-row result and expectedRow metadata.',
                    'recommendation': 'Return a single row from DAX and define expectedRow in the test definition.'
                }

            deltas = {}
            passed = True
            for key, expected_value in expected_row.items():
                actual_value = TestAssertionEvaluator._normalize_value(actual_row.get(key))
                if actual_value is None:
                    passed = False
                    deltas[key] = None
                    continue
                delta = abs(float(actual_value) - float(expected_value))
                deltas[key] = delta
                if delta >= float(tolerance):
                    passed = False

            return {
                'status': 'PASS' if passed else 'FAIL',
                'actualValue': actual_row,
                'expectedValue': expected_row,
                'delta': deltas,
                'assertionType': assertion_type,
                'assertionMessage': f'Per-column deltas validated with tolerance {float(tolerance):.6f}.',
                'recommendation': None if passed else 'Investigate dimensional filter propagation or the row-level expected values.'
            }

        if assertion_type == 'exact':
            passed = actual_scalar == expected_scalar
            return {
                'status': 'PASS' if passed else 'FAIL',
                'actualValue': actual_scalar,
                'expectedValue': expected_scalar,
                'delta': None,
                'assertionType': assertion_type,
                'assertionMessage': 'Exact match confirmed.' if passed else f'Expected {expected_scalar!r} but got {actual_scalar!r}.',
                'recommendation': None if passed else 'Check the DAX expression and the expected output encoded in the test definition.'
            }

        execution_time = float(query_result.get('execution_time', 0))
        status = 'WARNING' if execution_time > 5.0 else 'PASS'
        return {
            'status': status,
            'actualValue': actual_scalar if actual_scalar is not None else actual_row,
            'expectedValue': None,
            'delta': None,
            'assertionType': assertion_type,
            'assertionMessage': 'Legacy execution-only test definition. Query executed successfully but no machine-readable assertion was supplied.',
            'recommendation': 'Add assertionType and expectedValue/expectedRow to avoid execution-only passes.' if status == 'PASS' else 'Optimize the query and add a machine-readable assertion.'
        }


class TestReportGenerator:
    """Generates markdown test execution report"""

    @staticmethod
    def generate_report(
        test_results: List[Dict[str, Any]],
        test_definition: Dict[str, Any],
        output_path: Path
    ):
        """Generate comprehensive markdown report"""
        report_lines = [
            f"# Test Execution Report — {test_definition['projectName']}",
            "",
            f"**Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Model**: {test_definition['projectName']}",
            f"**Test Plan**: tests_definition.json (v{test_definition.get('modelVersion', 'N/A')})",
            f"**Execution Mode**: Automated (Python + ADOMD.NET via pythonnet)",
            "",
            "---",
            "",
            "## Executive Summary",
            ""
        ]

        # Calculate summary statistics
        total_tests = len(test_results)
        passed = sum(1 for r in test_results if r['status'] == 'PASS')
        warnings = sum(1 for r in test_results if r['status'] == 'WARNING')
        failed = sum(1 for r in test_results if r['status'] == 'FAIL')

        report_lines.extend([
            "| Metric | Count |",
            "|---|---:|",
            f"| Total Tests | {total_tests} |",
            f"| ✅ Passed | {passed} |",
            f"| ⚠️ Warnings | {warnings} |",
            f"| ❌ Failed | {failed} |",
            "",
            f"**Overall Status**: {'✅ ALL TESTS PASSED' if failed == 0 and warnings == 0 else '⚠️ WARNINGS EXIST' if failed == 0 else '❌ FAILURES DETECTED'}",
            "",
            "---",
            "",
            "## Detailed Test Results",
            ""
        ])

        # Group results by suite
        for suite in test_definition.get('testSuites', []):
            suite_id = suite['suiteId']
            suite_name = suite['suiteName']
            priority = suite.get('priority', 'MEDIUM')
            suite_test_ids = {test['testId'] for test in suite.get('tests', [])}
            suite_results = [r for r in test_results if r['testId'] in suite_test_ids]

            suite_total = len(suite_results)
            suite_passed = sum(1 for r in suite_results if r['status'] == 'PASS')
            suite_warnings = sum(1 for r in suite_results if r['status'] == 'WARNING')
            suite_failed = sum(1 for r in suite_results if r['status'] == 'FAIL')

            report_lines.extend([
                f"### {suite_id}: {suite_name} (Priority: {priority})",
                "",
                "| Total | PASS | WARNING | FAIL |",
                "|---:|---:|---:|---:|",
                f"| {suite_total} | {suite_passed} | {suite_warnings} | {suite_failed} |",
                ""
            ])

            for result in suite_results:
                status_emoji = {'PASS': '✅', 'WARNING': '⚠️', 'FAIL': '❌'}.get(result['status'], '❓')

                report_lines.extend([
                    f"#### {status_emoji} {result['testId']} — {result['testName']}",
                    f"- **Measure**: `{result.get('measureName', 'N/A')}`",
                    f"- **Status**: {status_emoji} **{result['status']}**",
                    f"- **Assertion Type**: `{result.get('assertionType', 'N/A')}`",
                    f"- **Expected**: `{result.get('expectedValue')}`",
                    f"- **Actual**: `{result.get('actualValue')}`",
                    f"- **Delta**: `{result.get('delta')}`",
                    f"- **Query Time**: {result.get('executionTime', 0):.2f} sec",
                    f"- **Assertion Note**: {result.get('assertionMessage', 'N/A')}",
                    ""
                ])

                if result['status'] == 'FAIL':
                    report_lines.extend([
                        f"- **Error**: {result.get('error', 'Unknown error')}",
                        ""
                    ])
                elif result.get('recommendation'):
                    report_lines.extend([
                        f"- **Recommendation**: {result['recommendation']}",
                        ""
                    ])

                report_lines.append("")

        output_path.write_text('\n'.join(report_lines), encoding='utf-8')


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Execute functional tests for Power BI semantic model (universal tool)'
    )
    parser.add_argument(
        'project',
        help='Project folder name (e.g., SalesOverviewFYTD). '
             'Test definition: <project>/tests/tests_definition.json'
    )
    parser.add_argument('--port', type=int, help='Analysis Services port (auto-detect if not specified)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument(
        '--test-definition',
        default=None,
        help='Override test definition file path (default: <project>/tests/tests_definition.json)'
    )

    args = parser.parse_args()

    print("🧪 Power BI Semantic Model Functional Testing (Universal)")
    print("=" * 60)

    # Resolve project paths
    project_dir = REPO_ROOT / args.project
    tests_dir = project_dir / "tests"
    data_dir = project_dir / "data"

    if not project_dir.exists():
        print(f"❌ Project folder not found: {project_dir}")
        sys.exit(1)

    # Load test definition
    test_def_path = Path(args.test_definition) if args.test_definition else tests_dir / 'tests_definition.json'
    if not test_def_path.exists():
        print(f"❌ Test definition file not found: {test_def_path}")
        sys.exit(1)

    with open(test_def_path, 'r', encoding='utf-8') as f:
        test_definition = json.load(f)

    print(f"📋 Loaded test definition: {test_definition['projectName']}")
    print(f"📂 Project folder: {project_dir}")

    # Detect or use provided port
    port = args.port
    if not port:
        print("🔍 Auto-detecting Analysis Services workspace...")
        port = AnalysisServicesDetector.find_workspace_port()
        if not port:
            print("❌ Could not auto-detect Analysis Services workspace.")
            print("   Ensure Power BI Desktop is open with the model loaded.")
            print("   Or specify port manually: --port 12345")
            sys.exit(1)

    print(f"🔌 Using Analysis Services port: {port}")

    # Initialize executor
    executor = DAXTestExecutor(port, verbose=args.verbose)
    if not executor.connect():
        print("❌ Failed to connect to Analysis Services")
        sys.exit(1)

    # Execute tests
    test_results = []
    total_suites = len(test_definition.get('testSuites', []))
    total_tests = sum(len(suite['tests']) for suite in test_definition.get('testSuites', []))

    print(f"\n🚀 Executing {total_tests} tests across {total_suites} suites...\n")

    for suite in test_definition.get('testSuites', []):
        suite_name = suite['suiteName']
        print(f"📦 {suite['suiteId']}: {suite_name}")

        for test in suite['tests']:
            test_id = test['testId']
            test_name = test['testName']

            print(f"  🧪 {test_id}: {test_name}...", end=' ')

            query_result = executor.execute_query(test['daxQuery'])
            assertion_result = TestAssertionEvaluator.evaluate(test, query_result)
            status = assertion_result['status']

            if status == 'FAIL':
                print("❌ FAIL")
            elif status == 'WARNING':
                print("⚠️  WARNING")
            else:
                print("✅ PASS")

            test_results.append({
                'testId': test_id,
                'testName': test_name,
                'measureName': test.get('measureName'),
                'status': status,
                'executionTime': query_result['execution_time'],
                'data': query_result.get('data'),
                'error': query_result.get('error'),
                'assertionType': assertion_result.get('assertionType'),
                'assertionMessage': assertion_result.get('assertionMessage'),
                'expectedValue': assertion_result.get('expectedValue'),
                'actualValue': assertion_result.get('actualValue'),
                'delta': assertion_result.get('delta'),
                'recommendation': assertion_result.get('recommendation') or (test.get('recommendation') if status == 'WARNING' else None)
            })

        print()

    # Close connection
    executor.close()

    # Generate report — output to project tests folder
    tests_dir.mkdir(parents=True, exist_ok=True)
    report_path = tests_dir / 'tests_execution.md'
    raw_path = tests_dir / 'tests_execution_raw.json'

    print("📝 Generating test execution report...")
    TestReportGenerator.generate_report(test_results, test_definition, report_path)

    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"📄 Report saved: {report_path}")
    print(f"📄 Raw results: {raw_path}")

    # Summary
    passed = sum(1 for r in test_results if r['status'] == 'PASS')
    warnings = sum(1 for r in test_results if r['status'] == 'WARNING')
    failed = sum(1 for r in test_results if r['status'] == 'FAIL')

    print("\n" + "=" * 60)
    print("📊 Test Execution Summary")
    print("=" * 60)
    print(f"  Total Tests:  {total_tests}")
    print(f"  ✅ Passed:    {passed}")
    print(f"  ⚠️  Warnings:  {warnings}")
    print(f"  ❌ Failed:    {failed}")
    print()

    if failed == 0 and warnings == 0:
        print("✅ ALL TESTS PASSED! Model is validated.")
        return 0
    elif failed == 0:
        print("⚠️  All tests passed with warnings. Review report for optimization opportunities.")
        return 0
    else:
        print("❌ TESTS FAILED. Review report for details and fix recommendations.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
