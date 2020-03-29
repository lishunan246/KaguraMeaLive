# coding: utf-8

import json

from flask import request
from telegram import Bot, Update
from telegram.ext import CommandHandler, CallbackContext
from telegram.ext import Dispatcher
from telegram.ext import MessageHandler, Filters

from KaguraMeaLive import app

b = Bot(app.config["TELEGRAM_BOT_TOKEN"])


def start(update: Update, context: CallbackContext):
    app.logger.info(f'start: {update}')
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text="欢迎。")


def echo(update: Update, context: CallbackContext):
    app.logger.info(f'echo: {update}')
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text="这个我不懂。")


def unknown(update: Update, context: CallbackContext):
    app.logger.info(f'unknown: {update}')
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text="这个我不懂。")


def enable(update: Update, context: CallbackContext):
    app.logger.info(f'enable: {update}')
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text="提醒已启用。")


def disable(update: Update, context: CallbackContext):
    app.logger.info(f'disable: {update}')
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text="提醒已停用。")


def status(update: Update, context: CallbackContext):
    app.logger.info(f'status: {update}')
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text='提醒开启')


def help_(update: Update, context: CallbackContext):
    app.logger.info(f'help: {update}')
    bot = context.bot
    bot.send_message(chat_id=update.message.chat_id, text="/enable 启用提醒\n/disable 关闭提醒\n /status 查看状态")


def setup():
    d = Dispatcher(b, None, workers=0, use_context=True)

    start_handler = CommandHandler('start', start)
    d.add_handler(start_handler)
    enable_handler = CommandHandler('enable', enable)
    d.add_handler(enable_handler)
    disable_handler = CommandHandler('disable', disable)
    d.add_handler(disable_handler)
    status_handler = CommandHandler('status', status)
    d.add_handler(status_handler)
    help_handler = CommandHandler('help', help_)
    d.add_handler(help_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    d.add_handler(echo_handler)

    # This handler must be added last.
    unknown_handler = MessageHandler(Filters.command, unknown)
    d.add_handler(unknown_handler)
    return d


dispatcher = setup()


@app.route(f'/telegram_bot/{app.config["TELEGRAM_BOT_TOKEN"]}', methods=['POST'])
def answer_telegram():
    data = request.get_data().decode("utf-8")
    app.logger.info(f'{data}')

    update = Update.de_json(json.loads(data), b)
    dispatcher.process_update(update)
    return ''


@app.route(f'/telegram_bot/{app.config["TELEGRAM_BOT_TOKEN"]}', methods=['GET'])
def answer_telegram_get():
    return '¿'
