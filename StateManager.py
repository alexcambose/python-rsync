"""
StateManager class
"""
from copy import deepcopy

def sortFunc(e):
  return e['is_directory']

class StateManager:
    """
    Keeps the current and previous states in sync
    """

    def __init__(self):
        self.previous_state = []
        self.current_state = []

    def set_state(self, state = []):
        """
    `   set current state
        """
        self.previous_state = deepcopy(self.current_state)
        state.sort(key=sortFunc)
        self.current_state = state

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
