import logging
from datetime import datetime

from telegram import Update, User, Chat, constants
from telegram.ext import Dispatcher, CallbackContext

import money_main
import tg_hdl
from g3b1_data import tg_db
from g3b1_log.log import cfg_logger
from g3b1_test import test_utils

tg_chat_id: int = -579559871
tg_user_id: int = 1749165037

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)


def c(msg: str):
    # print(str(f'\n\n>>>{msg}\n'))
    dispatcher: Dispatcher = test_utils.setup(tg_hdl.__file__)
    user: User = User(tg_user_id, 'Gunnar', False)
    chat: Chat = Chat(tg_chat_id, constants.CHAT_GROUP)

    msg_callback = test_utils.MsgCallback()
    msg_callback.msg_li = []
    ext_id = tg_db.next_negative_ext_id(tg_chat_id, tg_user_id).result
    message = test_utils.MyMessage(ext_id, datetime.now(),
                                   chat=chat, from_user=user, reply_to_message=None)
    message.text = msg
    test_utils.MyMessage.msg_callback = msg_callback
    upd = Update(333, message)
    ctx: CallbackContext = CallbackContext(dispatcher)
    # bot_li: dict[str, dict] = db.bot_all()
    # ctx.bot: Bot = Bot(bot_li['trans']['token'])
    message.bot = ctx.bot
    ctx.bot.send_message = message.reply_html

    money_main.hdl_message(upd, ctx)
    for i in msg_callback.msg_li:
        print(i)


def main():
    a = 'go'
    while a != 'exit':
        # taking input from the user
        a = input()
        try:
            c(a)
        except Exception as e:
            logger.exception(e)


main()
