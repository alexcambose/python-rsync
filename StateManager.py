"""
StateManager class
"""
from copy import deepcopy
from utils import sort_state


class StateManager:
    """
    Keeps the current and previous states in sync
    """

    def __init__(self):
        self.previous_state = []
        self.current_state = []

    def set_state(self, state=[]):
        """
    `   set current state
        """
        self.previous_state = deepcopy(self.current_state)
        self.current_state = sort_state(state)

    def get_current_state(self):
        """
    `   get current state
        """
        return deepcopy(self.current_state)

    def get_previous_state(self):
        """
    `   get previous state
        """
        return deepcopy(self.previous_state)
