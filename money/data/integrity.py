from typing import Any

from sqlalchemy import Table
from sqlalchemy.engine import Row, Connection

from g3b1_data.entities import EntTy, ET
from g3b1_data.integrity import orm
from money.data.enums import Crcy
from money.data.model import Owner, ENT_TY_money_owner, ENT_TY_money_accnt, Accnt, Categ, ENT_TY_money_categ, \
    ENT_TY_money, Money


def from_row_owner(row: Row) -> Owner:
    return Owner(row['chat_id'], row['bkey'], row['id'])


def from_row_categ(row: Row) -> Categ:
    return Categ(row['chat_id'], row['bkey'], row['emoji'], row['id'])


def from_row_money(row: Row, repl_dct: dict) -> Money:
    return Money(
        repl_dct.get('accnt_id', row['accnt_id']),
        repl_dct.get('categ_id', row['categ_id']),
        Crcy.fin(row['crcy']), row['amnt'], row['id']
    )


def from_row_accnt(row: Row, repl_dct: dict) -> Accnt:
    return Accnt(row['chat_id'], row['bkey'],
                 repl_dct.get('owner_id', row['owner_id']),
                 Crcy.fin(row['crcy']), row['id'])


def fetch_fk_ent(con: Connection, tbl: Table, row: Row, repl_dct=None) -> dict[str, Any]:
    return orm(con, tbl, row, from_row_any, repl_dct)


def from_row_any(ent_ty: EntTy[ET], row: Row, repl_dct: dict) -> ET:
    if ent_ty == ENT_TY_money_owner:
        return from_row_owner(row)
    elif ent_ty == ENT_TY_money_categ:
        return from_row_categ(row)
    elif ent_ty == ENT_TY_money_accnt:
        return from_row_accnt(row, repl_dct)
    elif ent_ty==ENT_TY_money:
        return from_row_money(row, repl_dct)


    return row['id']
