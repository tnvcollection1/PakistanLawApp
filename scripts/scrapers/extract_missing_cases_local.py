"""
Extract Missing Cases Local - Find and extract missing cases locally
"""
import json
import os

class MissingCaseExtractor:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir

    def get_existing_ids(self):
        existing = set()
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.data_dir, filename), 'r') as f:
                    data = json.load(f)
                    for item in data:
                        existing.add(item.get('id'))
        return existing

    def find_missing(self, start=1, end=10000):
        existing = self.get_existing_ids()
        missing = [i for i in range(start, end + 1) if str(i) not in existing]
        return missing

    def save_missing(self, missing, output_file='missing_cases.json'):
        with open(output_file, 'w') as f:
            json.dump(missing, f, indent=2)
        print(f"Saved {len(missing)} missing cases to {output_file}")

if __name__ == '__main__':
    extractor = MissingCaseExtractor()
    missing = extractor.find_missing(1, 1000)
    print(f"Found {len(missing)} missing cases")
    extractor.save_missing(missing)
