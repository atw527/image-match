
video_id = ruZ2v27KHCE

# dedup
print "[{0}] Running dedup...".format(video_id)
frames = os.listdir("frames/{0}".format(video_id))

for x in range(0, len(frames) - 1):
    for y in range(x + 1, len(frames)):
        try:
            output = subprocess.check_output("compare -metric RMSE {0} {1} NULL: 2>&1".format(frames[x], frames[y]), shell=True)
            diff = int(re.search('[0-9]+', output).group())

            print "compare -metric RMSE {0} {1} NULL: 2>&1".format(frames[x], frames[y]), output,  diff

            if diff < 5000 and diff != 0:
                # frame is similar enough to remove
                print "del frames/{0}.jpg".format(frames[y]))
            else:
                # frame has changed, set this as the new starting point
                x = y
                print "frames different"
                break
        except Exception, e:
            print "exception"
            continue
