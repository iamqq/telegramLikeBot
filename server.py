"""Сервер Telegram бота, запускаемый непосредственно"""
from aiogram import Bot, Dispatcher, executor, types 

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ContentType

import db

API_TOKEN = "278107460:AAETVY7_ANRT-CkPnKq1hS5pFuMN1jasmVw"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer(
        text="<b>Бот для лайков</b>\n"
        "Добавите бота в ваш чат и он будет добавлять кнопки\n"
        " ❤️ 🙈 😔 😁 \n"
        "под каждое новое фото и видео добавляемое в чат\n\n"
        "сменить текущий набор кнопок чата \n"
        "<b>/chatlikes 👍 👌 😡 Yes! No!</b>\n" 
        "сменить текущий набор кнопок для себя в чате\n"
        "<b>/userlikes Нет Like ⚙️ Да Очень_хорошо</b>\n" 
        "отдельные значения разделять <b>пробелом</b>\n"
        "пробел в тексте заменяйте <b>подчеркиванием _</b>\n\n"
        "<b>/chatlikes</b> и <b>/userlikes</b> без параметров\n"
        " - вернуться к набору по умолчанию",
        parse_mode="HTML")

@dp.message_handler(commands=['chatlikes'])
async def set_chat_likes(message: types.Message):
    likes = message.text[11:]
    db.set_chat_likes(message.chat.id,likes)

@dp.message_handler(commands=['userlikes'])
async def set_user_likes(message: types.Message):
    likes = message.text[11:]
    db.set_user_likes(message.chat.id, message.from_user.id,likes)

# добавляем оценку под фото и видео 
@dp.message_handler(content_types=[ContentType.PHOTO,ContentType.VIDEO])
async def photo_handler(message: types.Message):
    likes = db.get_likes(message.chat.id, message.from_user.id)
    # print(len(likes))
    if len(likes) > 0:
        kb = InlineKeyboardMarkup(row_width=len(likes))
        step = 0
        for like in likes:
            step = step+1
            like = "0 "+like.replace("_"," ")
            kb.insert(InlineKeyboardButton(like, callback_data='b'+str(step)))
        await message.answer(text="Оцени!",reply_markup=kb,reply=True)

@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    mess = callback_query.message
    kb = InlineKeyboardMarkup(len(callback_query.message.reply_markup.inline_keyboard[0]))
    for button in callback_query.message.reply_markup.inline_keyboard[0]:
        if callback_query.data == button.callback_data :
            words = button.text.split()
            rows = db.likes(mess.chat.id, mess.message_id, button.callback_data, callback_query.from_user.id)
            words[0] = str(rows)
            button.text = " ".join(words)
            # if rows == 0:
            #     button.text = button.text[0]
            # else:
            #     button.text = button.text[0] +str(rows)
        kb.insert(InlineKeyboardButton(text=button.text, callback_data=button.callback_data))
    await bot.edit_message_reply_markup(chat_id=mess.chat.id,message_id=mess.message_id,reply_markup=kb)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)