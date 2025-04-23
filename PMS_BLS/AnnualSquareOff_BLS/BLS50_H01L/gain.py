import pandas as pd
from datetime import datetime

df = pd.read_csv("/root/equityResearch/PMS_BLS/AnnualSquareOff_BLS/BLS50_H01L/BacktestResults/AK_BLS50_H30K_Annual_SquareOff_v1/1/closePnl_AK_BLS50_H30K_Annual_SquareOff_v1_1.csv", parse_dates=["Key", "ExitTime"])

def categorize_trade(row):
    trade_duration = (row['ExitTime'] - row['Key']).days

    if row['Pnl'] < 0:
        if trade_duration > 365:
            return "longtermlossmaking"
        else:
            return "shorttermlossmaking"
    else:
        if trade_duration > 365:
            return "longtermprofitmaking"
        else:
            return "shorttermprofitmaking"

df['Gain'] = df.apply(categorize_trade, axis=1)
df.to_csv("dfto_.csv")