from os import walk, path, mkdir, remove, rmdir
import math
from StateManager import StateManager


def log(*content):
    print('[FILESYSTEM] ', *content)

class Filesystem:
    def __init__(self, path):
        self.state_manager = StateManager()
        self.path = path

    def create_state(self):
        # set current state for class_a
        state = []
        for (index, (dirname, dirnames, filenames)) in enumerate(list(walk(self.path))):
            dirname = dirname.replace(self.path, '')
            real_path = path.normpath(self.path + dirname)

            if index > 0:
                state.append({'path': dirname, 'is_directory': True, 'last_modified': self.get_last_modified_time(real_path)})
            for filename in filenames:
                path_with_file = path.join(dirname, filename)
                state.append({'path': path_with_file, 'is_directory': False,
                              'last_modified': self.get_last_modified_time(path.join(self.path, path_with_file))})
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(), self.state_manager.get_previous_state()

    def get_last_modified_time(self, filepath):
        return math.floor(path.getmtime(path.abspath(filepath)) / 10)

    def read(self, filename):
        f = open(filename, "r")
        content = f.read()
        f.close()
        return content

    def is_directory(self, filename):
        return path.isdir(filename)

    def create_directory(self, filename):
        return mkdir(filename)

    def delete(self, filename):
        filename = path.normpath(self.path + filename)
        log('Delete from ', filename)
        if self.is_directory(filename):
            return rmdir(filename)
        return remove(filename)

    def copy_from(self, class_b, filename):
        target_path = path.normpath(self.path + filename)
        from_path = path.normpath(class_b.path + filename)
        log('Copy from ',from_path, 'to', target_path)
        if class_b.is_directory(from_path):
            self.create_directory(target_path)
        else:
            contents = class_b.read(from_path)
            f = open(target_path, 'w')
            f.write(contents)
            f.close()
