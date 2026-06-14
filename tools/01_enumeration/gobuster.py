import subprocess

class Gobuster:
    def __init__(self, target,):
        self.target = target
        
    def run(self):
        print(f"Running Gobuster for {self.target}...")

    def scan_url(self):
        result = subprocess.run(['gobuster', 'dir', '-u', self.target, '-w', '/usr/share/wordlists/dirb/common.txt'], capture_output=True, text=True)
        return result
    
    def scan_with_extensions(self):
        result = subprocess.run(['gobuster', 'dir', '-u', self.target, '-w', '/usr/share/wordlists/dirb/common.txt', '-x', 'php,html,txt'], capture_output=True, text=True)
        return result
    
    def faster_scan(self):
        result = subprocess.run(['gobuster', 'dir', '-u', self.target, '-w', '/usr/share/wordlists/dirb/common.txt', '-t', '50'], capture_output=True, text=True)
        return result
    
    def filter_status(self):
        result = subprocess.run(['gobuster', 'dir', '-u', self.target, '-w', '/usr/share/wordlists/dirb/common.txt', '-b', '404'], capture_output=True, text=True)
        return result
    
    def power_scan(self):
        result = subprocess.run(['gobuster', 'dir', '-u', self.target, '-w', '/usr/share/wordlists/dirb/common.txt', '-x', 'php,html,txt', '-t', '50', '-b', '404'], capture_output=True, text=True)
        return result
    