import subprocess



class AssetFinder:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running AssetFinder for {self.target}...")

    def assetfinder_domain(self):
        result = subprocess.run(["assetfinder", self.target], capture_output=True, text=True)
        return result
    
    def assetfinder_subs(self):
        result = subprocess.run(["assetfinder", "--subs-only", self.target], capture_output=True, text=True)
        return result





