# Download and Build Test Data

```bash
#[user]$
docker-compose -f docker-compose-testdata.yml up
```

This image will download the tools to build the test data.  It will take some time to run.

Once complete, there will be a rather large `./test/data` folder.
