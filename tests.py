#!/usr/bin/python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c), 2017, Rod Manning <rod.t.manning@gmail.com>

import unittest
import caldav_available as cda
from datetime import datetime, timedelta
import uuid


"""Test suite for CalDAV availability program."""

# Templates for assembling test events and test CalDAV-format files
TEST_ICS_FILE_TEMPLATE = """BEGIN:VCALENDAR
CALSCALE:GREGORIAN
{{events}}
BEGIN:VTIMEZONE
TZID:Australia/Darwin
END:VTIMEZONE
END:VCALENDAR
"""

TEST_EVENT_TEMPLATE = """BEGIN:VEVENT
UID:{uid}
DTSTART;VALUE=DATE-TIME;TZID={timezone}:{datetime_as_string}
DTEND;VALUE=DATE-TIME;TZID={timezone}:{datetime_as_string}
SUMMARY:{summary}
LOCATION:{location}
TRANSP:{transp}
CATEGORIES:{categories}
STATUS:CONFIRMED
END:VEVENT
"""

TEST_ALLDAY_EVENT_TEMPLATE = """BEGIN:VEVENT
UID:{uid}
DTSTART;VALUE=DATE;{datetime_as_string}
DTEND;VALUE=DATE;{datetime_as_string}
SUMMARY:{summary}
LOCATION:{location}
TRANSP:{transp}
CATEGORIES:{categories}
STATUS:CONFIRMED
END:VEVENT
"""

# String format for datetime conversion
DT_STR_FMT = "%Y%m%dT%H%M%S"


class TestEventObjects(unittest.TestCase):
    """Test Event objects."""

    def setUp(self):
        self._event_data = [
            {
                "UID": uuid.uuid4(),
                "DTSTART": datetime.strptime("20170201T120000", DT_STR_FMT),
                "DTEND": datetime.strptime("20170201T1400", DT_STR_FMT),
                "SUMMARY": "Test event",
                "CATEGORIES": "Test Python",
                "LOCATION": "Melbourne",
            },
        ]
        self._event = cda.Event(**self._event_data[0])

    def test_creation(self):
        """Test that an Event is created given correct input data."""
        event = cda.Event(**self._event_data[0])
        self.assertIsNotNone(event)

    def test_missing_uuid(self):
        """Test creating and Event with no uuid data."""
        malformed_data = self._event_data.copy()
        del malformed_data[0]["UID"]
        with self.assertRaises(KeyError) as context:
            cda.Event(**malformed_data[0])
        
        
    def test_missing_start(self):
        """Test malformed data: start dt missing."""
        # Test an Event with no start dt
        malformed_data = self._event_data.copy()
        malformed_data[0]["DTSTART"] = None
        with self.assertRaises(TypeError) as context:
            cda.Event(**malformed_data[0])

    def test_zero_length_event(self):
        # Test a zero-length Event
        malformed_data = self._event_data.copy()
        malformed_data[0]["DTSTART"] = malformed_data[0]["DTEND"]
        self.assertEqual(malformed_data[0]["DTEND"],
                         malformed_data[0]["DTSTART"])
        with self.assertRaises(ValueError) as context:
            event = cda.Event(**malformed_data[0])

    def test_invalid_length_event(self):
        # Test an Event that has a start after the end
        malformed_data = self._event_data.copy()
        malformed_data[0]["DTEND"] = datetime.strptime(
            "2016201T120000", DT_STR_FMT)
        self.assertTrue(malformed_data[0]["DTEND"] < malformed_data[0]["DTSTART"])
        with self.assertRaises(ValueError) as context:
            cda.Event(**malformed_data[0])        
        
    def test_length(self):
        """Test that the length of an Event is calculated correctly."""
        self.assertEqual(self._event.start,
                         datetime(year=2017, month=2, day=1,
                                  hour=12, minute=0, second=0)
                         )
        self.assertEqual(self._event.end,
                         datetime(year=2017, month=2, day=1,
                                  hour=14, minute=0, second=0)
                         )
        self.assertEqual(self._event.length, timedelta(hours=2))

    def test_categories(self):
        self.assertEqual(self._event.categories, ["Test", "Python"])

    def test_location(self):
        self.assertEqual(self._event.location, "Melbourne")



class TestBlockObjects(unittest.TestCase):
    """Test Block objects."""

    @classmethod
    def setUpClass(cls):
        pass

    def test_assign_opaque(self):
        """Test the assign() method when the event is "Busy"."""
        pass

    def test_assign_transparent(self):
        """Test the assign() method when the event is "Free"."""
        pass

    def test_classify_leave(self):
        """Test the css classification for "Leave" events."""
        pass

    def test_classify_off(self):
        """Test the css classification for "Off" events."""
        pass

    def test_classify_assigned_hours(self):
        """Test the css classification when hours are assigned."""
        pass

    @classmethod
    def tearDownClass(cls):
        pass


class TestFunctions(unittest.TestCase):
    """Test the functions in the caldav-available program."""
    pass

    def test_get_calendar(self):
        """Test how the calendar file is retrieved."""
        pass

    def test_normalize_dt(self):
        """Test the function used to normalize a dt to UTC."""
        pass

    def test_process_cal_data(self):
        """Test the function used to process calendar data."""
        pass

    def test_create_block(self):
        """Test the function used to create the calendar blocks."""
        pass

    def test_check_overlap(self):
        """Test the function used to check for overlap between dt's."""
        pass

    def test_calculate_overlap(self):
        """Test the calculation of the size of the overlap between events."""
        pass


def main():
    unittest.main()


if __name__ == "__main__":
    main()
