from dataclasses import asdict

from telegram import Update
from telegram.ext import CallbackContext

from g3b1_data.model import MenuIt
from g3b1_serv import generic_hdl
from g3b1_serv.generic_hdl import send_menu_keyboard
from g3b1_ui.model import TgUIC
from money.config.cfg import MoneyCfg
from money.data import eng_MONEY, md_MONEY
from money.data.model import Owner, Categ, Accnt
from money.serv.services import owner_01
from subscribe.serv import services as sub_services


@generic_hdl.tg_handler()
def cmd_li_user(upd: Update, chat_id: int) -> None:
    """List the users id/uname for the bot"""
    sub_services.tbl_chat_user_send(upd, chat_id, eng_MONEY, md_MONEY)


@generic_hdl.tg_handler()
def cmd_menu(upd: Update, ctx: CallbackContext, mi_str: str) -> None:
    m_cfg = MoneyCfg.get_current()
    mi_list: list[MenuIt]
    if mi_str:
        mi = m_cfg.menu.mi_by_id(mi_str)
        if mi.g3_cmd:
            # Set cmd default
            send_str = ' '.join([arg.arg for arg in mi.g3_cmd.extra_args() if arg.f_current == False])
            if send_str:
                TgUIC.uic.send(send_str)
            else:
                mi.g3_cmd.handler(upd, ctx)
            return
        mi_list = mi.it_li
    else:
        mi_list = m_cfg.menu.first_level()

    send_menu_keyboard(m_cfg.g3m_str, mi_list)


@generic_hdl.tg_handler()
def cmd_owner_01(req__bkey: str) -> Owner:
    """Create owner"""
    return owner_01(req__bkey)


@generic_hdl.tg_handler()
def cmd_owner_03(cur__owner: Owner) -> None:
    """Display selected owner"""
    TgUIC.uic.send(asdict(cur__owner))


@generic_hdl.tg_handler()
def cmd_owner_04(req__owner: Owner) -> Owner:
    """Select owner"""
    TgUIC.uic.cmd_sccs()
    return req__owner


@generic_hdl.tg_handler()
def cmd_categ_01(req__bkey: str, uname: str) -> None:
    """Create categ"""
    pass


@generic_hdl.tg_handler()
def cmd_categ_03() -> None:
    """Display selected categ"""
    pass


@generic_hdl.tg_handler()
def cmd_categ_04(req__categ: Categ) -> None:
    """Select categ"""
    pass


@generic_hdl.tg_handler()
def cmd_accnt_01(cur__owner: Owner, req__bkey: str, uname: str) -> None:
    """Create accnt"""
    pass


@generic_hdl.tg_handler()
def cmd_accnt_03() -> None:
    """Display selected accnt"""
    pass


@generic_hdl.tg_handler()
def cmd_accnt_04(req__accnt: Accnt) -> None:
    """Select accnt"""
    pass


@generic_hdl.tg_handler()
def cmd_accnt_bal_01(cur__accnt: Accnt, amnt: float) -> None:
    """Create accnt_bal"""
    pass


@generic_hdl.tg_handler()
def cmd_accnt_bal_12(cur__accnt: Accnt) -> None:
    """Calculate accnt_bal"""
    pass


@generic_hdl.tg_handler()
def cmd_transfer(req_bkey: str, req__owner: Owner) -> None:
    """Create account"""
    pass
