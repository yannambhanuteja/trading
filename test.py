from flask import Flask, render_template_string
import ccxt
from ccxt import ExchangeError, BadSymbol

app = Flask(__name__)

@app.route('/')
def home():
    # Connect to Binance
    exchange = ccxt.binance({
        'enableRateLimit': True,  # required by the Binance API
        'options': {
            'defaultType': 'future',
        }
    })

    # Get all symbols
    markets = exchange.load_markets()
    symbols = [symbol for symbol in markets.keys() if '/USDT' in symbol]  # Filter out non-USDT pairs

    messages = []

    # For each symbol
    for symbol in symbols:
        try:
            ticker = exchange.fetch_ticker(symbol)
            last_price = ticker['last']
            low_price = ticker['low']
            high_price = ticker['high']

            if last_price is not None and low_price is not None and high_price is not None:
                # Compute the percentage distance from the low and high
                low_diff = (last_price - low_price) / low_price
                high_diff = (high_price - last_price) / last_price

                # If within 0.2% - 0.5% of the low or high, add a message
                if 0.002 <= low_diff <= 0.005:
                    messages.append(f'{symbol} is within 0.2% - 0.5% of its 24-hour low')
                if 0.002 <= high_diff <= 0.005:
                    messages.append(f'{symbol} is within 0.2% - 0.5% of its 24-hour high')
            else:
                continue
        except BadSymbol:
            continue
        except ExchangeError:
            continue

    return render_template_string('<br>'.join(messages))

if __name__ == "__main__":
    app.run(debug=True)
