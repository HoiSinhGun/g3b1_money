from typing import Any

from g3b1_cfg.tg_cfg import G3Context
from g3b1_data.elements import ELE_TY_amnt, ELE_TY_descr
from g3b1_serv import utilities
from g3b1_serv.generic_mdl import TgTable, TgColumn, TableDef
from g3b1_serv.utilities import row_li_2_tbl
from g3b1_ui.model import TgUIC
from money.data.db import ins_ent_ty, ins_money_mp, fin_money_mp
from money.data.enums import Crcy
from money.data.model import Owner, Accnt, Categ, AccntBal, MoneyMp, Money, ELE_TY_money_categ_id, \
    ELE_TY_crcy


def owner_01(bkey: str) -> Owner:
    chat_id, user_id = utilities.upd_extract_chat_user_id()
    owner: Owner = Owner(chat_id, bkey)
    g3r = ins_ent_ty(owner)
    TgUIC.uic.cmd_sccs()
    return g3r.result


def categ_01(bkey: str, emoji:str) -> Categ:
    chat_id, user_id = utilities.upd_extract_chat_user_id()
    categ: Categ = Categ(chat_id, bkey, emoji)
    g3r = ins_ent_ty(categ)
    TgUIC.uic.cmd_sccs()
    return g3r.result


def accnt_01(bkey: str, owner: Owner, crcy=Crcy.VND) -> Accnt:
    chat_id, user_id = utilities.upd_extract_chat_user_id()
    accnt: Accnt = Accnt(chat_id, bkey, owner, crcy)
    g3r = ins_ent_ty(accnt)
    TgUIC.uic.cmd_sccs()
    return g3r.result


def accnt_bal_01(accnt: Accnt, amnt=0, crcy=Crcy.VND) -> AccntBal:
    accnt_bal: AccntBal = AccntBal(accnt, amnt, crcy)
    g3r = ins_ent_ty(accnt_bal)
    TgUIC.uic.cmd_sccs()
    return g3r.result


def accnt_money_li(accnt: Accnt) -> (TgTable, int):
    money_mp_li: list[MoneyMp] = fin_money_mp(accnt)
    ent_ty = ELE_TY_money_categ_id.ent_ty
    tg_col_li: list[TgColumn] = [
        TgColumn(ent_ty.id, 1, ELE_TY_money_categ_id.descr, 20),
        TgColumn(ELE_TY_crcy.id_, 2, ELE_TY_crcy.descr, 3),
        TgColumn(ELE_TY_amnt.id_, 3, ELE_TY_amnt.descr, 13),
        TgColumn(ELE_TY_descr.id_, 3, ELE_TY_descr.descr, 20)
    ]
    row_li: list[dict[str, Any]] = []
    total: int = 0
    for mmp in money_mp_li:
        money: Money
        if mmp.src__money.accnt == accnt:
            money = mmp.src__money
            money.amnt *= -1
        else:
            money = mmp.trg__money
        row_li.append({ent_ty.id: money.categ.bkey,
                       ELE_TY_crcy.id_: money.crcy.value,
                       ELE_TY_amnt.id_: money.amnt,
                       ELE_TY_descr.id_: mmp.descr})
        total += money.amnt

    tbl_def = TableDef(tg_col_li)
    tg_tbl: TgTable = row_li_2_tbl(row_li, tbl_def)
    return tg_tbl, total


def money_transfer(src__accnt: Accnt, trg__accnt: Accnt, categ: Categ, amnt: int, crcy=Crcy.VND, descr='') -> MoneyMp:
    src_money = Money(src__accnt, categ, crcy, amnt)
    trg_money = Money(trg__accnt, categ, crcy, amnt)
    money_mp = MoneyMp(src_money, trg_money, G3Context.for_user_id(), descr)
    return ins_money_mp(money_mp)
