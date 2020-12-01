from os import walk, path, mkdir, remove, rmdir, rename
import math
from StateManager import StateManager
from zipfile import ZipFile, ZipInfo
import datetime
import ntpath
import re


def log(*content):
    print('[ZIP] ', *content)


class Zip:
    def __init__(self, path):
        self.state_manager = StateManager()
        self.path = path
        self.zip_r = None
        self.zip_w = None
        self.open_read()
        self.open_write()

    @staticmethod
    def selector_matches(selector):
        regex = r"zip:(.*)$"
        x = re.match(regex, selector)
        if not x:
            return None
        return x.group(1)

    def open_read(self):
        if self.zip_r:
            self.zip_r.close()
        self.zip_r = ZipFile(self.path, 'r')

    def open_write(self):
        if self.zip_w:
            self.zip_w.close()
        self.zip_w = ZipFile(self.path, 'a')

    def create_state(self):
        self.open_read()

        name_list = self.zip_r.namelist()
        # set current state for class_a
        state = []
        for file in name_list:
            info = self.zip_r.getinfo(file)
            if info.is_dir():
                state.append({'path': file[0:-1], 'is_directory': True})
            else:
                state.append({'path': file, 'is_directory': False,
                              'last_modified': self.get_last_modified_time(info)})
        # add top level folder
        if len(name_list) > 0 and name_list[0].split('/')[0] + '/' not in name_list:
            state.insert(0, {'path':   name_list[0].split(
                '/')[0][0:-1], 'is_directory': True})
        self.state_manager.set_state(state)
        return self.state_manager.get_current_state(), self.state_manager.get_previous_state()

    def get_last_modified_time(self, zip_info):
        # (year, month, day, hour, minute, second) = zip_info.date_time
        date_string = ''
        for item in zip_info.date_time:
            date_string = date_string + str(item)
        date_time_obj = datetime.datetime.strptime(date_string, '%Y%m%d%H%M%S')
        return math.floor(date_time_obj.timestamp())

    def read(self, filename):
        for item in self.zip_r.infolist():
            if (item.filename == filename):
                return self.zip_r.read(item.filename).decode('utf-8')

    def is_directory(self, filename):
        current_state = self.state_manager.get_current_state()
        for item in current_state:
            if item['path'] == filename:
                return item['is_directory']

    def create_directory(self, filename):
        zfi = ZipInfo(filename + '/')
        self.zip_w.writestr(zfi, '')
        log('Creating directory', filename)
        self.open_read()
        self.open_write()

    def delete(self, filename):
        log("Delete ", filename)
        zout = ZipFile('./temp.zip', 'w')
        for item in self.zip_r.infolist():
            buff = self.zip_r.read(item.filename)
            if item.filename != filename and item.filename != filename + '/':
                zout.writestr(item, buff)
        zout.close()
        rename("./temp.zip",
               self.path)
        self.open_read()

    def write(self, filename, content):
        zout = ZipFile('./temp.zip', 'w')
        did_write = False
        for item in self.zip_r.infolist():
            buff = self.zip_r.read(item.filename)
            if (item.filename == filename):
                zout.writestr(item, content)
                did_write = True
            else:
                zout.writestr(item, buff)
        if not did_write:
            zout.writestr(filename, content)
        zout.close()
        rename("./temp.zip",
               self.path)
        self.open_read()

    def copy_from(self, class_b, filename):
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
