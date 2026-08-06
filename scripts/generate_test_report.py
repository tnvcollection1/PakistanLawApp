import json, os, datetime

def generate_test_report(test_dir='tests', out='test_report.json'):
    results = []
    for fname in os.listdir(test_dir):
        if fname.endswith('.json'):
            path = os.path.join(test_dir, fname)
            with open(path, 'r') as f:
                data = json.load(f)
            results.append({
                'file': fname,
                'passed': data.get('passed', 0),
                'failed': data.get('failed', 0),
                'total': data.get('total', 0),
                'duration': data.get('duration', 0),
            })
    summary = {
        'generated_at': datetime.datetime.now().isoformat(),
        'total_tests': sum(r['total'] for r in results),
        'total_passed': sum(r['passed'] for r in results),
        'total_failed': sum(r['failed'] for r in results),
        'tests': results,
    }
    with open(out, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"[+] Test report generated: {out}")
    return summary

if __name__ == '__main__':
    generate_test_report()
