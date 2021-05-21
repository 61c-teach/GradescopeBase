"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:01:33 
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-01-23 21:02:27
 */
 """
from . import Autograder, AutograderTest, AutograderSubTest

class AutograderState:
    def __init__(self, ag: Autograder, test: Autograder, subtest: AutograderSubTest=None):
        self.ag = ag
        self.test = test
        self.subtest = subtest