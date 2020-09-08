
import sqlite3
import emoji_likes


conn = sqlite3.connect("likes.db")
cursor = conn.cursor()
default_likes = "❤️🙈😔😁"

def set_user_likes(chat_id:int, user_id:int, likes:str):
    likes = " ".join(likes.split())
    if likes=="":
        cursor.execute(f"delete from userlikes where chat_id={chat_id} and user_id={user_id}")
    else:    
        cursor.execute(f"select * from userlikes where chat_id={chat_id} and user_id={user_id}")
        rows = len(cursor.fetchall())
        if rows==0:
            cursor.execute(f"insert into userlikes (chat_id,user_id,likes) values ({chat_id},{user_id},'{likes}')")
        else:
            cursor.execute(f"update userlikes set likes = '{likes}' where chat_id={chat_id} and user_id={user_id}")
    conn.commit()

def set_chat_likes(chat_id:int, likes:str):
    likes = " ".join(likes.split())
    if likes=="":
        likes = default_likes
    cursor.execute(f"select * from chatlikes where chat_id={chat_id}")
    rows = len(cursor.fetchall())
    if rows==0:
        cursor.execute(f"insert into chatlikes (chat_id,likes) values ({chat_id},'{likes}')")
    else:
        cursor.execute(f"update chatlikes set likes = '{likes}' where chat_id={chat_id}")
    conn.commit()

def get_likes(chat_id:int, user_id:int):
    cursor.execute(f"select likes from userlikes where chat_id={chat_id} and user_id={user_id}")
    likes = cursor.fetchone()
    if likes:
        return emoji_likes.likes_list(likes[0])
    else:
        cursor.execute(f"select likes from chatlikes where chat_id={chat_id}")
        likes = cursor.fetchone()
        if likes:
            return emoji_likes.likes_list(likes[0])
        else:
            return emoji_likes.likes_list(default_likes)

def likes(chat_id:int, message_id:int, button:str, user_id:int):

    cursor.execute(f"select * from likes where chat_id={chat_id} and message_id={message_id} and button='{button}' and user_id={user_id}")
    rows = len(cursor.fetchall())
    if rows==0:
        cursor.execute(f"insert into likes (chat_id,message_id,button,user_id) values ({chat_id},{message_id},'{button}',{user_id})")
    else:
        cursor.execute(f"delete from likes where chat_id={chat_id} and message_id={message_id} and button='{button}' and user_id={user_id}")

    cursor.execute(f"select * from likes where chat_id={chat_id} and message_id={message_id} and button='{button}'")
    rows = len(cursor.fetchall())
    conn.commit()
    return rows


