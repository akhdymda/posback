from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# ロギング設定
logger = logging.getLogger("db")

# 環境変数の読み込み　
base_path = Path(__file__).parents[1]  # backendディレクトリへのパス
env_path = base_path / '.env'
load_dotenv(dotenv_path=env_path)

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# MySQLのURL構築
# DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# DATABASE_URLを環境変数から取得、なければ個別変数から構築
DATABASE_URL_ENV = os.getenv('DATABASE_URL')
if DATABASE_URL_ENV:
    logger.info("DATABASE_URL environment variable found.")
    if DATABASE_URL_ENV.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL_ENV.replace("postgresql://", "postgresql+psycopg2://", 1)
    else:
        DATABASE_URL = DATABASE_URL_ENV
else:
    logger.warning("DATABASE_URL environment variable not found. Falling back to individual DB variables.")
    logger.info(f"DB_HOST value from environment: '{DB_HOST}'")
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# エンジンの作成
engine = create_engine(
    DATABASE_URL,
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
Base.metadata.create_all(engine)

logger.info("データベース接続が初期化されました")