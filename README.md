# Download and Build Test Data

```bash
#[user]$
docker-compose -f docker-compose-video-download.yml up
```

This image will download the tools to process the video downloads and frame extraction.  It will take some time to run.

Once complete, there will be a rather large `./data/video` and `./data/frames` folders.
