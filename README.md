# Download and Build Test Data

This process will fill up 50G and over 560k files with the current queue file (11G bandwidth, rest is processing).  If another local machine has this data, it will be better to rsync it over.

Otherwise, the download scripts run in a Docker container, so to not install temp software on the host machine.

```bash
#[user]$
docker-compose -f docker-compose-video-download.yml up
```

This image will download the tools to process the video downloads and frame extraction.  It will take some time to run and stop automatically when complete.

Since the only output is in stdout of docker-compose, ffmpeg and youtube-dl don't report progress very well.  Run `du -sh` on the data folders to see their current size and get an idea of progress.  The `video` folder will grow first, followed by the `frames` folder.

Once complete, there will be a rather large `./data/video` and `./data/frames` folders.

# Server Layout

## Master

Master contains a copy of all data - video MP4, meta, and frames.  The current data size is 190G total.

The `front` instance powers the web interface and should be ran on the server box.

## Slaves

Slaves don't need to contain anything in `data/video`.  Tasks will run faster if they are able to hold copies of `data/frames`, requiring > 50G available storage.
