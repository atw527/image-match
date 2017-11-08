
import os
import re
import sys
import os.path
import commands

video_id = "a3D8bLacGHA"

# dedup
print "[{0}] Running dedup...".format(video_id)

os.chdir("frames/{0}".format(video_id))
frames = sorted(os.listdir("."))

for x in range(0, len(frames) - 1):
    for y in range(x + 1, len(frames)):
        print x, y
        try:
            # subprocess.run?
            (return_val, output) = commands.getstatusoutput("compare -metric RMSE {0} {1} NULL: 2>&1".format(frames[x], frames[y]))
            diff = int(re.search('[0-9]+', output).group())

            print "compare -metric RMSE {0} {1} NULL: 2>&1".format(frames[x], frames[y]), output,  diff

            if diff < 5000 and diff != 0:
                # frame is similar enough to remove
                print "del frames/{0}.jpg".format(frames[y])
            else:
                # frame has changed, set this as the new starting point
                x = y
                print "frames different"
                break
        except Exception, e:
            print str(e)
            print "exception"
            continue
