"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 20:57:36 
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-04-25 14:56:44
 */
"""
"""
This is the base of the autograder.
"""
import datetime
import importlib
import json
import os
from typing import Callable, List, Union

from .AutograderErrors import AutograderSafeEnvError
from .AutograderLeaderboard import Leaderboard
from .AutograderRateLimit import RateLimit
from .AutograderSetup import global_setups
from .AutograderTeardown import global_teardowns
from .AutograderTest import AutograderTest, global_tests, Max
from .Utils import root_dir, submission_dir, results_path, get_welcome_message, is_local, submission_metadata_dir, module_from_file

printed_welcome_message = False

class Autograder:
    use_ratelimit_when_local = False

    def __init__(self, *,
        rate_limit: RateLimit=None, 
        reverse_tests: bool=False, 
        export_tests_after_test: bool=True, 
        modify_results=lambda results: results,
        print_welcome_message: bool=True,
    ):
        if print_welcome_message:
            global printed_welcome_message
            if not printed_welcome_message:
                printed_welcome_message = True
                print(get_welcome_message())
        self.tests = []
        self.setups = []
        self.teardowns = []
        self.results_file = results_path()
        self.score = None
        self.output = None
        self.visibility = None
        self.stdout_visibility = None
        self.extra_data = {}
        self.leaderboard = Leaderboard()
        self.reverse_tests = reverse_tests
        self.export_tests_after_test = export_tests_after_test
        # rate_limit takes in a RateLimit class.
        # reset_time is when you want to reset the submission time. You
        # can leave it out to ignore. Put the time stirng in this format:
        #  "2018-11-29T16:15:00"
        if rate_limit is None:
            rate_limit = RateLimit()
        self.rate_limit: RateLimit = rate_limit
        self.start_time = datetime.datetime.now()
        self.modify_results = modify_results

        if not is_local():
            with open(submission_metadata_dir(), "r") as jsonMetadata:
                self.metadata = json.load(jsonMetadata)
            self.extra_data["id"] = self.metadata["id"]
        else:
            if os.path.isfile(submission_metadata_dir()):
                with open(submission_metadata_dir(), "r") as jsonMetadata:
                    self.metadata = json.load(jsonMetadata)
                self.extra_data["id"] = self.metadata["id"]
            else:
                self.extra_data["id"] = "LOCAL"
                self.metadata = None

    def run(self, import_globals: bool=True):
        def load_and_execute_autograder(ag: "Autograder"):
            if import_globals:
                for t in global_tests:
                    ag.add_test(t)
                for s in global_setups:
                    ag.add_setup(s)
                for t in global_teardowns:
                    ag.add_teardown(t)
            ag.execute()
        return self.safe_main(load_and_execute_autograder)

    def safe_main(self, f: Callable[["Autograder"], None]):
        def handler(exception):
            self.ag_fail("An exception occured in the autograder's main function. Please contact a TA to resolve this issue.")
            return True
        def wrapper():
            return f(self)
        return self.safe_env(wrapper, handler)

    def dump_results(self, data: dict) -> None:
        jsondata = json.dumps(data, ensure_ascii=False)
        with open(self.results_file, "wb") as f:
            f.write(jsondata.encode("ascii", errors="backslashreplace"))
        return self

    def import_tests(self, *, 
        tests_dir: Union[str, List[str]]=None, 
        test_files: Union[str, List[str]]=None, 
        blacklist: Union[str, List[str]]=None,
        verbose: bool=True
    ):
        if tests_dir is None:
            tests_dir = []
        if isinstance(tests_dir, str):
            tests_dir = [tests_dir]

        if test_files is None:
            test_files = []
        if isinstance(test_files, str):
            test_files = [test_files]
        
        def import_file(filepath):
            if verbose:
                print(f"Importing file {filepath}.") 
            try:
                # importlib.import_module(".{}".format(file), package=package)
                module_from_file(filepath)
            except Exception as e:
                print(f"Could not add a test file {filepath}!")
                import traceback
                traceback.print_exc()
                print(e)
        
        for test_file in test_files:
            import_file(test_file)
        
        for dir in tests_dir:
            files = sorted(os.listdir(dir), reverse=True)
            for file in files:
                filepath = os.path.join(dir, file)
                if file.endswith(".py") and file not in blacklist and os.path.isfile(filepath):
                    import_file(filepath)
        return self

    def add_test(self, test, index=None):
        if isinstance(test, AutograderTest):
            if index is None:
                self.tests.append(test)
            else:
                self.tests.insert(index, test)
        else:
            raise ValueError("You must add type Test to the autograder.")
        return self

    def add_setup(self, setupfn):
        self.setups.append(setupfn)
        return self

    def add_teardown(self, teardownfn):
        self.teardowns.append(teardownfn)
        return self

    def set_score(self, score):
        self.score = score
        return self
    
    def add_score(self, addition):
        if self.score is None:
            self.score = 0
        self.score += addition
        return self
    
    def get_score(self):
        score = None
        for test in self.tests:
            test_score = test.get_score()
            if test_score is not None:
                if score is None:
                    score = test_score
                else:
                    score += test_score
        if score is None:
            score = self.score
        return score

    def print(self, *args, sep=' ', end='\n', file=None, flush=True, also_stdout=False):
        if self.output is None:
            self.output = ""
        msg = sep.join(map(str, args)) + end
        if also_stdout:
            print(msg)
        self.output += msg
        return self

    def create_test(self, *args, **kwargs):
        test = AutograderTest(*args, **kwargs)
        self.add_test(test)
        return self

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
        return self
    
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
                    h = handler(exc)
                    if h:
                        return AutograderSafeEnvError(h)
                except Exception as exc:
                    print("An exception occurred while executing the exception handler!")
                    traceback.print_exc()
            self.ag_fail("An unexpected exception ocurred while trying to execute the autograder. Please try again or contact a TA if this persists.")
            return AutograderSafeEnvError(exc)

    def run_tests(self):
        global printed_welcome_message
        if not printed_welcome_message:
            printed_welcome_message = True
            print(get_welcome_message())
        local = is_local()
        def handle_failed():
                self.set_score(0)
                if "sub_counts" in self.extra_data:
                    self.print("[Rate Limit]: Since the autograder failed to run, you will not use up a token!")
                    self.rate_limit.rate_limit_unset_submission(self)
        for setup in self.setups:
            if not setup.when_to_run.okay_to_run(local):
                continue
            res = setup.run(self)
            if not res:
                print(f"[Error]: ({setup.name}) Returned non-true value `{res}` so assuming it failed!")
                self.print("[Error]: An error occurred in the setup of the Autograder!")
                handle_failed()
                return False
        for test in self.tests:
            test.run(self)
            if self.export_tests_after_test:
                self.generate_results(print_main_score_warning_error=False)
        for teardown in self.teardowns:
            if not teardown.when_to_run.okay_to_run(local):
                continue
            res = teardown.run(self)
            if not res:
                print(f"[Error]: ({teardown.name}) Returned non-true value `{res}` so assuming it failed!")
                self.print("[Error]: An error occurred in the teardown of the Autograder!")
                handle_failed()
                return False
        return True

    def generate_results(self, test_results=None, leaderboard: Leaderboard=None, dump=True, print_main_score_warning_error=True):
        results = {
            "execution_time": (datetime.datetime.now() - self.start_time).total_seconds(),
        }
        if test_results is None:
            tests = []
            if self.reverse_tests:
                tsts = reversed(self.tests)
            else:
                tsts = self.tests
            for test in tsts:
                res = test.get_results()
                if res:
                    tests.append(res)
            if tests:
                results["tests"] = tests
        else:
            if isinstance(test_results, list):
                results["tests"] = test_results
        if self.score is not None:
            results["score"] = self.score
        else:
            if "tests" not in results or len(results["tests"]) == 0 or not any(["score" in t for t in results["tests"]]):
                results["score"] = 0
                if print_main_score_warning_error:
                    self.print("This autograder does not set the main score or have any tests which give points!")
        if self.output is not None:
            results["output"] = self.output
        if self.visibility is not None:
            results["visibility"] = self.visibility
        if self.stdout_visibility is not None:
            results["stdout_visibility"] = self.stdout_visibility
        if self.extra_data:
            results["extra_data"] = self.extra_data
        if leaderboard is not None:
            leaderboard_export = leaderboard.export()
        else:
            leaderboard_export = self.leaderboard.export()
        if leaderboard_export:
            results["leaderboard"] = leaderboard_export
        results = self.modify_results(results)
        if dump:
            self.dump_results(results)
        return results
        
    def execute(self, generate_results: bool=True):
        global printed_welcome_message
        if not printed_welcome_message:
            printed_welcome_message = True
            print(get_welcome_message())
        self.rate_limit.rate_limit_main(self)
        if not self.run_tests():
            print("An error has occurred when attempting to run all tests.")
        if self.rate_limit.is_enabled():
            if self.output is None:
                self.output = ""
            self.output = self.rate_limit.get_rate_limit_str(self) + self.output
        if generate_results:
            self.generate_results()
        return self

    @staticmethod
    def root_dir() -> str:
        return root_dir()

    @staticmethod
    def submission_dir() -> str:
        return submission_dir()

    @staticmethod
    def DUMP(msg):
        ag = Autograder()
        ag.print(msg)
        ag.set_score(0)
        ag.generate_results()