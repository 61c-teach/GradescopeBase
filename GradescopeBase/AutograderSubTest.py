"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:02:33 
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-01-30 16:17:58
 */
"""
from .AutograderTest import AutograderTest
from .Autograder import Autograder, AutograderSafeEnvError
from . import Visibility
from typing import Callable
from .AutograderErrors import AutograderFormatError
from .Utils import NoneLooseVersion

SUB_TESTS_KEY = "sub_tests"
ISPASSFAIL = True

class AutograderSubTest(AutograderTest):
    def __init__(
        self,
        test: AutograderTest,
        test_fn: Callable[["Autograder", AutograderTest], any]=None,
        name: str=None, 
        max_score: float=None,
        score: float=None,
        number: str=None, 
        tags: [str]=None,
        visibility: Visibility=None,
        extra_data=None,
        kill_autograder_on_error: bool=False,
        do_not_set_score: bool=False,
        timeout: int=None,
        ceil: bool=True,
        floor: bool=True,
        do_not_override_test_fn: bool=False,
    ):
        self.test = test
        self.test_fn = test_fn
        self.max_score = max_score
        self.number = number
        self.name = name
        self.tags = tags
        self.extra_data = extra_data
        self.score = score
        self.output = ""
        self.kill_autograder_on_error = kill_autograder_on_error
        self.do_not_set_score = do_not_set_score
        self.timeout = timeout
        self.ceil = ceil
        self.floor = floor
        test_case_has_test_runner_fn = False
        if issubclass(type(test.test_fn), SubTestRunner):
            test_case_has_test_runner_fn = True
        if test.test_fn is not None and not test_case_has_test_runner_fn:
            raise ValueError("The test case given already has a custom subtest function! If you do not want to override it, please set do_not_override_test_fn to true.")
        if test.test_fn is None and do_not_override_test_fn:
            raise ValueError("The test function for the test case does not have a test function!")
        if not do_not_override_test_fn and not test_case_has_test_runner_fn:
            test.test_fn = SubTestRunner()
        if SUB_TESTS_KEY not in test.__dict__:
            test.__dict__[SUB_TESTS_KEY] = []
        test.__dict__[SUB_TESTS_KEY].append(self)

    def set_score(self, score):
        if type(score) is bool:
            self.score = score
            return
        return super().set_score(score)

    def passed(self):
        if self.score is True or self.score == self.max_score:
            return True
        return False

    def get_score(self, convert_true_false=True):
        score = self.score
        if convert_true_false:
            if score is True:
                score = self.max_score
            elif score is False:
                score = 0
        if score is None:
            return 0
        return score

class StopSubTestRunner(BaseException):
    def __init__(self, info=""):
        self.info = info
        
class SubTestRunner(object):
    def __init__(
        self,
        is_pass_fail: bool=True,
        pass_fail_ratio: float=1,
    ):
        self.separator_count = 40
        self.is_pass_fail = is_pass_fail
        self.pass_fail_ratio = pass_fail_ratio

    def pre_test_run(self, ag: Autograder, test: AutograderTest, data):
        pass

    def get_sub_tests(self, ag: Autograder, test: AutograderTest, data):
        if SUB_TESTS_KEY not in test.__dict__:
            raise AutograderFormatError("This test should have test cases but none exist!")
        sub_test = test.__dict__[SUB_TESTS_KEY]
        sub_test = sorted(sub_test, key=lambda st: NoneLooseVersion(st.number))
        return sub_test

    def score_post(self, ag: AutograderTest, test: AutograderTest, data):
        test.print()
        test.print("+" * self.separator_count)
        if self.is_pass_fail:
            if self.did_pass(data):
                test.set_score(True)
                passed = "[✓] PASSED"
            else:
                test.set_score(False)
                passed = "[X] FAILED"
            test.print(passed)
        else:
            test.set_score(data["score"])
            test.print(f"{data['score']} / {test.max_score}")
        test.print("+" * self.separator_count)

    def post_test_run(self, ag: Autograder, test: AutograderTest, data):
        pass

    def pre_subtest_run(self, ag: Autograder, test: AutograderTest, t: AutograderSubTest, data):
        test.print("=" * self.separator_count)
        test.print(f"[SubTest]: {t.name}")
        test.print("-" * self.separator_count)

    def post_subtest_run(self, ag: Autograder, test: AutograderTest, t: AutograderSubTest, data):
        passed = t.passed()
        score = t.get_score()
        self.increment_score(data, score)
        self.add_test_passed_status(data, passed)
        test.print(t.output)
        test.print("-" * self.separator_count)
        if self.is_pass_fail:
            msg = "[X] FAILED"
            if passed:
                msg = "[✓] PASSED"
            test.print(msg)
        else:
            test.print(f"{score} / {t.max_score}")
        test.print("_" * self.separator_count)
        test.print("\n")

    def increment_score(self, data, score):
        data["score"] += score

    def get_full_score(self, data, score):
        return data["score"]

    def add_test_passed_status(self, data, status):
        data["passed"].append(status)

    def did_pass(self, data):
        amt = len(data["passed"])
        if amt == 0:
            return False
        return sum(data["passed"]) / amt >= self.pass_fail_ratio

    def run_test(self, ag: Autograder, test: AutograderTest, t, data):
        try:
            res = t.run(ag, handler=self.stopSubTestRunnerHandler)
        except StopSubTestRunner as e:
            if e.info:
                test.print(e.info)
            return e
        if isinstance(res, AutograderSafeEnvError):
            return res.info

    def part_stopped(self, idx: str, ag: Autograder, test: AutograderTest, t: AutograderSubTest, data: dict):
        test.print("[Warning]: This test stopped early!")
        return StopSubTestRunner(idx)

    def __call__(self, ag: Autograder, test: AutograderTest):
        r = self.runner(ag, test)
        if isinstance(r, StopSubTestRunner):
            print(f"[Warning]: The subtest runner stopped on {r.info}! ({test.name})")

    @staticmethod
    def stopSubTestRunnerHandler(exception):
        if isinstance(exception, StopSubTestRunner):
            return exception

    def runner(self, ag: Autograder, test: AutograderTest):
        data = {
            "score": 0,
            "passed": [],
        }
        sub_test = self.get_sub_tests(ag, test, data)
        if sub_test is False:
            r = self.part_stopped("get_sub_tests", ag, test, None, data)
            if isinstance(r, StopSubTestRunner):
                return r
        if self.pre_test_run(ag, test, data) is False:
            r = self.part_stopped("pre_test_run", ag, test, None, data)
            if isinstance(r, StopSubTestRunner):
                return r
        for t in sub_test:
            if self.pre_subtest_run(ag, test, t, data) is False:
                r = self.part_stopped("pre_subtest_run", ag, test, t, data)
                if isinstance(r, StopSubTestRunner):
                    return r
            res = self.run_test(ag, test, t, data)
            is_subtest_stopper = isinstance(res, StopSubTestRunner)
            if res is False or is_subtest_stopper:
                r = self.part_stopped("run_test", ag, test, t, data)
                if isinstance(r, StopSubTestRunner):
                    return r
            if self.post_subtest_run(ag, test, t, data) is False:
                r = self.part_stopped("post_subtest_run", ag, test, t, data)
                if isinstance(r, StopSubTestRunner):
                    return r
        if self.score_post(ag, test, data) is False:
            r = self.part_stopped("score_post", ag, test, None, data)
            if isinstance(r, StopSubTestRunner):
                return r
        if self.post_test_run(ag, test, data) is False:
            r = self.part_stopped("post_test_run", ag, test, None, data)
            if isinstance(r, StopSubTestRunner):
                return r
