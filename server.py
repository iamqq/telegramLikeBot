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

def update_message_text(text: str, user_name: str, icon: str):
    """
    Parses the text, toggles the icon for the user, and returns:
    1. The new text
    2. A dictionary of counts for each icon
    """
    lines = text.split('\n')
    user_line_index = -1
    user_icons = []
    
    # 1. Parse existing text
    new_lines = []
    for i, line in enumerate(lines):
        if line.startswith(user_name + ":"):
            user_line_index = i
            # Extract existing icons (everything after "Name:")
            content = line[len(user_name) + 1:].strip()
            if content:
                user_icons = content.split()
            new_lines.append(line) # Placeholder, will replace later
        elif line.strip() != "": # Keep other lines
            new_lines.append(line)

    # 2. Toggle the icon
    if icon in user_icons:
        user_icons.remove(icon)
    else:
        user_icons.append(icon)

    # 3. Reconstruct User Line
    new_user_line = f"{user_name}: {' '.join(user_icons)}"
    
    if user_line_index != -1:
        if not user_icons:
            # If no icons left, remove the line entirely
            del new_lines[user_line_index]
        else:
            new_lines[user_line_index] = new_user_line
    elif user_icons:
        # New user adding a like
        new_lines.append(new_user_line)

    # 4. Calculate Counts
    counts = {}
    final_text = "\n".join(new_lines)
    
    for line in new_lines:
        parts = line.split(":")
        if len(parts) > 1:
            icons = parts[1].strip().split()
            for i in icons:
                counts[i] = counts.get(i, 0) + 1
                
    return final_text, counts

@dp.callback_query_handler()
async def process_callback_button1(callback_query: types.CallbackQuery):
    mess = callback_query.message
    user = callback_query.from_user
    # Use first_name as the identifier (simple but has collisions)
    user_name = user.first_name 
    
    # Get the button icon (the text part, e.g., "❤️" from "5 ❤️")
    # We need to find which icon this button represents.
    # The callback_data is like 'b1', 'b2'. We need to map 'b1' -> '❤️'
    
    # Reconstruct the map from the keyboard
    # We assume the keyboard layout hasn't changed structure
    icon_map = {}
    for button in mess.reply_markup.inline_keyboard[0]:
        # Button text is like "5 ❤️" or "❤️" or "0 ❤️"
        parts = button.text.split()
        if len(parts) > 1 and parts[0].isdigit():
            icon_char = " ".join(parts[1:]) # Everything after the number
        else:
            icon_char = button.text # Just the icon
        
        icon_map[button.callback_data] = icon_char

    clicked_icon = icon_map.get(callback_query.data)
    if not clicked_icon:
        return # Should not happen

    # Update Text and Get Counts
    current_text = mess.text if mess.text and mess.text != "Оцени!" else ""
    new_text, counts = update_message_text(current_text, user_name, clicked_icon)
    
    if not new_text:
        new_text = "Оцени!"

    # Update Keyboard Numbers
    kb = InlineKeyboardMarkup(row_width=len(mess.reply_markup.inline_keyboard[0]))
    for button in mess.reply_markup.inline_keyboard[0]:
        icon = icon_map[button.callback_data]
        count = counts.get(icon, 0)
        new_button_text = f"{count} {icon}"
        kb.insert(InlineKeyboardButton(text=new_button_text, callback_data=button.callback_data))

    if new_text != mess.text or True: # Always try to update to ensure consistency
        try:
            await bot.edit_message_text(text=new_text, chat_id=mess.chat.id, message_id=mess.message_id, reply_markup=kb)
        except Exception as e:
            # Telegram throws error if message content is exactly the same
            pass
    
    await callback_query.answer() # Stop the loading animation

if __name__ == '__main__':
    # Ensure DB is initialized (optional, but good practice if we had an init function)
    # Since we don't have an explicit init loop here, we rely on the functions opening connections.
    # But for the schema, we might want to run it once.
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(db.init_db())
    
    executor.start_polling(dp, skip_updates=True)