from g3b1_cfg.tg_cfg import sel_g3_m
from g3b1_data.entities import G3_M_MONEY
from g3b1_data.model import Menu, MenuIt, G3Module
from money.data.model import ENT_TY_money_owner, ENT_TY_money_categ, ENT_TY_money_accnt


class MoneyCfg:
    current: "MoneyCfg" = None
    g3m_str = 'money'

    def __init__(self) -> None:
        super().__init__()
        self.g3m_str = MoneyCfg.g3m_str
        self.menu: Menu = Menu(MoneyCfg.g3m_str, MoneyCfg.g3m_str)

    @classmethod
    def get_current(cls):
        if cls.current:
            return cls.current
        g3_m: G3Module = sel_g3_m(G3_M_MONEY)
        cls.current = cls()
        # noinspection PyTypeChecker
        mi_owner = MenuIt(ENT_TY_money_owner.id, ENT_TY_money_owner.descr, menu=cls.current.menu)
        MenuIt(lbl='01', parent=mi_owner, g3_cmd=g3_m.cmd_dct['owner_01'])
        MenuIt(lbl='03', parent=mi_owner, g3_cmd=g3_m.cmd_dct['owner_03'])
        MenuIt('666', '\n', parent=mi_owner)
        MenuIt('owner_33', '33', parent=mi_owner)
        MenuIt(lbl='04', parent=mi_owner, g3_cmd=g3_m.cmd_dct['owner_04'])
        MenuIt('616', '\n', parent=mi_owner)
        MenuIt('back', lbl='Back', parent=mi_owner, g3_cmd=g3_m.cmd_dct['menu'])

        mi_categ = MenuIt(ENT_TY_money_categ.id, ENT_TY_money_categ.descr, menu=cls.current.menu)
        MenuIt(lbl='01', parent=mi_categ, g3_cmd=g3_m.cmd_dct['categ_01'])
        MenuIt(lbl='03', parent=mi_categ, g3_cmd=g3_m.cmd_dct['categ_03'])
        MenuIt('666', '\n', parent=mi_categ)
        MenuIt('categ_33', '33', parent=mi_categ)
        MenuIt(lbl='04', parent=mi_categ, g3_cmd=g3_m.cmd_dct['categ_04'])
        MenuIt('111', '\n', parent=mi_categ)
        MenuIt('back', lbl='Back', parent=mi_categ, g3_cmd=g3_m.cmd_dct['menu'])

        mi_accnt = MenuIt(ENT_TY_money_accnt.id, ENT_TY_money_accnt.descr, menu=cls.current.menu)
        MenuIt(lbl='01', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['accnt_01'])
        MenuIt(lbl='03', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['accnt_03'])
        MenuIt('accnt_33', '33', parent=mi_accnt)
        MenuIt('666', '\n', parent=mi_accnt)
        MenuIt(lbl='04', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['accnt_04'])
        MenuIt(lbl='src', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['accnt_src'])
        MenuIt(lbl='trg', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['accnt_trg'])
        MenuIt('16566', '\n', parent=mi_accnt)
        MenuIt(lbl='bal_01', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['accnt_bal_01'])
        MenuIt(lbl='🧮 bal_12', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['accnt_bal_12'])
        MenuIt('616', '\n', parent=mi_accnt)
        MenuIt('back', lbl='Back', parent=mi_accnt, g3_cmd=g3_m.cmd_dct['menu'])

        MenuIt(menu=cls.current.menu, g3_cmd=g3_m.cmd_dct['transfer'])

        return cls.current
