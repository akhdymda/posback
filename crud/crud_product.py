from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from models.product import ProductMaster
from schemas.product import ProductBase # ProductCreate スキーマは今回は未使用

# ロガーの設定
logger = logging.getLogger("db_crud")

def get_product_by_code(db: Session, product_code: str):
    try:
        logger.info(f"商品コード '{product_code}' のデータベース検索を開始します")
        
        # まずSQLAlchemyのORMを使用して検索
        product = db.query(ProductMaster).filter(ProductMaster.CODE == product_code).first()
        
        if product:
            logger.info(f"商品コード '{product_code}' の商品を見つけました: {product.NAME}")
            return product
        
        # ORMで見つからない場合、直接SQLを試行
        logger.warning(f"ORM検索で商品コード '{product_code}' の商品が見つかりませんでした。直接SQLを試行します")
        
        # 文字列の前後のスペースをトリム
        trimmed_code = product_code.strip()
        
        # 直接SQLを使用
        result = db.execute(
            text(f"SELECT * FROM PRODUCT_MASTER WHERE CODE = :code OR CODE = :trimmed_code"),
            {"code": product_code, "trimmed_code": trimmed_code}
        )
        
        row = result.fetchone()
        if row:
            logger.info(f"直接SQLで商品コード '{product_code}' の商品を見つけました")
            # ProductMasterオブジェクトに変換
            product = ProductMaster(
                PRD_ID=row.PRD_ID,
                CODE=row.CODE,
                NAME=row.NAME,
                PRICE=row.PRICE
            )
            return product
        
        # それでも見つからない場合、デバッグ情報を記録
        logger.warning(f"商品コード '{product_code}' の商品はデータベースに存在しません")
        
        # 登録されている商品コードのサンプルを取得（デバッグ用）
        sample_result = db.execute(text("SELECT CODE FROM PRODUCT_MASTER LIMIT 5"))
        sample_codes = [row[0] for row in sample_result.fetchall()]
        
        if sample_codes:
            logger.info(f"データベースに登録されている商品コード例: {', '.join(sample_codes)}")
        else:
            logger.warning("データベースに商品が登録されていません")
        
        return None
    except Exception as e:
        logger.error(f"商品コード '{product_code}' の検索中にエラーが発生しました: {str(e)}", exc_info=True)
        raise

# 以下はサンプルとして追加（posback-rulesには明示的な記載なし）
# def create_product(db: Session, product: ProductBase):
#     db_product = ProductMaster(**product.model_dump())
#     db.add(db_product)
#     db.commit()
#     db.refresh(db_product)
#     return db_product
