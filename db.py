import sqlite3


def create_users_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # ユーザーテーブルが存在しない場合は作成する
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
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



def create_posts_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # cursor.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)')
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
    select_query = 'INSERT INTO POSTS (content) VALUES (?)'
    cursor.execute(insert_query)
    conn.commit()
    conn.close()


def delete_all_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM users')

    conn.commit()
    conn.close()

def print_all_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    users = cursor.execute('SELECT * FROM users')
    users_name = []
    for i in users:
        users_name.append(i[1])
    conn.commit()
    conn.close()
    return users_name