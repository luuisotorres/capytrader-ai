import yfinance as yf
import json
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class StockDataFetcher:
    def __init__(self, ticker):
        self.ticker = ticker
        self.data = {}

    def round_data(self, value, decimals=2):
        return round(value, decimals) if isinstance(value, (int, float)) else value

    def fetch_data(self):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=50)  # Last 50 days

        try:
            logging.info(f"Fetching data for {self.ticker}")
            stock = yf.Ticker(self.ticker)
            history = stock.history(start=start_date, end=end_date)

            if history.empty:
                logging.warning(f"No data found for '{self.ticker}'")
                return

            stock_data = []
            for date, row in history.iterrows():
                stock_data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Close': self.round_data(row['Close']),
                    'Volume': int(row['Volume'])
                })

            for i in range(len(stock_data)):
                if i == 0:
                    stock_data[i]['PercentChange'] = None
                else:
                    percent_change = (stock_data[i]['Close'] - stock_data[i-1]['Close']) / stock_data[i-1]['Close'] * 100
                    stock_data[i]['PercentChange'] = self.round_data(percent_change)

                mas9 = sum(d['Close'] for d in stock_data[max(0, i-8):i+1]) / min(9, i+1)
                mas20 = sum(d['Close'] for d in stock_data[max(0, i-19):i+1]) / min(20, i+1)
                stock_data[i]['MA9'] = self.round_data(mas9)
                stock_data[i]['MA20'] = self.round_data(mas20)

            self.data[self.ticker] = stock_data
            logging.info(f"Successfully fetched data for {self.ticker}")

        except Exception as e:
            logging.error(f"Error fetching data for '{self.ticker}': {e}")

    def get_stock_history(self):
        return self.data

    def save_to_json(self, filename='stock_history.json'):
        with open(filename, 'w') as f:
            json.dump(self.data, f, indent=4)
        logging.info(f"Saved data to {filename}")
        return filename

def fetch_stock_history(ticker):
    fetcher = StockDataFetcher(ticker)
    fetcher.fetch_data()
    filename = fetcher.save_to_json()
    with open(filename, 'r') as f:
        data = json.load(f)
    logging.info(f"Loaded data from {filename}: {data}")
    return data

if __name__ == "__main__":
    stock = "AAPL"
    stock_history = fetch_stock_history(stock)
    print(json.dumps(stock_history, indent=2))