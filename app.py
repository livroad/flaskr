import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
import authentication as auth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, inspect, func
from sqlalchemy.orm import relationship
from flask_migrate import Migrate

app = Flask(__name__)
app.secret_key = 'secr;alksjfneet_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


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


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    description = Column(String)
    age = Column(String)
    work = Column(String)

    @classmethod
    def authenticate_user(cls, db_session, username, password):
        user = db_session.query(cls).filter(cls.username == username).first()
        if user and auth.verify_password(password, user.password):
            return True
        else:
            return False


class Post(db.Model):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String)
    created_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')


# with app.app_context():
#     inspector = inspect(db.engine)
#     columns = inspector.get_columns('posts')
#     for column in columns:
#         print(column['name'], column['type'])


##### top #####
@app.route('/')
def top():
    users = db.session.query(User).all()
    if 'username' in session:
        user = session.get('username')
        return render_template('top.html', user=user, users=users)
    else:
        return render_template('top.html', users=users)


##### register #####
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = auth.hash_password(password)
        new_user = User(username=username, email=email,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Success!! Thank you for registration!', 'success')
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

##### login #####
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.authenticate_user(db.session, username, password):
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



##### profile #####
@app.route('/profile')
def profile():
    if 'username' in session:
        success_message = request.args.get('success_message')
        username = session.get('username')
        user = db.session.query(User).filter(User.username == username).first()
        if user is None:
            flash('User not found', 'error')
            return redirect(url_for('login'))
        return render_template('profile.html', user=user, success_message=success_message)
    else:
        flash('Please login')
        return redirect(url_for('login'))


##### create_profile #####
@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if 'username' in session:
        if request.method == 'GET':
            username = session.get('username')
            user = db.session.query(User).filter(User.username == username).first()
            return render_template('create_profile.html', user=user)
        else:
            description = request.form.get('description')
            age = request.form.get('age')
            work = request.form.get('work')
            username = session.get('username')
            updated_user = db.session.query(User).filter(User.username == username).first()
            if updated_user is None:
                flash('User not found', 'error')
                return redirect(url_for('login'))
            updated_user.description = description
            updated_user.age = age
            updated_user.work = work
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
    else:
        flash('Please login')
        return redirect(url_for('login'))



##### post #####
@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        content = request.form.get('content')
        user = db.session.query(User).filter(User.username == session.get('username')).first()
        post = Post(content=content, user_id=user.id)
        db.session.add(post)
        db.session.commit()
        flash('Posted Sccessfully', 'success')
        return redirect(url_for('timeline'))
    else:
        return render_template('post.html')

##### timeline #####
@app.route('/timeline')
def timeline():
    success_message = request.args.get('success_message')
    posts = db.session.query(Post).all()
    return render_template('timeline.html', success_message=success_message, posts=posts)


##### edit #####
@app.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit(post_id):
    if request.method == 'GET':
        post = Post.query.get_or_404(post_id)
        return render_template('edit.html', post=post)
    else:
        post = Post.query.get_or_404(post_id)
        content = request.form.get('content')
        post.content = content
        db.session.commit()
        flash('Post Updated Successfully', 'success')
        return redirect(url_for('timeline'))


##### delete #####
@app.route('/delete/<int:post_id>')
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post Deleted Successfully', 'success')
    return redirect(url_for('timeline'))




##### ログアウト #####
@app.route('/logout')
def logout():
    # ログアウト処理: セッションからユーザー名を削除
    session.pop('username', None)
    return redirect('/')


if __name__ == '__main__':
    app.run()
