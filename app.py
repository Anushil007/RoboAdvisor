from flask import Flask,request,render_template
from database import  insert_user
from risk_calc import calculate_recommendations
import yfinance as yf
from flask import jsonify
import smtplib
from email.mime.text import MIMEText
from apscheduler.schedulers.background import BackgroundScheduler

# define the app using Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    # Render the portfolio performance tracking page
    return render_template('analytics.html')


# This is the home page route
@app.route('/process_form', methods=['POST'])
def process_form():
    age = request.form['age']
    income = request.form['income']
    experience = request.form['experience']
    horizon = request.form['horizon']
    risk = request.form['risk']
    style = request.form['style']
    products = request.form.getlist('products[]')
    #updates = request.form['updates']

    # Store the data in a SQLite database
     # Store the data in the database
    insert_user(age, income, experience, horizon, risk, style, products)
    recommendations = calculate_recommendations(age, income, experience, horizon, risk, style, products)

    return render_template('results.html', recommendations=recommendations)

@app.route('/get_company_data')
def get_company_data():
    symbol = request.args.get('symbol')
    company = yf.Ticker(symbol)
    history = company.history(period='max')
    data = {
        'dates': list(history.index.strftime('%Y-%m-%d')),
        'prices': list(history['Close'])
    }
    return jsonify(data)

scheduler = BackgroundScheduler()
scheduler.start()

def send_email(email, symbol, threshold, current_price):
    msg = MIMEText(f"The current price of {symbol} is {current_price}. It has exceeded the threshold of {threshold}.")
    msg['Subject'] = f"{symbol} price alert!"
    msg['From'] = 'your-email@example.com'
    msg['To'] = email

# Replace the placeholders with your SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'your-smtp-username'
    smtp_password = 'your-smtp-password'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

def check_price(symbol, threshold, email):
    stock = yf.Ticker(symbol)
    current_price = stock.info['MarketPrice']

    if current_price > threshold:
        send_email(email, symbol, threshold, current_price)

@app.route('/update_notification_preferences', methods=['POST'])
def update_notification_preferences():
    email = request.form.get('email')
    threshold = float(request.form.get('threshold'))
    symbol = request.form.get('symbol')

    # Schedule a job to check the price every minute
    scheduler.add_job(check_price, 'interval', minutes=1, args=[symbol, threshold, email])

    # Save notification preferences to database or file system
    return 'Notification preferences updated successfully.'
if __name__ == '__main__':
    app.run(debug=True)
