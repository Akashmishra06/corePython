import pandas as pd
from backtestTools.util import calculate_mtm

df = pd.read_csv("/root/equityResearch/raviSirResearch/horizontallyCompounding/BacktestResults/AK_R_60_60_30_v1/1/closePnl_AK_R_60_60_30_v1_1.csv")

fileDir = "/root/equityResearch/raviSirResearch/horizontallyCompounding/mtm"
calculate_mtm(df, fileDir, timeFrame="1d", mtm=False, equityMarket=True)