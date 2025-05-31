from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from crud import crud_transaction
from schemas.transaction import TransactionCreate, TransactionResponse
from core.config import get_db

router = APIRouter()

@router.post("/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_new_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    try:
        header, total_amt, ttl_amt_ex_tax = crud_transaction.create_transaction(db, transaction_data=transaction)
        return {
            "success": True,
            "trd_id": header.TRD_ID,
            "total_amt": total_amt,
            "ttl_amt_ex_tax": ttl_amt_ex_tax
        }
    except Exception as e:
        # 本来はもっと詳細なエラーハンドリングが必要
        raise HTTPException(status_code=500, detail=str(e))
