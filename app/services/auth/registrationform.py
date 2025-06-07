from fastapi import Request
from typing import List

class RegistrationForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.email: str
        self.password: str
        self.confirm_password: str

    async def load_data(self):
        form = await self.request.form()
        self.email = form.get("email")
        self.password = form.get("password")
        self.confirm_password = form.get("confirm_password")

    async def is_valid(self):
        if not self.email or "@" not in self.email:
            self.errors.append("Это ошибочный email")
        if not self.password or len(self.password) < 3:  
            self.errors.append("Пароль должен содержать не менее 3 символов")
        if self.password != self.confirm_password:
            self.errors.append("Пароли должны совпадать")

        if not self.errors:
            return True
        return False