import alt.time
from datetime import datetime, timedelta
from alt.dict_ import dict_

def diff_format(dt0, dt1=None, tz=None):

    if not dt1:
        dt1 = datetime.now()
        if tz:
            dt1 += timedelta(hours=tz)

    if isinstance(dt1, (str)):
        dt1 = alt.time.from_iso(dt1)
    if isinstance(dt0, (str)):
        dt0 = alt.time.from_iso(dt0)

    diff = dt1 - dt0

    diff = abs(int(diff.total_seconds()))
    h = diff // 3600
    m = (diff % 3600) // 60
    if h>=24:
        d = diff // (3600*24)
        h = (diff % (3600*24)) // 3600
        sd = '({0:d}d {1:02d}:{2:02d})'.format(d,h,m)
    else:
        sd = '({0:02d}:{1:02d})'.format(h,m)
    
    return sd

def dates(date):

    today = alt.time.today_utc_iso()
    default = date is None
    if default:
        date = today

    date = alt.time.from_iso(date)
    prev_date = alt.time.iso(date - timedelta(days=1))
    next_date = alt.time.iso(date + timedelta(days=1))
    date = alt.time.iso(date)

    label = date
    if next_date >= today:
        next_date = ''
    if date == today:
        label = 'Today'

    dates = dict_(date=date, label=label, prev=prev_date, next=next_date, today=today)

    return dates
