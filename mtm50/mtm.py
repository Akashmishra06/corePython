import pandas as pd
from backtestTools.util import calculate_mtm

df = pd.read_csv("/root/equityResearch/pms/fifty/BLS50_H1LA101.csv")

fileDir = "/root/equityResearch/mtm50"
calculate_mtm(df, fileDir, timeFrame="1d", mtm=False, equityMarket=True)