# coding: utf-8

from datetime import datetime

import pytz
from dateutil.parser import parse


def rfc3339_to_datetime(rfc3999: str) -> datetime:
    shanghai = pytz.timezone('Asia/Shanghai')

    return parse(rfc3999).astimezone(shanghai)
