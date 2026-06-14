import subprocess

class Dnsx:
    def __init__(self, target):
        self.target = target

    def run(self):
        print(f"Running Dnsx for {self.target}...")


    def run_dnsx(self):
        result = subprocess.run(['dnsx', '-d', self.target], capture_output=True, text=True)
        return result

