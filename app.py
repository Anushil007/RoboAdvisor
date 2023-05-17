from flask import Flask,request,render_template
from database import  insert_user
from risk_calc import calculate_recommendations
import yfinance as yf
from flask import jsonify


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
    updates = request.form['updates']

    # Store the data in a SQLite database
     # Store the data in the database
    insert_user(age, income, experience, horizon, risk, style, products, updates)
    recommendations = calculate_recommendations(age, income, experience, horizon, risk, style, products, updates)

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

@app.route('/update_notification_preferences', methods=['POST'])
def update_notification_preferences():
    email = request.form.get('email')
    threshold = request.form.get('threshold')
    symbol = request.form.get('symbol')
    # Save notification preferences to database or file system
    return 'Notification preferences updated successfully.'


if __name__ == '__main__':
    app.run(debug=True)
