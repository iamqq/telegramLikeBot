create table likes(
    chat_id integer,
    message_id integer,
    button text,
    user_id integer,
    PRIMARY KEY(chat_id,message_id,button,user_id)
);

CREATE INDEX idx_likes_user_id ON likes(user_id);

create table userlikes(
    chat_id integer,
    user_id integer,
    likes text,
    PRIMARY KEY(chat_id,user_id)
);

create table chatlikes(
    chat_id integer,
    likes text,
    PRIMARY KEY(chat_id)
);