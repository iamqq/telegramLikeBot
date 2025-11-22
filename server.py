"""Сервер Telegram бота, запускаемый непосредственно"""
import os
import asyncio
import logging
from typing import List, Dict

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, ContentType

import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.environ.get('API_TOKEN')
if not API_TOKEN:
    logger.error("API_TOKEN environment variable not set!")
    exit(1)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Album handling state
media_groups: Dict[str, List[types.Message]] = {}

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
    await db.set_chat_likes(message.chat.id, likes)
    await message.reply("Chat likes updated.")

@dp.message_handler(commands=['userlikes'])
async def set_user_likes(message: types.Message):
    likes = message.text[11:]
    await db.set_user_likes(message.chat.id, message.from_user.id, likes)
    await message.reply("User likes updated.")

@dp.message_handler(commands=['currentlikes'])
async def get_current_likes(message: types.Message):
    txt = 'userlikes:\n'
    rows = await db.get_userlikes(message.chat.id)
    for row in rows:
        txt = txt + str(row[1])+'-'+row[0]+'\n'

    txt = txt+'chatlikes:\n'
    rows = await db.get_chatlikes(message.chat.id)
    for row in rows:
        txt = txt + row[0]+'\n'
    await message.answer(text=txt)        

async def send_likes_markup(message: types.Message):
    """Helper to send likes markup for a message"""
    likes = await db.get_likes(message.chat.id, message.from_user.id)
    if len(likes) > 0:
        kb = InlineKeyboardMarkup(row_width=len(likes))
        step = 0
        for like in likes:
            step = step+1
            like = "0 "+like.replace("_"," ")
            kb.insert(InlineKeyboardButton(like, callback_data='b'+str(step)))
        await message.answer(text="Оцени!", reply_markup=kb, reply=True)

async def process_album(media_group_id: str):
    """Wait for album to complete then send one markup"""
    await asyncio.sleep(2.0) # Wait for other messages in the album
    
    messages = media_groups.pop(media_group_id, [])
    if not messages:
        return

    # Send markup only for the last message in the album
    last_message = messages[-1]
    await send_likes_markup(last_message)

# добавляем оценку под фото и видео 
@dp.message_handler(content_types=[ContentType.PHOTO, ContentType.VIDEO])
async def photo_handler(message: types.Message):
    if message.media_group_id:
        if message.media_group_id not in media_groups:
            media_groups[message.media_group_id] = []
            asyncio.create_task(process_album(message.media_group_id))
        media_groups[message.media_group_id].append(message)
    else:
        # Single file
        await send_likes_markup(message)

@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    mess = callback_query.message
    # Note: callback_query.from_user is the user who clicked, mess.chat.id is the chat
    # We need to pass the user who clicked to the db function
    rows = await db.likes(mess.chat.id, mess.message_id, callback_query.data, callback_query.from_user.id)
    
    users = {}
    buttons = {}
    for row in rows:
        if row[1] not in users:
            try:
                chat_member = await bot.get_chat_member(mess.chat.id, row[1])
                users[row[1]] = {'icons': [row[0]], 'name': chat_member} 
            except Exception as e:
                logger.error(f"Error getting chat member: {e}")
                continue
        else:
            users[row[1]]['icons'].append(row[0])
        if row[0] not in buttons:
            buttons[row[0]] = 1
        else:
            buttons[row[0]] = buttons[row[0]] + 1
            
    kb = InlineKeyboardMarkup(len(callback_query.message.reply_markup.inline_keyboard[0]))
    em = {}
    for button in callback_query.message.reply_markup.inline_keyboard[0]:
        words = button.text.split()
        if len(words) > 1:
            del words[0]
        em[button.callback_data] = " ".join(words)
        words.insert(0,"0")
        if button.callback_data in buttons:
            words[0] = str(buttons[button.callback_data])
        button.text = " ".join(words)
        kb.insert(InlineKeyboardButton(text=button.text, callback_data=button.callback_data))
        
    if len(rows) == 0:
        text = "Оцени!"
    else:
        text = ""
        for key in users:
            text+= users[key]['name'].user.first_name+":"
            for icon in users[key]['icons']:
                text+=em[icon]+" "
            text+="\n"

    await bot.edit_message_text(text=text, chat_id=mess.chat.id, message_id=mess.message_id, reply_markup=kb)

if __name__ == '__main__':
    # Ensure DB is initialized (optional, but good practice if we had an init function)
    # Since we don't have an explicit init loop here, we rely on the functions opening connections.
    # But for the schema, we might want to run it once.
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(db.init_db())
    
    executor.start_polling(dp, skip_updates=True)