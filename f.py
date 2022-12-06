from datetime import datetime
import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017")
mydb = myclient["tg_bot_bd"]
users_and_values = mydb["col"]
dateformat = "%d.%m.%Y %H:%M"
time = datetime.strptime("19.10.2004 0:59", dateformat)
d = {"username": "user_name", "date": time, "text": "ifj"}
print(str(datetime.now())[:16])
users_and_values.insert_one(d)
print(users_and_values.find().sort("date", 1)[0])
