import subprocess

class Gau:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Gau for {self.target}...")

    def scan_url(self):
        result = subprocess.run(['gau', self.target], capture_output=True, text=True)
        return result