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
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ローカル環境かどうかを判定
is_local = DB_HOST in ['localhost', '127.0.0.1'] or (DB_HOST and (DB_HOST.startswith('192.168.') or DB_HOST.startswith('10.')))

# エンジンの作成
if is_local:
    # ローカル環境ではSSL接続を無効化
    logger.info("ローカル環境を検出しました。SSL接続を無効化します。")
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # SQLログを無効化（本番環境用）
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,  # 同時接続数を制限
        max_overflow=20,  # 最大オーバーフロー接続数
        pool_timeout=30  # 接続タイムアウト
    )
else:
    # 本番環境ではSSL接続を有効化
    logger.info("本番環境を検出しました。SSL接続を有効化します。")
    ssl_cert = str(base_path / 'CombinedCACert.crt.pem')
    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "ssl": {
                "ssl_ca": ssl_cert
            }  
        },
        echo=False,  # SQLログを無効化（本番環境用）
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=10,  # 同時接続数を制限
        max_overflow=20,  # 最大オーバーフロー接続数
        pool_timeout=30  # 接続タイムアウト
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