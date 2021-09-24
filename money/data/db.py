from dataclasses import asdict
from enum import Enum
from typing import Any, Dict

from sqlalchemy import Table, select, insert
from sqlalchemy.engine import Result, Row, CursorResult, Connection

from g3b1_data import settings
from g3b1_data.entities import ET, EntId
from g3b1_data.model import G3Result
from g3b1_data.tg_db import fetch_id
from money.data import eng_MONEY, md_MONEY
from money.data.integrity import from_row_any, fetch_fk_ent


def read_setting(setng_dct: dict[str, ...]) -> G3Result:
    with eng_MONEY.connect() as con:
        g3r = settings.read_setting(con, md_MONEY, setng_dct)
        return g3r


def iup_setting(setng_dct: dict[str, ...]) -> G3Result:
    with eng_MONEY.connect() as con:
        settings.iup_setting(con, md_MONEY, setng_dct)
        return G3Result()


def sel_ent_ty(ent_id: EntId[ET], con: Connection = None) -> G3Result[ET]:
    def wrapped(_con: Connection):
        tbl: Table = md_MONEY.tables[ent_id.ent_ty.tbl_name]
        c = tbl.columns
        stmnt = (select(tbl).
                 where(c['id'] == ent_id.id))
        rs: Result = _con.execute(stmnt)
        row: Row = rs.fetchone()
        repl_dct = fetch_fk_ent(_con, tbl, row, {})
        ent: ET = from_row_any(ent_id.ent_ty, row, repl_dct)
        return G3Result(0, ent)
    if not con:
        with eng_MONEY.connect() as con:
            return wrapped(con)
    else:
        return wrapped(con)


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
    with eng_MONEY.begin() as con:
        tbl: Table = md_MONEY.tables[ent.ent_ty().tbl_name]
        stmnt = (insert(tbl).
                 values(new_val_dct))
        rs: CursorResult = con.execute(stmnt)
        if not (id_ := fetch_id(con, rs, tbl.name)):
            return G3Result(4)
        return sel_ent_ty(EntId(ent.ent_ty(),id_), con)
