import subprocess


class Hakrawler:
    def __init__(self, target):
        self.target = target

    def _run(self, *args):
        return subprocess.run(["hakrawler", *args], input=self.target, capture_output=True, text=True)

    def run(self):
        print(f"Running Hakrawler on {self.target}...")

    def simple_scan(self):
        return self._run()
    
    def scan_all(self):
        return self._run("-d", "3")
    
    def scan_subs(self):
        return self._run("-subs")
    
    def scan_unique(self):
        return self._run("-u")
    
    def scan_json(self):
        return self._run("-json")
    
    def scan_threads(self):
        return self._run("-t", "20")

    def scan_redirects(self):
        return self._run("-dr")
    
    def scan_insecure(self):
        return self._run("-insecure")
    
    def scan_inside(self):
        return self._run("-i")

    def scan_timeout(self):
        return self._run("-timeout", "10")
    
    def scan_size(self):
        return self._run("-size", "500")

    def scan_source(self):
        return self._run("-s")

    def scan_url_found(self):
        return self._run("-w")

    def custom_scan(self):
        return self._run("-d", "3", "-subs", "-u", "-t", "20", "-s", "-w")
