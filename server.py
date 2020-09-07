"""Сервер Telegram бота, запускаемый непосредственно"""
# import logging
# import os

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
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Бот для учёта финансов\n\n"
        "Добавить расход: 250 такси\n"
        "Сегодняшняя статистика: /today\n"
        "За текущий месяц: /month\n"
        "Последние внесённые расходы: /expenses\n"
        "Категории трат: /categories")

@dp.message_handler(content_types=[ContentType.PHOTO,ContentType.VIDEO])
async def photo_handler(message: types.Message):
    await message.answer(text="Оцени!",reply_markup=inline_kb_full,reply=True)

# @dp.message_handler(lambda message: message.text.startswith('/del'))
# async def del_expense(message: types.Message):
#     """Удаляет одну запись о расходе по её идентификатору"""
#     row_id = int(message.text[4:])
#     # expenses.delete_expense(row_id)
#     answer_message = "Удалил"
#     await message.answer(answer_message)


# @dp.message_handler(commands=['categories'])
# async def categories_list(message: types.Message):
#     """Отправляет список категорий расходов"""
#     categories = Categories().get_all_categories()
#     answer_message = "Категории трат:\n\n* " +\
#             ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
#     await message.answer(answer_message)


# @dp.message_handler(commands=['today'])
# async def today_statistics(message: types.Message):
#     """Отправляет сегодняшнюю статистику трат"""
#     answer_message = expenses.get_today_statistics()
#     await message.answer(answer_message)


# @dp.message_handler(commands=['month'])
# async def month_statistics(message: types.Message):
#     """Отправляет статистику трат текущего месяца"""
#     answer_message = expenses.get_month_statistics()
#     await message.answer(answer_message)


# @dp.message_handler(commands=['expenses'])
# async def list_expenses(message: types.Message):
#     """Отправляет последние несколько записей о расходах"""
#     last_expenses = expenses.last()
#     if not last_expenses:
#         await message.answer("Расходы ещё не заведены")
#         return

#     last_expenses_rows = [
#         f"{expense.amount} руб. на {expense.category_name} — нажми "
#         f"/del{expense.id} для удаления"
#         for expense in last_expenses]
#     answer_message = "Последние сохранённые траты:\n\n* " + "\n\n* "\
#             .join(last_expenses_rows)
#     await message.answer(answer_message)


# @dp.message_handler()
# async def others_message(message: types.Message):
#     print(repr(message))
#     # # """Добавляет новый расход"""
#     # # try:
#     # #     expense = expenses.add_expense(message.text)
#     # # except exceptions.NotCorrectMessage as e:
#     # #     await message.answer(str(e))
#     # #     return
#     # answer_message = (
#     #     f"Добавлены траты .\n\n"
#     #     f"  ")
#     # await message.answer(answer_message)

# @dp.callback_query_handler(func=lambda c: c.data == 'button1')
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
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,message_id=callback_query.message.message_id,text=callback_query.message.text,reply_markup=keyb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)