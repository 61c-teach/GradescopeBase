"""
This is the visibility of an assignment.
"""
from enum import Enum

class Visibility(Enum):
    hidden = "hidden"
    after_due_date = "after_due_date"
    after_published = "after_published"
    visible = "visible"
