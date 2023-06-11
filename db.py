import sqlite3
from app import session


##### "users" table #####

def create_users_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # ユーザーテーブルが存在しない場合は作成する
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            description TEXT,
            age TEXT,
            work TEXT,
            partner TEXT
        )
    '''
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()


def add_user(username, email, password):
    # データベースへの接続とカーソルの作成
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # ユーザーデータをデータベースに挿入する
    insert_query = '''
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    '''
    cursor.execute(insert_query, (username, email, password))
    conn.commit()
    conn.close()

def update_user(description, age, work, partner):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    username = session.get('username')
    query = "UPDATE users SET description = ?, age = ?, work = ?, partner = ? WHERE username = ?"
    result = cursor.execute(query, (description, age, work, partner, username))
    conn.commit()
    conn.close()
    print(result)


def show_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    db_users = cursor.execute('SELECT * FROM users').fetchall()
    users_name = [user for user in db_users]
    conn.close()
    return users_name

def show_user_profile(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE username = ?',(username, )).fetchone()
    return user


def delete_all_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users')
    conn.commit()
    conn.close()



##### "posts" table #####


def create_posts_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT
        )
    '''
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def add_post(content):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    insert_query = 'INSERT INTO POSTS (content) VALUES (?)'
    cursor.execute(insert_query, (content,))
    conn.commit()
    conn.close()

def show_posts():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    select_query = 'SELECT * FROM POSTS'
    cursor.execute(select_query)
    conn.commit()
    conn.close()




