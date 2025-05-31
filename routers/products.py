from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud import crud_product
from schemas.product import Product
from core.config import get_db

router = APIRouter()

@router.get("/products/{product_code}", response_model=Product)
def read_product(product_code: str, db: Session = Depends(get_db)):
    db_product = crud_product.get_product_by_code(db, product_code=product_code)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(
        prd_id=db_product.PRD_ID,
        code=db_product.CODE,
        name=db_product.NAME,
        price=db_product.PRICE
    )
