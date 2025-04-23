import pandas as pd

df = pd.read_csv("/root/equityResearch/annualWeeklyDaily/BacktestResults/NA_Buying_v1/1/closePnl_NA_Buying_v1_1.csv")

# df.rename(columns={"ExitType": "EntryTime"}, inplace=True)

df = df[["Key", "ExitTime", "Symbol"]]

df['Key'] = pd.to_datetime(df['Key']).dt.date
df['ExitTime'] = pd.to_datetime(df['ExitTime']).dt.date

print(df)

df.to_csv("range.csv", index=False)