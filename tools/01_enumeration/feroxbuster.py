import subprocess

class Feroxbuster:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Feroxbuster for {self.target}...")

    def run_feroxbuster(self):
        result = subprocess.run(['feroxbuster', '-u', self.target, '-w', '/usr/share/wordlists/seclists/Web-Content/common.txt'], capture_output=True, text=True)
        return result

