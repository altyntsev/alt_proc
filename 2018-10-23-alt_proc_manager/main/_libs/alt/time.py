from __future__ import absolute_import
from datetime import datetime, timedelta

def iso(dt):

    if dt.__class__.__name__=='date':
        return dt.strftime('%Y-%m-%d')
    elif dt.__class__.__name__=='time':
        return dt.strftime('%H:%M:%S')
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

def from_iso(iso):
    
    if len(iso)==19:
        return datetime.strptime(iso,'%Y-%m-%d %H:%M:%S')
    
    if len(iso)==10:
        return datetime.strptime(iso,'%Y-%m-%d').date()

def now():

    return iso( datetime.now() )

def today():

    return iso( datetime.now().date() )