# posアプリbackend機能
---
## アプリ名称
---
**POS（Point of Sales）アプリケーション**

## アーキテクチャ
---
- FastAPI
- バージョン
    - FastAPI: >=0.109.0
    - Python: 3.11.11
    - MySQL: 8.4.4

## API機能(backend機能)
### 1. 機能名: 商品マスタ検索
-   説明: JANコードに基づいて商品マスタから商品情報を取得する。
-   エンドポイント: (例: `/api/products/{product_code}`)
-   HTTPメソッド: GET
-   パラメータ:
    -   `product_code` (パスパラメータ): 商品のJANコード (char(13))
-   リターン（成功時: HTTP 200 OK）: 商品情報
    ```json
    {
      "prd_id": 123, // 商品一意キー (integer)
      "code": "4901234567890", // 商品JANコード (char(13))
      "name": "おーいお茶", // 商品名称 (varchar(50))
      "price": 150 // 商品単価 (integer)
    }
    ```
-   リターン（失敗時: HTTP 404 Not Found）: 対象商品が見つからない場合
    ```json
    {
      "detail": "Product not found"
    }
    ```
    または、下記のようなNULL情報（要件定義による）
    ```json
    null
    ```

### 2. 機能名: 購入
-   説明: 購入リストの商品情報を受け取り、取引情報としてDBに登録する。
-   エンドポイント: (例: `/api/transactions`)
-   HTTPメソッド: POST
-   パラメータ (リクエストボディ):
    ```json
    {
      "emp_cd": "1234567890", // レジ担当者コード (char(10)), 省略時は "9999999999" を使用
      "items": [ // 商品リスト
        {
          "prd_id": 123, // 商品一意キー (integer)
          "prd_code": "4901234567890", // 商品JANコード (char(13))
          "prd_name": "おーいお茶", // 商品名称 (varchar(50))
          "prd_price": 150, // 商品単価 (integer)
          "quantity": 1 // 商品数量 (integer、省略時は1)　
        }
        // ... 他の商品
        // 同一商品は数量としてまとめて送信することも、個別に送信することも可能です。
        // quantityフィールドは省略された場合、1として扱われます。
      ]
    }
    ```
    *   店舗コード (`STORE_CD`) はAPI側で `'30'` を固定値として設定。
    *   POS機ID (`POS_NO`) はAPI側で `'90'` (モバイルレジ) を固定値として設定。
-   リターン（成功時: HTTP 201 Created）:
    ```json
    {
      "success": true,
      "trd_id": 5001, // 作成された取引一意キー
      "total_amt": 1650, // 合計金額（税込）
      "ttl_amt_ex_tax": 1500 // 合計金額（税抜）
    }
    ```
-   リターン（失敗時: HTTP 4xx/5xx）:
    ```json
    {
      "success": false,
      "detail": "エラーメッセージ"
    }
    ```
-   処理詳細:
    1.  取引テーブル (`TRANSACTION_HEADER`) へ登録:
        *   `TRD_ID`: DBにて自動採番 (AUTO_INCREMENT)
        *   `DATETIME`: 現在日時 (システム日付)
        *   `EMP_CD`: パラメータの `emp_cd`。提供されない場合は `"9999999999"`。
        *   `STORE_CD`: `'30'` (固定)
        *   `POS_NO`: `'90'` (固定、モバイルレジ)
        *   `TOTAL_AMT`: `0` (初期値、後で更新)
        *   `TTL_AMT_EX_TAX`: `0` (初期値、後で更新)
        *   登録後、採番された `TRD_ID` を取得。
    2.  取引明細テーブル (`TRANSACTION_DETAIL`) へ登録: パラメータの `items` リストの各商品について登録。
        *   `TRD_ID`: 2.1で採番された `TRD_ID`。
        *   `DTL_ID`: `TRD_ID` ごとに1から連番 (DBでの採番、またはアプリケーションでの採番ロジックが必要)。
        *   `PRD_ID`: パラメータの `prd_id`。
        *   `PRD_CODE`: パラメータの `prd_code`。
        *   `PRD_NAME`: パラメータの `prd_name`。
        *   `PRD_PRICE`: パラメータの `prd_price`。
        *   `QUANTITY`: パラメータの `quantity`。指定がない場合は `1`。
        *   `TAX_CD`: `'10'` (消費税10%、固定)。
    3.  合計金額・税抜金額の計算:
        *   登録された取引明細の `PRD_PRICE` を合計し、`V_合計金額（税抜）` (TTL_AMT_EX_TAX) を算出。
        *   消費税（10%）を計算し（端数処理が必要な場合は仕様確認）、`V_合計金額（税込）` (TOTAL_AMT) を算出。
    4.  取引テーブル (`TRANSACTION_HEADER`) を更新:
        *   条件: 2.1で採番された `TRD_ID`。
        *   更新値: `TOTAL_AMT` = `V_合計金額（税込）`, `TTL_AMT_EX_TAX` = `V_合計金額（税抜）`。
    5.  計算結果の `total_amt`、`ttl_amt_ex_tax` および `trd_id` をフロントへ返す。

## DBイメージ (テーブル物理名も併記推奨)
---
### 1. 商品マスタ (例: `PRODUCT_MASTER`)
-   `PRD_ID` (PK) integer, AUTO_INCREMENT
    -   COMMENT: 商品一意キー
-   `CODE` char(16) NOT NULL
    -   COMMENT: 商品JANコード（原則）
    -   CONSTRAINT: UNIQUE (`CODE`)
-   `NAME` varchar(50) NOT NULL
    -   COMMENT: 商品名称
-   `PRICE` integer NOT NULL
    -   COMMENT: 商品単価（税抜）

### 2. 取引ヘッダ (例: `TRANSACTION_HEADER`)
-   `TRD_ID` (PK) integer, AUTO_INCREMENT
    -   COMMENT: 取引一意キー
-   `DATETIME` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    -   COMMENT: 取引日時
-   `EMP_CD` char(10) NOT NULL DEFAULT '9999999999'
    -   COMMENT: レジ担当者コード
-   `STORE_CD` char(5) NOT NULL DEFAULT '30'
    -   COMMENT: 店舗コード
-   `POS_NO` char(3) NOT NULL DEFAULT '90'
    -   COMMENT: POS機ID (90: モバイルレジ)
-   `TOTAL_AMT` integer NOT NULL DEFAULT 0
    -   COMMENT: 合計金額（税込）
-   `TTL_AMT_EX_TAX` integer NOT NULL DEFAULT 0
    -   COMMENT: 合計金額（税抜）

### 3. 取引明細 (例: `TRANSACTION_DETAIL`)
-   `TRD_ID` (PK, FK) integer NOT NULL
    -   COMMENT: 取引一意キー (TRANSACTION_HEADER.TRD_ID を参照)
-   `DTL_ID` (PK) integer NOT NULL
    -   COMMENT: 取引明細一意キー (TRD_ID内で連番)
-   `PRD_ID` integer NOT NULL
    -   COMMENT: 商品一意キー (PRODUCT_MASTER.PRD_ID を参照)
-   `PRD_CODE` char(13) NOT NULL
    -   COMMENT: 商品JANコード (購入時点の商品コード)
-   `PRD_NAME` varchar(50) NOT NULL
    -   COMMENT: 商品名称 (購入時点の商品名称)
-   `PRD_PRICE` integer NOT NULL
    -   COMMENT: 商品単価（税抜、購入時点の単価）
-   `QUANTITY` integer NOT NULL DEFAULT 1
    -   COMMENT: 数量
-   `TAX_CD` char(2) NOT NULL DEFAULT '10'
    -   COMMENT: 消費税区分 (10: 10%)
-   PRIMARY KEY (`TRD_ID`, `DTL_ID`)
-   FOREIGN KEY (`TRD_ID`) REFERENCES `TRANSACTION_HEADER` (`TRD_ID`)
-   FOREIGN KEY (`PRD_ID`) REFERENCES `PRODUCT_MASTER` (`PRD_ID`) (※必要に応じて設定)

## ディレクトリ設計
---
```
posback/                 
├── .gitignore              # Gitで無視するファイルやディレクトリを指定
├── README.md               # プロジェクトの説明ファイル
├── requirements.txt        # プロジェクトの依存ライブラリ一覧
├── .env                    # 環境変数の格納先
├── app.py                  # FastAPIアプリケーションのインスタンス化、ミドルウェア設定、ルーターのインクルードを行うメインファイル
├── core/                   # アプリケーション全体の設定や共通ユーティリティ
│   ├── __init__.py
│   └── config.py           # 設定値（データベース接続情報、APIキーなど）
├── crud/                   # データベースへのCRUD（作成、読み取り、更新、削除）操作を行うロジック
│   ├── __init__.py
│   ├── crud_product.py     # 商品マスタテーブルへのCRUD操作
│   └── crud_transaction.py # 取引関連テーブルへのCRUD操作
├── models/                 # SQLAlchemyで使用するデータベースモデル（テーブル定義）
│   ├── __init__.py
│   ├── product.py          # PRODUCT_MASTER テーブルのモデル
│   ├── transaction_header.py # TRANSACTION_HEADER テーブルのモデル
│   └── transaction_detail.py # TRANSACTION_DETAIL テーブルのモデル
├── routers/                # APIエンドポイント（ルーター）関連
│   ├── __init__.py
│   ├── products.py       # 商品マスタ検索APIのエンドポイント
│   └── transactions.py     # 購入APIのエンドポイント
└── schemas/                # Pydanticモデル（APIリクエスト/レスポンスのデータ検証・シリアライズ用）
    ├── __init__.py
    ├── product.py          # 商品関連のPydanticモデル
    └── transaction.py      # 取引関連のPydanticモデル
```

## 更新ログ
---
*2025/05031* API機能(backend機能)修正