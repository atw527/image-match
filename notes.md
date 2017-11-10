### Find all video IDs for downloaded MP4s

```bash
#[user image-match/data]$
ls -1 video | grep "mp4" | cut -c1-11 | sort
```

### Find all video IDs that have frames

```bash
#[user image-match/data]$
ls -1 frames | sort
```

### Start all the containers

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
