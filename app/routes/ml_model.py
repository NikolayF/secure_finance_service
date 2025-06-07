from fastapi import APIRouter, HTTPException, status, Depends, Request
from database.database import get_session
from models.ml_model import MlModel
from services.crud import ml_model as ModelService
from services.crud import balance as BalanceService
from typing import Optional
from pika import BlockingConnection, ConnectionParameters, PlainCredentials, BasicProperties
from uuid import uuid4
import json
import os
from dotenv import load_dotenv
from database.config import get_settings
from auth.authenticate import authenticate_cookie, get_current_user
#from services.auth.predictform import  WineQualityForm
from services.auth.paymentform import  PaymentDataForm
from services.auth.logsform import PredictionLogForm
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from services.crud import user as UserService
from services.crud import balance as BalanceService
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()
templates = Jinja2Templates(directory="view")

ml_model_route = APIRouter(tags=['Ml_model'])

rabbitmq_host = settings.RABBITMQ_HOST
rabbitmq_port = settings.RABBITMQ_PORT
rabbitmq_user = settings.RABBITMQ_USER
rabbitmq_password = settings.RABBITMQ_PASS
rabbitmq_queue = settings.RABBITMQ_QUEUE


async def publish_message(message: str):
    try:
        credentials = PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = ConnectionParameters(rabbitmq_host, rabbitmq_port, '/', credentials)
        connection = BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue=rabbitmq_queue, durable=True)

        channel.basic_publish(exchange='', routing_key=rabbitmq_queue, body=message.encode('utf-8'),
        properties=BasicProperties(
        delivery_mode = 2,
        ))
        logging.info(f" [x] Sent '{message}' to RabbitMQ queue: {rabbitmq_queue}")
        connection.close()
        return True
    except Exception as e:
        logging.info(f"Error publishing message to RabbitMQ: {e}")
        return False


def check_data(predict_data: dict):
    if type(predict_data["feature1"]) is not float:
        return False
    if type(predict_data["feature2"]) is not str:
        return False
    if type(predict_data["feature3"]) is not bool:
        return False
    if type(predict_data["feature4"]) is not int:
        return False
    return True


@ml_model_route.post('/model')
async def create_model(data: MlModel, session=Depends(get_session)) -> dict:  
    ModelService.create_ml_model(data, session)
    return {"message": "Ml_model successfully created"}

@ml_model_route.post('/prediction')
async def predict(data: MlModel, user_id: int, session=Depends(get_session)) -> dict:  
    generated_uid = uuid4()
    message = {
        "name": data.name,
        "user_id": user_id,
        "model_request_id": str(generated_uid),
        "amount": 15,
        "prediction_data": {
            "feature1": data.prediction_data["feature1"],
            "feature2": data.prediction_data["feature2"],
            "feature3": data.prediction_data["feature3"],
            "feature4": data.prediction_data["feature4"]
        }
    }
    logging.info('message complete')
    if check_data(message["prediction_data"]) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Data is not valid")
    
    Balance = BalanceService.get_balance_by_user_id(user_id, session)
    if Balance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Balance for user_id = {user_id} not exist")   
    if Balance.amount < float(15):
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Недостаточно средств для списания.")
    
    
    

    message_str = json.dumps(message)
    logging.info('publish message')
    if publish_message(message_str):
        return {
            "message": f"Sending message for predict, show logs for details. Use get_prediction_log with model_request_id",
            "model_request_id": generated_uid
                }
    else:
        raise HTTPException(status_code=500, detail="Failed to send predict task to worker.")
    

@ml_model_route.get('/get_prediction_log')
async def predict(model_request_id, session=Depends(get_session)) -> list: 
    return ModelService.view_model_logs(model_request_id, session)


@ml_model_route.get("/payment", response_class=HTMLResponse)
async def wine_quality_form(request: Request):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        user = await authenticate_cookie(token)
    else:
        user = None
    return templates.TemplateResponse("payment.html", {"request": request, "errors": [], "user": user})

@ml_model_route.post("/predict", response_class=HTMLResponse)
async def send_predict_task(request: Request, session: AsyncSession = Depends(get_session), user: Optional[str] = Depends(get_current_user)):
    form = PaymentDataForm(request)
    await form.load_data()
    if not form.errors:
    
        try:

            generated_uid = uuid4()
            user = UserService.get_user_by_email(user, session)
            
            message = {
                "name": "latest_model",
                "user_id": user.id,
                "model_request_id": str(generated_uid),
                "amount": form.amount,
                "prediction_data": {
                    "card_number": form.card_number,
                    "expiry_date": form.expiry_date,
                    "cvv": form.cvv,
                    "cardholder_name": form.cardholder_name,
                    "bank_name": form.bank_name
                    
                }
            }


            Balance = BalanceService.get_balance_by_user_id(user.id, session)
            if Balance is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Баланс для пользователя {user.id} не существует")   
            if Balance.amount < float(15):
                raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Недостаточно средств для списания.")
   
            message_str = json.dumps(message)
            is_message = await publish_message(message_str)
            if is_message:             
                return templates.TemplateResponse(
                    "payment.html",
                    {"request": request, "errors": [], "success": ["Операция отправлена в обработку, ход выполнения можно посмотреть в истории операций"], "user": user},
                )

            else:
                form.errors.append("При оплате произошла ошибка")
                return templates.TemplateResponse("payment.html", form.__dict__)


        except Exception as e:
            form.errors.append(f"Возникла ошибка: {str(e)}")

    return templates.TemplateResponse("payment.html", form.__dict__)


@ml_model_route.get("/prediction_log", response_class=HTMLResponse)
async def get_prediction_log_form(request: Request, session: AsyncSession = Depends(get_session)):
    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        user = await authenticate_cookie(token)
    else:
        user = None

    errors = []

    try:
        logs = await ModelService.view_model_logs(session)
        if not logs:
            errors.append(f"Вы ещё не совершили ни одной операции, история пуста")
            return templates.TemplateResponse(
                "prediction_log.html", {"request": request, "errors": errors, "logs": [], "user": user}
            )

        return templates.TemplateResponse(
            "prediction_log.html", {"request": request, "errors": [], "logs": logs, "user": user}
        )

    except Exception as e:
        errors.append(f"Произошла ошибка при получении логов: {str(e)}")
        return templates.TemplateResponse(
            "prediction_log.html", {"request": request, "errors": errors, "logs": [], "user": user}
        )

@ml_model_route.post("/prediction_log", response_class=HTMLResponse)
async def get_logs_with_guid(request: Request, session: AsyncSession = Depends(get_session), user: Optional[str] = Depends(get_current_user)):
    form = PredictionLogForm(request)
    await form.load_data()
    if await form.is_valid():
        model_request_id = form.prediction_id
        try:
            logs = await ModelService.view_model_logs(model_request_id, session)
            if not logs:
                form.errors.append(f"Нет логов для предсказания с ID {model_request_id}")
                return templates.TemplateResponse("prediction_log.html", form.__dict__)

            return templates.TemplateResponse(
                "prediction_log.html", {"request": request, "errors": [], "logs": logs, "user": user}
            )

        except Exception as e:
            form.errors.append(f"Произошла ошибка при получении логов: {str(e)}")
            return templates.TemplateResponse("prediction_log.html", form.__dict__)

    return templates.TemplateResponse("prediction_log.html", form.__dict__)
