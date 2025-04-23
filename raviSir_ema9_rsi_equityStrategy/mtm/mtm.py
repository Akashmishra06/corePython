import pandas as pd
from backtestTools.util import calculate_mtm

df = pd.read_csv("/root/equityResearch/pms/fifty/BLS50_H1LA102.csv")

fileDir = "/root/equityResearch/raviSir_ema9_rsi_equityStrategy/mtm"
calculate_mtm(df, fileDir, timeFrame="1d", mtm=False, equityMarket=True)