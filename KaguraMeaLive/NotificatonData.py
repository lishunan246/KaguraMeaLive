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
    title_zh: str = ""
    action: str = ""
    publish_time: datetime = None
    delete_time: datetime = None
    update_time: datetime = None
    livestreaming_details: LiveStreamingDetails = None

    def __str__(self):
        if self.action == "delete":
            return f"{self.channel_name} deleted a video: " \
                   f"https://www.youtube.com/watch?v={self.video_id} @{self.delete_time}"
        elif self.action == "update":
            return f"{self.channel_name} updated a video '{self.title}': " \
                   f"https://www.youtube.com/watch?v={self.video_id} " \
                   f"publish @{self.publish_time}, " \
                   f"update @{self.update_time}"
        else:
            return super().__str__()

    def get_message_text(self) -> str:
        assert self.livestreaming_details.isLiveStream
        return f"{self.channel_name}添加了新直播。\n" \
               f"{self.video_url}\n" \
               f"预定开始时间：{self.livestreaming_details.scheduledStartTime}\n" \
               f"标题：{self.title}\n" \
               f"翻译：{self.title_zh}\n"
