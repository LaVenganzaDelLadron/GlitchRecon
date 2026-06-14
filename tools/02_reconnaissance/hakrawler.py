import subprocess


class Hakrawler:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Hakrawler on {self.target}...")

    def simple_scan(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler"], capture_output=True, text=True)
        return result
    
    def scan_all(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-d", "3"], capture_output=True, text=True)
        return result
    
    def scan_subs(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-subs"], capture_output=True, text=True)
        return result
    
    def scan_unique(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-u"], capture_output=True, text=True)
        return result
    
    def scan_json(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-json"], capture_output=True, text=True)
        return result
    
    def scan_threads(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-t", "20"], capture_output=True, text=True)
        return result

    def scan_redirects(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-dr"], capture_output=True, text=True)
        return result
    
    def scan_insecure(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-insecure"], capture_output=True, text=True)
        return result
    
    def scan_inside(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-i"], capture_output=True, text=True)
        return result

    def scan_timeout(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-timeout", "10"], capture_output=True, text=True)
        return result
    
    def scan_size(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-size", "500"], capture_output=True, text=True)
        return result

    def scan_source(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-s"], capture_output=True, text=True)
        return result

    def scan_url_found(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-w"], capture_output=True, text=True)
        return result

    def custom_scan(self):
        result = subprocess.run(["echo", self.target, "|", "hakrawler", "-d", "3", "-subs", "-u", "-t", "20", "-s", "-w"], capture_output=True, text=True)
        return result