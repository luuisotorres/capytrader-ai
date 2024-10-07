from flask import Flask, render_template, request
from PIL import Image
from gpt_utils import get_response
from fetch_stock_data import fetch_stock_history
import logging
import json
import os

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def analyze_stock(stock_symbol):
    if stock_symbol:
        logging.info(f"Analyzing stock: {stock_symbol}")
        stock_data = fetch_stock_history(stock_symbol)
        
        # Check if there is content in stock_history.json
        if os.path.exists('stock_history.json'):
            with open('stock_history.json', 'r') as f:
                stock_data = json.load(f)
            if stock_data:
                logging.info("stock_history.json found and loaded")
                logging.debug(f"Stock data: {stock_data}")
            else:
                logging.warning("stock_history.json is empty")
        else:
            logging.warning("stock_history.json not found")
        
        prompt = f"Analyze the last financial data and provide a brief analysis and trading advice for the following stock: {stock_symbol}"
        ai_response = get_response(prompt)
        return ai_response
    return "Please enter a valid stock symbol."

@app.route('/', methods=['GET', 'POST'])
def home():
    ai_response = ""
    if request.method == 'POST':
        stock_symbol = request.form.get('stock_symbol')
        ai_response = analyze_stock(stock_symbol)
        if ai_response.startswith("An error occurred"):
            print(f"Error: {ai_response}") 
            ai_response = "Sorry, I couldn't analyze the stock right now. Please try again later!"

    return render_template('index.html', ai_response=ai_response)

if __name__ == '__main__':
    if not os.path.exists('static/capytrader.jpg'):
        image = Image.open("capytrader.jpg")
        image.save('static/capytrader.jpg')
    
    app.run(debug=True)