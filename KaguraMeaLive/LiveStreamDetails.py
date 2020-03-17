# coding: utf-8


from dataclasses import dataclass
from datetime import datetime

import requests

from .utils import rfc3339_to_datetime


@dataclass
class LiveStreamingDetails:
    video_id: str
    actualStartTime: datetime = None
    scheduledStartTime: datetime = None
    concurrentViewers: int = 0
    activeLiveChatId: str = ""
    isLiveStream: bool = False

    def get(self, key: str) -> None:
        url = 'https://www.googleapis.com/youtube/v3/videos'
        params = {
            'part': 'liveStreamingDetails',
            'id': self.video_id,
            'key': key
        }

        r = requests.get(url, params=params, timeout=0.5)
        r.raise_for_status()
        json_str = r.json()
        items = json_str['items']
        if not items:
            return
        self.isLiveStream = "liveStreamingDetails" in items[0]
        d = items[0]['liveStreamingDetails']
        self.concurrentViewers = int(d.get("concurrentViewers", "0"))
        st = d.get("scheduledStartTime")
        if st:
            self.scheduledStartTime = rfc3339_to_datetime(st)
        ast = d.get("actualStartTime")
        if ast:
            self.actualStartTime = rfc3339_to_datetime(ast)
        self.activeLiveChatId = d.get("activeLiveChatId", "")
