import subprocess

class Katana:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Katana on {self.target}...")

    def scan_url(self):
        result = subprocess.run(["katana","-u", self.target], capture_output=True, text=True)
        return result
    
    def scan_depth(self):
        result = subprocess.run(["katana","-u", self.target, "-d", "3"], capture_output=True, text=True)
        return result
    
    def scan_include_subs(self):
        result = subprocess.run(["katana","-u", self.target, "-include-subdomains"], capture_output=True, text=True)
        return result
    
    def scan_json(self):
        result = subprocess.run(["katana","-u", self.target, "-jc"], capture_output=True, text=True)
        return result
    
    def scan_unique(self):
        result = subprocess.run(["katana","-u", self.target, "-duc"], capture_output=True, text=True)
        return result
    
    def scan_source(self):
        result = subprocess.run(["katana","-u", self.target, "-s"], capture_output=True, text=True)
        return result