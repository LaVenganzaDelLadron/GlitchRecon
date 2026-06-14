import subprocess

class Findomain:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Findomain for {self.target}...")

    def scan_domain(self):
        result = subprocess.run(['findomain', '-t', self.target], capture_output=True, text=True)
        return result
    
    def silent_scan_domain(self):
        result = subprocess.run(['findomain', '-t', self.target, '-q'], capture_output=True, text=True)
        return result
    
    def ip_scan_domain(self):
        result = subprocess.run(['findomain', '-t', self.target, '--resolve'], capture_output=True, text=True)
        return result