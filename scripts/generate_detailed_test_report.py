#!/usr/bin/env python3
"""
Generate a detailed test report with coverage analysis.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path


def run_tests():
    """Run the test suite and capture output."""
    print("Running tests...")
    
    # Run pytest with coverage
    result = subprocess.run(
        ["python", "-m", "pytest", "-v", "--tb=short", "--cov=.", "--cov-report=xml", "--cov-report=html"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    
    return result


def parse_test_output(output):
    """Parse pytest output to extract test results."""
    results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": 0,
        "total": 0,
        "failures": [],
        "errors_list": []
    }
    
    for line in output.split('\n'):
        if ' passed' in line:
            try:
                results["passed"] = int(line.split(' passed')[0].split()[-1])
            except (ValueError, IndexError):
                pass
        elif ' failed' in line:
            try:
                results["failed"] = int(line.split(' failed')[0].split()[-1])
            except (ValueError, IndexError):
                pass
        elif ' skipped' in line:
            try:
                results["skipped"] = int(line.split(' skipped')[0].split()[-1])
            except (ValueError, IndexError):
                pass
        elif ' error' in line:
            try:
                results["errors"] = int(line.split(' error')[0].split()[-1])
            except (ValueError, IndexError):
                pass
    
    results["total"] = results["passed"] + results["failed"] + results["skipped"] + results["errors"]
    
    return results


def generate_html_report(test_results, coverage_data):
    """Generate an HTML report."""
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - {timestamp}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .metric {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .success {{ color: #4CAF50; }}
        .failure {{ color: #f44336; }}
        .warning {{ color: #ff9800; }}
        .info {{ color: #2196F3; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .timestamp {{
            color: #666;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Detailed Test Report</h1>
        <p class="timestamp">Generated on: {timestamp}</p>
        
        <div class="summary">
            <div class="metric">
                <div class="metric-value success">{passed}</div>
                <div class="metric-label">Passed</div>
            </div>
            <div class="metric">
                <div class="metric-value failure">{failed}</div>
                <div class="metric-label">Failed</div>
            </div>
            <div class="metric">
                <div class="metric-value warning">{skipped}</div>
                <div class="metric-label">Skipped</div>
            </div>
            <div class="metric">
                <div class="metric-value info">{total}</div>
                <div class="metric-label">Total</div>
            </div>
        </div>
        
        <h2>Coverage Summary</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-value">{coverage}%</div>
                <div class="metric-label">Coverage</div>
            </div>
        </div>
        
        <h2>Test Results</h2>
        <table>
            <tr>
                <th>Status</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
            <tr>
                <td class="success">Passed</td>
                <td>{passed}</td>
                <td>{pass_rate}%</td>
            </tr>
            <tr>
                <td class="failure">Failed</td>
                <td>{failed}</td>
                <td>{fail_rate}%</td>
            </tr>
            <tr>
                <td class="warning">Skipped</td>
                <td>{skipped}</td>
                <td>{skip_rate}%</td>
            </tr>
        </table>
    </div>
</body>
</html>
"""
    
    total = test_results["total"]
    passed = test_results["passed"]
    failed = test_results["failed"]
    skipped = test_results["skipped"]
    
    pass_rate = round((passed / total * 100), 2) if total > 0 else 0
    fail_rate = round((failed / total * 100), 2) if total > 0 else 0
    skip_rate = round((skipped / total * 100), 2) if total > 0 else 0
    
    html = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        passed=passed,
        failed=failed,
        skipped=skipped,
        total=total,
        coverage=coverage_data.get("coverage", 0),
        pass_rate=pass_rate,
        fail_rate=fail_rate,
        skip_rate=skip_rate
    )
    
    return html


def main():
    """Main function to generate the test report."""
    print("=" * 50)
    print("GENERATING DETAILED TEST REPORT")
    print("=" * 50)
    
    # Run tests
    test_result = run_tests()
    
    print("\nTest Output:")
    print(test_result.stdout)
    
    if test_result.stderr:
        print("\nErrors:")
        print(test_result.stderr)
    
    # Parse results
    test_results = parse_test_output(test_result.stdout)
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Skipped: {test_results['skipped']}")
    print(f"Errors: {test_results['errors']}")
    
    # Calculate coverage
    coverage_data = {"coverage": 0}
    
    try:
        with open("coverage.xml", "r") as f:
            import xml.etree.ElementTree as ET
            tree = ET.parse(f)
            root = tree.getroot()
            coverage_data["coverage"] = round(float(root.get("line-rate", 0)) * 100, 2)
    except Exception as e:
        print(f"Warning: Could not parse coverage data: {e}")
    
    print(f"Coverage: {coverage_data['coverage']}%")
    
    # Generate HTML report
    report_dir = Path("test-reports")
    report_dir.mkdir(exist_ok=True)
    
    html_report = generate_html_report(test_results, coverage_data)
    
    report_file = report_dir / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    with open(report_file, "w") as f:
        f.write(html_report)
    
    print(f"\nReport saved to: {report_file}")
    
    # Save JSON summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "tests": test_results,
        "coverage": coverage_data
    }
    
    summary_file = report_dir / "test-summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to: {summary_file}")
    
    return test_results["failed"] == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
