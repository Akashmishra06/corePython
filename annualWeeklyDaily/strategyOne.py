from backtestTools.util import createPortfolio, calculateDailyReport, limitCapital, generateReportFile
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityHistData
# from backtestTools.histData import getWeeklyBacktestData
from termcolor import colored, cprint
from backtestTools.util import setup_logger
from datetime import datetime, time, timedelta
from datetime import datetime, timedelta
import talib
import pandas_ta as ta
import logging
import numpy as np
import pandas as pd
from wm import getWeeklyBacktestData
import multiprocessing


class Buying(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "Buying":
            raise Exception("Strategy Name Mismatch")
        total_backtests = sum(len(batch) for batch in portfolio)
        completed_backtests = 0
        cprint(f"Backtesting: {self.strategyName} UID: {self.fileDirUid}", "green")
        print(colored("Backtesting 0% complete.", "light_yellow"), end="\r")
        for batch in portfolio:
            processes = []
            for stock in batch:
                p = multiprocessing.Process(target=self.backtest, args=(stock, startDate, endDate))
                p.start()
                processes.append(p)
            for p in processes:
                p.join()
                completed_backtests += 1
                percent_done = (completed_backtests / total_backtests) * 100
                print(colored(f"Backtesting {percent_done:.2f}% complete.", "light_yellow"), end=("\r" if percent_done != 100 else "\n"))
        return self.fileDir["backtestResultsStrategyUid"], self.combinePnlCsv()

    def backtest(self, stockName, startDate, endDate):

        startTimeEpoch = startDate.timestamp()
        endTimeEpoch = endDate.timestamp()

        stockAlgoLogic = equityOverNightAlgoLogic(stockName, self.fileDir)

        logger = setup_logger(stockName, f"{self.fileDir['backtestResultsStrategyLogs']}/{stockName}.log",)
        logger.propagate = False

        try:
            df = getWeeklyBacktestData(stockName, startTimeEpoch-(86400*500), endTimeEpoch)
            print(df)
        except Exception as e:
            raise Exception(e)

        if df is not None:
            df.dropna(inplace=True)

            df["rsi"] = talib.RSI(df["c"], timeperiod=14)
            df['datetime1'] = df['datetime'].shift(-1)

            df = df[df.index > startTimeEpoch]
            df.to_csv(f"{self.fileDir['backtestResultsCandleData']}{stockName}_df.csv")

            amountPerTrade = 100000
            lastIndexTimeData = None

            for timeData in df.index:
                stockAlgoLogic.timeData = timeData
                stockAlgoLogic.humanTime = datetime.fromtimestamp(timeData)

                if lastIndexTimeData in df.index:
                    logger.info(f"Datetime: {stockAlgoLogic.humanTime}\tStock: {stockName}\tClose: {df.at[lastIndexTimeData,'c']}")

                if not stockAlgoLogic.openPnl.empty:
                    for index, row in stockAlgoLogic.openPnl.iterrows():
                        try:
                            stockAlgoLogic.openPnl.at[index, 'CurrentPrice'] = df.at[lastIndexTimeData, "c"]
                        except Exception as e:
                            logging.info(e)
                stockAlgoLogic.pnlCalculator()

                for index, row in stockAlgoLogic.openPnl.iterrows():
                    if lastIndexTimeData in df.index:
                        if row['PositionStatus'] == 1:
                            if df.at[lastIndexTimeData, "rsi"] < 30:
                                exitType = f"{row['datetime1']}"
                                stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

                if (lastIndexTimeData in df.index) & (stockAlgoLogic.openPnl.empty):
                    if df.at[lastIndexTimeData, "rsi"] > 60:
                        entry_price = df.at[lastIndexTimeData, "c"]
                        stockAlgoLogic.entryOrder(entry_price, stockName, (amountPerTrade//entry_price), "BUY", {"datetime1":df.at[lastIndexTimeData, "datetime1"]})

                lastIndexTimeData = timeData
                stockAlgoLogic.pnlCalculator()

            if not stockAlgoLogic.openPnl.empty:
                for index, row in stockAlgoLogic.openPnl.iterrows():
                    exitType = f"{row['datetime1']}"
                    stockAlgoLogic.exitOrder(index, exitType)
            stockAlgoLogic.pnlCalculator()


if __name__ == "__main__":
    startNow = datetime.now()

    devName = "NA"
    strategyName = "Buying"
    version = "v1"

    startDate = datetime(2019, 1, 1, 9, 15)
    endDate = datetime(2025, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/akashEquityBacktestAlgos/stocksList/nifty500 copy.md",20)

    algoLogicObj = Buying(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    dailyReport = calculateDailyReport(closedPnl, fileDir, timeFrame=timedelta(days=1), mtm=True, fno=False)
    
    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")