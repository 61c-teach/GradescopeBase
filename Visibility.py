"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:04:08 
 * @Last Modified by:   ThaumicMekanism [Stephan K.] 
 * @Last Modified time: 2020-01-23 21:04:08 
 */
"""
"""
This is the visibility of an assignment.
"""
from enum import Enum

class Visibility(Enum):
    hidden = "hidden"
    after_due_date = "after_due_date"
    after_published = "after_published"
    visible = "visible"
