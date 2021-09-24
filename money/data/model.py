from dataclasses import dataclass
from typing import Union

from g3b1_data.elements import EleTy, ELE_TY_li
from g3b1_data.entities import EntTy, G3_M_MONEY, ENT_TY_li
from money.data.enums import Crcy


@dataclass
class Owner:
    chat_id: int
    bkey: str
    id_: int = None

    @staticmethod
    def ent_ty() -> EntTy["Owner"]:
        return ENT_TY_money_owner

    def ins_values(self) -> dict[str, Union[str, int]]:
        return dict(chat_id=self.chat_id, bkey=self.bkey)


@dataclass
class Accnt:
    chat_id: int
    bkey: str
    owner: Owner
    crcy: Crcy
    id_: int = None

    @staticmethod
    def ent_ty() -> EntTy:
        return ENT_TY_money_accnt

    def ins_values(self) -> dict[str, Union[str, int]]:
        return dict(chat_id=self.chat_id, bkey=self.bkey, owner_id=self.owner.id_, crcy=self.crcy)


@dataclass
class Categ:
    chat_id: int
    bkey: str
    id_: int = None

    @staticmethod
    def ent_ty() -> EntTy:
        return ENT_TY_money_categ

    def ins_values(self) -> dict[str, Union[str, int]]:
        return dict(chat_id=self.chat_id, bkey=self.bkey)


@dataclass
class Money:
    accnt: Accnt
    categ: Categ
    crcy: Crcy
    amnt: int
    id_: int = None

    @staticmethod
    def ent_ty() -> EntTy:
        return ENT_TY_money


@dataclass
class MoneyMp:
    src__money: Money
    trg__money: Money
    tst: str
    id_: int

    @staticmethod
    def ent_ty() -> EntTy:
        return ENT_TY_money_mp


@dataclass
class AccntBal:
    accnt: Accnt
    tst: str
    last__money_mp: MoneyMp
    id_: int

    @staticmethod
    def ent_ty() -> EntTy:
        return ENT_TY_money_accnt_bal


ENT_TY_money_owner = EntTy[Owner](G3_M_MONEY, 'owner', 'Owner')
ENT_TY_money_categ = EntTy[Categ](G3_M_MONEY, 'categ', 'Category')
ENT_TY_money_accnt = EntTy[Accnt](G3_M_MONEY, 'accnt', 'Account')
ENT_TY_money = EntTy[Money](G3_M_MONEY, 'money', 'Money')
ENT_TY_money_mp = EntTy[MoneyMp](G3_M_MONEY, 'money_mp', 'Money Transfer')
ENT_TY_money_accnt_bal = EntTy[AccntBal](G3_M_MONEY, 'accnt_bal', 'Accnt Balance')

ENT_TY_money_li = [ENT_TY_money_owner, ENT_TY_money_categ, ENT_TY_money_accnt,
                   ENT_TY_money, ENT_TY_money_mp, ENT_TY_money_accnt_bal]
ENT_TY_li.extend(ENT_TY_money_li)

ELE_TY_money_owner_id = EleTy(id_='owner_id', descr='Owner', ent_ty=ENT_TY_money_owner)
ELE_TY_money_categ_id = EleTy(id_='categ_id', descr='Category', ent_ty=ENT_TY_money_categ)
ELE_TY_money_accnt_id = EleTy(id_='accnt_id', descr='Account', ent_ty=ENT_TY_money_accnt)
ELE_TY_money_accnt_bal_id = EleTy(id_='accnt_bal_id', descr='Accnt Balance', ent_ty=ENT_TY_money_accnt_bal)
ELE_TY_money_id = EleTy(id_='money_id', descr='Money', ent_ty=ENT_TY_money)
ELE_TY_money_mp_id = EleTy(id_='money_mp_id', descr='Money', ent_ty=ENT_TY_money_mp)
ELE_TY_li.extend([ELE_TY_money_owner_id, ELE_TY_money_categ_id, ELE_TY_money_accnt_id, ELE_TY_money_accnt_bal_id,
                 ELE_TY_money_id, ELE_TY_money_mp_id])
