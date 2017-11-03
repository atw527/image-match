#!/bin/bash

# sync meta files to front server to it knows which videos are available (should improve this)
rsync data/video/*.json andrew@a01-docker-01:/home/andrew/go/src/github.com/atw527/image-match/data/video/
rsync data/video/*.description andrew@a01-docker-01:/home/andrew/go/src/github.com/atw527/image-match/data/video/
rsync data/video/*.jpg andrew@a01-docker-01:/home/andrew/go/src/github.com/atw527/image-match/data/video/
