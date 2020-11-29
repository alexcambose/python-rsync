from copy import deepcopy


class StateManager:
    def __init__(self):
        self.previous_state = []
        self.current_state = []

    def set_state(self, state):
        # if not self.current_state:
        #     self.previous_state = deepcopy(state)
        self.previous_state = deepcopy(self.current_state)
        self.current_state = state

    def get_current_state(self):
        return deepcopy(self.current_state)

    def get_previous_state(self):
        return deepcopy(self.previous_state)
