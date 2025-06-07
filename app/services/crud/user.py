from models.user import User
from typing import List, Optional
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_all_users(session) -> List[User]:
    return session.query(User).all()

def get_user_by_id(id:int, session) -> Optional[User]:
    users = session.get(User, id) 
    if users:
        return users 
    return None

def get_user_by_email(email:str, session) -> Optional[User]:
    user = session.query(User).filter(User.email == email).first()
    if user:
        return user 
    return None

async def create_user(new_user: User, session) -> None:
    logger.info(f"Создание пользователя с email: {new_user.email}")
    try:
        new_user.is_superuser = False
        session.add(new_user) 
        session.commit() 
        session.refresh(new_user)
    except Exception as e:
            logger.exception(f"Ошибка создания пользователя {new_user.email}: {e}")
            session.rollback()
            raise

def view_logs(user_id: int, session):
    user = session.get(User, user_id)
    logs_list: List[dict] = []
    if user:
        for log in user.logs:
            logs_list.append({"timestamp": log.timestamp, "event_type": log.event_type, "description": log.description})
    else:
        logger.info(f"Пользователь с ID {user_id} не найден")
    return logs_list