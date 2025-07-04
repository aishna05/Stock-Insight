import os
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, r2_score
from math import sqrt
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLOT_DIR = os.getenv("PLOT_DIR", os.path.join(BASE_DIR, "plots"))
MODEL_PATH = os.getenv("MODEL_PATH", "stock_prediction_model.keras")

if not os.path.exists(PLOT_DIR):
    os.makedirs(PLOT_DIR)

# Load model once (lazy load)
_model = None
def load_trained_model():
    global _model
    if _model is None:
        try:
            _model = load_model(MODEL_PATH)
        except Exception as e:
            raise RuntimeError(f"Error loading model: {e}")
    return _model

def generate_prediction(ticker: str):
    try:
        df = yf.download(ticker, period="10y")
        if df.empty:
            raise ValueError("No data found for ticker")

        data = df[['Close']].values
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data)

        X, y = [], []
        window = 60
        for i in range(window, len(data_scaled)):
            X.append(data_scaled[i - window:i])
            y.append(data_scaled[i])

        X, y = np.array(X), np.array(y)

        model = load_trained_model()
        predictions = model.predict(X)

        # Metrics
        mse = mean_squared_error(y, predictions)
        rmse = sqrt(mse)
        r2 = r2_score(y, predictions)

        # Inverse transform
        last_60 = data_scaled[-60:]
        last_60 = np.expand_dims(last_60, axis=0)
        next_day_scaled = model.predict(last_60)
        next_day_price = scaler.inverse_transform(next_day_scaled)[0][0]

        # Inverse for plots
        y_true = scaler.inverse_transform(y)
        y_pred = scaler.inverse_transform(predictions)

        # Plot 1: closing price history
        plot1_path = os.path.join(PLOT_DIR, f"{ticker}_history.png")
        df['Close'].plot(title=f"{ticker} - Price History")
        plt.savefig(plot1_path)
        plt.close()

        # Plot 2: actual vs predicted
        plot2_path = os.path.join(PLOT_DIR, f"{ticker}_prediction.png")
        plt.plot(y_true, label="Actual")
        plt.plot(y_pred, label="Predicted")
        plt.title(f"{ticker} - Actual vs Predicted")
        plt.legend()
        plt.savefig(plot2_path)
        plt.close()

        return {
            "ticker": ticker,
            "next_day_price": round(next_day_price, 2),
            "metrics": {
                "mse": round(mse, 4),
                "rmse": round(rmse, 4),
                "r2": round(r2, 4),
            },
            "plot_urls": [f"/media/{os.path.basename(plot1_path)}", f"/media/{os.path.basename(plot2_path)}"],
            "plot_paths": [plot1_path, plot2_path]
        }

    except Exception as e:
        raise RuntimeError(f"Prediction failed: {str(e)}")
