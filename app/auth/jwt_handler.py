import time
from datetime import datetime
from fastapi import HTTPException, status, Cookie 
from jose import jwt, JWTError
from database.database import get_settings
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY

def create_access_token(user: str) -> str: 
    payload = {
    "user": user,
    "expires": time.time() + 3600
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_access_token(token: str) -> dict: 
    try:
        data = jwt.decode(token, SECRET_KEY, 
        algorithms=["HS256"])
        expire = data.get("expires")
        if expire is None:
            raise HTTPException( 
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No access token supplied"
            )
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException( 
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Token expired!"
            )
        return data
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    

async def get_current_user_from_cookie(Bearer: str | None = Cookie(None)):
    if not Bearer:
        logger.info("Cookie 'Bearer' not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        data = verify_access_token(Bearer)
        user = data.get("user")
        if user is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user not found"
            )
        return user
    except HTTPException as e:
        logger.info(f"Authentication error: {e.detail}")
        raise e