from sqlalchemy import Column, Integer, String, CHAR, ForeignKeyConstraint
# from sqlalchemy.ext.declarative import declarative_base # 削除
from core.config import Base # 共通Baseをインポート

# Base = declarative_base() # 削除

# 取引明細テーブル
class TransactionDetail(Base):
    __tablename__ = "transaction_detail"

    trd_id = Column(Integer, primary_key=True, comment="取引一意キー")
    dtl_id = Column(Integer, primary_key=True, comment="取引明細一意キー (TRD_ID内で連番)")
    prd_id = Column(Integer, nullable=False, comment="商品一意キー")
    prd_code = Column(CHAR(13), nullable=False, comment="商品JANコード (購入時点の商品コード)")
    prd_name = Column(String(50), nullable=False, comment="商品名称 (購入時点の商品名称)")
    prd_price = Column(Integer, nullable=False, comment="商品単価（税抜、購入時点の単価）")
    quantity = Column(Integer, nullable=False, default=1, comment="数量")
    tax_cd = Column(CHAR(2), nullable=False, server_default="10", comment="消費税区分 (10: 10%)")

    __table_args__ = (
        ForeignKeyConstraint(['trd_id'], ['transaction_header.trd_id']),
        ForeignKeyConstraint(['prd_id'], ['product_master.prd_id']),
        {}
    )
