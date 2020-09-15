from flask import Flask, request
from flask_cors import CORS
from peewee import *
from playhouse.shortcuts import model_to_dict
import time
import random

app = Flask(__name__)

db = SqliteDatabase('message.db')


class BaseModel(Model):
    class Meta:
        database = db


class MessageModel(BaseModel):
    url = CharField(30, unique=True)
    message = TextField()


db.connect()
db.create_tables([MessageModel])


@app.route('/message-id/<url>', methods=["GET"])
def get_message(url):
    message = MessageModel.get_or_none(MessageModel.url == url)
    if message is None:
        return "Сообщение не было найдено.", 404
    return model_to_dict(message), 200


@app.route('/message', methods=["POST"])
def create_message():
    message = request.get_json()
    if message is None:
        return "Неправильный формат данных.", 404
    id = str(round(random.uniform(1, 100))) + str(round(time.time() * 1000))
    new_message = MessageModel.create(url=id, message=message['message'])
    return model_to_dict(new_message), 200


@app.route('/message-id/<url>', methods=["DELETE"])
def delete_message(url):
    message = MessageModel.get_or_none(MessageModel.url == url)
    if message is None:
        return "Сообщение не было найдено.", 404
    message.delete_instance()
    return "Сообщение успешно удалено.", 200


cors = CORS(app)
if __name__ == '__main__':
    app.run(port=5000)