import asyncio
import pprint
from sys import exit

import uvicorn
from fastapi import FastAPI, Request
from httpx import AsyncClient
from pyngrok import ngrok

from COIN_MARKET_CAP import price_of_crypt
from DB_alchemy import my_DB
from my_own_valids import Price_of_crypt, Message_from_BD
from validations import MessageBodyModel, ResponseToMessage

TOKEN = "5141013666:AAFDkri_oHLhSxP5fbu0qFEAgm_BDwZ2Hn4"
TELEGRAM_SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
TELEGRAM_SET_WEBHOOK_URL = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
HOST_URL = None

db = my_DB()

# https://github.com/FarukOzderim/Telegram-Bot-Python-FastAPI


app = FastAPI()

if TOKEN == "":
    exit("No secret found, exiting now!")


@app.get("/get_price")
def get_price(crypt: str, currency: str):
    """Функция-обработчик позволяющая с помощью API получить цену критовалюты
    как в телеграм боте но уже в JSON"""
    price = price_of_crypt(crypt, currency)
    my_dict = {"fromm": f"{crypt}", "to": f"{currency}", "price": f"{price}"}
    price_dict = Price_of_crypt(**my_dict)
    # print(price_dict)
    return price_dict


@app.get("/get_message")
async def get_message(numb: int):
    """Функция-обработчик позволяющая с помощью API получить весь запрос
    с помощью его номера"""
    mes = await db.get_from_db(numb)
    mess_dict = Message_from_BD(id=mes.id, message=mes.message, answer=mes.answer, date=mes.date)
    return mess_dict


@app.post("/webhook/{TOKEN}")
async def post_process_telegram_update(message: MessageBodyModel, request: Request):
    """Чуть чуть адаптированная функция"""
    try:
        mes = message.message.text
        crypt, currency = mes.split(" ")
        resp = get_price(crypt, currency)
        price = resp.price
        my_dict = {"text": f"Цена {crypt} в {currency}: {price}", "chat_id": message.message.chat.id}
        await db.insert_into_db(mes, my_dict["text"])
    except Exception as e:
        print(e)
        my_dict = {"text": "Извините, но вы что-то не так ввели!", "chat_id": message.message.chat.id}
    finally:
        js = ResponseToMessage(**my_dict)
        pprint.pprint(js)
        return js


async def request(url: str, payload: dict, debug: bool = False):
    """ПОЛНОСТЬЮ СКОПИРОВАННАЯ ФУНКЦИЯ"""
    async with AsyncClient() as client:
        request = await client.post(url, json=payload)
        if debug:
            print(request.json())
        return request


# async def send_a_message_to_user(telegram_id: int, message: str) -> bool:
#     message = ResponseToMessage(
#         **{
#             "text": message,
#             "chat_id": telegram_id,
#         }
#     )
#     req = await request(TELEGRAM_SEND_MESSAGE_URL, message.dict())
#     return req.status_code == 200


async def set_telegram_webhook_url() -> bool:
    """ПОЛНОСТЬЮ СКОПИРОВАННАЯ ФУНКЦИЯ"""
    payload = {"url": f"{HOST_URL}/webhook/{TOKEN}"}
    req = await request(TELEGRAM_SET_WEBHOOK_URL, payload)
    return req.status_code == 200


if __name__ == "__main__":
    PORT = 8000
    http_tunnel = ngrok.connect(PORT, bind_tls=True)
    public_url = http_tunnel.public_url
    HOST_URL = public_url

    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(set_telegram_webhook_url())
    if success:
        uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="info")
    else:
        print("Fail, closing the app.")
