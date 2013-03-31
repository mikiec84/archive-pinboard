#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
import requests


def brutal_error_handler():
    """ Silly, simple error handling. Never do this. """
    print("Something went horribly wrong, so we're not continuing")
    sys.exit(1)


# Parameters.
bookmarkdir = os.path.join(os.environ['HOME'], 'Dropbox/Personal/pinboard')
pinboard_api = 'https://api.pinboard.in/v1/'
yearfmt = '%Y'
datefmt = '%m-%d'
y = datetime.utcnow().strftime(yearfmt)
t = datetime.utcnow().strftime(datefmt)

"""
Get the user's authentication token
It's available at https://pinboard.in/settings/password
Store it in your home dir, in a file named .pinboard-credentials
"""
try:
    with open(
        os.path.join(
            os.environ['HOME'],
            '.pinboard-credentials')) as credentials:
                for line in credentials:
                    me, token = line.split(':')
except IOError:
    print("Couldn't get your credentials from %s" % credentials.name)
    brutal_error_handler()

if not me and token:
    raise Exception(
        "There was a problem with your pinboard credentials:\n\
They should be stored in the format 'pinboard_username:xxxxxxxxxxxxxxxxxxxx'")

outdir = bookmarkdir + y
if not os.path.exists(outdir):
    try:
        os.makedirs(outdir)
    except OSError:
        print("Couldn't create a directory at %s" % outdir)
        brutal_error_handler()

# write a new bookmarks file
try:
    with open(
        os.path.join(
            outdir, 'pinboard-backup_' + t + '.xml'), 'w') as out:
        # Get all the posts from Pinboard
        payload = {"auth_token": me + ":" + token}
        req = requests.get(
            pinboard_api + 'posts/all',
            params=payload)
        # raise an exception for a 4xx code
        req.raise_for_status()
        print("Authentication successful, trying to write backup.")
        out.write(req.text.encode("utf-8"))
except IOError:
    print("Couldn't create new bookmarks file at %s" % outdir)
    brutal_error_handler()
print("Done! Backed up bookmarks to %s" % out.name)
