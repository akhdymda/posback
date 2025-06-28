from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
#from pathlib import Path
from dotenv import load_dotenv
import logging
import psycopg2
from urllib.parse import quote_plus

logger = logging.getLogger("db")

# Load environment variables from .env
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD_RAW = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# パスワードをURLエンコード
DB_PASSWORD = quote_plus(DB_PASSWORD_RAW) if DB_PASSWORD_RAW else ''

# .envファイルの情報からデータベースURLを構築
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)

# セッションファクトリを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Baseクラスの作成
Base = declarative_base()

# DBセッションを取得するヘルパー関数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# テーブル作成
try:
    Base.metadata.create_all(engine)
    logger.info("データベース接続が初期化されました")
except Exception as e:
    logger.error(f"データベース接続またはテーブル作成中にエラーが発生しました: {e}")
    raise