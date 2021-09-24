from sqlalchemy import MetaData, create_engine

BOT_BKEY_MONEY = "money"

DB_FILE_MONEY = rf'C:\Users\IFLRGU\Documents\dev\g3b1_{BOT_BKEY_MONEY}.db'
md_MONEY = MetaData()
eng_MONEY = create_engine(f"sqlite:///{DB_FILE_MONEY}")
md_MONEY.reflect(bind=eng_MONEY)

