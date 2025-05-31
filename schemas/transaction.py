from pydantic import BaseModel
from typing import List, Optional

# 購入APIリクエストボディ内の商品情報
class ItemCreate(BaseModel):
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: int
    quantity: int

# 購入APIリクエストボディ
class TransactionCreate(BaseModel):
    emp_cd: Optional[str] = "9999999999"
    items: List[ItemCreate]

# 購入APIレスポンスボディ
class TransactionResponse(BaseModel):
    success: bool
    trd_id: int
    total_amt: int
    ttl_amt_ex_tax: int

# 取引ヘッダ情報（DBアクセス用などに使用）
class TransactionHeaderBase(BaseModel):
    emp_cd: str
    store_cd: str
    pos_no: str
    total_amt: int
    ttl_amt_ex_tax: int

class TransactionHeader(TransactionHeaderBase):
    trd_id: int
    datetime: str # or datetime object, adjust as needed

    class Config:
        orm_mode = True

# 取引明細情報（DBアクセス用などに使用）
class TransactionDetailBase(BaseModel):
    prd_id: int
    prd_code: str
    prd_name: str
    prd_price: int
    quantity: int
    tax_cd: str

class TransactionDetailCreate(TransactionDetailBase):
    trd_id: int
    dtl_id: int # dtl_idはアプリケーションロジックで採番想定

class TransactionDetail(TransactionDetailBase):
    trd_id: int
    dtl_id: int

    class Config:
        orm_mode = True
