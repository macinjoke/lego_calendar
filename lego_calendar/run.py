from flask import Flask
from datetime import datetime
import pytz
from pytz import timezone

from lego_calendar.google_calendar import api_manager
from lego_calendar.lego import lego

app = Flask(__name__)
service = api_manager.build_service()


@app.route("/")
def hello():
    now = datetime.utcnow()
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        # calendarId='3vagneb571okn62ul5e8f28rbg@group.calendar.google.com', # iwailab
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    if not events:
        return '予定がありません'
    for event in events:
        if 'dateTime' in event['start']:  # 時間指定イベントなら
            nearest_event = event
            break
    if nearest_event is None:
        return '近いうちに時間指定の予定はありません'

    now = datetime.now(pytz.utc)
    start = nearest_event['start']['dateTime']
    remaining_time = datetime.replace(datetime.strptime(start, '%Y-%m-%dT%H:%M:%S+09:00'),
                                      tzinfo=timezone('Asia/Tokyo')) - now
    response = '[{}] の予定は {}'.format(nearest_event['summary'], start)
    alert_case = 0
    if remaining_time.days < 1:
        if remaining_time.seconds < 60 * 5:
            response += ' あと5分！急げ！'
            alert_case = 1
        elif remaining_time.seconds < 60 * 30:
            response += ' あと30分です'
            alert_case = 2
        elif remaining_time.seconds < 60 * 60:
            response += ' あと1時間です'
            alert_case = 3
    lego.alert(alert_case)
    return response

if __name__ == "__main__":
    app.run()
