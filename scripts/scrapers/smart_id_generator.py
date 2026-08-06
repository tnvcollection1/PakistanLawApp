"""
Smart ID Generator - Generate smart IDs for case scraping
"""
import random
import string

class SmartIdGenerator:
    def __init__(self, prefix='PLS'):
        self.prefix = prefix
        self.seen = set()

    def generate_id(self, length=8):
        while True:
            suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
            id_str = f"{self.prefix}-{suffix}"
            if id_str not in self.seen:
                self.seen.add(id_str)
                return id_str

    def generate_range(self, count=100):
        return [self.generate_id() for _ in range(count)]

if __name__ == '__main__':
    gen = SmartIdGenerator()
    ids = gen.generate_range(10)
    for id_str in ids:
        print(id_str)
