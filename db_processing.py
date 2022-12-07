import pymongo
from datetime import datetime
import bot

myclient = pymongo.MongoClient("mongodb://localhost:27017")
mydb = myclient["tg_bot_bd"]
users_and_values = mydb["col"]


def ChangingOfUserRecords(user_name, record): #user_name is a billet for additional features
    time = DateFormater(record.get("time"))
    users_and_values.insert_one({"username": record.get("username"), "date": time, "text": record.get("text")})
    return 0


async def EventsChecker():
    rec = users_and_values.find().sort("date", 1)[0]
    if str(users_and_values.find().sort("date", 1)[0]['date'])[:16] == str(datetime.now())[:16]:
        await bot.SendMessege(rec['username'], rec['text'])
        users_and_values.delete_one({'_id': rec['_id']})


def DateFormater(time):
    dateformat = "%d.%m.%Y %H:%M"
    return datetime.strptime(time, dateformat)
