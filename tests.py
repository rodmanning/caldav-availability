#!/usr/bin/python
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (c), 2017, Rod Manning <rod.t.manning@gmail.com>

import unittest
import caldav_available as cda
import datetime
import uuid
import pytz


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
                "DTSTART": datetime.datetime.strptime("20170201T120000", DT_STR_FMT),
                "DTEND": datetime.datetime.strptime("20170201T1400", DT_STR_FMT),
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
        malformed_data[0]["DTEND"] = datetime.datetime.strptime(
            "2016201T120000", DT_STR_FMT)
        self.assertTrue(malformed_data[0]["DTEND"] < malformed_data[0]["DTSTART"])
        with self.assertRaises(ValueError) as context:
            cda.Event(**malformed_data[0])        
        
    def test_length(self):
        """Test that the length of an Event is calculated correctly."""
        self.assertEqual(self._event.start,
                         datetime.datetime(year=2017, month=2, day=1,
                                  hour=12, minute=0, second=0)
                         )
        self.assertEqual(self._event.end,
                         datetime.datetime(year=2017, month=2, day=1,
                                  hour=14, minute=0, second=0)
                         )
        self.assertEqual(self._event.length, datetime.timedelta(hours=2))

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
    def setUp(self):
        self._event_data = [
            {
                "UID": uuid.uuid4(),
                "DTSTART": datetime.datetime.strptime("20170201T120000", DT_STR_FMT),
                "DTEND": datetime.datetime.strptime("20170201T140000", DT_STR_FMT),
                "SUMMARY": "Test event",
                "CATEGORIES": "Test Python",
                "LOCATION": "Melbourne",
            },
            {
                "UID": uuid.uuid4(),
                "DTSTART": datetime.datetime.strptime("20170202T120000", DT_STR_FMT),
                "DTEND": datetime.datetime.strptime("20170202T140000", DT_STR_FMT),
                "SUMMARY": "Test event",
                "CATEGORIES": "Test Python",
                "LOCATION": "Melbourne",
            },
            {
                "UID": uuid.uuid4(),
                "DTSTART": datetime.datetime.strptime("20170201", "%Y%m%d").date(),
                "DTEND": datetime.datetime.strptime("20170202", "%Y%m%d").date(),
                "SUMMARY": "All-day event",
                "CATEGORIES": "Test Python",
                "LOCATION": "Melbourne",
            },

        ]
        self._event1 = cda.Event(**self._event_data[0])
        self._event2 = cda.Event(**self._event_data[1])
        self._event3 = cda.Event(**self._event_data[2])

        self._blocks = cda.create_blocks(
            datetime.datetime.strptime("20170201T000000", DT_STR_FMT),
            datetime.datetime.strptime("20170203T000000", DT_STR_FMT),
            6, 22, 4
        )
        
        
    def test_get_calendar(self):
        """Test how the calendar file is retrieved."""
        pass

    def test_normalize_dt(self):
        """Test the function used to normalize a dt to UTC."""
        # Test normal time
        tz_str = "Australia/Melbourne"
        local_ts = "20170610T140000"
        ts_fmt = "%Y%m%dT%H%M%S"
        nml_dt = cda.normalize_dt(tz_str, local_ts, ts_fmt)
        self.assertEqual(nml_dt,
                         datetime.datetime(year=2017, month=6, day=10,
                                  hour=4, minute=0, second=0,
                                  tzinfo=pytz.utc)
        )
        # Test daylight savings time            
        local_ts = "20170210T140000"
        nml_dt = cda.normalize_dt(tz_str, local_ts, ts_fmt)
        self.assertEqual(nml_dt,
                         datetime.datetime(year=2017, month=2, day=10,
                                  hour=3, minute=0, second=0,
                                  tzinfo=pytz.utc)
        )

        
    def test_process_cal_data(self):
        """Test the function used to process calendar data."""
        pass

    def test_create_block(self):
        """Test the function used to create the calendar blocks."""
        pass

    def test_check_overlap(self):
        """Test the function used to check for overlap between dt's."""
        # Check that event1 and event2 use datetime objects
        self.assertTrue(type(self._event1.start)==datetime.datetime)
        self.assertTrue(type(self._event1.end)==datetime.datetime)
        self.assertTrue(type(self._event2.start)==datetime.datetime)
        self.assertTrue(type(self._event2.end)==datetime.datetime)
        # Check that the overlap is as expected for event1 and event2
        result = [cda.check_overlap(self._event1, blk) for blk in self._blocks]
        expected = [ False, True, True, False, False, False, False,
                     False, False, False, False, False, False, False]
        self.assertEqual(result, expected)
        result = [cda.check_overlap(self._event2, blk) for blk in self._blocks]
        expected = [ False, False, False, False, False, False, True, True,
                     False, False, False, False, False, False ]
        self.assertEqual(result, expected)
        # Check that event3 uses date objects (*not* datetime.datetime objects)
        self.assertTrue(type(self._event3.start)==datetime.date)
        self.assertTrue(type(self._event3.end)==datetime.date)
        # Check that the overlap is as expected for event3, which is an 'All
        # Day' event
        result = [cda.check_overlap(self._event3, blk) for blk in self._blocks]
        expected = [ True, True, True, True, True, True, True,
                     True, True, True, False, False, False, False ]
        self.assertEqual(result, expected)


        
    def test_calculate_overlap(self):
        """Test the calculation of the size of the overlap between events."""
        pass


def main():
    unittest.main()


if __name__ == "__main__":
    main()
