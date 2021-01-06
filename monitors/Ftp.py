"""
Class for managing the ftp mode
"""
import datetime
import hashlib
import math
import re
from ftplib import FTP
from io import BytesIO, StringIO
from os import mkdir, path, remove, rmdir, walk

from StateManager import StateManager
from utils import handle_failure, retry_function


def log(*content):
    """
    Logging function used for console logging
    :param content: - The content that needs to be logged to the console
    :return:
    """
    print('[FTP] ', *content)


class Ftp:
    """
    Handles ftp files
    """

    def __init__(self, username, password, host, path):
        ftp = FTP(host)
        try:
            ftp.login(user=username, passwd=password)
        except:
            log('Incorrect credentials')
            exit()

        log('Connected to {} with username {} and password {} on path {}'.format(
            host, username, password, path))
        self.ftp = ftp
        self.state_manager = StateManager()
        self.path = path

    @staticmethod
    def selector_matches(selector):
        """
        Checks if the specified selector is in the right format
        :param selector: Mode selection string
        :return: True if the specified string is in the correct format
        """
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
                ls_type, name, size = info[0], ' '.join(info[8:]), info[4]
                if ls_type.startswith('d'):
                    dirs.append(name)
                else:
                    modification_time = self.parse_ftp_date(self.ftp.voidcmd(
                        f"MDTM " + name).split()[-1])
                    
                    nondirs.append(
                        (name, modification_time, int(size)))
            return dirs, nondirs

    @handle_failure(log)
    def walk(self, filepath=path.sep):
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

    def generate_filedata(self):
        state = []
        files = list(
            self.walk(
                self.path))
        for (
                index, (dirname, _, filenames)) in enumerate(
                files):
            dirname = dirname.replace(self.path, '')

            # ignore the first directory
            if index > 0:
                state.append({'path': dirname, 'is_directory': True})
            for (filename, last_modified, size) in filenames:
                path_with_file = path.join(dirname, filename)
                state.append({'path': path_with_file, 'is_directory': False,
                              'last_modified': last_modified, 'size': size})
        return state
    @handle_failure(log)
    def create_state(self):
        """
        Creates a state of the files
        :return: Tuple of the current state and the previous state
        """
        state = self.generate_filedata()
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(
        ), self.state_manager.get_previous_state()

    @handle_failure(log)
    @retry_function(2)
    def parse_ftp_date(self, date_string):
        """
        Parse a date string
        :param date_string: Date string
        :return: Date timestamp
        """
        date_time_obj = datetime.datetime.strptime(
            date_string, '%Y%m%d%H%M%S')
        return math.floor(date_time_obj.timestamp() / 2)

    @handle_failure(log)
    @retry_function(2)
    def read(self, filepath):
        """
        Read the contents of a file
        :param filepath: File path
        :return: The contents of the specified file
        """
        directory_name, file_name = path.split(
            path.normpath(self.path + filepath))
        r = BytesIO()
        self.ftp.cwd(directory_name)
        self.ftp.retrbinary(
            'RETR ' +
            path.join(
                directory_name,
                file_name),
            r.write)
        self.ftp.cwd(self.path)

        contents = r.getvalue()
        return contents

    @handle_failure(log)
    @retry_function(2)
    def file_exists(self, filepath):
        """
        Check the existence of a file
        :param filename: File path
        :return: True if the file exists
        """
        files = self.generate_filedata()
        for file in files:
            if filepath == file['path']:
                return True
        return False
    @handle_failure(log)
    @retry_function(2)
    def create_directory(self, filename):
        """
        Create a new directory
        :param filename: Directory path
        """
        log('Create directory ', filename)
        try:
            self.ftp.mkd(filename)
        except Exception:
            # silent fail, directory already exists
            return

    @handle_failure(log)
    @retry_function(2)
    def delete(self, filename):
        """
       Delete a file or directory
       :param filename: File pth to be deleted
       """
        if self.is_directory(filename):
            return self.ftp.rmd(filename)
        return self.ftp.delete(filename)

    @handle_failure(log)
    def is_directory(self, filename):
        """
        Checks to see whether the file specified is a directory
        :param filename: File path
        :return: True if the specified file is a directory
        """
        current_state = self.state_manager.get_current_state()
        for item in current_state:
            if item['path'] == filename:
                return item['is_directory']

    @handle_failure(log)
    @retry_function(2)
    def write(self, filename, content):
        """
        Write contents to a file
        :param filename: File path
        :param content: Content to be written
        """
        bio = BytesIO(content)
        directory_name, file_name = path.split(
            path.join(self.path,filename))
        self.ftp.cwd(directory_name)
        log('Writing', content, ' to', directory_name)

        self.ftp.storbinary('STOR ' + file_name, bio)

    @handle_failure(log)
    @retry_function(2)
    def copy_from(self, class_b, filename):
        """
        Copy filename from class_b
        :param class_b: Class instance that will provide the contents of the file
        :param filename: File path
        """
        target_path = filename
        from_path = filename

        if target_path[0] == path.sep:
            target_path = '.' + target_path
        log('Copy', path.join(class_b.path, from_path), 'to', path.join(self.path, target_path))
        
        if class_b.is_directory(from_path):
            self.create_directory(target_path)
        else:
            self.write(target_path, class_b.read(from_path))
    
    @handle_failure(log)
    @retry_function(2)
    def create_file_hash(self, filename):
        """
        create a hash of a file
        """
        m = hashlib.sha1()
        self.ftp.retrbinary('RETR ' + self.path + filename, m.update)
        return m.hexdigest()
