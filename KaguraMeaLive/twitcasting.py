# coding：utf-8

import time
from dataclasses import dataclass
from urllib.parse import unquote

import requests

from KaguraMeaLive import db, app
from .schema import TwitcastingChannel
from .translate import translate


@dataclass
class TwitCastingMessage:
    id: str = ""
    name: str = ""
    title: str = ""
    title_cn: str = ""

    def get_message_text(self) -> str:
        text = f'{self.name}正在TwitCasting直播\n' \
               f'https://twitcasting.tv/{id}\n'
        if self.title:
            text += f'标题：{self.title}\n'
        if self.title_cn:
            text += f'翻译：{self.title_cn}\n'
        return text


def get_title(u: str) -> str:
    r = requests.get("https://twitcasting.tv/streamchecker.php?u=%s&v=999", params={
        'u': u,
        'v': 999,
    }, timeout=1)
    r.raise_for_status()
    res = r.text
    title = unquote(res.split('\t')[7])
    return title if title != '0' else ""


def scan_tc(c: TwitcastingChannel) -> None:
    r = requests.get("https://twitcasting.tv/streamserver.php", params={
        "target": c.id,
        "mode": "client"
    }, timeout=1)
    r.raise_for_status()
    j = r.json()
    is_live_now = j["movie"]["live"]
    if is_live_now and not c.is_live:
        # todo alert
        m = TwitCastingMessage(
            id=c.id,
            name=c.name,
        )
        try:
            m.title = get_title(c.id)
            if m.title:
                m.title_cn = translate(m.title, app.config['TRANSLATE_APPID'], app.config['TRANSLATE_SECRET'])

        except Exception as e:
            app.logger.error(f'when get title: {e}')

    c.is_live = is_live_now
    db.session.merge(c)
    db.session.commit()


def scan_twitcasting() -> None:
    for c in db.session.query(TwitcastingChannel).filter_by(is_deleted=False).all():
        try:
            scan_tc(c)
        except Exception as e:
            app.logger.error(f'when scan TwitCasting channel {c.id}, {e}')

        time.sleep(1.0)

    app.logger.info('All TwitCasting channels scanned.')
