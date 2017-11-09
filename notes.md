Find all video IDs for downloaded MP4s.

```bash
ls -1 video | grep "mp4" | cut -c1-11 | sort
```

Find all video IDs that have frames.

```bash
ls -1 frames | sort
```
