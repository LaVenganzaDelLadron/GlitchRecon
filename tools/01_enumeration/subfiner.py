import subprocess

class Subfiner:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Subfiner for {self.target}...")

    def scan_url(self):
        result = subprocess.run(['subfiner', '-d', self.target], capture_output=True, text=True)
        return result
    
    def silent_scan(self):
        result = subprocess.run(['subfiner', '-d', self.target, '-silent'], capture_output=True, text=True)
        return result
    
    def fast_scan(self):
        result = subprocess.run(['subfiner', '-d', self.target, '-t', '50'], capture_output=True, text=True)
        return result
    
    def unique_scan(self):
        result = subprocess.run(['subfiner', '-d', self.target, '-u'], capture_output=True, text=True)
        return result
