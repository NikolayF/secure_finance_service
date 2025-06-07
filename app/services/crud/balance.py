from contextlib import contextmanager
from decimal import Decimal
from typing import Generator
from typing import Optional
from sqlmodel import Session
from models.balance import Balance
from models.log import Log
import uuid

class InsufficientFunds(Exception):
    pass

def get_balance_by_user_id(user_id:int, session) -> Optional[Balance]:
    balance = session.get(Balance, user_id) 
    if balance:
        return balance 
    return None

@contextmanager
def transaction(session: Session) -> Generator[None, None, None]:
    try:
        yield
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

async def create_balance(new_balance: Balance, session) -> None:
    session.add(new_balance) 
    session.commit() 
    session.refresh(new_balance)

async def increase_balance(balance: Balance, source_amount: float, session: Session) -> None:
    amount = Decimal(str(source_amount))
    balance.increase(float(amount))
    description = f"Пополнение счета на сумму: {amount}"
    log = Log(
        user_id=balance.user_id,
        event_type="пополнение",
        description=description,
        model_request_id = uuid.uuid4()
    )
    session.add(balance)
    session.add(log)
    session.commit()
    session.refresh(balance)


def decrease_balance(balance: Balance, source_amount: float, session: Session) -> None:
    amount = Decimal(str(source_amount))
    if balance.amount < float(amount):
        raise InsufficientFunds("Недостаточно средств для списания.")

    balance.decrease(float(amount))
    description = f"Списание со счета на сумму: {amount}"
    log = Log(
        user_id=balance.user_id,
        event_type="списание",
        description=description,
        model_request_id = uuid.uuid4()
    )
    session.add(balance)
    session.add(log)
    session.commit()
    session.refresh(balance)