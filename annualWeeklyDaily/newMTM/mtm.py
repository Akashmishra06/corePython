from backtestTools.util import calculateDailyReport, limitCapital, generateReportFile, calculate_mtm
from datetime import timedelta, datetime, date, time
import pandas as pd

df = pd.read_csv("/root/akashEquityBacktestAlgos/annualWeeklyDaily/Horizontal50/BacktestResults/NA_Horizontal50_v1/1/ClosePnlCsv/yRENUKA_closedPnl.csv")
fileDir = "/root/akashEquityBacktestAlgos/annualWeeklyDaily/newMTM"
dailyReport = calculate_mtm(df, fileDir, timeFrame="D", mtm=False, equityMarket=True, conn=None)