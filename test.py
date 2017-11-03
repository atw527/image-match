import os

dirs = next(os.walk('data/frames'))[1]
dir_list = "'" + "', '".join(dirs) + "'"

print dir_list
