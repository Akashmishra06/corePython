import pandas as pd
from backtestTools.util import calculate_mtm

df = pd.read_csv("/root/equityResearch/niftyFifty/BacktestResults/NA_NiftyBacktest_v1/1/closePnl_NA_NiftyBacktest_v1_1.csv")

fileDir = "/root/equityResearch/niftyFifty/mtm"
calculate_mtm(df, fileDir, timeFrame="1d", mtm=False, equityMarket=True)