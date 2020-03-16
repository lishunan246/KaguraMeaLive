# coding: utf-8

import logging
import os

import requests


def test_answer():
    with open(os.path.join("tests", "update.xml"), encoding='utf-8') as f:
        lines = "".join(f.readlines())

        logging.info(lines)
    r = requests.post(f'http://127.0.0.1:5000/WebSub/{os.environ.get("WEBSUB_TOKEN")}', data=lines.encode("utf-8"))
    logging.info(r)
