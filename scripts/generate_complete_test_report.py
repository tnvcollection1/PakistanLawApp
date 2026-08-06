#!/usr/bin/env python3
"""
Generate a complete test report with detailed analysis.
"""

import os
import sys
import json
import unittest
import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock


def discover_tests(test_dir='tests'):
    """Discover all tests in the test directory."""
    loader = unittest.TestLoader()
    start_dir = Path(test_dir)
    
    if not start_dir.exists():
        print(f"Test directory {test_dir} not found")
        return None
    
    suite = loader.discover(str(start_dir), pattern='test_*.py')
    return suite


def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    print("Running tests with coverage...")
    
    # Run pytest with coverage
    result = subprocess.run(
        [
            'python', '-m', 'pytest',
            '-v',
            '--tb=short',
            '--cov=.',
            '--cov-report=xml:coverage.xml',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '-x'  # Stop on first failure
        ],
        capture_output=True,
        text=True
    )
    
    return result


def parse_test_results(output):
    """Parse test results from pytest output."""
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'errors': 0,
        'duration': 0.0,
        'failures': [],
        'errors_list': []
    }
    
    lines = output.split('\n')
    
    for line in lines:
        # Parse summary line
        if ' passed' in line or ' failed' in line or ' skipped' in line:
            parts = line.split(',')
            for part in parts:
                part = part.strip()
                if ' passed' in part:
                    try:
                        results['passed'] = int(part.split(' passed')[0].strip())
                    except ValueError:
                        pass
                elif ' failed' in part:
                    try:
                        results['failed'] = int(part.split(' failed')[0].strip())
                    except ValueError:
                        pass
                elif ' skipped' in part:
                    try:
                        results['skipped'] = int(part.split(' skipped')[0].strip())
                    except ValueError:
                        pass
                elif ' error' in part:
                    try:
                        results['errors'] = int(part.split(' error')[0].strip())
                    except ValueError:
                        pass
        
        # Parse duration
        if 's ' in line and ('passed' in line or 'failed' in line):
            try:
                duration_str = line.split(' in ')[1].split('s')[0]
                results['duration'] = float(duration_str)
            except (IndexError, ValueError):
                pass
    
    results['total'] = results['passed'] + results['failed'] + results['skipped'] + results['errors']
    
    return results


def generate_html_report(test_results, coverage_data, output_file='test_report.html'):
    """Generate HTML test report."""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        
        h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .timestamp {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .card h3 {{
            font-size: 0.9em;
            text-transform: uppercase;
            color: #666;
            margin-bottom: 10px;
        }}
        
        .metric {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        
        .metric.success {{
            color: #28a745;
        }}
        
        .metric.danger {{
            color: #dc3545;
        }}
        
        .metric.warning {{
            color: #ffc107;
        }}
        
        .metric.info {{
            color: #17a2b8;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }}
        
        .details {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .details h2 {{
            margin-bottom: 20px;
            color: #333;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        
        .badge-success {{
            background-color: #d4edda;
            color: #155724;
        }}
        
        .badge-danger {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        
        .badge-warning {{
            background-color: #fff3cd;
            color: #856404;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Complete Test Report</h1>
            <p class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        </header>
        
        <div class="summary">
            <div class="card">
                <h3>Total Tests</h3>
                <div class="metric info">{test_results['total']}</div>
            </div>
            <div class="card">
                <h3>Passed</h3>
                <div class="metric success">{test_results['passed']}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {(test_results['passed']/test_results['total']*100) if test_results['total'] > 0 else 0}%"></div>
                </div>
            </div>
            <div class="card">
                <h3>Failed</h3>
                <div class="metric danger">{test_results['failed']}</div>
            </div>
            <div class="card">
                <h3>Skipped</h3>
                <div class="metric warning">{test_results['skipped']}</div>
            </div>
            <div class="card">
                <h3>Errors</h3>
                <div class="metric danger">{test_results['errors']}</div>
            </div>
            <div class="card">
                <h3>Coverage</h3>
                <div class="metric info">{coverage_data.get('coverage', 0)}%</div>
            </div>
        </div>
        
        <div class="details">
            <h2>Test Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><span class="badge badge-success">Passed</span></td>
                        <td>{test_results['passed']}</td>
                        <td>{(test_results['passed']/test_results['total']*100) if test_results['total'] > 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-danger">Failed</span></td>
                        <td>{test_results['failed']}</td>
                        <td>{(test_results['failed']/test_results['total']*100) if test_results['total'] > 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-warning">Skipped</span></td>
                        <td>{test_results['skipped']}</td>
                        <td>{(test_results['skipped']/test_results['total']*100) if test_results['total'] > 0 else 0:.1f}%</td>
                    </tr>
                    <tr>
                        <td><span class="badge badge-danger">Errors</span></td>
                        <td>{test_results['errors']}</td>
                        <td>{(test_results['errors']/test_results['total']*100) if test_results['total'] > 0 else 0:.1f}%</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generated by Pakistan Law App Test Suite</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"HTML report generated: {output_file}")


def main():
    """Main function to generate complete test report."""
    print("=" * 60)
    print("GENERATING COMPLETE TEST REPORT")
    print("=" * 60)
    
    # Run tests
    test_result = run_tests_with_coverage()
    
    print("\nTest Output:")
    print(test_result.stdout)
    
    if test_result.stderr:
        print("\nStderr:")
        print(test_result.stderr)
    
    # Parse results
    test_results = parse_test_results(test_result.stdout)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {test_results['total']}")
    print(f"Passed: {test_results['passed']}")
    print(f"Failed: {test_results['failed']}")
    print(f"Skipped: {test_results['skipped']}")
    print(f"Errors: {test_results['errors']}")
    print(f"Duration: {test_results['duration']:.2f}s")
    
    # Get coverage data
    coverage_data = {'coverage': 0}
    
    if os.path.exists('coverage.xml'):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse('coverage.xml')
            root = tree.getroot()
            
            line_rate = root.get('line-rate')
            if line_rate:
                coverage_data['coverage'] = round(float(line_rate) * 100, 2)
        except Exception as e:
            print(f"Warning: Could not parse coverage: {e}")
    
    print(f"Coverage: {coverage_data['coverage']}%")
    
    # Generate HTML report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    generate_html_report(test_results, coverage_data, report_file)
    
    # Save JSON summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'test_results': test_results,
        'coverage': coverage_data
    }
    
    with open('test_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"JSON summary saved: test_summary.json")
    
    # Return exit code
    if test_results['failed'] > 0 or test_results['errors'] > 0:
        print("\nTests FAILED")
        return 1
    else:
        print("\nTests PASSED")
        return 0


if __name__ == '__main__':
    sys.exit(main())
