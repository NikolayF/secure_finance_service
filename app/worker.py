import json
from services.crud import ml_model as ModelService
from services.crud import balance as BalanceService
import time
import logging
from database.database import get_session
from worker import prediction
from models.log import Log



logging.basicConfig(level=logging.INFO)
def callback(ch, method, properties, body):
    with next(get_session()) as db:
        try:
            message_str = body.decode('utf-8')
            message_dict = json.loads(message_str)

            name = message_dict.get('name')
            user_id = message_dict.get('user_id')
            amount = message_dict.get('amount')
            model_request_id=message_dict.get('model_request_id')
            prediction_data = message_dict.get('prediction_data')
            bank_name = prediction_data.get('bank_name')
            Balance = BalanceService.get_balance_by_user_id(user_id, db)

            log = Log(
            user_id=user_id,
            model_request_id=model_request_id,
            event_type="финансовые операции",
            description='Операция находится в обработке',
            )
            db.add(log)
            db.commit()

            #Осуществляем проверку операции через модель:
            time.sleep(10)

            if bank_name != 'opg':

                ModelService.get_prediction(name, Balance, amount, db, model_request_id)

                db.commit()
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
            else:               
                ModelService.cancel_prediction(name, Balance, amount, db, model_request_id)

                db.commit()
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            db.rollback()
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def main():
    queue_name = 'task_queue_predict'
    channel = prediction.prediction_worker(queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    channel.start_consuming()

if __name__ == "__main__":
    main()