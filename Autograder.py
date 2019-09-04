"""
This is the base of the autograder.
"""
import json
import datetime
import os
from .AutograderTest import AutograderTest, global_tests

results_file = "/autograder/results/results.json"
if os.path.isfile("/.localhost"):
    results_file = "./results.json"

class Autograder:
    def __init__(self):
        self.tests = []
        self.results_file = results_file
        self.score = None
        self.output = None
        self.visibility = None
        self.stdout_visibility = None
        self.extra_data = {}
        self.leaderboard = None
        self.start_time = datetime.datetime.now()

    @staticmethod
    def run(ag = None):
        def f(ag):
            for t in global_tests:
                ag.add_test(t)
            ag.execute()
        Autograder.main(f, ag=ag)

    @staticmethod
    def main(f, ag=None):
        if ag is None:
            ag = Autograder()
        def handler():
            ag.ag_fail("An exception occured in the autograder's main function. Please contact a TA to resolve this issue.")
            return True
        ag.safe_env(lambda: f(ag), handler)

    def dump_results(self, data: dict) -> None:
        jsondata = json.dumps(data, ensure_ascii=False)
        with open(self.results_file, "w") as f:
            f.write(jsondata)

    def add_test(self, test):
        if isinstance(test, AutograderTest):
            self.tests.append(test)
            return
        raise ValueError("You must add type Test to the autograder.")

    def set_score(self, score):
        self.score = score
    
    def add_score(self, addition):
        if self.score is None:
            self.score = 0
        self.score += addition
    
    def get_score(self):
        return self.score

    def create_test(self, *args, **kwargs):
        test = AutograderTest(*args, **kwargs)
        self.add_test(test)

    def ag_fail(self, message: str, extra: dict={}, exit_prog=True) -> None:
        data = {
            "score": 0,
            "output": message
        }
        data.update(extra)
        self.dump_results(data)
        if exit_prog:
            import sys
            sys.exit()
    
    def safe_env(self, f, handler=None):
        try:
            f()
        except Exception as exc:
            print("An exception occured in the safe environment!")
            import traceback
            traceback.print_exc()
            print(exc)
            if handler is not None:
                try:
                    if handler():
                        return
                except Exception as exc:
                    print("An exception occured while executing the exception handler!")
            self.ag_fail("An unexpected exception ocurred while trying to execute the autograder. Please try again or contact a TA if this persists.")

    def run_tests(self):
        for test in self.tests:
            test.run(self)

    def generate_results(self, dump=True):
        results = {
            "execution_time": (datetime.datetime.now() - self.start_time).total_seconds(),
        }
        tests = []
        for test in self.tests:
            res = test.get_results()
            if res:
                tests.append(res)
        if tests:
            results["tests"] = tests
        if self.output is not None:
            results["output"] = self.output
        if self.visibility is not None:
            results["visibility"] = self.visibility
        if self.stdout_visibility is not None:
            results["stdout_visibility"] = self.stdout_visibility
        if self.extra_data:
            results["extra_data"] = self.extra_data
        if self.leaderboard is not None:
            results["leaderboard"] = self.leaderboard
        if dump:
            self.dump_results(results)
        return results
        
    def execute(self):
        self.run_tests()
        self.generate_results()