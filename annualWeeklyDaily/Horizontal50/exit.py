import pandas as pd

df = pd.read_csv('/root/AkashMockAlgo/weekly_500_stocks/Horizontal50/BacktestResults/NA_Horizontal50_v1/6/OpenPnlCsv/COALINDIA_openPnl.csv')
# ,Key,ExitTime,Symbol,EntryPrice,ExitPrice,Quantity,PositionStatus,Pnl,ExitType

df.rename(columns={'EntryTime': 'Key', 'CurrentPrice': 'ExitPrice', 'quantity':"ExitType"}, inplace=True)
df['ExitTime'] = '2024-12-12'
df['ExitType'] = "timeUp"
df = df[['Key', 'ExitTime', 'Symbol', 'EntryPrice', 'ExitPrice', 'Quantity', 'PositionStatus', 'Pnl', 'ExitType']]

print(df)
df.to_csv('exit.csv')