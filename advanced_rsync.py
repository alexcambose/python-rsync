from Syncer import Syncer
import sys
from time import sleep

from monitors.Filesystem import Filesystem
from monitors.Ftp import Ftp
from monitors.Zip import Zip
# check number of arguments
if len(sys.argv) < 3:
    print("Invalid number of arguments")
    exit()

# array that will hold the handlers instance
instances = [None, None]

params = sys.argv[1:]
# maximum 2
for i in range(0, 2):
    match = Ftp.selector_matches(params[i])
    if match:
        instances[i] = Ftp(match['user'], match['password'],
                           match['host'], match['path'])
        continue
    match = Filesystem.selector_matches(params[i])
    if match:
        instances[i] = Filesystem(match)
        continue
    match = Zip.selector_matches(params[i])
    if match:
        instances[i] = Zip(match)
        continue
    raise Exception(params[i] + ' is not a valid location')

# initialise syncer
syncer = Syncer(instances[0], instances[1])
# file changes via polling
while True:
    print('===============================================================================')
    sleep(3)
    syncer.update()
# print(instances[1].read('aa'))
