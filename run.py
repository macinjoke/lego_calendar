from flask import Flask, render_template
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
    message = {}
    if not events:
        message['has_event'] = False
        message['no_event_message'] = '予定がありません'
        return render_template('index.html', message=message)
    for event in events:
        if 'dateTime' in event['start']:  # 時間指定イベントなら
            nearest_event = event
            break
    if nearest_event is None:
        message['has_event'] = False
        message['no_event_message'] = '近いうちに時間指定の予定はありません'
        return render_template('index.html', message=message)

    now = datetime.now(pytz.utc)
    start = nearest_event['start']['dateTime']
    start_datetime = datetime.replace(datetime.strptime(start, '%Y-%m-%dT%H:%M:%S+09:00'), tzinfo=timezone('Asia/Tokyo'))
    start = start_datetime.strftime('%Y年%m月%d日 %H:%M')
    remaining_time = start_datetime - now
    message['schedule'] = nearest_event['summary']
    message['start'] = start
    print('直近の予定{}'.format(message))
    message['has_event'] = True
    alert_case = 0
    remaining_time_types = [5, 30, 60]
    if remaining_time.days < 1:
        for i, remaining_time_type in enumerate(remaining_time_types):
            if remaining_time.seconds < 60 * remaining_time_type:
                message['remaining_time_type'] = remaining_time_type
                message['remaining_time'] = int(remaining_time.seconds / 60)
                if remaining_time_type * 60 - remaining_time.seconds < 80:
                    alert_case = i + 1
                break
    lego.alert(alert_case)
    message['alert_case'] = alert_case
    return render_template('index.html', message=message)

if __name__ == "__main__":
    app.run()
