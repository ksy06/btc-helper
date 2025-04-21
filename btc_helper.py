from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return "<h1>BTC Helper</h1><p><a href='/login'>Login</a> | <a href='/signup'>Sign Up</a></p>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Login failed. <a href='/login'>Try again</a>"
    return "<h2>Login</h2><form method='POST'>Email: <input name='email'><br>Password: <input name='password' type='password'><br><input type='submit'></form><a href='/signup'>Sign up</a>"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return "<h2>Sign Up</h2><form method='POST'>Email: <input name='email'><br>Password: <input name='password' type='password'><br><input type='submit'></form><a href='/login'>Login</a>"

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        content = request.form['memo']
        date = datetime.date.today()
        new_memo = Memo(user_id=current_user.id, date=date, content=content)
        db.session.add(new_memo)
        db.session.commit()
    memos = Memo.query.filter_by(user_id=current_user.id).order_by(Memo.date.desc()).all()
    memo_html = ''.join([f"<p><strong>{memo.date}</strong><br>{memo.content}</p>" for memo in memos])
    return f"<h2>Welcome, {current_user.email}!</h2><form method='POST'><textarea name='memo'></textarea><br><input type='submit'></form><h3>Your Memos</h3>{memo_html}<p><a href='/logout'>Logout</a></p>"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/check_alerts')
def check_alerts():
    price_today = 35000
    moving_avg_60 = 34000
    if price_today > moving_avg_60:
        print("BTC Alert: Price crossed above 60-day MA")
    return "Alert check complete."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000)

