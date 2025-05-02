from backtestTools.util import createPortfolio, calculateDailyReport, limitCapital, generateReportFile
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData
from backtestTools.histData import getEquityHistData
from backtestTools.util import setup_logger
from datetime import datetime, timedelta
from termcolor import colored, cprint
from datetime import datetime, time
import multiprocessing
import numpy as np
import logging
import talib
import pandas_ta as ta
import pandas as pd

class equityDelta(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "equityDelta":
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
            df = getEquityBacktestData(stockName, startTimeEpoch-(86400*500), endTimeEpoch, "45Min")
        except Exception as e:
            print(stockName)
            raise Exception(e)
        print(df)

        upper_band, middle_band, lower_band = talib.BBANDS(df['c'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        df['BollingerUpper'] = upper_band
        df['BollingerLower'] = lower_band

        period = 20
        multiplier = 2

        middle_line = talib.EMA(df['c'], timeperiod=period)
        atr = talib.ATR(df['h'], df['l'], df['c'], timeperiod=period)

        upper_line = middle_line + (multiplier * atr)
        lower_line = middle_line - (multiplier * atr)

        df['MiddleRange'] = middle_line
        df['KeltnerChannelUpper'] = upper_line
        df['KeltnerChannelLower'] = lower_line

        df.dropna(inplace=True)

        supertrend_one = ta.supertrend(df["h"], df["l"], df["c"], length=100, multiplier=3.6)
        print(supertrend_one)
        supertrend_two = ta.supertrend(df["h"], df["l"], df["c"], length=100, multiplier=1.8)

        df['SupertrendColourOne'] = supertrend_one['SUPERTd_100_3.6']
        df['SupertrendColourTwo'] = supertrend_two['SUPERTd_100_1.8']

        df['EntryLong'] = np.where(
            (df['BollingerUpper'] > df['KeltnerChannelUpper']) &
            (df['KeltnerChannelLower'] > df['BollingerLower']) &
            (df['SupertrendColourOne'] == 1) &
            (df['SupertrendColourTwo'] == 1),
            "EntryLong", ""
        )

        df['ExitLong'] = np.where(df['SupertrendColourOne'] == -1, "ExitLong", "")

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

                    if df.at[lastIndexTimeData, "ExitLong"] == "ExitLong":
                        exitType = "ExitUsingSupertrend"
                        stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

            if (lastIndexTimeData in df.index) & (stockAlgoLogic.openPnl.empty) & (stockAlgoLogic.humanTime.time() < time(15, 15)):

                if (df.at[lastIndexTimeData, "EntryLong"] == "EntryLong"):
                    entry_price = df.at[lastIndexTimeData, "c"]
                    stockAlgoLogic.entryOrder(entry_price, stockName, (amountPerTrade//entry_price), "BUY")

            lastIndexTimeData = timeData
            stockAlgoLogic.pnlCalculator()

        if not stockAlgoLogic.openPnl.empty:
            for index, row in stockAlgoLogic.openPnl.iterrows():
                exitType = "Time Up"
                stockAlgoLogic.exitOrder(index, exitType)
        stockAlgoLogic.pnlCalculator()

if __name__ == "__main__":
    startNow = datetime.now()

    devName = "NA"
    strategyName = "equityDelta"
    version = "v1"

    startDate = datetime(2021, 1, 1, 9, 15)
    endDate = datetime(2025, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/equityResearch/stocksList/nifty50.md", 1)

    algoLogicObj = equityDelta(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")