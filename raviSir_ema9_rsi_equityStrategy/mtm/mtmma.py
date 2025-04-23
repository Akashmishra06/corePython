from backtestTools.util import calculateDailyReport, limitCapital, generateReportFile, calculate_mtm
from datetime import timedelta, datetime, date, time
import pandas as pd

df = pd.read_csv("/root/equityResearch/pms/fifty/BLS50_H1LA102.csv")
fileDir = "/root/equityResearch/raviSir_ema9_rsi_equityStrategy/mtm"

dailyReport = calculate_mtm(df, fileDir, timeFrame="D", mtm=False, equityMarket=True, conn=None)