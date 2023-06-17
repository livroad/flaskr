import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, current_app, flash
import db
import authentication as auth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, inspect, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.orm import relationship
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'secr;alksjfneet_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
engine = db.create_engine('sqlite:///database.db')
Base = declarative_base()
Session = sessionmaker(engine)
db_session = Session()
migrate = Migrate(app, db)
inspector = inspect(engine)


# テーブル名を指定してスキーマ情報を取得
# table_name = 'posts'
# table_schema = inspector.get_columns(table_name)
# print(table_schema)



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
    created_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')


Base.metadata.create_all(engine)


##### top #####
@app.route('/')
def top():
    users = db_session.query(User).all()
    if 'username' in session:
        user = session.get('username')
        return render_template('top.html', user=user, users=users)
    else:
        return render_template('top.html', users=users)


##### register #####
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = auth.hash_password(password)

        new_user = User(username=username, email=email,
                        password=hashed_password)
        db_session.add(new_user)
        db_session.commit()
        flash('Success!! Thank you for registration!', 'success')
        return render_template('top.html')
    return render_template('register.html')

##### login #####


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.authenticate_user(db_session, username, password):
            session['username'] = username
            flash('Logged in Successfully!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    else:
        error_message = request.args.get('error_message')
        if error_message:
            flash(error_message, 'error')
            return render_template('login.html')
        else:
            return render_template('login.html')

##### profile #####


@app.route('/profile')
def profile():
    if 'username' in session:
        success_message = request.args.get('success_message')
        username = session.get('username')
        user = db_session.query(User).filter(User.username == username).first()
        return render_template('profile.html', username=session['username'], user=user, success_message=success_message)
    else:
        error_message = 'You are not logged in.'
        return redirect(url_for('login', error_message=error_message))

##### create_profile #####


@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'GET':
        return render_template('create_profile.html')
    else:
        description = request.form['description']
        age = request.form['age']
        work = request.form['work']
        partner = request.form['partner']
        username = session.get('username')
        updated_user = db_session.query(User).filter(
            User.username == username).first()
        updated_user.description = description
        updated_user.age = age
        updated_user.work = work
        updated_user.partner = partner
        db_session.commit()
        return redirect(url_for('profile', user=updated_user))


##### post #####
@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        content = request.form['content']
        new_content = Post(content=content)
        db_session.add(new_content)
        db_session.commit()
        flash('Posted Sccessfully', 'success')
        return redirect(url_for('timeline'))
    else:
        return render_template('post.html')

##### timeline #####


@app.route('/timeline')
def timeline():
    success_message = request.args.get('success_message')
    posts = db_session.query(Post).all()
    print(posts)
    # print(posts.content, posts.user_id)
    for post in posts:
        print(post.content)
    return render_template('timeline.html', success_message=success_message, posts=posts)


##### ログアウト #####
@app.route('/logout')
def logout():
    # ログアウト処理: セッションからユーザー名を削除
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()
