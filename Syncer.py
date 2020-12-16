"""
Syncer class
"""
from utils import remove_dictionary_key, sort_state
from copy import deepcopy


def log(*content):
    """
    Logging function used for console logging
    :param content: - The content that needs to be logged to the console
    :return:
    """
    print('[SYNCER] ', *content)


class Syncer:
    """
    The bridge between modes, check for file changes.
    """

    def __init__(self, class_a, class_b):
        self.class_a = class_a
        self.class_b = class_b
        self.startup()

    def startup(self):
        """
        executed upon startup
        initial sync between two locations
        :return:
        """

        state_a = self.class_a.create_state()[0]
        state_b = self.class_b.create_state()[0]
        state_a = remove_dictionary_key(state_a, 'last_modified')
        state_b = remove_dictionary_key(state_b, 'last_modified')
        state_a = sort_state(state_a)
        state_b = sort_state(state_b)
        log('a', state_a)
        log('b', state_b)
        log('')
        # copy missing files
        for i in range(max(len(state_a), len(state_b))):
            if i < len(state_a) and state_a[i] not in state_b:
                self.class_b.copy_from(self.class_a, state_a[i]['path'])
            if i < len(state_b) and state_b[i] not in state_a:
                self.class_a.copy_from(self.class_b, state_b[i]['path'])

        # refresh state
        state_a = self.class_a.create_state()[0]
        state_b = self.class_b.create_state()[0]
        # compare if there new, modified or deleted files between states

        state_a = list(filter(lambda x: x['is_directory'] == False, state_a))
        state_b = list(filter(lambda x: x['is_directory'] == False, state_b))

        state_a = sort_state(state_a)
        state_b = sort_state(state_b)

        log(state_a)
        log(state_b)
        log('')
        # compare file last_modified
        for i in range(max(len(state_a), len(state_b))):
            # we have a difference
            for j in range(min(len(state_a), len(state_b))):
                # we have the same file but with different last_modified
                # timestamps
                if i < len(state_a) and i < len(state_b) and j < len(
                        state_a) and j < len(state_b):
                    # the locations are matching and they are not a directory
                    if state_a[i]['path'] == state_b[j]['path'] and state_a[i]['is_directory'] == state_b[
                            j]['is_directory'] and state_a[i]['last_modified'] != state_b[j]['last_modified']:
                        # copy the most recent modified file
                        if state_a[i]['last_modified'] < state_b[j][
                                'last_modified']:
                            self.class_a.copy_from(
                                self.class_b, state_b[i]['path'])
                        else:
                            self.class_b.copy_from(
                                self.class_a, state_a[i]['path'])

        # finally, run create state again to update the states after the
        # changes
        self.class_a.create_state()
        self.class_b.create_state()

    def compute_states(self, state, previous_state, class_a, class_b):
        """
        Compares the current state with the previous state and executes commands from/to class_a and class_b to keeps files in sync
        :param state: - Current state
        :param previous_state: - Previous state
        :param class_a: - Class instance from where the files are being copied
        :param class_b: - Class instance to where the files are being copied
        :return:
        """
        state = sort_state(state)
        previous_state = sort_state(previous_state)
        log(state)
        log(previous_state)
        modified = False
        for element_b in state:
            for element_a in previous_state:
                # element already exists
                if element_a['path'] == element_b['path'] and element_b[
                        'is_directory'] == element_a['is_directory'] and not element_a['is_directory']:
                    if element_a['last_modified'] > element_b['last_modified']:
                        class_b.copy_from(class_a, element_a['path'])
                        modified = True

            # new file added
            if element_b not in previous_state:
                log('File {} added'.format(element_b))
                class_b.copy_from(class_a, element_b['path'])
                # new file could be added by moving, therefore we need to check
                # for deleted files also
                for element_c in sort_state(previous_state, True):
                    if element_c not in state:
                        log('File {} deleted (moved)'.format(element_c))
                        class_b.delete(element_c['path'])
                        modified = True
                return True

        state = sort_state(state, True)
        previous_state = sort_state(previous_state, True)

        # check for removed files
        for element_b in previous_state:
            # if the current state is empty and the previous state has files,
            # delete them
            if len(state) == 0:
                log('File {} deleted'.format(element_b), previous_state)
                class_b.delete(element_b['path'])
                modified = True
            else:
                for element_a in state:
                    # if an element from the previous state does not exist in
                    # the current state
                    if element_b not in state:
                        log('File {} deleted (previous state)'.format(element_b))
                        class_b.delete(element_b['path'])
                        modified = True
                        break
        return modified

    def update(self):
        """
        Monitors file changes, called every x seconds
        :return:
        """
        log('UPDATE')
        (state_a, previous_state_a) = self.class_a.create_state()

        (state_b, previous_state_b) = self.class_b.create_state()
        # check for differences between the current and previous states
        log('a')
        modified = self.compute_states(
            state_a, previous_state_a, self.class_a, self.class_b)
        if modified:
            log('REFRESH')
            self.class_b.create_state()
            self.update()
            return
        log('b')
        # check for differences between the current and previous states
        modified = self.compute_states(
            state_b, previous_state_b, self.class_b, self.class_a)
        if modified:
            log('REFRESH')
            self.class_a.create_state()
            self.update()
        if str(state_a) != str(state_b):
            self.startup()
