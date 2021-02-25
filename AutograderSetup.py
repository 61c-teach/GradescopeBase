"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 20:56:43 
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-01-23 21:00:55
 */
"""
from .Timeout import Timeout
from .Utils import WhenToRun

global_setups = []

class AutograderSetup:
    def __init__(self, setupfn, name, timeout: int=None, when_to_run: WhenToRun=WhenToRun.BOTH):
        self.setupfn = setupfn
        self.name = name
        self.timeout = timeout
        self.when_to_run = when_to_run
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

        def handler(exception):
            nonlocal success
            success = False
            print(f"The setup {self.name} has encountered an error!")
            ag.print("[Error]: An unexpected error occured in the Autograder when attempting to run a setup of the Autograder! Please contact a TA if this persists.")

        ag.safe_env(f, handler=handler)
        return success
    
