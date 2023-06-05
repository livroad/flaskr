import sqlite3
import bcrypt
from flask import current_app

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # ユーザーの検証
    query = "SELECT * FROM users WHERE username=?"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    if user and verify_password(password, user[3]):
        return True
    else:
        return False

    conn.close()
