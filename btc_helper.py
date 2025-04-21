from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    content = db.Column(db.Text, nullable=False)

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        content = request.form['memo']
        date = datetime.date.today()
        new_memo = Memo(date=date, content=content)
        db.session.add(new_memo)
        db.session.commit()
    memos = Memo.query.order_by(Memo.date.desc()).all()
    memo_html = ''.join([f"<p><strong>{memo.date}</strong><br>{memo.content}</p>" for memo in memos])
    return f"""
        <h2>BTC Helper - 메모 기록</h2>
        <form method='POST'>
            <textarea name='memo'></textarea><br>
            <input type='submit'>
        </form>
        <h3>전체 메모</h3>
        {memo_html}
    """

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
