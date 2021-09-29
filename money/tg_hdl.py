from dataclasses import asdict

from sqlalchemy.engine import Row
from telegram import Update
from telegram.ext import CallbackContext

from g3b1_cfg.tg_cfg import G3Context, sel_g3_m
from g3b1_data import settings
from g3b1_data.elements import ELE_TY_su__user_id, ELE_TY_out__chat_id
from g3b1_data.entities import G3_M_MONEY
from g3b1_data.model import MenuIt
from g3b1_serv import generic_hdl
from g3b1_serv.generic_hdl import send_menu_keyboard
from g3b1_serv.tg_reply import bold
from g3b1_serv.utilities import upd_extract_chat_user_id
from g3b1_ui.model import TgUIC
from money.config.cfg import MoneyCfg
from money.data import eng_MONEY, md_MONEY
from money.data.db import sel_ent_ty_li
from money.data.model import Owner, Categ, Accnt, ELE_TY_src__accnt_id, ELE_TY_trg__accnt_id, ENT_TY_money_categ
from money.serv.services import accnt_01, owner_01, categ_01, money_transfer, accnt_money_li
from subscribe.data.db import eng_SUB, md_SUB
from subscribe.serv import services as sub_services


@generic_hdl.tg_handler()
def cmd_li_user(upd: Update, chat_id: int) -> None:
    """List the users id/uname for the bot"""
    sub_services.tbl_chat_user_send(upd, chat_id, eng_MONEY, md_MONEY)


@generic_hdl.tg_handler()
def cmd_su_exit() -> None:
    """Exit SU (switch user)"""
    setng = settings.cu_setng(ELE_TY_su__user_id)
    setng['user_id'] = G3Context.user_id()
    settings.iup_setting(eng_SUB, md_SUB, setng)


@generic_hdl.tg_handler()
def cmd_su(req__user_id: id) -> None:
    """SU (switch user)"""
    setng = settings.cu_setng(ELE_TY_su__user_id, req__user_id)
    setng['user_id'] = G3Context.user_id()
    settings.iup_setting(eng_SUB, md_SUB, setng)


@generic_hdl.tg_handler()
def cmd_out_chat(trg_chat_id: str) -> None:
    """Set chat for output"""
    setng = settings.cu_setng(ELE_TY_out__chat_id, trg_chat_id)
    setng['user_id'] = G3Context.user_id()
    settings.iup_setting(eng_SUB, md_SUB, setng)
    TgUIC.uic.cmd_sccs()


@generic_hdl.tg_handler()
def cmd_menu(upd: Update, ctx: CallbackContext, mi_str: str) -> None:
    m_cfg = MoneyCfg.get_current()
    mi_list: list[MenuIt]
    if mi_str and not mi_str.endswith(':back'):
        mi = m_cfg.menu.mi_by_id(mi_str)
        cmd_dct = sel_g3_m(G3_M_MONEY).cmd_dct
        if not mi:
            mi_str_split = mi_str.split(' ', 1)
            g3_cmd = cmd_dct[mi_str_split[0]]
            ctx.args = mi_str_split[1].split(' ')
            g3_cmd.handler(upd, ctx)
            return
        if mi.g3_cmd:
            g3_cmd_info_str = mi.g3_cmd.name + '_info'
            if g3_cmd_info_str in cmd_dct.keys():
                g3_cmd_info = cmd_dct[g3_cmd_info_str]
                g3_c_dct = G3Context.as_dict()
                g3_cmd_info.handler(upd, ctx)
                G3Context.from_dict(g3_c_dct)
            else:
                send_str = ' '.join([arg.arg for arg in mi.g3_cmd.extra_args() if arg.f_current == False])
                if send_str:
                    TgUIC.uic.send(send_str)
                else:
                    mi.g3_cmd.handler(upd, ctx)
            if mi.g3_cmd.name != 'transfer':
                return
            row_li: list[Row] = sel_ent_ty_li(ENT_TY_money_categ)
            mi_list = []
            g3_cmd_categ_04 = cmd_dct['categ_04']
            for idx, row in enumerate(row_li):
                if idx and idx % 2 == 0:
                    mi_list.append(MenuIt(str(idx), '\n'))
                emoji = ''
                if row["emoji"]:
                    emoji = row["emoji"] + ' '
                mi_list.append(
                    MenuIt(f'{g3_cmd_categ_04.name} {row["id"]}', f'{emoji}{row["bkey"]}', None, g3_cmd_categ_04, None,
                           row['id']))
            mi_list.append(MenuIt('-777', '\n'))
            mi_list.append(MenuIt('transfer:back', lbl='Back', g3_cmd=cmd_dct['menu'])
                           )
        else:
            mi_list = mi.it_li
    else:
        mi_list = m_cfg.menu.first_level()

    root_str = mi_str
    if not root_str:
        root_str = m_cfg.g3m_str
    send_menu_keyboard(root_str, mi_list)


@generic_hdl.tg_handler()
def cmd_owner_01(req__bkey: str) -> Owner:
    """Create owner"""
    return owner_01(req__bkey)


@generic_hdl.tg_handler()
def cmd_owner_03(cur__owner: Owner) -> None:
    """Display selected owner"""
    if cur__owner:
        TgUIC.uic.send(asdict(cur__owner))
    else:
        TgUIC.uic.no_data()


@generic_hdl.tg_handler()
def cmd_owner_04(req__owner: Owner) -> Owner:
    """Select owner"""
    if req__owner:
        TgUIC.uic.cmd_sccs()
        return req__owner
    else:
        TgUIC.uic.cmd_fail()


@generic_hdl.tg_handler()
def cmd_categ_01(req__bkey: str, emoji: str) -> Categ:
    """Create categ"""
    return categ_01(req__bkey, emoji)


@generic_hdl.tg_handler()
def cmd_categ_03(cur__categ: Categ) -> None:
    """Display selected categ"""
    if cur__categ:
        TgUIC.uic.send(asdict(cur__categ))
    else:
        TgUIC.uic.no_data()


@generic_hdl.tg_handler()
def cmd_categ_04(req__categ: Categ) -> Categ:
    """Select categ"""
    if req__categ:
        TgUIC.uic.cmd_sccs()
        return req__categ
    else:
        TgUIC.uic.cmd_fail()


@generic_hdl.tg_handler()
def cmd_accnt_01(req__bkey: str, cur__owner: Owner) -> Accnt:
    """Create accnt"""
    return accnt_01(req__bkey, cur__owner)


@generic_hdl.tg_handler()
def cmd_accnt_03(cur__accnt: Accnt) -> None:
    """Display selected accnt"""
    if cur__accnt:
        TgUIC.uic.send(str(cur__accnt.to_dict()))
    else:
        TgUIC.uic.no_data()


@generic_hdl.tg_handler()
def cmd_accnt_04(req__accnt: Accnt) -> Accnt:
    """Pick accnt"""
    if req__accnt:
        TgUIC.uic.cmd_sccs()
        return req__accnt
    else:
        TgUIC.uic.cmd_fail()


@generic_hdl.tg_handler()
def cmd_accnt_src(uname: str, cur__accnt: Accnt) -> None:
    """Pick src__accnt_id for chat-user"""
    chat_id, user_id = upd_extract_chat_user_id()
    for_user_id = sub_services.for_user(uname, user_id)
    settings.ent_to_setng((chat_id, for_user_id), cur__accnt, ELE_TY_src__accnt_id)
    TgUIC.uic.cmd_sccs()


@generic_hdl.tg_handler()
def cmd_accnt_trg(uname: str, cur__accnt: Accnt) -> None:
    """Pick src__accnt_id for chat-user"""
    chat_id, user_id = upd_extract_chat_user_id()
    for_user_id = sub_services.for_user(uname, user_id)
    settings.ent_to_setng((chat_id, for_user_id), cur__accnt, ELE_TY_trg__accnt_id)
    TgUIC.uic.cmd_sccs()


@generic_hdl.tg_handler()
def cmd_accnt_mny_li(cur__accnt: Accnt) -> None:
    """View all transfers of the cur__accnt"""
    tg_tbl, total = accnt_money_li(cur__accnt)
    TgUIC.uic.send_tg_tbl(tg_tbl, bold(f'Total: VND {total}'))


@generic_hdl.tg_handler()
def cmd_accnt_bal_01(cur__accnt: Accnt, amnt: float) -> None:
    """Create accnt_bal"""
    pass


@generic_hdl.tg_handler()
def cmd_accnt_bal_12(cur__accnt: Accnt) -> None:
    """Calculate accnt_bal"""
    pass


@generic_hdl.tg_handler()
def cmd_transfer(req__amnt: str, descr: str, cur__src__accnt: Accnt, cur__trg__accnt: Accnt, cur__categ: Categ) -> None:
    """Create money_mp"""
    req__amnt = req__amnt.lower()
    amnt_str = ''.join(filter(str.isdigit, req__amnt))
    if not req__amnt.startswith(amnt_str) or len(req__amnt) - len(amnt_str) > 1:
        TgUIC.uic.cmd_fail()
        return
    if amnt_str != req__amnt and not req__amnt.endswith('k') and not req__amnt.endswith('m'):
        TgUIC.uic.cmd_fail()
        return
    amnt = int(amnt_str)
    if req__amnt.endswith('k'):
        amnt *= 1000
    if req__amnt.endswith('m'):
        amnt *= 1000000
    money_transfer(cur__src__accnt, cur__trg__accnt, cur__categ, amnt, descr=descr)
    TgUIC.uic.cmd_sccs()
    cmd_accnt_mny_li(G3Context.upd, G3Context.ctx)


@generic_hdl.tg_handler()
def cmd_transfer_swap(uname: str, cur__src__accnt: Accnt, cur__trg__accnt: Accnt) -> None:
    """Swap src__accnt_id for chat-user"""
    chat_id, user_id = upd_extract_chat_user_id()
    for_user_id = sub_services.for_user(uname, user_id)
    settings.ent_to_setng((chat_id, for_user_id), cur__src__accnt, ELE_TY_trg__accnt_id)
    settings.ent_to_setng((chat_id, for_user_id), cur__trg__accnt, ELE_TY_src__accnt_id)
    TgUIC.uic.cmd_sccs()


@generic_hdl.tg_handler()
def cmd_transfer_info(cur__src__accnt: Accnt, cur__trg__accnt: Accnt, cur__categ: Categ) -> None:
    bkey = '?'
    if cur__categ:
        bkey = cur__categ.bkey
    send_str = f'Transfer from -> to: {bold(cur__src__accnt.bkey + " --> " + cur__trg__accnt.bkey)}\n' \
               f'Category: {bold(bkey)}\n' \
               f'Enter amount in VND and a description text, eg 200k water'
    TgUIC.uic.send(send_str)
