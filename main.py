from Syncer import Syncer
import sys

# if len(sys.argv) < 3:
#     print("Invalid number of arguments")
from time import sleep

from monitors.Filesystem import Filesystem
from monitors.Ftp import Ftp

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
fs2 = Ftp(locationB)
# syncer = Syncer(fs1, fs2)
# while 1:
#     sleep(2)
#     syncer.update()

print(list(fs2.walk('./Desktop/python-rsync/test')))
