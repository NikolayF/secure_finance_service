from sqlmodel import Session
from services.crud.user import User
from services.crud.balance import Balance
from models.log import Log

def test_database_connection(session: Session):
    assert session.is_active


def test_create_user(session: Session):
    user = User(email="test_2@mail.ru", password="123")
    session.add(user)
    session.commit()
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == "test_2@mail.ru"


def test_create_balance(session: Session):
    balance = Balance(user = session.get(User, 1))   
    session.add(balance) 
    session.commit() 
    retrieved_balance = session.get(Balance, balance.id)
    assert retrieved_balance is not None


def test_increase_balance_with_log(session: Session):

    balance = session.get(Balance, 1)
    amount = 500
    balance.increase(float(amount))
    description = f"Пополнение счета на сумму: {amount}"
    log = Log(
        user_id=balance.user_id,
        event_type="пополнение",
        description=description,
    )
    session.add(balance)
    session.add(log)
    session.commit()

    assert balance.amount == 500



def test_decrease_balance_with_log(session: Session):

    balance = session.get(Balance, 1)
    amount = 500
    balance.decrease(float(amount))
    description = f"Списание со счета на сумму: {amount}"
    log = Log(
        user_id=balance.user_id,
        event_type="списание",
        description=description,
    )
    session.add(balance)
    session.add(log)
    session.commit()
    assert balance.amount == 0


def test_decrease_balance_ziro(session: Session):

    balance = session.get(Balance, 1)
    amount = 500
    result = ''
    if balance.amount < amount:
        result = 'Недостаточно средств'
    
    assert result == 'Недостаточно средств'


def test_delete_all_logs(session: Session):
    logs = session.query(Log).all()
    for log in logs:
        session.delete(log)
    session.commit()
    remaining_logs = session.query(Log).all()
    assert len(remaining_logs) == 0


def test_delete_balance(session: Session):

    balance = session.get(Balance, 1)
    session.delete(balance)
    session.commit()
    retrieved_balance = session.get(Balance, balance.id)
    assert retrieved_balance is None


def test_delete_user(session: Session):

    user = session.get(User, 1)
    session.delete(user)
    session.commit()
    retrieved_user = session.get(User, user.id)
    assert retrieved_user is None




