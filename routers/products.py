from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from crud import crud_product
from schemas.product import Product
from core.config import get_db

# ロガーの設定
logger = logging.getLogger("api")

router = APIRouter()

@router.get("/products/{product_code}", response_model=Product)
def read_product(product_code: str, db: Session = Depends(get_db)):
    try:
        logger.info(f"商品コード '{product_code}' の情報を取得しています")
        db_product = crud_product.get_product_by_code(db, product_code=product_code)
        
        if db_product is None:
            logger.warning(f"商品コード '{product_code}' は見つかりませんでした")
            raise HTTPException(status_code=404, detail=f"商品コード '{product_code}' は見つかりませんでした")
        
        logger.info(f"商品コード '{product_code}' の情報を正常に取得しました: {db_product.name}")
        return Product(
            prd_id=db_product.prd_id,
            code=db_product.code,
            name=db_product.name,
            price=db_product.price
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"商品情報取得中にエラーが発生しました: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"データベースエラー: {str(e)}")
