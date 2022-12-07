import db_processing
import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode

logging.basicConfig(level=logging.INFO)
API_TOKEN = '5987156620:AAGHv-c6oaOXamUm0cWTEGa9jsYxsheawvE'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()


class FormSetDate(StatesGroup):
    user_event = State()
    user_date = State()
    user_time = State()


#Some additional features, currently not in use. The main project starts in line 79

@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.reply("Hi there! What's your name?")


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    await message.reply("How old are you?")


@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    return await message.reply("Age gotta be a number.\nHow old are you? (digits only)")


@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(age=int(message.text))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Male", "Female")
    markup.add("Other")
    await message.reply("What is your gender?", reply_markup=markup)


@dp.message_handler(lambda message: message.text not in ["Male", "Female", "Other"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Bad gender name. Choose your gender from the keyboard.")


#The main project starts below

@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text
        markup = types.ReplyKeyboardRemove()
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Hi! Nice to meet you,', md.bold(data['name'])),
                md.text('Age:', md.code(data['age'])),
                md.text('Gender:', data['gender']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN,
        )
    await state.finish()


@dp.message_handler(commands='set_event')
async def cmd_set_event(message: types.Message):
    await FormSetDate.user_event.set()
    await message.reply("Eneter your event, please")


@dp.message_handler(state=FormSetDate.user_event) #recieving a text of event
async def process_user_event(message: types.Message, state: FSMContext):
    async with state.proxy() as data_event:
        data_event['user_event'] = message.text
    await FormSetDate.next()
    await message.reply("Enter the date, please, in this format: day.month.year")


@dp.message_handler(state=FormSetDate.user_date) #recieving event's date
async def process_set_date(message: types.Message, state: FSMContext):
    async with state.proxy() as data_event:
        if not len(message.text.split('.')) == 3:
            return message.reply("Enter the correct date")
        if not (1 <= int(message.text.split('.')[0]) <= 31 and 1 <= int(message.text.split('.')[1]) <= 12 and 2000 <=
                int(message.text.split('.')[2]) <= 2030):
            return message.reply("Enter the correct date")
        data_event['user_date'] = message.text
    await FormSetDate.next()
    await message.reply(
        "Enter the time, please, in this format: hours:minutes . Assumed, that number of hours will be in range from 0 to 23 and minutes in range from 0 to 59")


@dp.message_handler(state=FormSetDate.user_time) #recieving event's time
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data_event:
        if not (len(message.text.split(':'))) == 2:
            return message.reply("Enter the correct time")
        if not (0 <= int(message.text.split(':')[0]) <= 23 and 0 <= int(message.text.split(':')[1]) <= 59):
            return message.reply("Enter the correct time")
        data_event['user_time'] = message.text
        record = {"username": message.from_user.id, "time": data_event['user_date'] + " " + data_event['user_time'],
                  "text": data_event['user_event']}
        db_processing.ChangingOfUserRecords(user_name=message.chat.id, record=record)
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text(data_event['user_event']),
                md.text(data_event['user_date']),
                md.text(data_event['user_time']),
                sep='\n',
            )
        )
    await state.finish()


async def SendMessege(id_of_chat, text): #send message to a specific chat
    await bot.send_message(
        id_of_chat,
        md.text(
            text
        )
    )
