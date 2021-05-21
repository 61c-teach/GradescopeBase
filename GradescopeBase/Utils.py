"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:03:57 
 * @Last Modified by: ThaumicMekanism [Stephan K.]
 * @Last Modified time: 2020-01-30 16:27:10
 */
"""
import enum
import os
import pathlib

from distutils.version import LooseVersion

with open(os.path.join(pathlib.Path(__file__).parent.absolute(), 'VERSION')) as version_file:
    VERSION = version_file.read().strip()

def get_welcome_message():
    return f"Initializing the GradescopeBase Autograder v{VERSION} created by ThaumicMekanism [Stephan K.]."

def is_local() -> bool:
    return os.environ.get("IS_LOCAL") == "true"

def root_dir() -> str:
    """
    This function assumes the root directory is the one right above the GradescopeBase folder.
    """
    dirname = os.path.dirname
    return dirname(dirname(os.path.realpath(__file__)))

def submission_dir() -> str:
    """
    This returns the dir which contains the submission.
    """
    if is_local():
        return "./submission"
    return "/autograder/submission"

def submission_metadata_dir() -> str:
    """
    This returns the dir which contains the submission.
    """
    if is_local():
        return "./submission_metadata.json"
    return "/autograder/submission_metadata.json"

def results_path() -> str:
    """
    This returns the path which the results json should be exported to.
    """
    if is_local():
        return "./results/results.json"
    return "/autograder/results/results.json"

class NoneLooseVersion(LooseVersion):
    def __init__ (self, vstring=None):
        if vstring:
            self.parse(vstring)
        else:
            self.version = None

    def _cmp (self, other):
        if isinstance(other, str):
            other = NoneLooseVersion(other)
        if self.version == other.version:
            return 0
        if self.version is not None:
            return -1
        if other.version is not None:
            return 1
        if self.version < other.version:
            return -1
        if self.version > other.version:
            return 1

def merge(a, b, path=None):
    "merges b into a"
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a

class WhenToRun(enum.Enum):
    NEITHER = 0
    LOCAL = 1
    GRADESCOPE = 2
    BOTH = 3
    
    def okay_to_run(self, state: bool=None) -> bool:
        if state is None:
            state = is_local()
        if self is self.NEITHER:
            return False
        if self is self.BOTH:
            return True
        return (state and self is self.LOCAL) or (not state and self is self.GRADESCOPE)