import datetime
from os import walk, path, mkdir, remove, rmdir
import math
from utils import handle_failure
from StateManager import StateManager
from ftplib import FTP
from io import StringIO, BytesIO
import re


def log(*content):
    print('[FTP] ', *content)


class Ftp:
    def __init__(self, username, password, host, path):
        ftp = FTP(host)
        ftp.login(user=username, passwd=password)
        log('Connected to {} with username {} and password {} on path {}'.format(
            host, username, password, path))
        self.ftp = ftp
        self.state_manager = StateManager()
        self.path = path

    @staticmethod
    def selector_matches(selector):
        regex = r"ftp:(\S*):([\S]+)@([\S^.]+?)([~.\/].*)"
        x = re.search(regex, selector)
        if not x:
            return None
        return {
            "user": x.group(1),
            "password": x.group(2),
            "host": x.group(3),
            "path": x.group(4),
        }
    
    @handle_failure(log)
    def listdir(self, _path):
        """
        return files and directory names within a path (directory)
        """

        file_list, dirs, nondirs = [], [], []
        try:
            self.ftp.cwd(_path)
        except Exception as exp:
            log("the current path is : ",
                self.ftp.pwd(), exp.__str__(), _path)
            return [], []
        else:

            self.ftp.retrlines(
                'LIST', lambda x: file_list.append(x.split()))
            # parse each file info result
            for info in file_list:
                ls_type, name = info[0], info[-1]
                if ls_type.startswith('d'):
                    dirs.append(name)
                else:
                    modification_time = self.parse_ftp_date(self.ftp.voidcmd(
                        f"MDTM " + name).split()[-1])
                    nondirs.append(
                        (name, modification_time))
            return dirs, nondirs
    
    @handle_failure(log)
    def walk(self, filepath='/'):
        """
        Walk through FTP server's directory tree
        """
        dirs, nondirs = self.listdir(filepath)
        yield filepath, dirs, nondirs
        for name in dirs:
            filepath = path.join(filepath, name)
            yield from self.walk(filepath)
            self.ftp.cwd('..')
            filepath = path.dirname(filepath)
    
    @handle_failure(log)
    def create_state(self):
        state = []
        files = list(
                self.walk(
                self.path))
        for (
            index, (dirname, dirnames, filenames)) in enumerate(
           files ):
            dirname = dirname.replace(self.path, '')
            real_path = path.normpath(self.path + dirname)

            # ignore the first directory
            if index > 0:
                state.append({'path': dirname, 'is_directory': True})
            for (filename, last_modified) in filenames:
                path_with_file = path.join(dirname, filename)
                state.append({'path': path_with_file, 'is_directory': False,
                              'last_modified': last_modified})
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(
        ), self.state_manager.get_previous_state()
    
    @handle_failure(log)
    def parse_ftp_date(self, date_string):
        date_time_obj = datetime.datetime.strptime(
            date_string, '%Y%m%d%H%M%S')
        return math.floor(date_time_obj.timestamp() / 10)
    
    @handle_failure(log)
    def read(self, filename):
        r = StringIO()
        # self.ftp.cwd('/')
        return r.getvalue()
    
    @handle_failure(log)
    def create_directory(self, currentDir):
        log('Create directory ', currentDir)
        try:
            self.ftp.mkd(currentDir)
        except:
            # silent fail, directory already exists
            return
    
    @handle_failure(log)
    def delete(self, filename):
        if self.is_directory(filename):
            return self.ftp.rmd(filename)
        return self.ftp.delete(filename)
    
    @handle_failure(log)
    def is_directory(self, filename):
        current_state = self.state_manager.get_current_state()
        filename = path.join('/', filename)
        print(filename)
        for item in current_state:
            if item['path'] == filename:
                return item['is_directory']
    
    @handle_failure(log)
    def write(self, filename, content):
        bio = BytesIO(content)
        self.ftp.storbinary('STOR ' + filename, bio)
    
    @handle_failure(log)
    def copy_from(self, class_b, filename):
        target_path = filename
        from_path = filename
        print(filename)
        if target_path[0] == '/':
            target_path = '.' + target_path
        if class_b.is_directory(from_path):
            log('Copy from ', from_path, 'to', target_path)
            self.create_directory(target_path)
        else:
            log('Copy ', class_b.read(from_path),
                ' from ', from_path, 'to', target_path)
            self.write(target_path, class_b.read(from_path))
