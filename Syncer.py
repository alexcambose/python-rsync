"""
Syncer class
"""
from utils import remove_dictionary_key


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
        (state_a, previous_state_a) = self.class_a.create_state()
        (state_b, previous_state_b) = self.class_b.create_state()
        # compare if there new, modified or deleted files between states

        state_a = list(filter(lambda x: x['is_directory'] == False, state_a))
        state_b = list(filter(lambda x: x['is_directory'] == False, state_b))
        print(state_a)
        print(state_b)
        print('')
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
                    # the locations are matching and they are not a directory
                    if state_b[i]['path'] == state_a[j]['path'] and state_b[i]['is_directory'] == state_a[
                            j]['is_directory'] and state_b[i]['last_modified'] != state_a[j]['last_modified']:
                        if state_b[i]['last_modified'] < state_a[j][
                                'last_modified']:
                            self.class_b.copy_from(
                                self.class_a, state_a[i]['path'])
                        else:
                            self.class_a.copy_from(
                                self.class_b, state_b[i]['path'])
        state_a = self.class_a.create_state()[0]
        state_b = self.class_b.create_state()[0]
        state_a = remove_dictionary_key(state_a, 'last_modified')
        state_b = remove_dictionary_key(state_b, 'last_modified')
        print('a', state_a)
        print('b', state_b)
        print('')
        # copy missing files
        for i in range(max(len(state_a), len(state_b))):
            if i < len(state_a) and state_a[i] not in state_b:
                self.class_b.copy_from(self.class_a, state_a[i]['path'])
            if i < len(state_b) and state_b[i] not in state_a:
                self.class_a.copy_from(self.class_b, state_b[i]['path'])
        # finally, run create state again to update the states after the changes
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
        for element_b in state:
            for element_a in previous_state:
                if element_a['path'] == element_b['path'] and element_b['is_directory'] == element_a[
                        'is_directory'] and not element_a['is_directory']:
                    if element_a['last_modified'] > element_b['last_modified']:
                        class_b.copy_from(class_a, element_a['path'])
                        return True
            # new file added
            if element_b not in previous_state:
                print('File {} added'.format(element_b))
                class_b.copy_from(class_a, element_b['path'])
                # new file could be added by moving, therefore we need to check for deleted files also
                for element_c in previous_state:
                    if element_c not in state:
                        print('File {} deleted (moved)'.format(element_c))
                        class_b.delete(element_c['path'])
                        return True
                return True
        # if the current state is empty and the previous state has files, delete them
        if len(state) == 0:
            for element_b in previous_state:
                print('File {} deleted'.format(element_b))
                class_b.delete(element_b['path'])
                return True
        # check for removed files
        for element_b in previous_state:
            for element_a in state:
                # if an element from the previous state does not exist in the current state
                if element_b not in state:
                    print('File {} deleted'.format(element_b))
                    class_b.delete(element_b['path'])
                    return True
        return False

    def update(self):
        """
        Monitors file changes, called every x seconds
        :return:
        """
        print('UPDATE')
        (state_a, previous_state_a) = self.class_a.create_state()
        print('state_a         ', state_a)
        print('previous_state_a', previous_state_a)
        print()

        (state_b, previous_state_b) = self.class_b.create_state()
        print('state_b         ', state_b)
        print('previous_state_b', previous_state_b)
        print()
        # check for differences between the current and previous states
        modified = False
        modified = self.compute_states(state_a, previous_state_a, self.class_a, self.class_b)
        if modified:
            print('REFRESH')
            self.class_b.create_state()
            self.update()
            return
        # check for differences between the current and previous states
        modified = self.compute_states(state_b, previous_state_b, self.class_b, self.class_a)
        if modified:
            print('REFRESH')
            self.class_a.create_state()
            self.update()
        if str(state_a) != str(state_b):
            self.startup()
