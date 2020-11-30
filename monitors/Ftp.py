import datetime
from os import walk, path, mkdir, remove, rmdir
import math
from StateManager import StateManager
from ftplib import FTP
from io import StringIO, BytesIO


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
                    nondirs.append(
                        (name, self.parse_ftp_date(self.ftp.voidcmd(f"MDTM " + name).split()[-1])))
            return dirs, nondirs

    def walk(self, filepath='/'):
        """
        Walk through FTP server's directory tree, based on a BFS algorithm.
        """
        dirs, nondirs = self.listdir(filepath)
        yield filepath, dirs, nondirs
        for name in dirs:
            filepath = path.join(filepath + name)
            yield from self.walk(filepath)
            self.ftp.cwd('..')
            filepath = path.dirname(filepath)

    def create_state(self):
        # set current state for class_a
        state = []
        for (index, (dirname, dirnames, filenames)) in enumerate(list(self.walk(self.path))):
            dirname = dirname.replace(self.path, '')
            real_path = path.normpath(self.path + dirname)

            if index > 0:
                state.append({'path': dirname, 'is_directory': True})
            for (filename, last_modified) in filenames:
                path_with_file = path.join(dirname, filename)
                state.append({'path': path_with_file, 'is_directory': False,
                              'last_modified': last_modified})
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(), self.state_manager.get_previous_state()

    def parse_ftp_date(self, date_string):
        date_time_obj = datetime.datetime.strptime(
            date_string, '%Y%m%d%H%M%S')
        return math.floor(date_time_obj.timestamp() / 10)

    def read(self, filename):
        r = StringIO()
        self.ftp.cwd('/')

        print(self.ftp.retrlines('RETR .' + self.path + filename, r.write))
        return r.getvalue()

    def create_directory(self, currentDir):
        log('Create directory ', currentDir)
        self.ftp.mkd(currentDir)

    def delete(self, filename):
        if self.is_directory(filename):
            return self.ftp.rmd(filename)
        return self.ftp.delete(filename)

    def is_directory(self, filename):
        current_state = self.state_manager.get_current_state()
        filename = path.join('/', filename)
        print(filename)
        for item in current_state:
            if item['path'] == filename:
                return item['is_directory']

    def copy_from(self, class_b, filename):
        target_path = filename
        from_path = filename
        if class_b.is_directory(from_path):
            log('Copy from ', from_path, 'to', target_path)
            self.create_directory(target_path)
        else:
            log('Copy ', class_b.read(from_path),
                ' from ', from_path, 'to', target_path)
            bio = BytesIO(class_b.read(from_path).encode('utf-8'))
            self.ftp.storbinary('STOR ' + filename, bio)
