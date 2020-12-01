from Syncer import Syncer
import sys
from time import sleep

from monitors.Filesystem import Filesystem
from monitors.Ftp import Ftp
from monitors.Zip import Zip

if len(sys.argv) < 3:
    print("Invalid number of arguments")


instances = [None, None]
params = sys.argv[1:]
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

syncer = Syncer(instances[0], instances[1])
while True:
    sleep(2)
    syncer.update()
