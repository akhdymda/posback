from sqlalchemy import Column, Integer, String, CHAR
# from sqlalchemy.ext.declarative import declarative_base # 削除
from core.config import Base # 共通Baseをインポート

# Base = declarative_base() # 削除

# 商品マスタテーブル
class ProductMaster(Base):
    __tablename__ = "product_master"

    prd_id = Column("PRD_ID", Integer, primary_key=True, index=True, autoincrement=True, comment="商品一意キー")
    code = Column("CODE", CHAR(16), unique=True, nullable=False, comment="商品JANコード（原則）")
    name = Column("NAME", String(50), nullable=False, comment="商品名称")
    price = Column("PRICE", Integer, nullable=False, comment="商品単価（税抜）")
