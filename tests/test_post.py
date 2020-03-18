# coding: utf-8

import logging
import os

import requests


def test_update():
    with open(os.path.join("tests", "update.xml"), encoding='utf-8') as f:
        lines = "".join(f.readlines())

        logging.debug(lines)
    r = requests.post(f'http://127.0.0.1:5000/websub/{os.environ.get("WEBSUB_TOKEN")}', data=lines.encode("utf-8"))
    logging.info(r)


def test_delete():
    with open(os.path.join("tests", "delete.xml"), encoding='utf-8') as f:
        lines = "".join(f.readlines())

        logging.debug(lines)
    r = requests.post(f'http://127.0.0.1:5000/websub/{os.environ.get("WEBSUB_TOKEN")}', data=lines.encode("utf-8"))
    logging.info(r)