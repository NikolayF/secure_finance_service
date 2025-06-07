from sqlmodel import SQLModel, Session, create_engine 
from .config import get_settings
from sqlalchemy import text
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

engine = create_engine(url=get_settings().DATABASE_URL_psycopg, 
                       echo=True, pool_size=5, max_overflow=10)

def get_session():
    with Session(engine) as session:
        yield session


def drop_all_tables_cascade(engine):
    SQLModel.metadata.reflect(bind=engine)
    with engine.begin() as conn:
        for table_name in SQLModel.metadata.tables.keys():
           conn.execute(text(f"DROP TABLE IF EXISTS public.{table_name} CASCADE;"))
    logger.info("Все таблицы успешно удалены (с CASCADE).")


def init_db():
    drop_all_tables_cascade(engine)
    SQLModel.metadata.create_all(engine)
