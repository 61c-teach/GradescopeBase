from .Timeout import Timeout

global_setups = []

class AutograderSetup:
    def __init__(self, setupfn, name, timeout: int=None):
        self.setupfn = setupfn
        self.name = name
        self.timeout = timeout
        global_setups.append(self)

    def run(self, ag: "Autograder"):
        success = False
        def f():
            nonlocal success
            try:
                with Timeout(self.timeout):
                    success = self.setupfn(ag)
            except Timeout.Timeout:
                print(f"The setup {self.name} has timed out!")
                ag.print("[ERROR]: A setup step timed out!")
                success = False

        def handler():
            nonlocal success
            success = False
            print(f"The setup {self.name} has encountered an error!")
            ag.print("[Error]: An unexpected error occured in the Autograder when attempting to run a setup of the Autograder! Please contact a TA if this persists.")

        ag.safe_env(f, handler=handler)
        return success
    
