from os import walk, path, mkdir, remove, rmdir
import math
from StateManager import StateManager
from ftplib import FTP


def log(*content):
    print('[FTP] ', *content)


class Ftp:
    def __init__(self, path):
        ftp = FTP('localhost')
        ftp.login(user="alex", passwd="1324")
        self.ftp = ftp
        self.state_manager = StateManager()
        self.path = path

    def listdir(self, _path):
        """
        return files and directory names within a path (directory)
        """

        file_list, dirs, nondirs = [], [], []
        try:
            self.ftp.cwd(_path[1:])
        except Exception as exp:
            print("the current path is : ",
                  self.ftp.pwd(), exp.__str__(), _path[1:])
            return [], []
        else:
            self.ftp.retrlines(
                'LIST', lambda x: file_list.append(x.split()))
            for info in file_list:
                ls_type, name = info[0], info[-1]
                if ls_type.startswith('d'):
                    dirs.append(name)
                else:
                    nondirs.append(name)
            return dirs, nondirs

    def walk(self, filepath='/'):
        """
        Walk through FTP server's directory tree, based on a BFS algorithm.
        """
        dirs, nondirs = self.listdir(filepath)
        yield filepath, dirs, nondirs
        for name in dirs:
            filepath = path.join(filepath + '/' + name)
            yield from self.walk(filepath)
            self.ftp.cwd('..')
            filepath = path.dirname(filepath)

    def create_state(self):
        # set current state for class_a
        state = []
        for (index, (dirname, dirnames, filenames)) in enumerate(list(walk(self.path))):
            dirname = dirname.replace(self.path, '')
            real_path = path.normpath(self.path + dirname)

            if index > 0:
                state.append({'path': dirname, 'is_directory': True,
                              'last_modified': self.get_last_modified_time(real_path)})
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
        log('Copy from ', from_path, 'to', target_path)
        if class_b.is_directory(from_path):
            self.create_directory(target_path)
        else:
            contents = class_b.read(from_path)
            f = open(target_path, 'w')
            f.write(contents)
            f.close()
