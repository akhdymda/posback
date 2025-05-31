from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import products, transactions
from core.config import engine , Base # Baseはテーブル作成時に使用
from models import product, transaction_header, transaction_detail # テーブル作成時にインポート

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

# 開発中はUvicornで直接実行する場合:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
