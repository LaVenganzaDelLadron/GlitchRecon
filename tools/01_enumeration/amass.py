import subprocess

class Amass:
    def __init__(self, target: str):
        self.target = target.strip()

    def run(self):
        pass


    def intel_domain(self):
        result = subprocess.run(["amass", "intel", "-whois", "-d", self.target], capture_output=True, text=True)
        return result

    def intel_cidr(self):
        result = subprocess.run(["amass", "intel", "-cidr", self.target], capture_output=True, text=True)
        return result

    def intel_ip(self):
        result = subprocess.run(["amass", "intel", "-ip", "-d", self.target], capture_output=True, text=True)
        return result

    def enum_domain(self):
        result = subprocess.run(["amass", "enum", "-d", self.target], capture_output=True, text=True)
        return result

    def enum_passive(self):
        result = subprocess.run(["amass", "enum", "-passive", "-d", self.target], capture_output=True, text=True)
        return result

    def enum_active(self):
        result = subprocess.run(["amass", "enum", "-active", "-d", self.target], capture_output=True, text=True)
        return result

    def enum_brute(self):
        result = subprocess.run(["amass", "enum", "-brute", "-d", self.target], capture_output=True, text=True)
        return result

    def enum_src(self):
        result = subprocess.run(["amass", "enum", "-src", "-d", self.target], capture_output=True, text=True)
        return result

    def enum_ip(self):
        result = subprocess.run(["amass", "enum", "-ip", "-d", self.target], capture_output=True, text=True)
        return result

    def enum_ipv4(self):
        return subprocess.run(["amass", "enum", "-ipv4", "-d", self.target], capture_output=True, text=True)
        return result

    def track_domain(self):
        result = subprocess.run(["amass", "track", "-d", self.target, "-last", "2"], capture_output=True, text=True)
        return result


