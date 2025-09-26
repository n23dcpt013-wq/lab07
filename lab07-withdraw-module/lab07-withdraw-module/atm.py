import hashlib
import decimal
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

load_dotenv()

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "atm_demo"),
    )

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def verify_pin(card_no: str, pin: str) -> bool:
    """Trả về True nếu PIN khớp với pin_hash trong DB cho card_no."""
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT pin_hash FROM cards WHERE card_no=%s", (card_no,))
        row = cur.fetchone()
        return bool(row and row[0] == sha256(pin))
    finally:
        conn.close()

def withdraw(card_no: str, amount_vnd: float, atm_id: int = 1):
    """Rút tiền an toàn bằng transaction & khoá FOR UPDATE."""
    if amount_vnd <= 0:
        raise ValueError("Amount must be positive.")
    amount = decimal.Decimal(str(round(amount_vnd, 2)))

    conn = get_conn()
    try:
        conn.start_transaction()
        cur = conn.cursor()

        cur.execute(
            '''
            SELECT a.account_id, a.balance
            FROM accounts a
            JOIN cards c ON c.account_id = a.account_id
            WHERE c.card_no=%s
            FOR UPDATE
            ''',
            (card_no,),
        )
        row = cur.fetchone()
        if not row:
            raise Exception("Card not found.")
        account_id, balance = row
        balance = decimal.Decimal(str(balance))

        if balance < amount:
            raise Exception("Insufficient funds")

        new_balance = balance - amount
        cur.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", (new_balance, account_id))

        cur.execute(
            '''
            INSERT INTO transactions(account_id, card_no, atm_id, tx_type, amount, balance_after)
            VALUES (%s, %s, %s, 'WITHDRAW', %s, %s)
            ''',
            (account_id, card_no, atm_id, amount, new_balance),
        )

        conn.commit()
        return {"ok": True, "account_id": account_id, "balance_after": float(new_balance)}
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()
