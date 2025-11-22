import os
import aiosqlite

DATABASE_URL = os.environ.get('DATABASE_URL', 'bot.db')
default_likes = "❤️ 🙈 😔 😁"

async def get_db_connection():
    return await aiosqlite.connect(DATABASE_URL)

async def init_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        with open('db.sql', 'r') as f:
            await db.executescript(f.read())
        await db.commit()

async def set_user_likes(chat_id: int, user_id: int, likes: str):
    likes = " ".join(likes.split())
    async with aiosqlite.connect(DATABASE_URL) as db:
        if likes == "":
            await db.execute("delete from userlikes where chat_id=? and user_id=?", (chat_id, user_id))
        else:
            cursor = await db.execute("select 1 from userlikes where chat_id=? and user_id=?", (chat_id, user_id))
            rows = len(await cursor.fetchall())
            if rows == 0:
                await db.execute("insert into userlikes (chat_id,user_id,likes) values (?,?,?)", (chat_id, user_id, likes))
            else:
                await db.execute("update userlikes set likes = ? where chat_id=? and user_id=?", (likes, chat_id, user_id))
        await db.commit()

async def set_chat_likes(chat_id: int, likes: str):
    likes = " ".join(likes.split())
    if likes == "":
        likes = default_likes
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("select 1 from chatlikes where chat_id=?", (chat_id,))
        rows = len(await cursor.fetchall())
        if rows == 0:
            await db.execute("insert into chatlikes (chat_id,likes) values (?,?)", (chat_id, likes))
        else:
            await db.execute("update chatlikes set likes = ? where chat_id=?", (likes, chat_id))
        await db.commit()

async def get_likes(chat_id: int, user_id: int):
    likes = default_likes
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("select likes from userlikes where chat_id=? and user_id=?", (chat_id, user_id))
        row = await cursor.fetchone()
        if row:
            likes = row[0]
        else:
            cursor = await db.execute("select likes from chatlikes where chat_id=?", (chat_id,))
            row = await cursor.fetchone()
            if row:
                likes = row[0]
    return likes.split()

async def get_userlikes(chat_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("select likes,user_id from userlikes where chat_id=?", (chat_id,))
        rows = await cursor.fetchall()
    return rows

async def get_chatlikes(chat_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("select likes from chatlikes where chat_id=?", (chat_id,))
        rows = await cursor.fetchall()
    return rows

async def likes(chat_id: int, message_id: int, button: str, user_id: int):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("select 1 from likes where chat_id=? and message_id=? and button=? and user_id=?", (chat_id, message_id, button, user_id))
        rows = len(await cursor.fetchall())
        if rows == 0:
            await db.execute("insert into likes (chat_id,message_id,button,user_id) values (?,?,?,?)", (chat_id, message_id, button, user_id))
        else:
            await db.execute("delete from likes where chat_id=? and message_id=? and button=? and user_id=?", (chat_id, message_id, button, user_id))
        
        await db.commit()
        
        cursor = await db.execute("select button,user_id from likes where chat_id=? and message_id=?", (chat_id, message_id))
        rows = await cursor.fetchall()
    return rows
