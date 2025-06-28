from sqlalchemy import Column, Integer, String, CHAR, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from core.config import Base

# 取引ヘッダテーブル
class TransactionHeader(Base):
    __tablename__ = "transaction_header"

    trd_id = Column("TRD_ID", Integer, primary_key=True, index=True, autoincrement=True, comment="取引一意キー")
    datetime = Column("DATETIME", TIMESTAMP, nullable=False, server_default=func.now(), comment="取引日時")
    emp_cd = Column("EMP_CD", CHAR(10), nullable=False, server_default="9999999999", comment="レジ担当者コード")
    store_cd = Column("STORE_CD", CHAR(5), nullable=False, server_default="30", comment="店舗コード")
    pos_no = Column("POS_NO", CHAR(3), nullable=False, server_default="90", comment="POS機ID (90: モバイルレジ)")
    total_amt = Column("TOTAL_AMT", Integer, nullable=False, server_default="0", comment="合計金額（税込）")
    ttl_amt_ex_tax = Column("TTL_AMT_EX_TAX", Integer, nullable=False, server_default="0", comment="合計金額（税抜）")
