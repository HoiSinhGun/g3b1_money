from dataclasses import asdict
from enum import Enum
from typing import Any, Dict

from sqlalchemy import Table, select, insert, or_
from sqlalchemy.engine import Result, Row, CursorResult, Connection

from g3b1_cfg.tg_cfg import G3Context
from g3b1_data import settings
from g3b1_data.entities import ET, EntId, EntTy
from g3b1_data.model import G3Result
from g3b1_data.tg_db import fetch_id
from money.data import eng_MONEY, md_MONEY
from money.data.integrity import from_row_any, fetch_fk_ent
from money.data.model import MoneyMp, ENT_TY_money, ENT_TY_money_mp, Money, Accnt


def read_setting(setng_dct: dict[str, ...]) -> G3Result:
    with eng_MONEY.connect() as con:
        g3r = settings.read_setting(con, md_MONEY, setng_dct)
        return g3r


def iup_setting(setng_dct: dict[str, ...]) -> G3Result:
    with eng_MONEY.connect() as con:
        settings.iup_setting(con, md_MONEY, setng_dct)
        return G3Result()


def sel_ent_ty(ent_id: EntId[ET], con: Connection = None) -> G3Result[ET]:
    # noinspection PyShadowingNames
    def wrapped(con: Connection):
        tbl: Table = md_MONEY.tables[ent_id.ent_ty.tbl_name]
        c = tbl.columns
        stmnt = (select(tbl).
                 where(c['id'] == ent_id.id))
        rs: Result = con.execute(stmnt)
        row: Row = rs.first()
        repl_dct = fetch_fk_ent(con, tbl, row, {})
        ent: ET = from_row_any(ent_id.ent_ty, row, repl_dct)
        return G3Result(0, ent)

    if not con:
        with eng_MONEY.connect() as con:
            return wrapped(con)
    else:
        return wrapped(con)


def sel_ent_ty_li(ent_ty: EntTy) -> list[Row]:
    tbl: Table = md_MONEY.tables[ent_ty.tbl_name]
    chat_id = G3Context.upd.effective_chat.id
    c = tbl.columns
    with eng_MONEY.begin() as con:
        if 'chat_id' in c:
            stmnt = (select(tbl).
                     where(c['chat_id'] == chat_id))
        else:
            stmnt = (select(tbl))
        rs: CursorResult = con.execute(stmnt)
        return rs.fetchall()


def ins_ent_ty(ent: Any) -> G3Result[Any]:
    val_dct = asdict(ent)
    new_val_dct: dict = {}
    for k, v in val_dct.items():
        if v is None:
            continue
        if isinstance(v, Enum):
            new_val_dct[k] = v.value
        elif isinstance(v, Dict):
            new_val_dct[f'{k}_id'] = v['id_']
        else:
            new_val_dct[k] = v
    with G3Context.eng.begin() as con:
        tbl: Table = G3Context.md.tables[ent.ent_ty().tbl_name]
        stmnt = (insert(tbl).
                 values(new_val_dct))
        rs: CursorResult = con.execute(stmnt)
        if not (id_ := fetch_id(con, rs, tbl.name)):
            return G3Result(4)
        g3r = sel_ent_ty(EntId(ent.ent_ty(), id_), con)
        return g3r


def ins_money(money: Money, con: Connection = None) -> Money:
    # noinspection PyShadowingNames
    def wrapped(con: Connection) -> Money:
        tbl: Table = md_MONEY.tables[ENT_TY_money.tbl_name]
        stmnt = (insert(tbl).
                 values(accnt_id=money.accnt.id_, categ_id=money.categ.id_,
                        amnt=money.amnt, crcy=money.crcy.value))
        rs: CursorResult = con.execute(stmnt)
        if not (id_ := fetch_id(con, rs, tbl.name)):
            # noinspection PyTypeChecker
            return
        return sel_ent_ty(EntId(ENT_TY_money, id_), con).result

    if con:
        return wrapped(con)
    else:
        with eng_MONEY.begin() as con:
            return wrapped(con)


def fin_money_mp(accnt: Accnt) -> list[MoneyMp]:
    with eng_MONEY.begin() as con:
        tbl: Table = md_MONEY.tables[ENT_TY_money_mp.tbl_name]
        tbl_mny_src: Table = md_MONEY.tables[ENT_TY_money.tbl_name].alias("mny_src")
        tbl_mny_trg: Table = md_MONEY.tables[ENT_TY_money.tbl_name].alias("mny_trg")
        j = tbl.join(tbl_mny_src, tbl.c.src__money_id == tbl_mny_src.c.id).join(tbl_mny_trg,
                                                                                tbl.c.trg__money_id == tbl_mny_trg.c.id)
        stmnt = select(tbl.c.id).select_from(j).where(
            or_(
                tbl_mny_src.c.accnt_id == accnt.id_,
                tbl_mny_trg.c.accnt_id == accnt.id_
            )
        ).group_by(tbl.c.id)
        rs: CursorResult = con.execute(stmnt)
        row_li: list[Row] = rs.fetchall()
        money_mp_li: list[MoneyMp] = [sel_money_mp(row['id'], con) for row in row_li]
        return money_mp_li


def sel_money_mp(id_: int, con: Connection = None) -> MoneyMp:
    # noinspection PyShadowingNames
    def wrapped(con: Connection) -> MoneyMp:
        tbl: Table = md_MONEY.tables[ENT_TY_money_mp.tbl_name]
        stmnt = (select(tbl).where(tbl.c.id == id_))
        rs: CursorResult = con.execute(stmnt)
        row: Row = rs.first()
        src_money: Money = sel_ent_ty(EntId(ENT_TY_money, row['src__money_id']), con).result
        trg_money: Money = sel_ent_ty(EntId(ENT_TY_money, row['trg__money_id']), con).result
        money_mp = MoneyMp(src_money, trg_money, row['user_id'], row['descr'], row['tst'], id_)
        return money_mp

    if con:
        return wrapped(con)
    else:
        with eng_MONEY.begin() as con:
            return wrapped(con)


def ins_money_mp(money_mp: MoneyMp) -> MoneyMp:
    src_money: Money = money_mp.src__money
    trg_money: Money = money_mp.trg__money
    with eng_MONEY.begin() as con:
        src_money = ins_money(src_money, con)
        trg_money = ins_money(trg_money, con)

        tbl: Table = md_MONEY.tables[ENT_TY_money_mp.tbl_name]
        stmnt = (insert(tbl).
                 values(src__money_id=src_money.id_, trg__money_id=trg_money.id_,
                        user_id=money_mp.user_id, descr=money_mp.descr))
        rs: CursorResult = con.execute(stmnt)
        if not (id_ := fetch_id(con, rs, tbl.name)):
            # noinspection PyTypeChecker
            return
        return sel_money_mp(id_, con)
