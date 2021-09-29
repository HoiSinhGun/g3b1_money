import logging

from telegram import Update
from telegram.ext import CallbackContext

from g3b1_cfg.tg_cfg import sel_g3_m, G3Context
from g3b1_data import tg_db
from g3b1_data.entities import EntTy
from g3b1_log.log import cfg_logger
from g3b1_serv import tgdata_main, utilities, generic_hdl
from g3b1_serv.generic_hdl import init_g3_ctx
from g3b1_serv.utilities import G3Command
from g3b1_serv.utilities import is_msg_w_cmd
from money import tg_hdl
from money.data import eng_MONEY, md_MONEY
from subscribe.serv import services as sub_services

logger = cfg_logger(logging.getLogger(__name__), logging.WARN)


def hdl_message(upd: Update, ctx: CallbackContext) -> None:
    """HDL Message"""
    init_g3_ctx(upd, ctx)

    message = upd.effective_message
    cmd_dct = sel_g3_m(G3Context.g3_m_str).cmd_dct
    text = message.text
    matched: bool = False
    if G3Context.g3_m_str == 'money' and text == '.m.':
        text = '.menu'
    # noinspection PyTypeChecker
    g3_cmd: G3Command = None
    is_command_explicit = True
    cmd_prefix = ''
    if not is_msg_w_cmd(text):
        ent_ty = EntTy.by_cmd_prefix(cmd_prefix)
        if ent_ty and ent_ty.but_cmd_def:
            text = ent_ty.get_cmd_by_but(text)
        else:
            # prefix with translates default cmd
            cmd_default = sub_services.sel_setng_cmd_default(f_shorten=True)
            if cmd_default:
                text = f'.{cmd_default} {text}'
        is_command_explicit = False
    if text.startswith('..') and not text.startswith('...'):
        pass
    elif text.startswith('.'):
        if text.strip() == '.':
            latest_cmd = utilities.read_latest_cmd(upd, sel_g3_m(G3Context.g3_m_str))
            text = latest_cmd.text
            is_command_explicit = False
            # pass text = utilities
        if text.startswith('...'):
            if cmd_prefix:
                text = text.replace('...', cmd_prefix, 1)
        word_li = text.split(' ')
        test_if_cmd = text[1:].strip()
        if len(word_li) > 1:
            test_if_cmd = ''
            if word_li[0] != '.':
                #  the space must occur after 2nd letter
                #  the first entry after removing the dot must be a valid cmd name
                #  or no command has been executed
                test_if_cmd = word_li[0][1:]
        test_if_cmd = test_if_cmd.replace('.', '_')
        if test_if_cmd in cmd_dct.keys():
            g3_cmd = cmd_dct[test_if_cmd]
            logger.debug(f'CMD: {g3_cmd}')
            if len(word_li) > 1:
                ctx.args = word_li[1:]
            g3_cmd.handler(upd, ctx)
            matched = True
        elif test_if_cmd.endswith('33'):
            # list
            ent_str = test_if_cmd[:-3]
            ent_ty = EntTy.by_id(ent_str)
            if ent_ty:
                # Generic list command on entity of type ent_ty
                generic_hdl.cmd_ent_ty_33_li(upd, ctx, ent_ty=ent_ty)
        logger.debug(f'matched: {matched}')
    logger.debug(f"Handle message {message.message_id}")
    message.bot = ctx.bot
    if matched:
        g3_cmd_long_str = g3_cmd.long_name
    else:
        g3_cmd_long_str = None
        is_command_explicit = False
    tg_db.synchronize_from_message(message, g3_cmd_long_str, is_command_explicit)


def start_bot():
    """Run the bot."""
    tgdata_main.start_bot(tg_hdl.__file__, eng=eng_MONEY, md=md_MONEY, hdl_for_message=hdl_message)


def main() -> None:
    start_bot()
    print('Finished')


if __name__ == '__main__':
    main()
