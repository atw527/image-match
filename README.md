# Quickstart

_There are currently some directory assumptions.  To make things easier, make sure your gopath and src matches mine.  The repo will live at `/home/andrew/go/src/github.com/atw527`._

```bash
export GOPATH=$HOME/go
export GOROOT=/usr/local/go
export PATH=$PATH:~/go/bin
```

Check it out.

```bash
#[user /home/andrew/go/src/github.com/atw527]$
git clone git@github.com:atw527/image-match.git
```

CD into `image-match` and set some permissions that are not saved in the repo.

```bash
#[user image-match]$
sudo bash permissions.sh
```

Now spin up the sandbox environment.  Images will take some time to build.

```bash
#[user image-match]$
export MASTER=`hostname`
docker-compose -f docker-compose.front.yml -f docker-compose.download.yml -f docker-compose.render.yml -f docker-compose.match.yml -f docker-compose.sandbox.yml up --build
```

Run this to spin everything down.  Databases will be lost, but the downloaded data will remain in the `data/` folder.  So videos that were downloaded and rendered will not have to be redone.  When spinning up the test environment the next time, it will take a few minutes to figure out that the video files & frames already exist and will not download them again.

```bash
#[user image-match]$
docker-compose -f docker-compose.front.yml -f docker-compose.download.yml -f docker-compose.render.yml -f docker-compose.match.yml -f docker-compose.sandbox.yml down --remove-orphans
```

# Download and Build Test Data

- Add data to `download` table
- Fire up `docker-compose.download.yml` on master
- Fire up `docker-compose.render.yml` on master (spin up additional slaves to help this go faster)

# Server Layout

## Master

Master contains a copy of all data - video MP4, meta, and frames.  The current data size is 190G total.

The `front` instance powers the web interface and should be ran on the server box.

## Slaves

Slaves don't need to contain anything in `data/video`.  Tasks will run faster if they are able to hold copies of `data/frames`, requiring > 50G available storage.

# Startup Commands

The master will be running front, download, and maybe the processing modules.

```bash
#[user image-match]$
docker-compose -f docker-compose.front.yml -f docker-compose.download.yml -f docker-compose.render.yml -f docker-compose.match.yml up --build
```

Any of the slaves will be running multiple instances of either of the processing modules.

```bash
#[user image-match]$
docker-compose -f docker-compose.render.yml up --build --scale im-render=2
```

```bash
#[user image-match]$
docker-compose -f docker-compose.match.yml up --build --scale im-match=2
```

This next example runs both processing modules on the same host.  The load could get high if both have tasks to do.

```bash
#[user image-match]$
docker-compose -f docker-compose.match.yml -f docker-compose.render.yml up --build --scale im-match=2 im-render=2
```

Super-long command for dev self-contained system!

```bash
#[user image-match]$
export MASTER=`hostname`
docker-compose -f docker-compose.front.yml -f docker-compose.download.yml -f docker-compose.render.yml -f docker-compose.match.yml -f docker-compose.sandbox.yml up --build
```

When ready to end the test...

```bash
#[user image-match]$
docker-compose -f docker-compose.front.yml -f docker-compose.download.yml -f docker-compose.render.yml -f docker-compose.match.yml -f docker-compose.sandbox.yml down --remove-orphans
```
