from fastapi import Request
from typing import List

class PredictionLogForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List[str] = []
        self.logs: List[dict] = []

