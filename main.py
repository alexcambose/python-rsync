from Syncer import Syncer
import sys

# if len(sys.argv) < 3:
#     print("Invalid number of arguments")
from time import sleep

from monitors.Filesystem import Filesystem
from monitors.Ftp import Ftp
from monitors.Zip import Zip

locationA = sys.argv[1]
locationB = sys.argv[2]

ftpRegex = "ftp:(?<user>\S*):(?<passwd>[\S^]+)@(?<url>\S+)\/(?<path>.*)"

# def filesystemData():
# previousState = []
# currentState = []

#     previousState = deepcopy(currentState)
#     currentState = []
#     for (dirpath, dirnames, filenames) in walk("./"):
#         for filename in filenames:
#             currentState.append((dirpath + filename))
#     print(currentState, previousState)
#     for fileCurrentState in currentState:
#         if fileCurrentState not in previousState:
#             print('Delete occured')
#
#
fs1 = Filesystem(locationA)
# fs2 = Filesystem(locationB)
# fs2 = Ftp('./Desktop/python-rsync/test/dirb/')
# syncer = Syncer(fs1, fs2)
# while 1:
#     sleep(2)
#     syncer.update()

fs3 = Zip('./test/dira.zip')
# fs3.create_directory('test1/')
# fs3.create_directory('te3st2/')`
fs3.delete('test1/')
print(fs3.create_state())
