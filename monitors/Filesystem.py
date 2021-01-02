"""
Class for managing the filesystem mode
"""
import math
import re
from os import mkdir, path, remove, walk
from shutil import rmtree
import sys
import hashlib

from StateManager import StateManager
from utils import create_hash, handle_failure


def log(*content):
    """
    Logging function used for console logging
    :param content: - The content that needs to be logged to the console
    :return:
    """
    print('[FILESYSTEM] ', *content)


class Filesystem:
    """
    Handles filesystem files
    """

    def __init__(self, target_path):
        self.state_manager = StateManager()
        if target_path[-1] != path.sep:
            target_path = target_path + path.sep
        self.path = target_path

    @staticmethod
    def selector_matches(selector):
        """
        Checks if the specified selector is in the right format
        :param selector: Mode selection string
        :return: True if the specified string is in the correct format
        """
        regex = r"folder:(.*)"
        x = re.match(regex, selector)
        if not x:
            return None
        return x.group(1)

    @handle_failure(log)
    def create_state(self):
        """
        Creates a state of the files
        :return: Tuple of the current state and the previous state
        """
        # set current state for class_a
        state = []
        file_list = list(
            walk(
                self.path))
        for (
                index, (dirname, _, filenames)) in enumerate(
                file_list):
            dirname = dirname.replace(self.path, '')

            if index > 0:
                state.append({'path': dirname, 'is_directory': True})
            for filename in filenames:
                path_with_file = path.join(dirname, filename)
                state.append(
                    {
                        'path': path_with_file,
                        'is_directory': False,
                        'size': self.get_file_size(path_with_file),
                        'last_modified': self.get_last_modified_time(
                            path.join(
                                self.path,
                                path_with_file))})
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(
        ), self.state_manager.get_previous_state()

  
    @handle_failure(log)
    def read(self, filename):
        """
        Read the contents of a file
        :param filename: File path
        :return: The contents of the specified file
        """
        filename = path.normpath(self.path + filename)
        log('Reading ', filename)
        f = open(filename, "rb")
        content = f.read()
        f.close()
        return content

    @handle_failure(log)
    def is_directory(self, filename):
        """
        Checks to see whether the file specified is a directory
        :param filename: File path
        :return: True if the specified file is a directory
        """
        filename = path.normpath(self.path + filename)
        return path.isdir(filename)
    
    @handle_failure(log)
    def get_last_modified_time(self, filepath):
        return math.floor(path.getmtime(path.abspath(filepath)) / 2)
    
    @handle_failure(log)
    def create_directory(self, filename):
        """
        Create a new directory
        :param filename: Directory path
        """
        filename = path.normpath(self.path + filename)
        mkdir(filename)

    @handle_failure(log)
    def delete(self, filename):
        """
        Delete a file or directory
        :param filename: File pth to be deleted
        """
        file = path.abspath(path.normpath(self.path + filename + path.sep))
        log('Delete from ', file, self.is_directory(filename))
        if self.is_directory(filename):
            rmtree(file)
        else:
            remove(file)

    @handle_failure(log)
    def copy_from(self, class_b, filename):
        """
        Copy filename from class_b
        :param class_b: Class instance that will provide the contents of the file
        :param filename: File path
        """
        target_path = filename
        from_path = filename
        log('reading ', from_path, 'from class b',
            class_b.is_directory(from_path))
        if class_b.is_directory(from_path):
            log('Create dir from ', from_path, 'to', target_path)
            self.create_directory(target_path)
        else:
            log('Copy from ', from_path, 'to',
                path.normpath(self.path + target_path))
            contents = class_b.read(from_path)
            f = open(path.normpath(self.path + target_path), 'wb')
            f.write(contents)
            f.close()
    def create_file_hash(self, filename):
      return create_hash(path.join(self.path, filename))
    def get_file_size(self, filename):
        return path.getsize(path.normpath(self.path + filename))