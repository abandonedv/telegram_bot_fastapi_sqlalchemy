from pydantic import BaseModel
from typing import Optional


class Price_of_crypt(BaseModel):
    fromm: str
    to: str
    price: float


class Message_from_BD(BaseModel):
    id: int
    message: str
    answer: str
    date: str
