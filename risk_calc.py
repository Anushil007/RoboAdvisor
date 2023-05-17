import sqlite3
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.optimize import minimize

def calculate_recommendations(age, income, experience, horizon, risk, style, products, updates):

    # Connect to the SQLite database
    conn = sqlite3.connect('mydatabase.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Execute the SELECT statement to retrieve the last row
    # Rowid is a unique identifier for each row in the table and is automatically generated when a new row is inserted into the table
    cursor.execute('SELECT * FROM users ORDER BY ROWID DESC LIMIT 1')

    # Fetch the last row
    last_row = cursor.fetchone()

    # Print the last row
    print(last_row)

    # Extract the relevant user data
    age = last_row[0]
    income = last_row[1]
    experience = last_row[2]
    horizon = last_row[3]
    risk = last_row[4]
    style = last_row[5]
    products = last_row[6].split(',') # Assuming the products are stored as a comma-separated string


    #print(user_age, user_income, user_experience, user_horizon, user_risk, user_style, user_products)
    # Define the investment products and their characteristics
    products_data = {
        'stocks': {
            'symbol': '^GSPC', # S&P 500 index as a proxy for stocks
            'expected_return': 0.10,
            'volatility': 0.25,
            'correlation': 1.0
        },
        'bonds': {
            'symbol': 'IEF', # iShares 7-10 Year Treasury Bond ETF as a proxy for bonds
            'expected_return': 0.03,
            'volatility': 0.05,
            'correlation': 0.2
        },
        'etfs': {
            'symbol': 'VTI', # Vanguard Total Stock Market ETF as a proxy for etfs
            'expected_return': 0.08,
            'volatility': 0.15,
            'correlation': 0.9
        },
        'mutual_funds': {
            'symbol': 'VTSAX', # Vanguard Total Stock Market Index Fund as a proxy for mutual funds
            'expected_return': 0.06,
            'volatility': 0.10,
            'correlation': 0.7
        }
    }

    # Retrieve historical prices for the investment products
    data = {}
    for product in products:
        symbol = products_data[product]['symbol']
        data[product] = yf.download(symbol, start='2010-01-01')['Adj Close']

    # Calculate the daily returns for each investment product
    returns = pd.DataFrame()
    for product in products:
        returns[product] = data[product].pct_change()

    #print(returns)


    # Calculate the mean and standard deviation of the daily returns for each investment product
    means = returns.mean()
    stds = returns.std()

    # Calculate the correlation matrix of the daily returns for the investment products
    correlations = returns.corr()

    # Define the investment portfolio
    portfolio = np.array([1 / len(products)] * len(products))

    # Define the objective function for the mean-variance optimization
    # Define the objective function for the mean-variance optimization
    def objective_function(weights, means, stds, correlations, age, income, experience, horizon, risk_tolerance, style, product_types):
        # Calculate the expected return and volatility of the portfolio
        portfolio_mean = np.sum(means * weights)
        portfolio_std = np.sqrt(np.dot(weights, np.dot(correlations, stds ** 2 * weights)))

        # Calculate the risk score adjustment factor based on age, income, experience, and horizon
        if experience == 'no_experience':
            experience_factor = 0.1
        elif experience == 'some_experience':
            experience_factor = 0.05
        else: # experienced
            experience_factor = 0

        if horizon == 'short_term':
            horizon_factor = -0.1
        elif horizon == 'medium_term':
            horizon_factor = 0
        else: # long-term
            horizon_factor = 0.1

        if risk_tolerance == 'low_risk':
            base_risk_score = (portfolio_mean - products_data['bonds']['expected_return']) / portfolio_std
        elif risk_tolerance == 'medium_risk':
            base_risk_score = portfolio_mean / portfolio_std
        else: # high risk tolerance
            base_risk_score = portfolio_mean / (portfolio_std ** 2)

        if style == 'conservative':
            style_factor = -0.1
        elif style == 'aggressive':
            style_factor = 0.1
        else: # balanced
            style_factor = 0
        
        # Calculate the adjustment factors based on age and income
        if age < 30:
            age_factor = 0.1
        elif age < 50:
            age_factor = 0.05
        else:
            age_factor = 0

        if income < 50000:
            income_factor = 0.1
        elif income < 100000:
            income_factor = 0.05
        else:
            income_factor = 0

        # Calculate the adjustment factor based on the selected product types
        product_risk_scores = {'stocks': 8, 'bonds': 4, 'etfs': 6, 'mutual_funds': 7}
        selected_product_risk_scores = [product_risk_scores.get(product_type, 0) for product_type in product_types]
        product_factor = np.mean(selected_product_risk_scores) / 10

        # Calculate the final risk score based on all the adjustment factors
        risk_score = base_risk_score * (1 + experience_factor + horizon_factor + style_factor + product_factor + age_factor + income_factor)

        # Return the negative of the risk score, since we want to maximize it
        return -risk_score
    # Define the constraints for the mean-variance optimization
    constraints = ({
        'type': 'eq',
        'fun': lambda weights: np.sum(weights) - 1 # The sum of the weights must be 1
    })

    # Define the bounds for the mean-variance optimization
    bounds = [(0, 1)] * len(products)

    # Define the initial guess for the portfolio weights
    portfolio = np.array([1 / len(products)] * len(products))

    # Optimize the investment portfolio based on the user's input data
    result = minimize(objective_function, portfolio, args=(means, stds, correlations, age, income, experience, horizon, risk, style, products), constraints=constraints, bounds=bounds, method='SLSQP')

    # Extract the optimized weights for the investment products
    optimized_weights = result.x

    # Recommend the investment products and their allocation to the user
    recommended_products = [products[i] for i in range(len( products)) if optimized_weights[i] > 0]
    recommended_allocation = optimized_weights[optimized_weights > 0]

    # print(f'Recommended Products: {recommended_products}')
    # print(f'Recommended Allocation: {recommended_allocation}')
    recommendation = dict(zip(recommended_products, recommended_allocation))
    return recommendation