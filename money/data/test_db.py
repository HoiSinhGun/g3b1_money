from dataclasses import asdict
from enum import Enum
from typing import Dict
from unittest import TestCase

from g3b1_data.entities import EntId, EntTy
from money.data import db
from money.data.model import ENT_TY_money_owner, ENT_TY_money_accnt


class Test(TestCase):
    def test_sel_ent_ty(self):
        g3r = db.sel_ent_ty(EntId(ENT_TY_money_owner, 1))
        print(g3r.result)
        print(asdict(g3r.result))

    def test_sel_ent_ty_accnt(self):
        g3r = db.sel_ent_ty(EntId(ENT_TY_money_accnt, 1))
        print(g3r.result)
        g3r.result.id_ = None
        val_dct = asdict(g3r.result)
        print(val_dct)
        new_val_dct: dict = {}
        for k,v in val_dct.items():
            if v is None:
                continue
            if isinstance(v, Enum):
                new_val_dct[k] = v.value
            elif isinstance(v, Dict):
                new_val_dct[f'{k}_id'] = v['id_']
            else:
                new_val_dct[k] = v
        print(new_val_dct)
