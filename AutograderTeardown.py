from .Timeout import Timeout

global_teardowns = []

class AutograderTeardown:
    def __init__(self, teardownfn, name, timeout: int=None):
        self.teardownfn = teardownfn
        self.name = name
        self.timeout = timeout
        global_teardowns.append(self)

    def run(self, ag: "Autograder"):
        success = False
        def f():
            nonlocal success
            try:
                with Timeout(self.timeout):
                    success = self.teardownfn(ag)
            except Timeout.Timeout:
                print(f"The teardown {self.name} has timed out!")
                ag.print("[ERROR]: A teardown step timed out!")
                success = False

        def handler():
            nonlocal success
            success = False
            print(f"The teardown {self.name} has encountered an error!")
            ag.print("[Error]: An unexpected error occured in the Autograder when attempting to run a teardown of the Autograder! Please contact a TA if this persists.")

        ag.safe_env(f, handler=handler)
        return success
    
