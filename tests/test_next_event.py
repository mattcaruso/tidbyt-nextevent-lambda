import json
import handler
import pytest
from datetime import date, datetime


def test_integration():
    event = {
        'body': json.dumps({'tz': 'America/New_York', 'ics_url': 'https://ics.calendarlabs.com/76/8d23255e/US_Holidays.ics'}),
        'headers': {}
    }
    response = handler.handler(event=event, context={})
    assert response['statusCode'] == 200
    assert response['has_next_event'] is True


def test_no_more_events():
    event = {
        'body': json.dumps({'tz': 'America/New_York', 'ics_url': 'https://www.phpclasses.org/browse/download/1/file/63438/name/example.ic'}),
        'headers': {}
    }
    response = handler.handler(event=event, context={})
    assert response['statusCode'] == 200
    assert response['has_next_event'] is False


def test_url_not_ics():
    """If the provided URL isn't an ics URL, make sure the Lambda fails gracefully."""
    event = {
        'body': json.dumps({'tz': 'America/New_York', 'ics_url': 'https://calendar.google.com/calendar'}),
        'headers': {}
    }
    response = handler.handler(event=event, context={})
    assert response['statusCode'] == 400
    assert response['has_next_event'] is False


@pytest.mark.parametrize(
    "start_date,now,result",
    [
        (date(2024, 4, 22), datetime(2024, 4, 22, 12), True),
        (date(2024, 4, 22), datetime(2024, 4, 21, 12), False),
        (date(2024, 4, 22), datetime(2024, 4, 26, 12), False)
    ]
)
def test_today(start_date, now, result):
    assert handler.is_today(start_date, now) == result


@pytest.mark.parametrize(
    "start_date,now,result",
    [
        (date(2024, 4, 22), datetime(2024, 4, 22, 12), False),
        (date(2024, 4, 22), datetime(2024, 4, 21, 12), True),
        (date(2024, 4, 22), datetime(2024, 4, 26, 12), False)
    ]
)
def test_tomorrow(start_date, now, result):
    assert handler.is_tomorrow(start_date, now) == result
