import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, current_app
# from flask_sqlalchemy import SQLAlchemy
import db   
import authentication as auth


app = Flask(__name__)
app.secret_key = 'secr;alksjfneet_key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:database.db'

##### base.htmlで使用する変数や関数はグローバルとして定義する#####

# 「is_acrive」関数をグローバルに定義
@app.context_processor
def inject_is_active():
    def is_active(page):
        return 'active' if request.path == url_for(page) else ''
    return dict(is_active=is_active)

# 「page_list」変数をグローバルに定義
@app.context_processor
def page_list():
    before_login_list = ['top', 'register', 'login']
    after_login_list = ['top', 'profile','timeline','post', 'logout']
    if 'username' in session:
        page_list = after_login_list
    else:
        page_list = before_login_list
    return dict(page_list=page_list)


##### db作成 #####
db.create_users_table()
db.create_posts_table()


##### top #####
@app.route('/')
def top():
    # db.delete_all_users()
    current_app.logger.info(print(db.print_all_users()))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    db_users = cursor.execute('SELECT * FROM users').fetchall()
    # 以下がdb_usersの中身
    # [(17, 'admin', 'takaki0106kondo@icloud.com', '$2b$12$tJk8SVBsquXVLvILYzO2UuMFxQoh4EUmbiUW4e1LtcTaqLAZ7nfxC'), 
    # (18, 'takaki', 'takaki0106kondo@icloud.com', '$2b$12$QuixEWx1YoXLNnuCM9CRk.b/KoH.JdjRvCUukx0p9BCjOZYKoYUF6')]
    conn.close()
    users = []
    for user in db_users:
        users.append(user[1])
    return render_template('top.html', users=users)


##### register #####
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = auth.hash_password(password)

        db.add_user(username, email, hashed_password)

        return render_template('top.html', success_message='Success!! Thank you for registration!')

    return render_template('register.html')

##### login #####
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if auth.authenticate_user(username, password):
            session['username'] = username
            print(session)
            return redirect(url_for('profile'))
        else:
            error_message = 'Invalid username or password'
            return render_template('login.html', error_message=error_message)
    else:
        error_message = request.args.get('error_message')
        if error_message:
            return render_template('login.html', error_message=error_message)
        else:
            return render_template('login.html')


@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', username = session['username'])
    else:
        error_message = 'You are not logged in.'
        return redirect(url_for('login', error_message=error_message))

@app.route('/create_profile')
def create_profile():
    return render_template('create_profile.html')


@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        content = request.form['content']
        db.add_post(content)
        success_message = 'Posted Sccessfully'
        return redirect(url_for('timeline', success_message=success_message))
    else:
        return render_template('post.html')

@app.route('/timeline')
def timeline():
    success_message = request.args.get('success_message')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    db_posts = cursor.execute('SELECT * FROM posts').fetchall()
    # posts = [i for i in db_posts]
    for i in db_posts:
        print(type(i))

    return render_template('timeline.html', success_message=success_message, posts=db_posts)



##### ログアウト #####
@app.route('/logout')
def logout():
    # ログアウト処理: セッションからユーザー名を削除
    session.pop('username', None)
    return redirect('/')




if __name__ == '__main__':
    app.run()
