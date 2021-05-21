"""
/*
 * @Author: ThaumicMekanism [Stephan K.]
 * @Date: 2020-01-30 11:35:10
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-01-30 16:09:58
 */
"""
class AutograderBaseError(Exception):
    """
    Base exception for autograders.
    """
    def __init__(self, info: any=None):
        self.info = info

class AutograderFormatError(AutograderBaseError):
    """
    This error is for when the expected state of the autograder is incorrect.
    """
    pass

class AutograderSafeEnvError(AutograderBaseError):
    pass

class AutograderHalt(AutograderBaseError):
    pass