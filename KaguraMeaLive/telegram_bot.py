# coding: utf-8

from telegram import Bot

from KaguraMeaLive import db, app
from .NotificatonData import NotificationData
from .schema import Channel, Message


class TelegramBot:
    def __init__(self, token):
        self.bot = Bot(token)

    def alert(self, n: NotificationData):
        channel = db.session.query(Channel).filter_by(id=n.channel_id).one()
        text = n.get_message_text()

        for chat in channel.chats:
            try:
                app.logger.info(f"bot start handle chat: {chat.id} for {n.video_id}")

                message = db.session.query(Message).filter_by(chat_id=chat.id, video_id=n.video_id).one_or_none()
                if message:
                    if message.text != text:
                        app.logger.info(f"Message text is not same.")
                        self.bot.editMessageText(text, chat.id, message.id, disable_web_page_preview=True, timeout=1)
                        message.text = text
                        db.session.merge(message)
                        db.session.commit()
                    else:
                        app.logger.info("Message text is same.")
                else:
                    app.logger.info("Message text needs create.")
                    m = self.bot.send_message(chat.id, text, disable_web_page_preview=True, timeout=1)
                    message = Message(text=text, message_id=m.message_id, chat_id=chat.id, video_id=n.video_id)
                    db.session.merge(message)
                    db.session.commit()
                app.logger.info(f"bot handled chat: {chat.id} for {n.video_id}")

            except Exception as e:
                app.logger.error(f'when alert: {e}')
