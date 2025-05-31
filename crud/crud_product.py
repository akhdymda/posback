from sqlalchemy.orm import Session
from models.product import ProductMaster
from schemas.product import ProductBase # ProductCreate スキーマは今回は未使用

def get_product_by_code(db: Session, product_code: str):
    return db.query(ProductMaster).filter(ProductMaster.CODE == product_code).first()

# 以下はサンプルとして追加（posback-rulesには明示的な記載なし）
# def create_product(db: Session, product: ProductBase):
#     db_product = ProductMaster(**product.model_dump())
#     db.add(db_product)
#     db.commit()
#     db.refresh(db_product)
#     return db_product
