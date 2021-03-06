#!/usr/bin/python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c), 2017, Rod Manning <rod.t.manning@gmail.com>

import argparse
import urllib.request
import pytz
import datetime
import math
import json
import pickle


"""Compute free/busy information from a CalDAV file.

Program returns a list of Block objects that are encoded with classes
indicating free/busy time and which are suitable for applying styles
to HTML or other calendars to indicate free busy time.

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

Outputs are:

Blocks:
  Objects with the following properties:

  self.start:
    The start of the block as a python datetime

  self.end:
    The end of the block as a python datetime

  self.length:
    The length of the block as a python timedelta

  self.busy:
    The amount of time in minutes (integer) that is busy during the block

  self.free:
    The amount of time in minutes (integer) that is free during the block

  self.classes:
    Classes assigned to the block based on the ratio of free/busy time

  categories:
    Categories of work assigned to the block (e.g. client name, etc.)

"""

__version__ = '1.0'
__author__ = 'Rod Manning <rod.t.manning@gmail.com>'


ARG_DEFAULTS = {
    "start": datetime.datetime.now(),
    "end": datetime.datetime.now() + datetime.timedelta(days=128),
    "day_start": "06",     # 0600 local time
    "day_end": "22",      # 2200 local time
    "block_length": "6",  # Hours
    "timezone": "Australia/Melbourne",  # Default local timezone
    "realm": "Roundcube Calendar",
    "format": "txt",
    "output": "availability.txt",
}
BUSY_THRESHOLDS = {
    "low": 0.20,
    "high": 0.75
}
TS_FMT = "%Y%m%dT%H%M%S"


class Event(object):
    """An event extracted from a CalDAV calendar entry.

    Each ``event`` has the following properties:

    uid:
      The unique ID assigned to the event by the calendar.

    name:
      The name, or description, or summary saved for the event

    start_dt:
      The datetime the event starts (in UTC).

    end_dt:
      The datetime the event ends (in UTC).

    length:
      A timedelta representing the length of the event.

    categories:
      The categories the event is tagged with.

    """

    def __init__(self, **kwargs):
        """Initialize an Event object.

        kwargs:
          A dictionary containing the data from the CalDAV calendar file for
          the event.

        """
        try:
            self.uid = kwargs["UID"]
            self.name = kwargs["SUMMARY"]
            self.start = kwargs["DTSTART"]
            self.end = kwargs["DTEND"]
        except KeyError as error:
            raise error
        if self.start >= self.end:
            raise ValueError("Start datetime must be before end datetime.")
        self.length = self.end - self.start
        try:
            self.transparency = kwargs["TRANSP"]
        except KeyError:
            self.transparency = ""
        try:
            self.location = kwargs["LOCATION"]
        except KeyError:
            self.location = ""
        try:
            self.categories = kwargs["CATEGORIES"].split(" ")
        except KeyError:
            self.categories = []


    def __str__(self):
        return "{0} ({1})".format(
            self.name,
            self.start.strftime("%d-%B %Y")
        )


class Block(object):
    """A block of time in a calendar.

    Blocks are of a defined length and are the units of time that are used to
    calculate the free/busy information for display in a calendar.

    """


    def __init__(self, **kwargs):
        """Initialize the Block object.

        start_dt:
          A datetime object representing the start of the block.

        end_dt:
          A datetime object representing the end of the block.

        Note that when the block is initialized the free time is set to the
        length of the block, and the busy time is set to zero (0).
        """
        self.start = kwargs["start_dt"]
        self.end = kwargs["end_dt"]
        self.length = self.end - self.start
        self.busy = datetime.timedelta(minutes=0)
        self.free = self.length
        self.classes = []
        self.categories = []
        self.location = []
        self.assigned = float(0)

    def __str__(self):
        return "{0} ({1})".format(
            self.start.date(),
            ", ".join(self.location),
        )


    def assign(self, event, hours):
        """Function to assign hours and meta-data to a block.

        This is a convenience function which assigned a period of time to a
        block as 'busy' and then updates the 'free' time.

        It also assigns the Categories and Location for the Event.

        event:
          An Event object.

        hours:
          A timedelta representing the amount of time to be assigned as busy.

        """
        # If the event is "Transparent" then it is set to "Show Me As" Free
        # in the calendar. So busy hours are only assigned for events that
        # are *not* "Transparent".
        if event.transparency != "TRANSPARENT":
            self.busy = self.busy + hours
            self.free = self.length - self.busy
            self.assigned = self.busy / self.length
        # Assign other properties to the block
        if event.location not in self.location:
            self.location.append(event.location)
        for item in event.categories:
            if item not in self.categories:
                self.categories.append(item)
        # Handle invalid data and munge it to show correct outputs
        if self.assigned > 1:
            self.assigned = 1
        if self.free < datetime.timedelta(seconds=0):
            self.free = "0:00:00"
        if self.busy > self.length:
            self.busy = self.length


    def _json_default(self, obj):
        """JSON serializer for objects not serializable by default"""

        if isinstance(obj, datetime.datetime):
            fmt = "%Y-%m-%dT%H:%M:%S%z"
            serial = obj.strftime(fmt)
            return serial
        elif isinstance(obj, datetime.timedelta):
            return str(obj)
        raise TypeError("Type not serializable")


    def as_json(self):
        """Output the Block and it's properties using json."""
        return json.dumps(self.__dict__, default=self._json_default)


    def as_pickle(self, f):
        """Output the Block and it's properties using Python's pickle module."""
        pickle.dump(self.__dict__, f)


    def classify(self):
        not_work = ("Leave" in self.categories) or ("Off" in self.categories)
        if not_work:
            self.classes.append("unavailable")
        elif self.assigned > BUSY_THRESHOLDS["high"]:
            self.classes.append("high")
        elif BUSY_THRESHOLDS["low"] < self.assigned <= BUSY_THRESHOLDS["high"]:
            self.classes.append("medium")
        elif self.assigned <= BUSY_THRESHOLDS["low"]:
            self.classes.append("low")


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


def normalize_dt(tz_str, local_ts, ts_fmt=None):
    """Normalize a local time to UTC.

    An example of what this function does is that it converts the following
    timezone string 'Asia/Hong_Kong' and a seperate timestamp string of
    '20170210T140000' into a UTC datetime of 2017-02-10 05:30:00+00:00.

    tz_str:
      A string representing a timestamp in local time. Note that this must
      include a timezone that can be parsed by pytz.

    local_ts:
      A string representing a timestamp in localtime.

    ts_fmt:
      A string specifying the format for the timestamp. Defaults to
      '%Y%m%dT%H%M%S'.

    """
    if ts_fmt is None:
        ts_fmt = TS_FMT
    try:
        tz_name = tz_str.split("=")[1]
    except IndexError:
        tz_name = tz_str
    tz = pytz.timezone(tz_name)
    local_dt = datetime.datetime.strptime(local_ts, ts_fmt)
    local_dt = tz.localize(local_dt)
    utc_dt = local_dt.astimezone(pytz.utc)
    return utc_dt


def process_cal_data(cal_data, start, end,
                     field_list=None, ts_fmt=TS_FMT):
    """Process a CalDAV file to extract information about an event.

    field_list:
      A list of strings of the field names containing the data to be
      extracted from the CalDAV file. (Note that this is case sensitive.)

    """
    if field_list is None:
        field_list = ("UID", "SUMMARY", "CATEGORIES", "LOCATION", "TRANSP",)
    stack = {}   # Stack to hold data about events
    idx = 1
    for line in cal_data:
        text = line.decode().rstrip("\r\n")
        try:
            field, _, data = text.partition(":")
            if (field == "BEGIN") and (data == "VEVENT"):
                stack[idx] = {}
            elif field in field_list:
                stack[idx][field] = data
            elif (field.startswith("DTSTART")) or (field.startswith("DTEND")):
                _sub_fields = field.split(";")
                if len(_sub_fields) == 1:
                    # Then there's nothing here, so break to the next iteration
                    break
                try:
                    if _sub_fields[1] == "VALUE=DATE":
                        field_name = _sub_fields[0]
                        date = datetime.datetime.strptime(data, "%Y%m%d")
                        tz = pytz.timezone(ARG_DEFAULTS["timezone"])
                        lcl_dt = tz.localize(date)
                        utc_dt = lcl_dt.astimezone(pytz.utc)
                        stack[idx][field_name] = utc_dt
                    elif _sub_fields[1].startswith("TZID="):
                        field_name = _sub_fields[0]
                        tz_str = _sub_fields[1]
                        utc_dt = normalize_dt(tz_str, data, ts_fmt)
                        stack[idx][field_name] = utc_dt
                except IndexError:
                    raise
            elif field == "END" and data == "VEVENT":
                idx = idx + 1
        except ValueError:
            pass
    return stack


def create_events(calendar_file, start, end):
    """Create events from data contained in a CalDAV file."""
    calendar_data = process_cal_data(calendar_file, start, end)
    stack = []   # List to hold the events
    for item in calendar_data.values():
        evt = Event(**item)
        stack.append(evt)
    return stack


def create_blocks(start_dt, end_dt, start_hour, end_hour, block_length):
    """Create the blocks used to calculate free/busy time."""
    stack = []
    # Get the start time for the first block
    blocks_per_day = math.ceil((end_hour - start_hour) / block_length)
    block_start = start_dt.replace(
        hour=start_hour,
        minute=0, second=0, microsecond=0
    )
    block_length = datetime.timedelta(hours=block_length)
    block_end = block_start + block_length
    day_start = block_start
    day_end = block_start.replace(hour=end_hour)
    end_of_period = end_dt.replace(
        hour=end_hour,
        minute=0, second=0, microsecond=0
    )
    # Create blocks for each day until calculated end_hours > end_hours
    # specified. When this happens, trim the end hours and increment to the
    # next day
    while block_start < end_of_period:
        # Test for incrementing to the next day
        if block_start > day_end:
            day_start = day_start + datetime.timedelta(hours=24)
            day_end = block_start.replace(hour=end_hour)
            block_start = day_start
            block_end = block_start + block_length
        # Test to set end of block to last hour in daily calendar
        if block_end > day_end:
            block_end = block_start.replace(hour=end_hour)
        data = {
            "start_dt": block_start,
            "end_dt": block_end,
        }
        stack.append(Block(**data))
        # Increment the block_start another n hours, then do the same for
        # the block_end. Note that because we update the block_start first,
        # The block end is incremented based onthe *new* starting dt :)
        block_start = block_start + block_length
        block_end = block_end + block_length
    return stack


def _is_date(obj):
    """Check whether objects are datetime.date objects.

    This function checks whether the '.start' and '.end' properties of an
    object are datetime.date objects and returns True/False accordingly.

    """
    start_is_date = type(obj.start) is datetime.date
    end_is_date = type(obj.end) is datetime.date
    if start_is_date or end_is_date:
        return True
    else:
        return False

def check_overlap(obj1, obj2):
    """Check whether two objects with start and end datetimes overlap."""
    try:
        check_1 = (obj1.start <= obj2.start <= obj1.end)
        check_2 = (obj2.start <= obj1.start <= obj2.end)
    except TypeError:
        # Will be raised if *one* of the objects is a date and the other is a
        # datetime.
        if _is_date(obj1):
            check_1 = (obj1.start <= obj2.start.date() <= obj1.end)
            check_2 = (obj2.start.date() <= obj1.start <= obj2.end.date())
        elif _is_date(obj2):
            check_1 = (obj1.start.date() <= obj2.start <= obj1.end.date())
            check_2 = (obj2.start <= obj1.start.date() <= obj2.end)
        else:
            raise
    if check_1 or check_2 is True:
        return True
    else:
        return False


def calculate_overlap(obj1, obj2):
    """Calculate the amount of overlap between two objects.

    Each object must have a start and end property expressed as a datetime.

    """
    # Handle date objects (as start/end time *must* be 0000/2359, so they
    # overlap for the duration of the block.
    obj1_is_date = _is_date(obj1)
    obj2_is_date = _is_date(obj2)
    if obj1_is_date == True or obj2_is_date == True:
        stack = []
        stack.append(obj1.end - obj1.start)
        stack.append(obj2.end - obj2.start)
        hours = min(h for h in stack if h > datetime.timedelta(minutes=0))
        return hours
    else:
        # Else it's a datetime.datetime object and calculate the size of the
        # overlap
        max_start = max(obj1.start, obj2.start)
        min_end = min(obj1.end, obj2.end)
        hours = min_end - max_start
        return hours


def assign_block_properties(events, blocks):
    """Assign the hours in an event to a particular block.

    This function is based on the logic that there are going to be more blocks
    than there are events, so it will be faster and easier to iterate through
    the events than it would be to iterate through the blocks.

    """
    for evt in events:
        # Get all of the blocks that overlap +/- 1 day when the event takes
        # place
        # Check if the block overlaps
        for blk in blocks:
            if check_overlap(evt, blk) is True:
                hours = calculate_overlap(evt, blk)
                blk.assign(evt, hours)


def classify_blocks(blocks):
    """Classify a block based on how free/busy it is.

    Blocks are classified as determined by the values set in BUSY_THRESHOLDS.

    """
    for blk in blocks:
        blk.classify()


def write_data(blocks, data_format, output_path):
    """Write the data to the output file."""

    output_file = "{0}.{1}".format(
        output_path.rsplit(".")[0], data_format
    )
    if data_format == "pickle":
        with open(output_file, 'wb+') as f:
            for blk in blocks:
                blk.as_pickle(f)
    else:
        with open(output_file, 'w+') as f:
            for blk in blocks:
                if data_format == "json":
                    f.writelines(blk.as_json() + "\n")
                elif data_format == "yml":
                    raise NotImplementedError("Yaml output not yet implemented")


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
        "--realm",
        help="Realm to access CalDAV file on server"
    )
    parser.add_argument(
        "--start",
        help="Start of period to be processed (default: today)",
        metavar="yyyy-mm-dd"
    )
    parser.add_argument(
        "--end",
        help="End of period to be processed (default: +28 days)",
        metavar="yyyy-mm-dd"
    )
    parser.add_argument(
        "--day_start",
        help="Earliest free/busy time is calculated (default: {0})"
             .format(ARG_DEFAULTS["day_start"]),
        metavar="H",
        type=int,
    )
    parser.add_argument(
        "--day_end",
        help="Latest free/busy time is calculated (default: {0})"
             .format(ARG_DEFAULTS["day_end"]),
        metavar="H",
        type=int,
    )
    parser.add_argument(
        "--block_length",
        help="Length of blocks of free/busy time (default: {0} hrs)"
             .format(ARG_DEFAULTS["block_length"]),
        metavar="H",
        type=int,
    )
    parser.add_argument(
        "--timezone",
        help="The local timezone to base the calendar on (default: {0})"
             .format(ARG_DEFAULTS["timezone"]),
    )
    parser.add_argument(
        "--format",
        help="Set how the results are returned",
        choices=["json", "pickle", "txt"]
    )
    parser.add_argument(
        "--output",
        help="Set the output file for the data.",
    )
    args = parser.parse_args()
    # Set defaults for args:
    for arg in ARG_DEFAULTS:
        if vars(args)[arg] is None:
            vars(args)[arg] = ARG_DEFAULTS[arg]
    # Ensure start and end date strings are converted to UTC datetimes
    for item in ("start", "end"):
        # Convert to datetime objects
        if type(vars(args)[item]) is str:
            vars(args)[item] = datetime.datetime.strptime(
                vars(args)[item], "%Y-%m-%d"
            )
        # Localize to the selected local time
        tz = pytz.timezone(ARG_DEFAULTS["timezone"])
        vars(args)[item] = tz.localize(vars(args)[item])
    # Convert the various hours values to int's
    args.block_length = int(args.block_length)
    args.day_start = int(args.day_start)
    args.day_end = int(args.day_end)
    # Validation of start and end date
    if args.start > args.end:
        raise ValueError("Start date must be before the end date")
    return args


def get_availability():
    args = parse_args()
    cal_data = get_calendar(
        args.username, args.password, args.url, args.realm)
    events = create_events(cal_data, args.start, args.end)
    blocks = create_blocks(
        args.start, args.end, args.day_start, args.day_end, args.block_length
    )
    assign_block_properties(events, blocks)
    classify_blocks(blocks)
    write_data(blocks, args.format, args.output)


if __name__ == "__main__":
    get_availability()
