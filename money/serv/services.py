from g3b1_cfg.tg_cfg import G3Context
from g3b1_serv import utilities
from g3b1_ui.model import TgUIC
from money.data.db import ins_ent_ty
from money.data.model import Owner


def owner_01(bkey: str) -> Owner:
    chat_id, user_id = utilities.upd_extract_chat_user_id(G3Context.upd)
    owner: Owner = Owner(chat_id, bkey)
    g3r = ins_ent_ty(owner)
    TgUIC.uic.cmd_sccs()
    return g3r.result
