from os import walk, path, mkdir, remove, rmdir
import math
from StateManager import StateManager
from zipfile import ZipFile, ZipInfo
import datetime


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

    def open_read(self):
        if self.zip_r:
            self.zip_r.close()
        self.zip_r = ZipFile(self.path, 'r')

    def open_write(self):
        if self.zip_w:
            self.zip_w.close()
        self.zip_w = ZipFile(self.path, 'a')

    def create_state(self):
        # set current state for class_a
        state = []
        for file in self.zip_r.namelist():
            info = self.zip_r.getinfo(file)
            if info.is_dir():
                state.append({'path': file, 'is_directory': True})
            else:
                state.append({'path': file, 'is_directory': False,
                              'last_modified': self.get_last_modified_time(info)})
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
        filename = path.normpath(self.path + filename)
        print(filename)
        f = open(filename, "r")
        content = f.read()
        f.close()
        return content

    def is_directory(self, filename):
        filename = path.normpath(self.path + filename)
        return path.isdir(filename)

    def create_directory(self, filename):
        zfi = ZipInfo(filename)
        self.zip_w.writestr(zfi, '')
        self.open_read()
        self.open_write()

    def delete(self, filename):
        zout = ZipFile(path, 'w')
        for item in self.zip_r.infolist():
            buff = self.zip_r.read(item.filename)
            print(buff)
            if (item.filename != filename):
                zout.writestr(item, buff)
        zout.close()
        self.open_read()

    def copy_from(self, class_b, filename):
        target_path = filename
        from_path = filename
        if class_b.is_directory(from_path):
            log('Copy from ', from_path, 'to', target_path)
            self.create_directory(target_path)
        else:
            log('Copy from ', from_path, 'to',
                path.normpath(self.path + target_path))
            contents = class_b.read(from_path)
            f = open(path.normpath(self.path + target_path), 'w')
            f.write(contents)
            f.close()
