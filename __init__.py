"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 20:56:28 
 * @Last Modified by:   ThaumicMekanism [Stephan K.] 
 * @Last Modified time: 2020-01-23 20:56:28 
 */
 """
from .Autograder import Autograder, AutograderError, RateLimit
from .AutograderTest import AutograderTest, Max, global_tests
from .AutograderSetup import AutograderSetup
from .AutograderTeardown import AutograderTeardown
from .Visibility import Visibility

def Test(*args, **kwargs):
    """
    The Test decorator is meant to signify an autograder test case. It will be auto added to the list of test cases so the main autograder can run it.
    You will supply the arguments to the decorator just as if you were calling the AutograderTest function WITHOUT the function. For example, if I wanted to 
    make a function with a name of "foo" with max score of 2, I could have:

    @Test("Foo", 2):
    def mytest(ag, test: AutograderTest):
        return 2

    Note: your function still MUST accept two positional arguments, the first gives you the main Autograder class while the second gives you the current
    tests AutograderTest class. That will be the method for interacting with the autograder.
    """
    def inner(func):
        AutograderTest(func, *args, **kwargs)
        return func
    return inner

def Setup(*args, **kwargs):
    """
    This is a decorator which will allow you to add a global setup function. 
    """
    def inner(func):
        AutograderSetup(func, *args, **kwargs)
        return func
    return inner

def Teardown(*args, **kwargs):
    """
    This is a decorator which will allow you have a global teardown function.
    """
    def inner(func):
        AutograderTeardown(func, *args, **kwargs)
        return func
    return inner

__all__ = [
    "Autograder",
    "AutograderError",
    "RateLimit",
    "AutograderTest",
    "Visibility",
    "Max",
    "global_tests",
    "Test",
    "Setup",
    "Teardown"
]