# coding:utf-8

from dataclasses import dataclass
from datetime import datetime

from .LiveStreamDetails import LiveStreamingDetails


@dataclass
class NotificationData:
    video_id: str
    video_url: str
    channel_name: str
    channel_id: str
    channel_url: str
    title: str = ""
    action: str = ""
    publish_time: datetime = None
    delete_time: datetime = None
    update_time: datetime = None
    livestreaming_details: LiveStreamingDetails = None

    def __str__(self):
        if self.action == "delete":
            return f"{self.channel_name} deleted a video: https://www.youtube.com/watch?v={self.video_id} @{self.delete_time}"
        elif self.action == "update":
            return f"{self.channel_name} updated a video '{self.title}': https://www.youtube.com/watch?v={self.video_id} publish @{self.publish_time}, update @{self.update_time}"
        else:
            return super().__str__()
