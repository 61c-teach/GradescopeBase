import os

SUBMISSION_BASE = '/autograder/submission'


def check_submitted_files(paths, base=SUBMISSION_BASE):
    """Checks that the files in the given list exist in the student's submission.

    Returns a list of missing files.

    eg. check_submitted_files(['src/calculator.py'])
    """
    missing_files = []
    for path in paths:
        target_path = os.path.join(base, path)
        if not os.path.isfile(target_path):
            missing_files.append(path)
    return missing_files
