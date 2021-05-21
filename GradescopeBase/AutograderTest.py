"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:03:09 
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-01-30 16:04:03
 */
"""

"""
This is a test in gradescope.
"""
from .Timeout import Timeout
from . import Visibility
from .Utils import root_dir, submission_dir
from typing import Callable

global_tests = []

class Max:
    pass

default_visibility = None
class AutograderTest:
    def __init__(self, 
        test_fn: Callable[["Autograder", "AutograderTest"], any]=None,
        name: str=None, 
        max_score: float=None, 
        score: float=None,
        number: str=None, 
        tags: [str]=None, 
        visibility: Visibility=default_visibility, 
        extra_data=None,
        kill_autograder_on_error: bool=False,
        do_not_set_score: bool=False,
        timeout: int=None,
        ceil: bool=True,
        floor: bool=True,
        ran: bool=False,
    ):
        """
        The test_fn MUST take in parameters Autograder and AutograderTest in that order.
        It is how the test will interact with the autograder.
        """
        self.test_fn = test_fn
        self.max_score = max_score
        self.name = name
        self.number = number
        self.tags = tags
        self.visibility = visibility
        self.extra_data = extra_data
        self.score = score
        self.output = ""
        self.kill_autograder_on_error = kill_autograder_on_error
        self.do_not_set_score = do_not_set_score
        self.timeout = timeout
        self.ceil = ceil
        self.floor = floor
        self.ran = ran
        global_tests.append(self)

    def print(self, *args, sep=' ', end='\n', file=None, flush=True, also_stdout=False):
        msg = sep.join(map(str, args)) + end
        if also_stdout:
            print(msg)
        self.output += msg

    def set_score(self, score):
        if score is None:
            return
        if score is True:
            score = self.max_score
        elif score is False:
            score = 0
        if isinstance(score, Max) and self.max_score is not None:
            score = self.max_score
        # if self.score is None:
        #     self.score = score
        #     return
        if self.ceil and self.max_score is not None and score > self.max_score:
            score = self.max_score
        if self.floor and score < 0:
            score = 0
        self.score = score
    
    def remove_score(self):
        self.score = None

    def get_score(self):
        return self.score

    def run(self, ag, handler=None):
        self.ran = True
        if self.test_fn is None:
            self.print("[ERROR]: This test case does not have a callable function!")
            self.set_score(0)
            return
        
        def set_score(r):
            if self.do_not_set_score:
                return
            self.set_score(r)

        def f():
            try:
                with Timeout(self.timeout):
                    r = self.test_fn(ag, self)
                    set_score(r)
            except Timeout.Timeout:
                self.print("[ERROR]: This test timed out!")
                set_score(0)

        def default_handler(exception):
            if not self.do_not_set_score:
                self.set_score(0)
            if self.kill_autograder_on_error:
                return False
            self.print("[Error]: An unexpected error occured in the Autograder when attempting to run this testcase! Please contact a TA if this persists.")
            return True
        ag.safe_env(f, handler=handler if handler is not None else default_handler)

    def get_results(self):
        o = self.output
        if self.ran is False:
            o = "[WARNING]: This test did not run!"
        data = {"output": o}
        if self.max_score is not None:
            data["max_score"] = self.max_score
        if self.name is not None:
            data["name"] = self.name
        if self.number is not None:
            data["number"] = self.number
        if isinstance(self.tags, list):
            data["tags"] = self.tags
        if self.visibility is not None:
            data["visibility"] = self.visibility.name
        if self.extra_data is not None:
            data["extra_data"] = self.extra_data
        if self.score is not None:
            data["score"] = self.score
        return data

    @staticmethod
    def root_dir() -> str:
        return root_dir()

    @staticmethod
    def submission_dir() -> str:
        return submission_dir()