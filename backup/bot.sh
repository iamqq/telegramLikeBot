#!/bin/sh
export DATABASE_URL="postgresql://admin:p0stavka@192.168.86.104:5432/telegram?client_encoding=utf8"
export API_TOKEN="278107460:AAETVY7_ANRT-CkPnKq1hS5pFuMN1jasmVw"
/usr/bin/python3 /root/telegramLikeBot/server.py
