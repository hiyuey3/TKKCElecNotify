import sqlite3
cursor = sqlite3.connect("userinfo.db")

# 创建表
cursor.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)')

# 插入数据
cursor.execute('INSERT INTO users(name, age) VALUES (?, ?)', ('Alice', 21))

# 更新数据
cursor.execute('UPDATE users SET age = ? WHERE id = ?', (22, 1))

# 查询数据
cursor.execute('SELECT * FROM users')
