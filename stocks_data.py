# External imports
from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from yahoo_fin import stock_info as si

# Initlize flask application
app = Flask(__name__)
cors = CORS(app)

@app.route('/stocks')
@cross_origin()
def stocks():
    """
    Calculate values for the Annualized Returns, Annualized Volatility, Cumulative Return, and Performance for each
    stock for the last year. For the caluclation of the Annualized Volatility the data for the last two year is taken.

    :return: JSON structure with the next keys and values: start_price, end_price, performance, cumulative_return, 
        annualized_return, annualized_volatility, dates
    """
    # Define the stocks and start date for the last year
    stocks = ['AAPL', 'MSFT', 'TSLA']
    start_date = datetime.now() - timedelta(days=365*2)

    # Get the historical prices for each stock
    prices = {}
    for stock in stocks:
        prices[stock] = si.get_data(stock, start_date=start_date)['adjclose']

    # Calculate the cumulative returns, annualized returns, and annualized volatility for each stock
    results = {}
    for stock in stocks:
        # Take the data for the last two years for calculation of volatility
        data_volatility = prices[stock][-504:]
        data = prices[stock][-252:]
        dates = prices[stock].index[-252:]
        start_price = data[-252]
        end_price = data[-1]

        # Calculate the values for the stock performance
        returns = (end_price - start_price) / start_price
        annualized_returns = ((1 + returns) ** (1/5)) - 1
        annualized_volatility = data_volatility.pct_change().rolling(window=252).std().iloc[-1] * (252 ** 0.5) # Assumes 252 trading days in a year
        cumulative_return = (data / start_price) * 100
        annual_performance = cumulative_return.pct_change(periods=252).fillna(0) + 1
        annual_performance.iloc[0] = 100 # Set first row to 1 for all stocks
        results[stock] = {
            'start_price': start_price,
            'end_price': end_price,
            'performance': cumulative_return.tolist()[-252:],
            'cumulative_return': round((end_price / start_price) * 100, 2),
            'annualized_return': round((annualized_returns * 100), 2),
            'annualized_volatility': round((annualized_volatility * 100), 2),
            'dates': dates.strftime('%d.%m.%Y').tolist(),
        }

    # Return the json structure with stock performance data
    return jsonify(results)


if __name__ == '__main__':

    app.run(debug=True)