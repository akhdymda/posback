from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from routers import products, transactions
from core.config import engine, Base, get_db # Baseはテーブル作成時に使用
from models import product, transaction_header, transaction_detail # テーブル作成時にインポート
from sqlalchemy.orm import Session
import os

# テーブル作成（初回実行時などにコメントを外して実行）
# Base.metadata.create_all(bind=engine) # app.pyでのcreate_allは重複の可能性があるので一旦コメントアウト (core.config.pyにもあるため)


app = FastAPI(
    title="POS API",
    description="ポップアップストア向け簡易POSシステムAPI",
    version="0.1.0"
)

# 許可するドメインリスト
# 環境変数から取得するか、デフォルト値を使用
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://app-step4-27.azurewebsites.net,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # 必要なHTTPメソッドのみ許可
    allow_headers=["Content-Type", "Authorization"],  # 必要なヘッダーのみ許可
)

# セキュリティヘッダーを追加するミドルウェア
#@app.middleware("http")
#async def add_security_headers(request: Request, call_next):
#    response = await call_next(request)
#    response.headers["X-Content-Type-Options"] = "nosniff"
#    response.headers["X-Frame-Options"] = "DENY"
#    response.headers["X-XSS-Protection"] = "1; mode=block"
#    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
#    response.headers["Content-Security-Policy"] = "default-src 'self'"
#    return response

# レート制限を実装するミドルウェア
#@app.middleware("http")
#async def rate_limiter(request: Request, call_next):
    # 本来はIPアドレスごとにリクエスト数を追跡し、
    # 短時間に多数のリクエストがあった場合は429エラーを返すべきです
    # 簡易的な実装のため、ここでは常に許可します
    #response = await call_next(request)
    #return response

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
