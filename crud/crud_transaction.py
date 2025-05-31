from sqlalchemy.orm import Session
from fastapi import HTTPException # HTTPExceptionをインポート
from models.transaction_header import TransactionHeader
from models.transaction_detail import TransactionDetail
from schemas.transaction import TransactionCreate, ItemCreate # TransactionHeaderCreate, TransactionDetailCreateは直接使わずTransactionCreateから展開
from datetime import datetime
from .crud_product import get_product_by_code # crud_productから関数をインポート

def create_transaction(db: Session, transaction_data: TransactionCreate):
    # 1. 取引テーブル (TRANSACTION_HEADER) へ登録
    db_transaction_header = TransactionHeader(
        EMP_CD=transaction_data.emp_cd, # スキーマでデフォルト値設定済み
        # DATETIMEはDB側で自動設定
        # STORE_CD, POS_NO はモデルのデフォルト値を使用
        # TOTAL_AMT, TTL_AMT_EX_TAX は後で更新
    )
    db.add(db_transaction_header)
    db.commit() # TRD_IDを採番するために一度コミット
    db.refresh(db_transaction_header)
    trd_id = db_transaction_header.TRD_ID

    # 2. 取引明細テーブル (TRANSACTION_DETAIL) へ登録
    total_amt_ex_tax = 0
    dtl_id_counter = 1 # DTL_IDをTRD_IDごとに1から採番
    for item in transaction_data.items:
        # item.prd_code を使って ProductMaster から PRD_ID を取得
        product_master_entry = get_product_by_code(db, product_code=item.prd_code)
        if not product_master_entry:
            # ここでロールバック処理を入れるか、あるいはトランザクション全体をtry-exceptで囲むべきかもしれない
            # 例えば db.rollback() を呼び、HTTPExceptionを送出する
            # 今回は簡潔にHTTPExceptionのみ
            raise HTTPException(status_code=404, detail=f"Product with code {item.prd_code} not found in master.")

        db_transaction_detail = TransactionDetail(
            TRD_ID=trd_id,
            DTL_ID=dtl_id_counter,
            PRD_ID=product_master_entry.PRD_ID, # 取得した正しいPRD_IDを使用
            PRD_CODE=item.prd_code,
            PRD_NAME=item.prd_name, # 本来はproduct_master_entry.NAMEを使用すべきだが、スキーマと合わせる
            PRD_PRICE=item.prd_price, # 同上 product_master_entry.PRICE
            QUANTITY=item.quantity,
            # TAX_CDはモデルのデフォルト値を使用
        )
        db.add(db_transaction_detail)
        total_amt_ex_tax += (item.prd_price * item.quantity) # 修正: 単価 * 数量
        dtl_id_counter += 1
    
    db.commit() # 明細をコミット

    # 3. 合計金額・税抜金額の計算 (消費税10%)
    # posback-rules では「端数処理が必要な場合は仕様確認」とあるが、ここでは単純計算
    tax = round(total_amt_ex_tax * 0.10)
    total_amt = total_amt_ex_tax + tax

    # 4. 取引テーブル (TRANSACTION_HEADER) を更新
    db_transaction_header.TOTAL_AMT = total_amt
    db_transaction_header.TTL_AMT_EX_TAX = total_amt_ex_tax
    db.commit()
    db.refresh(db_transaction_header)

    return db_transaction_header, total_amt, total_amt_ex_tax
