from fastapi import APIRouter, HTTPException, status, Depends, Request, Response
from database.database import get_session
from models.user import User
from models.balance import Balance
from services.crud import user as UserService
from services.crud import balance as BalanceService
from typing import List
import jwt
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from services.auth.registrationform import RegistrationForm
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from services.auth.registrationform import RegistrationForm
from fastapi.templating import Jinja2Templates
import logging
from jose import jwt
from database.config import get_settings
from auth.hash_password import HashPassword

hash_password = HashPassword()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
templates = Jinja2Templates(directory="view")
user_route = APIRouter(tags=['User'])

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), session=Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        user = UserService.get_user_by_email(email=email, session=session)
        if user is None:
            raise credentials_exception
        return user
    except InvalidTokenError:
        raise credentials_exception

@user_route.post('/signup_postman')
async def signup(data: User, session=Depends(get_session)) -> dict:
    if UserService.get_user_by_email(data.email, session) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with supplied username exists")

    hashed_password = get_password_hash(data.password)
    data.password = hashed_password

    await UserService.create_user(data, session)
    balance = Balance(user=data)
    await BalanceService.create_balance(balance, session)
    return {"message": "User successfully registered!"}


@user_route.post('/signin')
async def signin(data: User, session=Depends(get_session)):
    user = UserService.get_user_by_email(data.email, session)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не существует")
    
    if hash_password.verify_hash(data.password, user.password):
        return {"message": "Вход успешно выполнен"}
    
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Логин или пароль не совпадают")

    
@user_route.get('/members', response_model=List[User])
async def get_all_users(current_user: User = Depends(get_current_user), session=Depends(get_session)) -> list:
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not admin to perform this action")
    return UserService.get_all_users(session)


@user_route.get('/logs')
async def get_logs(user_id: int, current_user: User = Depends(get_current_user), session=Depends(get_session)) -> list:
    if not (current_user.is_superuser or current_user.id == user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized user or not admin to perform this action")

    return UserService.view_logs(user_id, session)





@user_route.post("/create_user")
async def create_user(response: Response, form_data, session=Depends(get_session)) -> dict[str, str]:    
    user_exist = UserService.get_user_by_email(form_data.username, session)
    if user_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User allready exists")
         
    user = UserService.create_user(form_data, session)
    balance = Balance(user=user)
    BalanceService.create_balance(balance, session)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid details passed."
    )


@user_route.post("/signup", response_class=HTMLResponse)
async def signup_post(request: Request, session: AsyncSession = Depends(get_session)):
    form = RegistrationForm(request)
    await form.load_data()

    if await form.is_valid():
        try:
            response = RedirectResponse("/auth/login", status.HTTP_302_FOUND)
            user = UserService.get_user_by_email(form.email, session)
            if user is not None:
                form.errors.append("Такой пользователь уже существует")
                return templates.TemplateResponse("register.html", form.__dict__)
            
            hashed_password = get_password_hash(form.password)

            db_user = User(email=form.email, password=hashed_password)

            await UserService.create_user(db_user, session)
            balance = Balance(user=db_user)
            await BalanceService.create_balance(balance, session)

            return response

        except Exception as e:
            logging.exception(f"Ошибка во время регистрации: {e}")
            await session.rollback() 
            form.errors.append("Во время регистрации произошла ошибка. Пожалуйста, попробуйте ещё раз")
            return templates.TemplateResponse("register.html", form.__dict__)

    form.__dict__.update(msg="")
    logging.info(f"Ошибка во время регистрации, ошибки в форме: {form.errors}")
    return templates.TemplateResponse("register.html", form.__dict__)

