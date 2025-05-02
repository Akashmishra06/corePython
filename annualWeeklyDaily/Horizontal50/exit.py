import pandas as pd

df = pd.read_csv('/root/equityResearch/annualWeeklyDaily/Horizontal50/BacktestResults/NA_Horizontal50_v1/2/OpenPnlCsv/yRENUKA_openPnl.csv')
# ,Key,ExitTime,Symbol,EntryPrice,ExitPrice,Quantity,PositionStatus,Pnl,ExitType

df.rename(columns={'EntryTime': 'Key', 'CurrentPrice': 'ExitPrice', 'quantity':"ExitType"}, inplace=True)
df['ExitTime'] = '2025-03-25'
df['ExitType'] = "timeUp"
df['Key'] = df['EntryDate']
df = df[['Key', 'ExitTime', 'Symbol', 'EntryPrice', 'ExitPrice', 'Quantity', 'PositionStatus', 'Pnl', 'ExitType']]

print(df)
df.to_csv('exit.csv')