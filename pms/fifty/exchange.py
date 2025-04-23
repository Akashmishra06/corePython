import pandas as pd

df = pd.read_csv("/root/equityResearch/pms/BacktestResults/AK_BLS50_H1LA101_v1/2/closePnl_AK_BLS50_H1LA101_v1_2.csv")
df = pd.DataFrame(df, columns=["Key", "ExitTime", "Symbol", "EntryPrice", "ExitPrice", "Quantity", "PositionStatus", "Pnl", "ExitType"])

df[['ExitTypeDesc', 'Date1', 'Date2']] = df['ExitType'].str.extract(r'(.*),\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\s*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')

df = df.drop(columns=['ExitTypeDesc',"Key", "ExitTime"])
df = df[['Date1', 'Date2', "Symbol", "EntryPrice", "ExitPrice", "Quantity", "PositionStatus", "Pnl", "ExitType"]]
df.to_csv("data.csv")