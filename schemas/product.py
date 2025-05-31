from pydantic import BaseModel

class ProductBase(BaseModel):
    code: str
    name: str
    price: int

class Product(ProductBase):
    prd_id: int

    class Config:
        orm_mode = True # SQLAlchemyモデルと連携するために必要
