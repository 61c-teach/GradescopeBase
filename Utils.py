import os

def is_local() -> bool:
        return os.path.isfile("/.localhost")

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
                return "./results.json"
        return "/autograder/results/results.json"