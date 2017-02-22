#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import urllib.request

"""Compute free/busy information from a CalDAV file.

Inputs are as follows:

cal_url:
  CalDAV file URL.

username:
  Username to access the CalDAV file.

password:
  Password to access the CalDAV file.

start_date:
  First date of period to be processed. Defaults to current local date.

end_date:
  Last date of period to be processed. Defaults to 14 days after current
  local date.

day_start:
  First hour of the day to be considered in free/busy calculations. Defaults to
  0600 local time.

day_end:
  Last hour of the day to be considered in free/busy calculations. Defaults to
  2200 local time.

block_length:
  Length (in hours) of blocks that each day is divided into when showing
  free/busy information. Defaults to 6 hours.

Logic of program is as follows:

1. Download CalDAV file from server (requires authentication)

2. Process the text of the CalDAV file to create a list of all published
   'event' objects within the date range specified (i.e. between start_date and
   end_date).

3. Create a list of all blocks within the date range specified.

4. Search the list of events and assign events to each block if they fall
   within the block.

5. For each block, compute the time assigned to events in that block to
  calculate the free/busy time for the block.

6. Assign a classification to the block to indicate if it has high (75 <= n),
   moderate (30 < n < 75), or low (n <= 30 ) time allocated.

"""


class event(object):
    """An event extracted from a CalDAV calendar entry.

    Each ``event`` has the following properties:

    uid:
      The unique ID assigned to the event by the calendar.

    name:
      The name of the event.

    summary:
      The description or summary saved for the event

    start_dt:
      The datetime the event starts (in UTC).

    end_dt:
      The datetime the event ends (in UTC).

    categories:
      The categories the event is tagged with.

    """
    pass


class block(object):
    """A block of time in a calendar.

    Blocks are of a defined length and are the units of time that are used to
    calculate the free/busy information for display in a calendar.

    """
    pass


def get_calendar(username, password, url, realm):
    """Get a CalDAV file from a server.

    This function first creates a handler to authenticate with the web
    server hosting the CalDAV file.

    It then sends a request to access the calendar at the supplied url.

    The data that's returned is returned as a list of strings (one string
    per line).

    """
    # Setup the authentication handler
    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(
        realm=realm, uri=url,
        user=username, passwd=password
    )
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)
    # Retrieve the CalDAV file
    with urllib.request.urlopen(url) as f:
        cal_data = f.readlines()
    return cal_data


def create_events(calendar_file, start_date, end_date):
    """Create events from data contained in a CalDAV file."""


def create_blocks(start_date, end_date, start_hours, end_hours, block_length):
    """Create the blocks used to calculate free/busy time."""
    pass


def assign_events(events, blocks):
    """Assign events to blocks that they fully or partially fall within."""
    pass


def calc_block_hours(blocks):
    """Calculate how many hours are assigned for each block."""
    pass


def classify_block(blocks):
    """Classify a block based on how free/busy it is."""
    pass


def parse_args():
    """Main program loop for user CLI interaction."""
    # Create the parser to process the CLI arguments
    parser = argparse.ArgumentParser(
        description="Calculate free/busy time from a CalDAV calendar file.",
        epilog="Copyright (c) Rod Manning 2017"
    )
    parser.add_argument(
        "username",
        help="Username to access CalDAV file on server"
    )
    parser.add_argument(
        "password",
        help="Password to access CalDAV file on server",
    )
    parser.add_argument(
        "url",
        help="URL to access CalDAV file on server"
    )
    parser.add_argument(
        "realm",
        help="Realm to access CalDAV file on server"
    )
    parser.add_argument(
        "--start",
        help="Start of period to be processed (default: today)",
        metavar="yyyy-mm-dd"
    )
    parser.add_argument(
        "--end",
        help="End of period to be processed (default: +14 days)",
        metavar="yyyy-mm-dd"
    )
    parser.add_argument(
        "--day_start",
        help="Earliest free/busy time is calculated (default: 6 AM)",
        metavar="H",
        type=int,
    )
    parser.add_argument(
        "--day_end",
        help="Latest free/busy time is calculated (default: 10 PM)",
        metavar="H",
        type=int,
    )
    parser.add_argument(
        "--block_length",
        help="Length of blocks to show free/busy time (default: 6 hrs)",
        metavar="H",
        type=int,
    )
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    cal_data = get_calendar(args.username, args.password, args.url, args.realm)
