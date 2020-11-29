from copy import deepcopy


class StateManager:
    def __init__(self):
        self.previous_state = []
        self.current_state = []

    def set_state(self, state):
        self.previous_state = deepcopy(self.current_state)
        self.current_state = state

    def get_current_state(self):
        return self.current_state

    def get_previous_state(self):
        return self.previous_state
