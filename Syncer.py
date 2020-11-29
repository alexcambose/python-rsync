from utils import remove_dictionary_key


class Syncer:
    def __init__(self, class_a, class_b):

        self.class_a = class_a
        self.class_b = class_b
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
                # we have the same file but with different last_modified timestamps
                if i < len(state_a) and i < len(state_b) and j < len(state_a) and j < len(state_b):
                    if state_a[i]['path'] == state_b[j]['path'] and state_a[i]['is_directory'] == state_b[j]['is_directory'] and state_a[i]['last_modified'] != state_b[j]['last_modified']:
                        if state_a[i]['last_modified'] < state_b[j]['last_modified']:
                            self.class_a.copy_from(self.class_b, state_b[i]['path'])
                        else:
                            self.class_b.copy_from(self.class_a, state_a[i]['path'])
                    if state_b[i]['path'] == state_a[j]['path'] and state_b[i]['is_directory'] == state_a[j]['is_directory'] and state_b[i]['last_modified'] != state_a[j]['last_modified']:
                        if state_b[i]['last_modified'] < state_a[j]['last_modified']:
                            self.class_b.copy_from(self.class_a, state_a[i]['path'])
                        else:
                            self.class_a.copy_from(self.class_b, state_b[i]['path'])
        (state_a, previous_state_a) = self.class_a.create_state()
        (state_b, previous_state_b) = self.class_b.create_state()
        state_a = remove_dictionary_key(state_a, 'last_modified')
        state_b = remove_dictionary_key(state_b, 'last_modified')
        print(state_a)
        print(state_b)
        print('')
        for i in range(max(len(state_a), len(state_b))):
            if i < len(state_a) and state_a[i] not in state_b:
                self.class_b.copy_from(self.class_a, state_a[i]['path'])
            if i < len(state_b) and state_b[i] not in state_a:
                self.class_a.copy_from(self.class_b, state_b[i]['path'])
    def update(self):
        print('UPDATE')
        (state_a, previous_state_a) = self.class_a.create_state()
        print('a', state_a)
        print(previous_state_a)
        print()
        # check for differences between the current and previous states
        modified = False
        for element_b in previous_state_a:
            for element_a in state_a:
                if element_a['path'] == element_b['path'] and element_b['is_directory'] == element_a['is_directory']:
                    if element_a['last_modified'] > element_b['last_modified']:
                        self.class_b.copy_from(self.class_a, element_a['path'])
                        modified = True
                # new file added
                elif element_a not in previous_state_a:
                    self.class_b.copy_from(self.class_a, element_a['path'])
                    modified = True
            # file removed
            if element_b not in state_a and len(previous_state_a) != len(state_a):
                self.class_b.delete(element_b['path'])
                modified = True
            if modified:
                break
        (state_b, previous_state_b) = self.class_b.create_state()
        print('b', state_b)
        print(previous_state_b)
        print()
        if modified:
            print('REFRESH')
            self.update()
            return;
        modified = False
        # check for differences between the current and previous states
        for element_b in previous_state_b:
            for element_a in state_b:
                if element_a['path'] == element_b['path'] and element_b['is_directory'] == element_a['is_directory']:
                    if element_a['last_modified'] > element_b['last_modified']:
                        self.class_a.copy_from(self.class_b, element_a['path'])
                        modified = True
                # new file added
                elif element_a not in previous_state_b:
                    self.class_a.copy_from(self.class_b, element_a['path'])
                    modified = True
            # file removed
            if element_b not in state_b and len(previous_state_b) != len(state_b):
                self.class_a.delete(element_b['path'])
                modified = True
            if modified:
                break
        if modified:
            print('REFRESH')
            self.class_a.create_state()
            self.update()