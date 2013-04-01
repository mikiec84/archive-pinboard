#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from datetime import datetime
import time
import requests


def retrieve():
    """ Get all the posts from Pinboard """
    req = requests.get(
        pinboard_api + 'posts/all',
        params=payload)
    # raise an exception for a 4xx code, unless it's rate-limiting
    try:
        req.raise_for_status()
    except requests.HTTPError:
        if req.status_code == 429:
            delay = wait.next()
            print("Waiting %ss because of rate-limiting" % delay)
            time.sleep(delay)
            retrieve()
        else:
            raise
    return req.text


def backoff():
    """ Return an exponential backoff period """
    delay = 2
    while True:
        if delay >= 300:
            print("Exceeded max. backoff period of 5 minutes. Try again later")
            brutal_error_handler()
        yield delay
        delay = delay * 2


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
                payload = {"auth_token": credentials.readline()}
except IOError:
    print("Couldn't get your credentials from %s" % credentials.name)
    brutal_error_handler()

if not payload.get("auth_token"):
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

wait = backoff()
bookmarks = retrieve()
print("Authentication successful, trying to write backup.")

# write a new bookmarks file
try:
    with open(os.path.join(outdir, 'pinboard-backup_' + t + '.xml'), 'w') as o:
        o.write(bookmarks.encode("utf-8"))
except IOError:
    print("Couldn't create new bookmarks file at %s" % outdir)
    brutal_error_handler()
print("Done! Backed up bookmarks to %s" % o.name)
