from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_stock_data(stock_data):
    if not stock_data:
        return {}
    
    ticker, data = next(iter(stock_data.items()))
    if not data:
        return {}
    
    latest = data[-1]
    oldest = data[0]
    return {
        "ticker": ticker,
        "start_date": oldest["Date"],
        "end_date": latest["Date"],
        "start_price": oldest["Close"],
        "end_price": latest["Close"],
        "percent_change": (latest["Close"] - oldest["Close"]) / oldest["Close"] * 100,
        "latest_ma9": latest["MA9"],
        "latest_ma20": latest["MA20"]
    }

def get_response(prompt):
    try:
        with open('stock_history.json', 'r') as f:
            stock_data = json.load(f)
        
        summarized_data = summarize_stock_data(stock_data)
        full_prompt = f"{prompt}\n\nSummarized Stock Data: {json.dumps(summarized_data)}"

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """
                        You are CapyTrader, a cool and relaxed Capybara that analyzes stock data for the user.
                        Your job is to determine whether the trend is up or down and provide your prediction for the next few days.
                        You speak with a chill tone, and you always remind the user that what you offer is not financial advice.
                        You also use emojis in your response.
                        Conclude every response with: 'And of course, this analysis is just for fun and I don't offer any financial advice!'
                    """
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            max_tokens=500,
            temperature=0.8,
            presence_penalty=0.0,
            frequency_penalty=0.5,
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"