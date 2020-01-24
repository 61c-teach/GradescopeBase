"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:03:57 
 * @Last Modified by:   ThaumicMekanism [Stephan K.] 
 * @Last Modified time: 2020-01-23 21:03:57 
 */
"""
import os

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

def results_path() -> str:
        """
        This returns the path which the results json should be exported to.
        """
        if is_local():
                return "./results/results.json"
        return "/autograder/results/results.json"