import logging

from dateutil.parser import parse


def test_date():
    string = "2016-01-29T20:00:00+01:00"

    date = parse(string)
    logging.info(date.timetz())

    s = '2020-03-15T09:02:31+00:00'
    date = parse(s)
    logging.info(date)

    s = '2020-03-16T10:18:20.200173322+00:00'
    date = parse(s)
    logging.info(type(date))