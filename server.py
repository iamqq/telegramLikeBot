"""Сервер Telegram бота, запускаемый непосредственно"""
# import logging
from pprint import pprint

from aiogram import Bot, Dispatcher, executor, types 

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ContentType

import  db

inline_btn_1 = InlineKeyboardButton('❤️', callback_data='button1')
inline_btn_2 = InlineKeyboardButton('🙈', callback_data='button2')
inline_btn_3 = InlineKeyboardButton('😔', callback_data='button3')
inline_btn_4 = InlineKeyboardButton('😁', callback_data='button4')

inline_kb_full = InlineKeyboardMarkup().row(inline_btn_1,inline_btn_2,inline_btn_3,inline_btn_4)

# logging.basicConfig(level=logging.INFO)

API_TOKEN = "278107460:AAETVY7_ANRT-CkPnKq1hS5pFuMN1jasmVw"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        text="<b>Бот для лайков</b>\n\n"
        "Добавите бота в ваш чат и он будет добавлять кнопки\n"
        " ❤️ 🙈 😔 😁 \n"
        "под каждое новое фото и видео добавляемое в чат\n\n"
        "сменить текущий набор кнопок чата /chatlikes 👍👌😡\n" 
        "сменить текущий набор кнопок для себя в чате /userlikes ⚙️🗑\n" 
        "удалить свой набор (использовать стандартный для чата) - /dropuserlikes",
        parse_mode="HTML")

@dp.message_handler(commands=['chatlikes'])
async def set_chat_likes(message: types.Message):
    pprint(message)
    # db.set_chat_likes(message.chat_id,message)

@dp.message_handler(commands=['userlikes'])
async def set_user_likes(message: types.Message):
    pp(message)
    # db.set_user_likes(message.chat.id, message.from_user.id)

@dp.message_handler(commands=['dropuserlikes'])
async def drop_user_likes(message: types.Message):
    # await message.answer(
    #     text="<b>Бот для лайков</b>\n\n"
    #      "вернуть стандартный - /defaultlikes",
    #     parse_mode="HTML")

# добавляем оценку под фото и видео 
@dp.message_handler(content_types=[ContentType.PHOTO,ContentType.VIDEO])
async def photo_handler(message: types.Message):
    await message.answer(text="Оцени!",reply_markup=inline_kb_full,reply=True)

@dp.callback_query_handler(func=lambda c: c.data == 'change')
async def callback_change(callback_query: types.CallbackQuery):

@dp.callback_query_handler(func=lambda c: c.data == 'drop')
async def callback_change(callback_query: types.CallbackQuery):

@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    # print(str(callback_query))
    # print(str(callback_query.message.reply_markup))
    # await bot.answer_callback_query(callback_query.id)
    # await bot.send_message(callback_query.from_user.id, callback_query.data)
    mess = callback_query.message
    keys = []
    for button in callback_query.message.reply_markup.inline_keyboard[0]:
        if callback_query.data == button.callback_data :
            rows = db.likes(mess.chat.id, mess.message_id, button.callback_data, callback_query.from_user.id)
            print(str(rows)+callback_query.from_user.username+'#'+callback_query.data)
            if rows == 0:
                button.text = button.text[0]
            else:
                button.text = button.text[0] +str(rows)
            # await bot.send_message(callback_query.from_user.id, button.text+"#"+button.callback_data)
        # else:
            # button.text=button.text+'$'
            # await bot.send_message(callback_query.from_user.id, button.text+"$"+button.callback_data)
        keys.append(InlineKeyboardButton(text=button.text, callback_data=button.callback_data))
    keyb = InlineKeyboardMarkup().row(keys[0],keys[1],keys[2],keys[3])
    await bot.edit_message_reply_markup(chat_id=mess.chat.id,message_id=mess.message_id,reply_markup=keyb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)