# import sqlite3

import os
import psycopg2

DATABASE_URL = "postgres://tskofeitnbwvja:bde35e8f7d47a8b20e4616c20474c4f0995bce00392151a5825031e489a580c5@ec2-52-200-134-180.compute-1.amazonaws.com:5432/d5n36m8235d8it"
# DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# conn = psycopg2.connect(du, sslmode='require')

# conn = sqlite3.connect("likes.db")

cursor = conn.cursor()

default_likes = "❤️ 🙈 😔 😁"

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
    likes = default_likes
    cursor.execute(f"select likes from userlikes where chat_id={chat_id} and user_id={user_id}")
    rows = cursor.fetchone()
    if rows:
        likes = rows[0] 
    else:
        cursor.execute(f"select likes from chatlikes where chat_id={chat_id}")
        rows = cursor.fetchone()
        if rows:
            likes = rows[0] 
    return likes.split() 

def get_userlikes(chat_id:int):
    cursor.execute(f"select likes,user_id from userlikes where chat_id={chat_id}")
    rows = cursor.fetchall()
    return rows 

def get_chatlikes(chat_id:int):
    cursor.execute(f"select likes from chatlikes where chat_id={chat_id}")
    rows = cursor.fetchall()
    return rows 

def likes(chat_id:int, message_id:int, button:str, user_id:int):
    cursor.execute(f"select * from likes where chat_id={chat_id} and message_id={message_id} and button='{button}' and user_id={user_id}")
    rows = len(cursor.fetchall())
    if rows==0:
        cursor.execute(f"insert into likes (chat_id,message_id,button,user_id) values ({chat_id},{message_id},'{button}',{user_id})")
    else:
        cursor.execute(f"delete from likes where chat_id={chat_id} and message_id={message_id} and button='{button}' and user_id={user_id}")

    cursor.execute(f"select button,user_id from likes where chat_id={chat_id} and message_id={message_id}") #" and button='{button}'")
    rows = cursor.fetchall()
    users = {}
    # for row in rows:
    #     if row[1] not in users:
    #         users[row[1]] = {'icons': [row[0]],'name': row[1]} 
    #     else:
    #         users[row[1]]['icons'].append(row[0])
    # return users
    conn.commit()
    return rows


