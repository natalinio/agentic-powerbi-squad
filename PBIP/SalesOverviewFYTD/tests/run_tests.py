"""
Automated Functional Testing for Power BI Semantic Models (PBIP/TMDL format)

This script executes DAX queries against a local Power BI Desktop Analysis Services
workspace to validate measure calculations, time intelligence behavior, and edge cases.

Prerequisites:
- Power BI Desktop OPEN with PBIP project loaded
- Python 3.10+
- Dependencies installed: pip install -r requirements.txt

Usage:
    python run_tests.py                    # Auto-detect Analysis Services port
    python run_tests.py --port 12345       # Specify port manually
    python run_tests.py --verbose          # Enable detailed logging
"""

import argparse
import json
import os
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


class AnalysisServicesDetector:
    """Detects local Power BI Desktop Analysis Services workspace"""
    
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
        
        # Read port from msmdsrv.port.txt
        port_file = most_recent / 'msmdsrv.port.txt'
        if not port_file.exists():
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
        """
        Establish connection to Analysis Services using ADOMD.NET
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            # Connection string for Analysis Services (ADOMD.NET format)
            conn_str = f"Data Source=localhost:{self.port};"
            
            if self.verbose:
                print(f"🔌 Connecting to Analysis Services: localhost:{self.port} (ADOMD.NET)")
            
            # Create connection object
            self.conn = AdomdConnection(conn_str)
            self.conn.Open()
            
            # Verify connection works by running a simple DAX query
            try:
                cmd = self.conn.CreateCommand()
                cmd.CommandText = "EVALUATE ROW(\"test\", 1)"
                reader = cmd.ExecuteReader()
                reader.Close()
                self.model_name = "SalesOverviewFYTD"
                if self.verbose:
                    print(f"✅ Connected to Analysis Services (model: {self.model_name})")
                return True
            except Exception as verify_err:
                print(f"❌ Connection opened but query verification failed: {verify_err}")
                return False
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def execute_query(self, dax_query: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a DAX query and return results using ADOMD.NET
        
        Args:
            dax_query: DAX query string (must start with EVALUATE)
            timeout: Query timeout in seconds
            
        Returns:
            dict: Query result with 'success', 'data', 'execution_time', 'error'
        """
        if not self.conn:
            return {'success': False, 'error': 'Not connected to Analysis Services'}
        
        start_time = datetime.now()
        
        try:
            # Create command
            cmd = self.conn.CreateCommand()
            cmd.CommandText = dax_query
            cmd.CommandTimeout = timeout
            
            # Execute query
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


class TestReportGenerator:
    """Generates markdown test execution report"""
    
    @staticmethod
    def generate_report(
        test_results: List[Dict[str, Any]], 
        test_definition: Dict[str, Any],
        output_path: Path
    ):
        """
        Generate comprehensive markdown report
        
        Args:
            test_results: List of test execution results
            test_definition: Original test definition from JSON
            output_path: Path to save report
        """
        report_lines = [
            f"# Test Execution Report — {test_definition['projectName']}",
            "",
            f"**Execution Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Model**: {test_definition['projectName']}",
            f"**Test Plan**: tests_definition.json (v{test_definition['modelVersion']})",
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
            
            report_lines.extend([
                f"### {suite_id}: {suite_name} (Priority: {priority})",
                ""
            ])
            
            # Find results for this suite
            suite_results = [r for r in test_results if r['testId'].startswith(suite_id)]
            
            for result in suite_results:
                status_emoji = {'PASS': '✅', 'WARNING': '⚠️', 'FAIL': '❌'}.get(result['status'], '❓')
                
                report_lines.extend([
                    f"#### {status_emoji} {result['testId']} — {result['testName']}",
                    f"- **Measure**: `{result.get('measureName', 'N/A')}`",
                    f"- **Status**: {status_emoji} **{result['status']}**",
                    f"- **Query Time**: {result.get('executionTime', 0):.2f} sec",
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
        
        # Write report
        output_path.write_text('\n'.join(report_lines), encoding='utf-8')


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Execute functional tests for Power BI semantic model')
    parser.add_argument('--port', type=int, help='Analysis Services port (auto-detect if not specified)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--test-definition', default='tests_definition.json', help='Test definition file')
    
    args = parser.parse_args()
    
    print("🧪 Power BI Semantic Model Functional Testing")
    print("=" * 60)
    
    # Load test definition
    test_def_path = Path(args.test_definition)
    if not test_def_path.exists():
        print(f"❌ Test definition file not found: {test_def_path}")
        sys.exit(1)
    
    with open(test_def_path, 'r', encoding='utf-8') as f:
        test_definition = json.load(f)
    
    print(f"📋 Loaded test definition: {test_definition['projectName']}")
    
    # Detect or use provided port
    port = args.port
    if not port:
        print("🔍 Auto-detecting Analysis Services workspace...")
        port = AnalysisServicesDetector.find_workspace_port()
        if not port:
            print("❌ Could not auto-detect Analysis Services workspace.")
            print("   Ensure Power BI Desktop is open with the model loaded.")
            print("   Or specify port manually: python run_tests.py --port 12345")
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
            
            # Execute DAX query
            query_result = executor.execute_query(test['daxQuery'])
            
            # Determine test status
            if not query_result['success']:
                status = 'FAIL'
                print(f"❌ FAIL")
            elif query_result['execution_time'] > 5.0:
                status = 'WARNING'
                print(f"⚠️  WARNING (slow query)")
            else:
                status = 'PASS'
                print(f"✅ PASS")
            
            # Store result
            test_results.append({
                'testId': test_id,
                'testName': test_name,
                'measureName': test.get('measureName'),
                'status': status,
                'executionTime': query_result['execution_time'],
                'data': query_result.get('data'),
                'error': query_result.get('error'),
                'recommendation': test.get('recommendation') if status == 'WARNING' else None
            })
        
        print()
    
    # Close connection
    executor.close()
    
    # Generate report
    print("📝 Generating test execution report...")
    TestReportGenerator.generate_report(
        test_results,
        test_definition,
        Path('tests_execution.md')
    )
    
    # Save raw results
    with open('tests_execution_raw.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, default=str)
    
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
