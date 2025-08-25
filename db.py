import os
import sqlite3

DATABASE_URL = os.environ['DATABASE_URL']
# check_same_thread=False is required for sqlite3 with aiogram
conn = sqlite3.connect(DATABASE_URL, check_same_thread=False)
cursor = conn.cursor()
default_likes = "❤️ 🙈 😔 😁"

def set_user_likes(chat_id:int, user_id:int, likes:str):
    likes = " ".join(likes.split())
    if likes=="":
        cursor.execute("delete from userlikes where chat_id=? and user_id=?", (chat_id, user_id))
    else:    
        cursor.execute("select 1 from userlikes where chat_id=? and user_id=?", (chat_id, user_id))
        rows = len(cursor.fetchall())
        if rows==0:
            cursor.execute("insert into userlikes (chat_id,user_id,likes) values (?,?,?)", (chat_id, user_id, likes))
        else:
            cursor.execute("update userlikes set likes = ? where chat_id=? and user_id=?", (likes, chat_id, user_id))
    conn.commit()

def set_chat_likes(chat_id:int, likes:str):
    likes = " ".join(likes.split())
    if likes=="":
        likes = default_likes
    cursor.execute("select 1 from chatlikes where chat_id=?", (chat_id,))
    rows = len(cursor.fetchall())
    if rows==0:
        cursor.execute("insert into chatlikes (chat_id,likes) values (?,?)", (chat_id, likes))
    else:
        cursor.execute("update chatlikes set likes = ? where chat_id=?", (likes, chat_id))
    conn.commit()

def get_likes(chat_id:int, user_id:int):
    likes = default_likes
    cursor.execute("select likes from userlikes where chat_id=? and user_id=?", (chat_id, user_id))
    rows = cursor.fetchone()
    if rows:
        likes = rows[0] 
    else:
        cursor.execute("select likes from chatlikes where chat_id=?", (chat_id,))
        rows = cursor.fetchone()
        if rows:
            likes = rows[0] 
    return likes.split() 

def get_userlikes(chat_id:int):
    cursor.execute("select likes,user_id from userlikes where chat_id=?", (chat_id,))
    rows = cursor.fetchall()
    return rows 

def get_chatlikes(chat_id:int):
    cursor.execute("select likes from chatlikes where chat_id=?", (chat_id,))
    rows = cursor.fetchall()
    return rows 

def likes(chat_id:int, message_id:int, button:str, user_id:int):
    cursor.execute("select 1 from likes where chat_id=? and message_id=? and button=? and user_id=?", (chat_id, message_id, button, user_id))
    rows = len(cursor.fetchall())
    if rows==0:
        cursor.execute("insert into likes (chat_id,message_id,button,user_id) values (?,?,?,?)", (chat_id, message_id, button, user_id))
    else:
        cursor.execute("delete from likes where chat_id=? and message_id=? and button=? and user_id=?", (chat_id, message_id, button, user_id))

    cursor.execute("select button,user_id from likes where chat_id=? and message_id=?", (chat_id, message_id))
    rows = cursor.fetchall()
    conn.commit()
    return rows
