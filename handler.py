import json
import requests
import pytz
from tatsu.exceptions import FailedParse  # tatsu is dependency of ics
from ics import Calendar
from datetime import date, datetime, timedelta


def handler(event, context):  # noQA

    del event['headers']['x-api-key']  # Prevent API key from being logged
    print(event['headers'])  # Log to CloudWatch for monitoring

    body = json.loads(event['body'])
    tz = body['tz']  # Will be a string like 'America/New_York'
    # All tz options are listed here
    # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    ics_url = body['ics_url']

    try:
        calendar = Calendar(requests.get(ics_url).text)
    except FailedParse:
        return {
            'statusCode': 400,
            'message': 'URL provided is not an ics file',
            'has_next_event': False
        }

    events = calendar.events
    sorted_events = sorted(events, reverse=False)

    now = datetime.now(pytz.timezone(tz))

    next_event = None
    for e in sorted_events:
        if e.begin > now:
            next_event = e
            break

    if not next_event:
        return {
            'statusCode': 200,
            'has_next_event': False
        }

    start_date = next_event.begin.astimezone(pytz.timezone(tz)).date()

    # is_today & is_tomorrow will be used to determine special
    # formatting on the Pixlet frontend
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'has_next_event': True,
            'title': next_event.name,
            'begin': next_event.begin.astimezone(pytz.timezone(tz)).isoformat(),
            'end': next_event.end.astimezone(pytz.timezone(tz)).isoformat(),
            'location': next_event.location,
            'is_today': is_today(start_date, now),
            'is_tomorrow': is_tomorrow(start_date, now)
        })
    }

    print(response)  # Logs to CloudWatch
    return response


def is_today(start_date: date, now: datetime):
    today = now.date()
    if today == start_date:
        return True
    else:
        return False


def is_tomorrow(start_date: date, now: datetime):
    today = now.date()
    tomorrow = today + timedelta(days=1)
    if tomorrow == start_date:
        return True
    else:
        return False
