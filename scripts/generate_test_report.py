#!/usr/bin/env python3
"""
generate_test_report.py
Generates a comprehensive test report from test results.
"""

import json, os, sys
from datetime import datetime

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Report - Pakistan Law App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #333; }
        .summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }
        .card { padding: 20px; border-radius: 6px; text-align: center; }
        .pass { background: #d4edda; color: #155724; }
        .fail { background: #f8d7da; color: #721c24; }
        .skip { background: #fff3cd; color: #856404; }
        .test-list { margin-top: 20px; }
        .test-item { padding: 10px; border-bottom: 1px solid #eee; }
        .test-pass { color: #28a745; }
        .test-fail { color: #dc3545; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Report - Pakistan Law App</h1>
        <p class="timestamp">Generated: {timestamp}</p>
        
        <div class="summary">
            <div class="card pass">
                <h2>{passed}</h2>
                <p>Passed</p>
            </div>
            <div class="card fail">
                <h2>{failed}</h2>
                <p>Failed</p>
            </div>
            <div class="card skip">
                <h2>{skipped}</h2>
                <p>Skipped</p>
            </div>
        </div>
        
        <div class="test-list">
            <h3>Test Details</h3>
            {test_details}
        </div>
    </div>
</body>
</html>
"""

def generate_report(test_results, output_path="test_report.html"):
    passed = sum(1 for r in test_results if r.get("status") == "pass")
    failed = sum(1 for r in test_results if r.get("status") == "fail")
    skipped = sum(1 for r in test_results if r.get("status") == "skip")
    
    test_details = ""
    for r in test_results:
        status_class = "test-pass" if r["status"] == "pass" else "test-fail" if r["status"] == "fail" else "test-skip"
        test_details += f'<div class="test-item"><span class="{status_class}">[{r["status"].upper()}]</span> {r["name"]}'
        if r.get("message"):
            test_details += f' - {r["message"]}'
        test_details += '</div>\n'
    
    html = REPORT_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        passed=passed,
        failed=failed,
        skipped=skipped,
        test_details=test_details
    )
    
    with open(output_path, "w") as f:
        f.write(html)
    
    print(f"Report generated: {output_path}")
    print(f"  Passed: {passed}, Failed: {failed}, Skipped: {skipped}")

if __name__ == "__main__":
    # Example usage with mock data
    sample_results = [
        {"name": "test_search_basic", "status": "pass"},
        {"name": "test_search_filters", "status": "pass"},
        {"name": "test_case_detail", "status": "pass"},
        {"name": "test_auth_login", "status": "fail", "message": "Timeout"},
        {"name": "test_export_csv", "status": "skip", "message": "Feature not ready"},
    ]
    generate_report(sample_results)
