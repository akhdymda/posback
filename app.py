from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import products, transactions
from core.config import engine, Base, get_db # Baseはテーブル作成時に使用
from models import product, transaction_header, transaction_detail # テーブル作成時にインポート
from sqlalchemy.orm import Session

# テーブル作成（初回実行時などにコメントを外して実行）
# Base.metadata.create_all(bind=engine) # app.pyでのcreate_allは重複の可能性があるので一旦コメントアウト (core.config.pyにもあるため)


app = FastAPI(
    title="POS API",
    description="ポップアップストア向け簡易POSシステムAPI",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api", tags=["Products"])
app.include_router(transactions.router, prefix="/api", tags=["Transactions"])

@app.get("/")
async def root():
    return {"message": "Welcome to POS API"}

# データベース接続テスト用エンドポイント
@app.get("/api/test-db")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        # 最初の5つの商品を取得
        from crud.crud_product import get_product_by_code
        result = []
        
        # シードデータから商品コードをいくつか試す
        test_codes = ["4901681328413", "4901681316717", "4901681316861"]
        for code in test_codes:
            product = get_product_by_code(db, code)
            if product:
                result.append({
                    "code": product.CODE,
                    "name": product.NAME,
                    "price": product.PRICE
                })
        
        return {
            "success": True,
            "message": "データベース接続は正常です",
            "products_found": len(result),
            "products": result
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"データベース接続エラー: {str(e)}"
        }

# 開発中はUvicornで直接実行する場合:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
