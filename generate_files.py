from os import path, utime, stat
from random import randrange


def create_file(file_path, filename):
    f = open(path.join(file_path, filename), "w")
    f.close()


def change_modification_time(file_path, filename, mtime):
    filename = path.join(file_path, filename)
    atime = stat(filename).st_atime
    utime(filename, (atime, mtime))


def change_file_contents(file_path, filename, contents):
    file = path.join(file_path, filename)
    mtime = stat(file).st_mtime
    print("Set content to '{}'".format(contents))
    f = open(file, "w")
    f.write(contents)
    f.close()
    change_modification_time(file_path, filename, mtime)


def change_file_size(file_path, filename):
    file = path.join(file_path, filename)
    mtime = stat(file).st_mtime
    f = open(file, "w")
    f.write(str(randrange(10)) * randrange(100))
    f.close()
    change_modification_time(file_path, filename, mtime)


location_a = './test/a'
location_b = './test/b'

# change_modification_time(location_a, 'fisier', 123)
change_file_contents(location_a, 'fisier', 'test' + str(randrange(8)))
# change_file_size(location_b, 'fisier')
