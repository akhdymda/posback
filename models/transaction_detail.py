from sqlalchemy import Column, Integer, String, CHAR, ForeignKeyConstraint
# from sqlalchemy.ext.declarative import declarative_base # 削除
from core.config import Base # 共通Baseをインポート

# Base = declarative_base() # 削除

# 取引明細テーブル
class TransactionDetail(Base):
    __tablename__ = "transaction_detail"

    TRD_ID = Column(Integer, primary_key=True, comment="取引一意キー")
    DTL_ID = Column(Integer, primary_key=True, comment="取引明細一意キー (TRD_ID内で連番)")
    PRD_ID = Column(Integer, nullable=False, comment="商品一意キー")
    PRD_CODE = Column(CHAR(13), nullable=False, comment="商品JANコード (購入時点の商品コード)")
    PRD_NAME = Column(String(50), nullable=False, comment="商品名称 (購入時点の商品名称)")
    PRD_PRICE = Column(Integer, nullable=False, comment="商品単価（税抜、購入時点の単価）")
    QUANTITY = Column(Integer, nullable=False, default=1, comment="数量")
    TAX_CD = Column(CHAR(2), nullable=False, server_default="10", comment="消費税区分 (10: 10%)")

    __table_args__ = (
        ForeignKeyConstraint(['TRD_ID'], ['TRANSACTION_HEADER.TRD_ID']),
        ForeignKeyConstraint(['PRD_ID'], ['PRODUCT_MASTER.PRD_ID']), # 必要に応じて設定
        {}
    )
