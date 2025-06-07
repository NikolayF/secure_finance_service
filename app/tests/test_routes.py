from fastapi.testclient import TestClient
import logging

logger = logging.getLogger(__name__)


def test_home_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200


def test_signup(client: TestClient):
    body = {
            "email": "test@mail.ru",
            "password": "123456"
            }
    response = client.post("/user/signup_postman", json=body)
    assert response.status_code == 200
    assert response.text == '{"message":"User successfully registered!"}'

def test_signin(client: TestClient):
    body = {
            "email": "test@mail.ru",
            "password": "123456"
            }
    response = client.post("/user/signin", json=body)
    assert response.status_code == 200
    response_json = response.json()
    assert "message" in response_json
    expected_message = "Вход успешно выполнен"
    assert response_json["message"] == expected_message


def test_increase_balanse(client: TestClient):
    body = {
            "user_id": 1,
            "amount": 1000
            }
    response = client.post("/balance/increase", json=body)
    assert response.status_code == 200
    assert response.text == '{"message":"Balance increase successuful"}'


def test_prediction(client: TestClient):
    body = {
        "name": "Test_Model",
        "version": 1,
        "description": "It`s test model for pytest",
        "prediction_data": {
            "feature1": 123.00,
            "feature2": "string",
            "feature3": True,
            "feature4": 15
        }
    }
    response = client.post("/ml_model/prediction?user_id=1", json=body)
    assert response.status_code == 200
    response_json = response.json()
    assert "message" in response_json
    expected_message = "Sending message for predict, show logs for details. Use get_prediction_log with model_request_id"
    assert response_json["message"] == expected_message
    assert "model_request_id" in response_json




def test_load_prediction_logs(client: TestClient):
    body = {
            "prediction_id": '944d421e-60fe-496e-acae-430c93104a38'
            }
    response = client.post("/ml_model/prediction_log", json=body)
    assert response.status_code == 200