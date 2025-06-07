from sqlmodel import Field, SQLModel, Relationship
import logging 
from models.user import User

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Balance(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    amount: float = Field(default=0.0)
    user: User = Relationship(back_populates="balance")


    def get_amount(self) -> float:
        return self.amount

    def increase(self, source_amount: float) -> None:
        self.amount += source_amount

    def decrease(self, source_amount: float) -> None:
        if self.amount >= source_amount:
            self.amount -= source_amount
        else:
            logger.info("Недостаточно средств")