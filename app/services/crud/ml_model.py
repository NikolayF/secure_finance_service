from models.ml_model import MlModel
from models.log import Log
from services.crud.balance import decrease_balance, increase_balance
from typing import Optional
from sqlmodel import select
from typing import List
from sqlalchemy import desc

def create_ml_model(new_ml_model: MlModel, session) -> None:
    session.add(new_ml_model) 
    session.commit() 
    session.refresh(new_ml_model)

def get_model_by_name(name:str, session) -> Optional[MlModel]:
    ml_model = session.query(MlModel).filter(MlModel.name == name).first()
    if ml_model:
        return ml_model 
    return None

def get_prediction(model, balance, source_amount: float, session, model_request_id) -> None:
    decrease_balance(balance, source_amount, session)
    
    ml_model = get_model_by_name(model, session)

    if ml_model:
        #Передаём параметры для определения мошеннической транзакции и записываем в лог результат
        pass
    else:
        description = f'Операция успешно одобрена перевод выполнен'
        log = Log(
            user_id=balance.user_id,
            model_request_id=model_request_id,
            event_type="финансовые операции",
            description=description,
        )
        session.add(log)
        session.commit()

def cancel_prediction(model, balance, source_amount: float, session, model_request_id) -> None:
    increase_balance(balance, source_amount, session)
    
    ml_model = get_model_by_name(model, session)

    if ml_model:
        #Передаём параметры для определения мошеннической транзакции и записываем в лог результат
        pass
    else:
        description = f'Операция отклонена, обнаружен подозрительный перевод'
        log = Log(
            user_id=balance.user_id,
            model_request_id=model_request_id,
            event_type="финансовые операции",
            description=description,
        )
        session.add(log)
        session.commit()

async def view_model_logs(session) -> List[Log]:
    query = select(Log).order_by(desc(Log.timestamp))
    logs = session.exec(query).all()
    return logs
