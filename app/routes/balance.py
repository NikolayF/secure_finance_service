from fastapi import APIRouter, HTTPException, status, Depends, Request
from database.database import get_session
from models.balance import Balance
from services.crud import user as UserService
from services.crud import balance as BalanceService
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from models.balance import Balance
from models.log import Log
from decimal import Decimal
from database.config import get_settings
from auth.authenticate import authenticate_cookie, get_current_user
from services.auth.balanceform import IncreaseBalanceForm
from typing import Optional
import uuid

settings = get_settings()
templates = Jinja2Templates(directory="view")


balance_router = APIRouter(tags=['Balance'])

@balance_router.post('/increase')
async def increase(data: Balance, session=Depends(get_session)) -> dict:
    Balance = BalanceService.get_balance_by_user_id(data.user_id, session)
    if Balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Balance for user_id = {data.user_id} not exist")
    
    await BalanceService.increase_balance(Balance, data.amount, session)

    return {"message": "Balance increase successuful"}

@balance_router.post('/decrease')
async def decrease(data: Balance, session=Depends(get_session)) -> dict:
    Balance = BalanceService.get_balance_by_user_id(data.user_id, session)
    if Balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Balance for user_id = {data.user_id} not exist")
    
    if Balance.amount < float(data.amount):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Недостаточно средств для списания.")
    
    BalanceService.decrease_balance(Balance, data.amount, session)
    
    return {"message": "Balance decrease successuful"}

@balance_router.get('/balance')
async def get_balance(user_id: int, session=Depends(get_session)) -> dict:
    Balance = BalanceService.get_balance_by_user_id(user_id, session)
    if Balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Balance for user_id = {user_id} not exist")
    
    return {"message": f"Текущий баланс пользователя: {Balance.amount}"}



@balance_router.get("/options", response_class=HTMLResponse)
async def get_increase_balance_page(request: Request, session=Depends(get_session)):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        user = await authenticate_cookie(token)
    else:
        user = None

    user = UserService.get_user_by_email(user, session)

    Balance = BalanceService.get_balance_by_user_id(user.id, session)
    default_amount = 200.00
    return templates.TemplateResponse(
        "balance_options.html",
        {"request": request, "errors": [], "default_amount": default_amount, "current_balance": Balance.amount, "user": user},
    )


async def increase_user_balance(balance: Balance, source_amount: float, session: AsyncSession) -> None:
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


@balance_router.post("/increase_balance", response_class=HTMLResponse)
async def increase_balance(request: Request, session: AsyncSession = Depends(get_session), user: Optional[str] = Depends(get_current_user)):
    form = IncreaseBalanceForm(request)
    await form.load_data()
    if await form.is_valid():
        amount = form.amount
        try:
            user = UserService.get_user_by_email(user, session)

            Balance = BalanceService.get_balance_by_user_id(user.id, session)
            await increase_user_balance(Balance, amount, session)

            form.success.append("Счёт успешно пополнен")
            return templates.TemplateResponse("balance_options.html", context={"request": request, "errors": [], "success": "Счет успешно пополнен", "default_amount": amount, "current_balance": Balance.amount, "user": user})


        except Exception as e:
            form.errors.append(f"Возникла ошибка: {str(e)}")

    return templates.TemplateResponse("balance_options.html", form.__dict__)
