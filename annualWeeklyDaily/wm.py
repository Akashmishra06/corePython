from backtestTools.histData import getEquityBacktestData
import numpy as np
import pandas as pd
from datetime import timedelta

def getWeeklyBacktestData(symbol, startDateTime, endDateTime, conn=None):
    """
    Fetches daily data from MongoDB and resamples it to weekly data aligned with the trading week (Monday-Friday).
    Handles weeks with no data by generating an empty candle and sets 'ti' as the index.
    The 'datetime' column reflects the start (Monday) of the weekly candle.
    
    Args:
        symbol (str): Stock symbol.
        startDateTime (datetime or int or float): Start datetime or timestamp for the data.
        endDateTime (datetime or int or float): End datetime or timestamp for the data.
        conn (MongoClient, optional): The MongoDB connection object. If None, a new connection will be created.
    
    Returns:
        pd.DataFrame: Resampled weekly data with columns: ['o', 'h', 'l', 'c', 'v', 'oi', 'datetime'] and 'ti' as index.
    """
    try:
        # Fetch daily data using the existing getEquityBacktestData function
        daily_data = getEquityBacktestData(symbol, startDateTime, endDateTime, 'D', conn)
        
        # Ensure 'datetime' column is in datetime format and set it as the index
        if 'datetime' not in daily_data.columns:
            raise KeyError("The 'daily_data' DataFrame does not have a 'datetime' column.")
        
        daily_data['datetime'] = pd.to_datetime(daily_data['datetime'])
        daily_data.set_index('datetime', inplace=True)
        
        # Filter data to include only Monday to Friday
        daily_data = daily_data[daily_data.index.dayofweek < 5]  # 0=Monday, 4=Friday
        
        # Resample daily data to weekly data (Monday-Friday candles)
        df_weekly = daily_data.resample('W-FRI').agg({
            'o': 'first',   # First open price of the week
            'h': 'max',     # Highest price of the week
            'l': 'min',     # Lowest price of the week
            'c': 'last',    # Last close price of the week
            'v': 'sum',     # Sum of volume for the week
            'oi': 'sum',    # Sum of open interest for the week
        })
        
        # Add missing weeks with empty candles
        all_weeks = pd.date_range(
            start=daily_data.index.min(), 
            end=daily_data.index.max(), 
            freq='W-FRI'
        )
        df_weekly = df_weekly.reindex(all_weeks, fill_value=np.nan)

        # Shift the 'datetime' index back to the start of the week (Monday)
        df_weekly.index = df_weekly.index - pd.Timedelta(days=4)

        # Add 'ti' as Unix timestamp and set it as the index
        df_weekly['ti'] = df_weekly.index.astype(np.int64) // 10**9
        df_weekly.reset_index(inplace=True)
        df_weekly.rename(columns={'index': 'datetime'}, inplace=True)

        # Adjust timezone (e.g., from UTC to IST)
        df_weekly['datetime'] = df_weekly['datetime'] + timedelta(hours=5, minutes=30)
        
        # Set 'ti' as the index
        df_weekly.set_index('ti', inplace=True)

        return df_weekly

    except Exception as e:
        raise Exception(f"Error in fetching weekly backtest data: {e}")