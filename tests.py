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
CATEGORIES:{categories}
STATUS:CONFIRMED
END:VEVENT
"""

# String format for datetime conversion
DT_STR_FMT = "%Y%m%dT%H%M%S"


class TestBlockObjects(unittest.TestCase):
    """Test Block objects."""

    @classmethod
    def setUpClass(cls):
        cls._event_data = [
            {
                "UID": uuid.uuid4(),
                "DTSTART": datetime.strptime("20170201T120000", DT_STR_FMT),
                "DTEND": datetime.strptime("20170201T1400", DT_STR_FMT),
                "SUMMARY": "Test event",
                "CATEGORIES": "Test Python",
                "LOCATION": "Melbourne",
            },
        ]
        cls._event = cda.Event(**cls._event_data[0])

    def test_creation(self):
        """Test that an Event is created given correct input data."""
        event = cda.Event(**self._event_data[0])
        self.assertIsNotNone(event)

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

    @classmethod
    def tearDownClass(cls):
        pass


class TestEventObjects(unittest.TestCase):
    """Test Event objects."""
    pass


class TestFunctions(unittest.TestCase):
    """Test the functions in the caldav-available program."""
    pass


def main():
    unittest.main()


if __name__ == "__main__":
    main()
