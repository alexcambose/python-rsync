import sys

# if len(sys.argv) < 3:
#     print("Invalid number of arguments")
from monitors.Filesystem import Filesystem

locationA = sys.argv[1]
locationB = sys.argv[2]
from Syncer import Syncer

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
fs2 = Filesystem(locationB)
syncer = Syncer(fs1, fs2)
# while 1:
#     sleep(3)
#     syncer.run_sync()