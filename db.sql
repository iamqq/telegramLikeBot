create table likes(
    chat_id integer,
    message_id integer,
    button text,
    user_id integer,
    PRIMARY KEY(chat_id,message_id,button,user_id)
);