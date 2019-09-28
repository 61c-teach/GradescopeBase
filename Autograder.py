"""
This is the base of the autograder.
"""
import json
import time
import datetime
import os
from .AutograderTest import AutograderTest, global_tests, Max
from .Utils import root_dir, submission_dir

results_file = "/autograder/results/results.json"
if os.path.isfile("/.localhost"):
    results_file = "./results.json"

submission_metadata = "/autograder/submission_metadata.json"

class AutograderError(Exception):
    def __init__(self, info: any=None):
        self.info = info

class RateLimit:
    def __init__(
        self,
        tokens:int=None,
        seconds:int=0,
        minutes:int=0,
        hours:int=0,
        days:int=0,
        reset_time:str=None
    ):
        self.tokens = tokens
        self.seconds = seconds
        self.minutes = minutes
        self.hours = hours
        self.days = days
        self.reset_time = reset_time

class Autograder:
    def __init__(self, rate_limit=None):
        self.tests = []
        self.results_file = results_file
        self.score = None
        self.output = None
        self.visibility = None
        self.stdout_visibility = None
        self.extra_data = {}
        self.leaderboard = None
        # rate_limit takes in a RateLimit class.
        # reset_time is when you want to reset the submission time. You
        # can leave it out to ignore. Put the time stirng in this format:
        #  "2018-11-29T16:15:00"
        self.rate_limit:RateLimit = None
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
        def wrapper():
            self.rate_limit_fn()
            f(ag)
        ag.safe_env(wrapper, handler)

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
            return f()
        except Exception as exc:
            print("An exception occured in the safe environment!")
            import traceback
            traceback.print_exc()
            print(exc)
            if handler is not None:
                try:
                    h = handler()
                    if h:
                        return AutograderError(h)
                except Exception as exc:
                    print("An exception occured while executing the exception handler!")
            self.ag_fail("An unexpected exception ocurred while trying to execute the autograder. Please try again or contact a TA if this persists.")
            return AutograderError()

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
 ß          results["leaderboard"] = self.leaderboard
        if dump:
            self.dump_results(results)
        return results
        
    def execute(self):
        self.run_tests()
        self.generate_results()

    @staticmethod
    def root_dir() -> str:
        return root_dir()

    @staticmethod
    def submission_dir() -> str:
        return submission_dir()
    
    def rate_limit_fn(self):
        if isinstance(self.rate_limit, RateLimit) and self.rate_limit.tokens is not None:
                    tokens = self.rate_limit.tokens
                    restart_subm_string = self.rate_limit.reset_time
                    s = self.rate_limit.seconds
                    m = self.rate_limit.minutes
                    h = self.rate_limit.hours
                    d = self.rate_limit.days
                    regen_time_seconds = s + 60 * (m + 60 * (h + (24 * d)))
                    def get_submission_time(s):
                        return s[:-13]
                    def pretty_time_str(s, m, h, d):
                        sstr = "" if s == 0 else str(s) + " second"
                        sstr += "" if s == 1 else "s"
                        mstr = "" if m == 0 else str(s) + " minute"
                        mstr += "" if m == 1 else "s"
                        hstr = "" if h == 0 else str(s) + " hour"
                        hstr += "" if h == 1 else "s"
                        dstr = "" if d == 0 else str(s) + " day"
                        dstr += "" if d == 1 else "s"
                        st = dstr
                        for tmpstr in [hstr, mstr, sstr]:
                            if st != "":
                                st += " "
                            st += tmpstr
                        if st == "":
                            st = "none"
                        return st
                    with open(submission_metadata, "r") as jsonMetadata:
                        metadata = json.load(jsonMetadata)
                    current_subm_string = get_submission_time(metadata["created_at"])
                    current_time = time.strptime(current_subm_string,"%Y-%m-%dT%H:%M:%S")
                    restart_time = time.strptime(restart_subm_string, "%Y-%m-%dT%H:%M:%S") if restart_subm_string is not None else None
                    tokens_used = 0
                    for i, v in enumerate(metadata["previous_submissions"]):
                        subm_string = get_submission_time(v["submission_time"])
                        subm_time = time.strptime(subm_string,"%Y-%m-%dT%H:%M:%S")
                        if restart_time is not None and time.mktime(subm_time) - time.mktime(restart_time) < 0:
                            print("Ignoring a submission, too early!")
                            continue
                        print("Current time: " + str(time.mktime(current_time)))
                        print("Subm time: " + str(time.mktime(subm_time)))
                        if (time.mktime(current_time) - time.mktime(subm_time) < regen_time_seconds): 
                            try:
                                print(metadata["previous_submissions"][i])
                                print("Tokens used: " + str(tokens_used))
                                print(str(metadata["previous_submissions"][i].keys()))
                                print("Current submission data: " + str(metadata["previous_submissions"][i]["results"]["extra_data"]))
                                if (metadata["previous_submissions"][i]["results"]["extra_data"]["counts"] == 1): 
                                    tokens_used = tokens_used + 1
                            except: 
                                tokens_used = tokens_used + 1
                                pass
                        print("------------------------------")
                    with open(results_file, "w+") as jsonResults:
                        results = json.load(jsonResults)
                        results["extra_data"] = {}
                        if tokens_used < tokens:
                            tokens_used += 1
                            results["extra_data"]["counts"] = 1
                            results["output"] = f"Students can get up to {tokens} graded submissions within any given period of {pretty_time_str(s, m, h, d)}. In the last period, you have had {tokens_used} graded submissions."
                        if tokens_used >= tokens:
                            results["extra_data"]["counts"] = 0
                            results["output"] = f"Students can get up to {tokens} graded submissions within any given period of {pretty_time_str(s, m, h, d)}. You have already had {tokens_used} graded submissions within the last {pretty_time_str(s, m, h, d)}, so the results of your last graded submission are being displayed. This submission will not count as a graded submission."
                            results["tests"] = metadata["previous_submissions"][len(metadata["previous_submissions"]) - 1]["results"]["tests"]
                            results["score"] = metadata["previous_submissions"][len(metadata["previous_submissions"]) - 1]["score"]
                        json.dump(results, jsonResults)
                        if tokens_used >= tokens:
                            import sys
                            sys.exit()