#!/bin/bash

# Samba and docker mess up directory and file permissions

# Run this in the repo base directory!
# I go up a directory and then back to verify this is in image-match

chown -R andrew: ../image-match

chmod -R 0644 ../image-match
chmod -R a+X ../image-match

chmod 0777 data/templates
