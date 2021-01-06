"""
Class for managing the zip mode
    """
import datetime
import math
import ntpath
import re
import tempfile
from os import mkdir, name, path, remove, rename, rmdir, walk
from pathlib import Path
from zipfile import ZipFile, ZipInfo

from StateManager import StateManager
from utils import create_hash, handle_failure


def log(*content):
    """
    Logging function used for console logging
    :param content: - The content that needs to be logged to the console
    :return:
    """
    print('[ZIP] ', *content)


class Zip:
    """
    Handles zip files
    """

    def __init__(self, path):
        self.state_manager = StateManager()
        self.path = path
        self.zip_r = None
        self.zip_w = None
        self.open_read()
        self.open_write()

    @staticmethod
    def selector_matches(selector):
        """
        Checks if the specified selector is in the right format
        :param selector: Mode selection string
        :return: True if the specified string is in the correct format
        """
        regex = r"zip:(.*)$"
        x = re.match(regex, selector)
        if not x:
            return None
        return x.group(1)

    @handle_failure(log)
    def open_read(self):
        """
        Open a zip file in read mode
        :return:
        """
        if self.zip_r:
            self.zip_r.close()
        self.zip_r = ZipFile(self.path, 'r')

    @handle_failure(log)
    def open_write(self):
        """
        Open a zip file in write mode
        :return:
        """
        if self.zip_w:
            self.zip_w.close()
        self.zip_w = ZipFile(self.path, 'a')

    @handle_failure(log)
    def create_state(self):
        """
        Creates a state of the files
        :return: Tuple of the current state and the previous state
        """
        state = []
        self.open_read()

        name_list = self.zip_r.namelist()
        # add nested folders if they doesn't exist
        for file in name_list:
            folder_path = str(Path(file).parent) + path.sep
            if folder_path not in name_list and not self.zip_r.getinfo(
                    file).is_dir() and folder_path != '.' + path.sep:
                state.append({'path': folder_path[:-1], 'is_directory': True})
        # set current state for class_a
        for file in name_list:
            info = self.zip_r.getinfo(file)
            if info.is_dir():
                state.append({'path': file[:-1], 'is_directory': True})
            else:
                state.append(
                    {'path': file, 'is_directory': False,'size': info.file_size,
                     'last_modified': self.get_last_modified_time(info)})
        # # add top level folder
        # if len(name_list) > 0 and name_list[0].split(path.sep)[0] + path.sep not in name_list:
        #     state.insert(0, {'path':   name_list[0].split(
        #         path.sep)[0], 'is_directory': True})
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(
        ), self.state_manager.get_previous_state()

    @handle_failure(log)
    def get_last_modified_time(self, zip_info):
        """
        Get the last modified time
        :param zip_info: ZipInfo object
        :return: Last modified time
        """
        # (year, month, day, hour, minute, second) = zip_info.date_time
        date_string = ''
        for item in zip_info.date_time:
            date_string = date_string + str(item)
        date_time_obj = datetime.datetime.strptime(date_string, '%Y%m%d%H%M%S')
        return math.floor(date_time_obj.timestamp() / 2)

    @handle_failure(log)
    def read(self, filename):
        """
        Read the contents of a file
        :param filename: File path
        :return: The contents of the specified file
        """
        for item in self.zip_r.infolist():
            if item.filename == filename:
                return self.zip_r.read(item.filename)

    @handle_failure(log)
    def file_exists(self, filename):
        """
        Check the existence of a file
        :param filename: File path
        :return: True if the file exists
        """
        for item in self.zip_r.infolist():
            if item.filename == filename:
                return True
        return False

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
    def create_directory(self, filename):
        """
        Create a new directory
        :param filename: Directory path
        """
        zfi = ZipInfo(filename + path.sep)
        self.zip_w.writestr(zfi, '')
        log('Creating directory', filename)
        self.open_read()
        self.open_write()

    @handle_failure(log)
    def delete(self, filename):
        """
       Delete a file or directory
       :param filename: File pth to be deleted
       """
        is_directory = self.is_directory(filename)
        log("Delete ", is_directory, filename)
        zout = ZipFile('./temp.zip', 'w')
        for item in self.zip_r.infolist():
            buff = self.zip_r.read(item.filename)
            if item.filename != filename and (
                    is_directory and not item.filename.startswith(filename)):
                zout.writestr(item, buff)
        zout.close()
        rename("./temp.zip",
               self.path)
        self.open_read()

    @handle_failure(log)
    def write(self, filename, content):
        """
        Write contents to a file
        :param filename: File
        :param content: Contents to be written
        """

        # zout = ZipFile('./temp.zip', 'w')
        # did_write = False
        # for item in self.zip_r.infolist():
        #     buff = self.zip_r.read(item.filename)
        #     if item.filename == filename:
        #         zout.writestr(item, content)
        #         did_write = True
        #     else:
        #         zout.writestr(item, buff)
        # if not did_write:
        #     zout.writestr(filename, content)
        # zout.close()
        # rename("./temp.zip",
        #        self.path)
        # self.open_read()
        with ZipFile(self.path, 'w') as zipped_f:
            zipped_f.writestr(filename, content)
    @handle_failure(log)
    def copy_from(self, class_b, filename):
        """
        Copy filename from class_b
        :param class_b: Class instance that will provide the contents of the file
        :param filename: File path
        """
        target_path = filename
        from_path = filename
        if class_b.is_directory(from_path):
            log('Copy from ', from_path, 'to', target_path)
            self.create_directory(target_path)
        else:
            log('Copy from ', from_path, 'to',
                target_path)
            contents = class_b.read(from_path)
            self.write(filename, contents)
    def create_file_hash(self, filename):
        """
        create a hash of a file
        """
        with tempfile.TemporaryDirectory() as dirpath:
            tempfilename = path.join(dirpath, filename)
            with open(tempfilename, 'wb') as f:
                f.write(self.read(filename))
            return create_hash(tempfilename)