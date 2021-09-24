import importlib
from unittest import TestCase

from g3b1_cfg import cfg
from g3b1_data.model import G3Module
from g3b1_serv import utilities
from money import tg_hdl


class Test(TestCase):
    def test_ins_g3_m(self):
        cfg.del_db_cfg()
        g3_m: G3Module = utilities.g3_m_dct_init(tg_hdl.__file__)
        cfg.ins_g3_m(g3_m)
        cfg.sel_g3_m(g3_m.name)

    def test_sel_g3_m(self):
        g3_m: G3Module = utilities.g3_m_dct_init(tg_hdl.__file__)
        cfg.ins_g3_m(g3_m)
        g3_m = cfg.sel_g3_m('money')
        print(g3_m)

