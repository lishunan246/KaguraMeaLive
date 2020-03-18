# coding: utf-8
import hashlib
import random

import requests


def translate(q: str, appid: str, secret: str) -> str:
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secret
    sign = hashlib.md5(sign.encode()).hexdigest()
    r = requests.get(
        "https://api.fanyi.baidu.com/api/trans/vip/translate",
        params={
            "appid": appid,
            "q": q,
            "from": "jp",
            "to": "zh",
            "salt": salt,
            "sign": sign
        },
        timeout=1.0
    )
    j = r.json()
    return j['trans_result'][0]['dst']
