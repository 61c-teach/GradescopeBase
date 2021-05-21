"""
/*
 * @Author: ThaumicMekanism [Stephan K.] 
 * @Date: 2020-01-23 21:03:21 
 * @Last Modified by:   ThaumicMekanism [Stephan K.] 
 * @Last Modified time: 2020-01-23 21:03:21 
 */
"""
from typing import TypeVar
T = TypeVar('T')

class Leaderboard:
    def __init__(self):
        self.items = {}

    def add_item(self, name: str, value: T, order: str=None):
        """
        The default order is descending ('desc') though it also accepts 'asc' for ascending order.
        """
        self.items[name] = LeaderboardItem(name, value, order)
    
    def get_item(self, name: str):
        return self.items
    
    def remove_item(self, name: str):
        if name in self.items:
            del self.items[name]
            return True
        return False

    def export(self):
        return [leaderboard_item.export() for leaderboard_item in self.items]


class LeaderboardItem:
    def __init__(self, name: str, value: T, order: str=None) -> None:
        self.name = name
        self.value = value
        self.order = order

    def export(self):
        item = {
            "name": self.name,
            "value": self.value
        }
        if self.order is not None:
            item["order"] = self.order
        return item