import subprocess


class Arjun:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Arjun for {self.target}...")

    def arjun_url(self):
        result = subprocess.run(["arjun", "-u", self.target], capture_output=True, text=True)
        return result

    def arjun_burp(self):
        result = subprocess.run(["arjun", "-u", self.target, "-oB"], capture_output=True, text=True)
        return result

    def arjun_get(self):
       result = subprocess.run(["arjun", "-u", self.target, "-m", "GET"], capture_output=True, text=True)
       return result




