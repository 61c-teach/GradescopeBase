"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:02:51 
 * @Last Modified by:   ThaumicMekanism [Stephan K.] 
 * @Last Modified time: 2020-01-23 21:02:51 
 */
"""
from .Timeout import Timeout
from .Utils import WhenToRun

global_teardowns = []

class AutograderTeardown:
    def __init__(self, teardownfn, name, timeout: int=None, when_to_run: WhenToRun=WhenToRun.BOTH):
        self.teardownfn = teardownfn
        self.name = name
        self.timeout = timeout
        self.when_to_run = when_to_run
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

        def handler(exception):
            nonlocal success
            success = False
            print(f"The teardown {self.name} has encountered an error!")
            ag.print("[Error]: An unexpected error occured in the Autograder when attempting to run a teardown of the Autograder! Please contact a TA if this persists.")

        ag.safe_env(f, handler=handler)
        return success
    
