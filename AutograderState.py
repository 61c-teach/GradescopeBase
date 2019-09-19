from . import Autograder, AutograderTest, AutograderSubTest

class AutograderState:
    def __init__(self, ag: Autograder, test: Autograder, subtest: AutograderSubTest=None):
        self.ag = ag
        self.test = test
        self.subtest = subtest