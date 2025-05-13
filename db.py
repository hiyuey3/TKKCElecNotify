import sqlite3
cursor = sqlite3.connect("userinfo.db")
cursor.execute("select * from userinfo")