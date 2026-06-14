import subprocess

class WaybackUrls:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running WaybackUrls for {self.target}...")

    def scan_url(self):
        result = subprocess.run(['waybackurls', self.target], capture_output=True, text=True)
        return result