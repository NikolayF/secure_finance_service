from fastapi import Request
from typing import Optional, List

class IncreaseBalanceForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.success: List = []
        self.amount: float
        self.default_amount: Optional[float] = None
        self.current_amount: Optional[float] = None

    async def load_data(self):
        form = await self.request.form()
        try:
            self.amount = float(form.get("amount"))
        except (ValueError, TypeError):
            self.amount = None
        self.default_amount = float(form.get("default_amount")) if form.get("default_amount") else None

    async def is_valid(self):
        if self.amount <= 0:
            self.errors.append("Сумма пополнения должна быть положительным числом")

        if not self.errors:
            return True
        return False