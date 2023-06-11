import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, current_app
import db
import authentication as auth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, inspect
from sqlalchemy.orm import declarative_base, sessionmaker


app = Flask(__name__)
app.secret_key = 'secr;alksjfneet_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
engine = db.create_engine('sqlite:///database.db')
Base = declarative_base()
Session = sessionmaker(engine)
db_session = Session()

inspector = inspect(engine)

# テーブル名を指定してスキーマ情報を取得
table_name = 'users'
table_schema = inspector.get_columns(table_name)

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
    after_login_list = ['top', 'profile', 'timeline', 'post', 'logout']
    if 'username' in session:
        page_list = after_login_list
    else:
        page_list = before_login_list
    return dict(page_list=page_list)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    description = Column(String)
    age = Column(String)
    work = Column(String)
    partner = Column(String)

    @classmethod
    def authenticate_user(cls, session, username, password):
        user = session.query(cls).filter(cls.username == username).first()
        if user and auth.verify_password(password, user.password):
            return True
        else:
            return False



class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(String)


Base.metadata.create_all(engine)



users = db_session.query(User).all()
for i in users:
    print(i.username)


##### top #####
@app.route('/')
def top():
    users = db_session.query(User).all()
    return render_template('top.html', users=users)


##### register #####
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = auth.hash_password(password)

        new_user = User(username=username, email=email, password=hashed_password)
        db_session.add(new_user)
        db_session.commit()

        return render_template('top.html', success_message='Success!! Thank you for registration!')
    return render_template('register.html')

##### login #####
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.authenticate_user(db_session, username, password):
            session['username'] = username
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

##### profile #####
@app.route('/profile')
def profile():
    if 'username' in session:
        return render_template('profile.html', username=session['username'])
    else:
        error_message = 'You are not logged in.'
        return redirect(url_for('login', error_message=error_message))

##### create_profile #####
@app.route('/create_profile')
def create_profile():
    return render_template('create_profile.html')

##### post #####
@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        content = request.form['content']
        new_content = Post(content=content)
        db_session.add(new_content)
        db_session.commit()
        success_message = 'Posted Sccessfully'
        return redirect(url_for('timeline', success_message=success_message))
    else:
        return render_template('post.html')

##### timeline #####
@app.route('/timeline')
def timeline():
    success_message = request.args.get('success_message')
    posts = db_session.query(Post.content).all()
    return render_template('timeline.html', success_message=success_message, posts=posts)
    


##### ログアウト #####
@app.route('/logout')
def logout():
    # ログアウト処理: セッションからユーザー名を削除
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()
