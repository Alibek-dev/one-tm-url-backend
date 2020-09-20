from flask import Flask, request
from flask_cors import CORS
from peewee import *
from playhouse.shortcuts import model_to_dict
import time
import random
from datetime import datetime, timezone
import dateutil.parser
import json

app = Flask(__name__)
db = SqliteDatabase('message.db')


class BaseModel(Model):
    class Meta:
        database = db


class MessageModel(BaseModel):
    messageId = CharField(30, unique=True)
    message = TextField()
    dueDate = CharField()
    password = CharField()
    notAskConfirmation = BooleanField()
    expired = False


db.connect()
db.create_tables([MessageModel])


@app.route('/message-id/<messageId>', methods=["GET"])
def get_message(messageId):
    message = MessageModel.get_or_none(MessageModel.messageId == messageId)
    if message is None:
        return "Сообщение не было найдено.", 404
    if message.dueDate != '':
        dateToDeleteMessage = dateutil.parser.parse(message.dueDate)
        dateUTC = datetime.now(timezone.utc)
        if dateUTC > dateToDeleteMessage:
            delete_message(message.messageId)
            message = {
                'expired': True
            }
            return json.dumps(message)
    return model_to_dict(message), 200


@app.route('/message', methods=["POST"])
def create_message():
    message = request.get_json()
    if message is None:
        return "Неправильный формат данных.", 404
    id = "id" + str(round(random.uniform(1, 100))) + str(round(time.time() * 1000))
    new_message = MessageModel.create(
        messageId=id,
        message=message['message'],
        dueDate=message['dateToDeleteMessage'],
        password=message['password'],
        notAskConfirmation=message['notAskConfirmation']
    )
    return model_to_dict(new_message), 200


@app.route('/message-id/<messageId>', methods=["DELETE"])
def delete_message(messageId):
    message = MessageModel.get_or_none(MessageModel.messageId == messageId)
    if message is None:
        return "Сообщение не было найдено.", 404
    message.delete_instance()
    return "Сообщение успешно удалено.", 200


cors = CORS(app)
if __name__ == '__main__':
    app.run(port=5000)