from scipy.optimize import minimize
import numpy as np
import yfinance as yf
from risk_calc import recommended_allocation, recommended_products, risk,products_data


#Change the recommended products to its tickers
for i in range(len(recommended_products)):
    recommended_products[i] = products_data[recommended_products[i]]['symbol']

#print(recommended_products) 

# Store the recommended products and their allocation in a dictionary
portfolio_weights = dict(zip(recommended_products, recommended_allocation))

#print(portfolio_weights)

# function to calculate the returns of a portfolio
# def calculate_returns(prices):
#     returns = np.diff(prices) / prices[:-1]
#     return returns

# function to calculate the returns of a portfolio
def calculate_portfolio_returns(weights, asset_data):
    portfolio_returns = []
    #max_len_returns = ((asset_data[asset]['returns']) for asset in asset_data.keys())
    for asset, weight in weights.items():
        asset_returns = asset_data[asset]['returns']
        # Pad or truncate the returns to match the length of the longest asset returns array
        # padding_length = max_len_returns - len(asset_returns)
        # if padding_length >= 0:
        #     asset_returns = np.pad(asset_returns, (0, padding_length), mode='constant')
        # else:
        #     asset_returns = asset_returns[:max_len_returns]
        portfolio_returns.append(weight * asset_returns)
    # Sum the returns across all assets
    portfolio_returns = np.sum(portfolio_returns, axis=0)
    return portfolio_returns
# function to calculate the covariance matrix of a portfolio
import numpy as np

def calculate_covariance_matrix(asset_data):
    all_returns = []
    # max_len_returns = max([len(asset_data[asset]['returns']) for asset in asset_data.keys()])
    for asset in asset_data.keys():
        asset_returns = asset_data[asset]['returns']
        # Pad or truncate the returns to match the length of the longest asset returns array
        # padding_length = max_len_returns - len(asset_returns)
        # if padding_length >= 0:
        #     asset_returns = np.pad(asset_returns, (0, padding_length), mode='constant')
        # else:
        #     asset_returns = asset_returns[:max_len_returns]
        all_returns.append(asset_returns)
    # Calculate the covariance matrix using the padded returns
    cov_matrix = np.cov(all_returns)
    return cov_matrix

# function to calculate the risk of a portfolio
def calculate_portfolio_risk(weights, cov_matrix):
    weights_list = list(weights.values())
    portfolio_risk = np.sqrt(np.dot(weights_list, np.dot(cov_matrix, weights_list)))
    return portfolio_risk

# function to optimize the portfolio weights
def optimize_portfolio(portfolio_returns,cov_matrix, risk):
    n_assets = 3
    bounds = [(0, 1) for i in range(n_assets)]
    constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    initial_weights = np.array([1 / n_assets for i in range(n_assets)])
    def objective_function(weights):
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        portfolio_return = np.sum(portfolio_returns * weights)
        risk_val = 0.1 if risk == 'low_risk' else 0.2 if risk == 'medium_risk' else 0.3
        risk_penalty = (portfolio_risk - risk_val) ** 2
        return -portfolio_return + risk_penalty
    result = minimize(objective_function, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
    optimized_weights = result.x
    return optimized_weights

    # # Set the optimization constraints
    # constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]

    # # Set the optimization bounds
    # bounds = [(0, 1) for asset in returns]

    # # Set the initial guess for the weights
    # initial_weights = [1 / len(returns) for asset in returns]

    # # Optimize the portfolio using the scipy minimize function
    # result = minimize(objective_function, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

    # # Return the optimized weights
    # return {asset: weight for asset, weight in zip(returns.keys(), result.x)}

def rebalance_portfolio(weights, asset_data):
    rebalanced_portfolio = {}
    for asset in weights.keys():
        asset_prices = asset_data[asset]['prices']
        asset_weight = weights[asset]
        asset_value = asset_weight * asset_prices[-1]
        rebalanced_portfolio[asset] = {'prices': np.append(asset_prices, asset_prices[-1]), 'value': asset_value}
    return rebalanced_portfolio

#get historical prices for each asset in the portfolio

def get_historical_prices(asset):
    asset_ticker = yf.Ticker(asset)
    asset_prices = asset_ticker.history(period="3y")
    prices = asset_prices['Close'].mean()
    return prices

asset_data = {}

# Retrieve historical prices for each asset in the portfolio
for asset in portfolio_weights.keys():
    asset_prices = get_historical_prices(asset)
    # Store the historical prices for each asset in a dictionary
    asset_data[asset] = {'prices': asset_prices}


# Calculate the returns for each asset in the portfolio
for asset in portfolio_weights.keys():
    asset_prices = asset_data[asset]['prices']
    #asset_returns = calculate_returns(asset_prices)
    asset_data[asset]['returns'] = asset_prices
#print(asset_data)

# Calculate the portfolio returns
portfolio_returns = calculate_portfolio_returns(portfolio_weights, asset_data)
#print("portfolio_returns",portfolio_returns)


# Calculate the covariance matrix of the assets
cov_matrix = calculate_covariance_matrix(asset_data)
#print('cov_matrix',cov_matrix)

# Calculate the portfolio risk
portfolio_risk = calculate_portfolio_risk(portfolio_weights, cov_matrix)
#print('portfolio_risk',portfolio_risk)


# Optimize the portfolio using mean-variance optimization
optimized_weights = optimize_portfolio(portfolio_returns,cov_matrix, portfolio_risk)
#print('optimized_weights',optimized_weights)

# Update the portfolio weights with the optimized weights
for asset in portfolio_weights.keys():
    portfolio_weights[int(asset)] = optimized_weights[(asset)]

# Rebalance the portfolio based on the new weights
rebalanced_portfolio = rebalance_portfolio(portfolio_weights, asset_data)

# Update the asset data with the rebalanced portfolio
for asset in portfolio_weights.keys():
    asset_data[asset]['prices'] = rebalanced_portfolio[asset]['prices']

print(rebalanced_portfolio)


