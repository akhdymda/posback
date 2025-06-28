from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
#from pathlib import Path
from dotenv import load_dotenv
import logging
import psycopg2

# Load environment variables from .env
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Connect to the database
try:
    connection = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")

# ロギング設定
#logger = logging.getLogger("db")

# 環境変数の読み込み
##env_path = base_path / '.env'
#load_dotenv(dotenv_path=env_path)



# .envファイルの情報からデータベースURLを構築
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
#try:
#    Base.metadata.create_all(engine)
#    Base.metadata.create_all(engine)

#    Base.metadata.create_all(engine)

#    logger.info("データベース接続が初期化されました")


#except Exception as e:
#    logger.error(f"データベース接続またはテーブル作成中にエラーが発生しました: {e}")
#    raise