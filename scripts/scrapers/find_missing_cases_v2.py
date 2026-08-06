"""
Find Missing Cases V2 - Improved missing case finder
"""
import json
import os

class MissingCaseFinderV2:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir

    def get_existing_ids(self):
        existing = set()
        if not os.path.exists(self.data_dir):
            return existing
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.data_dir, filename), 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            existing.add(str(item.get('id', '')))
        return existing

    def find_missing(self, start=1, end=10000):
        existing = self.get_existing_ids()
        missing = [i for i in range(start, end + 1) if str(i) not in existing]
        return missing

    def save_report(self, missing, output_file='missing_cases_v2.json'):
        report = {
            'total_expected': 10000,
            'total_found': 10000 - len(missing),
            'total_missing': len(missing),
            'missing_ids': missing,
        }
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Saved report to {output_file}")

if __name__ == '__main__':
    finder = MissingCaseFinderV2()
    missing = finder.find_missing(1, 1000)
    print(f"Found {len(missing)} missing cases")
    finder.save_report(missing)
