import subprocess

class Dirsearch:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Dirsearch for {self.target}...")

    def simple_scan(self):
        result = subprocess.run(['dirsearch', '-u', self.target], capture_output=True, text=True)
        return result
    
    def bug_bounty_scan(self):
        result = subprocess.run(['dirsearch', '-u', self.target, '-e', 'php,html,js,tt,bak', '-t', '50', '--random-agent', '--follow-redirects'], capture_output=True, text=True)
        return result
    
    def wordlist_scan(self):
        result = subprocess.run(['dirsearch', '-u', self.target, '-w', '/usr/share/wordlists/dirb/common.txt', '-e', 'php,html,js,tt,bak'], capture_output=True, text=True)
        return result
    
    def recursive_scan(self):
        result = subprocess.run(['dirsearch', '-u', self.target, '-e', 'php,html,js,tt,bak', '-t', '50', '--random-agent', '--follow-redirects', '--recursive'], capture_output=True, text=True)
        return result
    
    def filter_scan(self):
        result = subprocess.run(['dirsearch', '-u', self.target, '-e', 'php,html,js,tt,bak', '-t', '50', '--random-agent', '--follow-redirects', '--filter-status', '200,204,301,302,307,401,403'], capture_output=True, text=True)
        return result