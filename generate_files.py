from os import path, utime, stat

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
  f = open(file, "w")
  f.write(contents)
  f.close()
  change_modification_time(file_path, filename, mtime)


location_a = './test/a'
location_b = './test/b'
# create a file in both locations

# create_file(location_a, 'fisier');
change_modification_time(location_a, 'fisier', 123)
change_modification_time(location_b, 'fisier', 123)
# create_file(location_b, 'fisier');

change_file_contents(location_a, 'fisier', '1113');
change_file_contents(location_b, 'fisier', '1111');