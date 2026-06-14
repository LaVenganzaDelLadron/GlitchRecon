import subprocess

class Ffuf:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Ffuf for {self.target}...")

    def scan_url(self):
        result = subprocess.run(['ffuf', '-u', f'{self.target}/FUZZ', '-w', '/usr/share/wordlists/seclists/Web-Content/common.txt'], capture_output=True, text=True)
        return result