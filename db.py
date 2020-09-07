
import sqlite3


conn = sqlite3.connect("likes.db")
cursor = conn.cursor()

def likes(chat_id:int, message_id:int, button:str, user_id:int):

    cursor.execute(f"select * from likes where chat_id={chat_id} and message_id={message_id} and button='{button}' and user_id={user_id}")
    rows = len(cursor.fetchall())
    if rows==0:
        cursor.execute(f"INSERT INTO likes (chat_id,message_id,button,user_id) values ({chat_id},{message_id},'{button}',{user_id})")
    else:
        cursor.execute(f"delete from likes where chat_id={chat_id} and message_id={message_id} and button='{button}' and user_id={user_id}")

    cursor.execute(f"select * from likes where chat_id={chat_id} and message_id={message_id} and button='{button}'")
    rows = len(cursor.fetchall())
    conn.commit()
    return rows


