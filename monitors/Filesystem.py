from os import walk, path, mkdir
import math
from StateManager import StateManager


class Filesystem:
    def __init__(self, path):
        self.state_manager = StateManager()
        self.path = path

    def create_state(self):
        # set current state for class_a
        state = []
        for (index, (dirname, dirnames, filenames)) in enumerate(list(walk(self.path))):
            dirname = dirname.replace(self.path, '')
            real_path = path.join(self.path, dirname)
            if index > 0:
                state.append({'path': dirname, 'is_directory': True, 'last_modified': self.get_last_modified_time(real_path)})
            for filename in filenames:
                path_with_file = path.join(dirname, filename)
                state.append({'path': path_with_file, 'is_directory': False,
                              'last_modified': self.get_last_modified_time(path.join(self.path, path_with_file))})
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(), self.state_manager.get_previous_state()

    def get_last_modified_time(self, filepath):
        return math.floor(path.getmtime(path.abspath(filepath)) / 200)

    def read(self, filename):
        f = open(path.join(self.path, filename), "r")
        content = f.read()
        f.close()
        return content

    def is_directory(self, filename):
        return path.isdir(path.join(self.path, filename))

    def create_directory(self, filename):
        return mkdir(path.join(self.path, filename))

    def copy_from(self, class_b, filename):
        print('copy', filename, 'to', path.join(self.path, '../' + filename))
        if class_b.is_directory(filename):
            self.create_directory(filename)
        else:
            contents = class_b.read(filename)
            f = open(path.join(self.path, filename), 'w')
            f.write(contents)
            f.close()
