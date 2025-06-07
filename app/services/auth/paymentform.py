from fastapi import Request
from typing import List
import re

class PaymentDataForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List[str] = []
        self.success: List[str] = []
        self.card_number: int
        self.expiry_date: int
        self.cvv: int
        self.cardholder_name: str
        self.bank_name: str
        self.amount: float

    async def load_data(self):
        form = await self.request.form()
        self.card_number = form.get("card_number")
        self.expiry_date = form.get("expiry_date")
        self.cvv = form.get("cvv")
        self.cardholder_name = form.get("cardholder_name")
        self.bank_name = form.get("bank_name")
        self.amount = form.get("amount")
        self.errors = []

        try:
            if self.card_number:
                self.card_number = self.card_number.replace(" ", "")
                self.card_number = int(self.card_number)
            else:
                self.errors.append("Поле Номер карты обязательно для заполнения.")
        except (ValueError, TypeError):
            self.errors.append("Неверный формат номера карты. Пожалуйста, введите целое число.")

        try:
            if self.expiry_date:
                self.expiry_date = self.expiry_date.replace("/", "")
                self.expiry_date = int(self.expiry_date)
            else:
                self.errors.append("Поле Срок действия обязательно для заполнения.")
        except (ValueError, TypeError):
            self.errors.append("Неверный формат срока действия. Пожалуйста, введите целое число.")

        try:
            if self.cvv:
                self.cvv = int(self.cvv)
            else:
                self.errors.append("Поле CVV обязательно для заполнения.")
        except (ValueError, TypeError):
            self.errors.append("Неверный формат CVV. Пожалуйста, введите целое число.")

        if self.cardholder_name:
            if not re.match(r"^[A-Za-z\s]+$", self.cardholder_name):
                self.errors.append("Имя владельца карты содержит недопустимые символы. Разрешены только буквы и пробелы.")
        else:
            self.errors.append("Поле Имя владельца карты обязательно для заполнения.")