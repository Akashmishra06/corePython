from backtestTools.util import createPortfolio, calculateDailyReport, limitCapital, generateReportFile
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData
from backtestTools.histData import getEquityHistData
from backtestTools.util import setup_logger
from datetime import datetime, timedelta
from datetime import datetime, time
import talib
import pandas_ta as ta
import logging
import numpy as np
import multiprocessing
from termcolor import colored, cprint
import pandas as pd


class SupertrendStrategy(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "SupertrendStrategy":
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
            df = getEquityBacktestData(stockName, startTimeEpoch-7776000, endTimeEpoch, "1H")
        except Exception as e:
            raise Exception(e)

        if df is not None:
            df.dropna(inplace=True)
            # df.index = df.index + 33300

            df['body_size'] = abs(df['c'] - df['o'])
            df['candle_range'] = df['h'] - df['l']
            df['body_percentage'] = (df['body_size'] / df['candle_range']) * 100

            df['close_to_high'] = (df['h'] - df['c']) / (df['h'] - df['l'])
            df['close_to_low'] = (df['c'] - df['l']) / (df['h'] - df['l'])

            df['Strength'] = np.where((df['body_percentage'] > 60) & (df['close_to_high'] < 0.2), 'BuyerStrong',
                np.where((df['body_percentage'] > 60) & (df['close_to_low'] < 0.2), 'SellerStrong','Neutral'))

            df.drop(['body_size', 'candle_range', 'body_percentage', 'close_to_high', 'close_to_low'], axis=1, inplace=True)

            df["rsi"] = talib.RSI(df["c"], timeperiod=14)
            df['prev_rsi'] = df['rsi'].shift(1)

            supertrend = ta.supertrend(df["h"], df["l"], df["c"], 3, 10)
            df['supertrendColour'] = supertrend['SUPERTd_3_10.0']
            # df['longEntry'] = np.where((df['supertrendColour'] == 1) & (df['supertrendColour'].shift(1) == -1), "longEntry", "")

            # df['longExit'] = np.where((df['supertrendColour'] == -1) & (df['supertrendColour'].shift(1) == 1), "longExit", "")
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

                        if stockAlgoLogic.humanTime.time() >= time(15, 15) and ((df.at[lastIndexTimeData, "c"] > row['EntryPrice']*1.1) or (df.at[lastIndexTimeData, "c"] < row['EntryPrice']*0.99)):
                            exitType = "Time Up"
                            stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

                        # if df.at[lastIndexTimeData, "l"] <= (0.99*row["EntryPrice"]):
                        #     exitType = "Stoploss Hit"
                        #     stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

                        # elif df.at[lastIndexTimeData, "longExit"] == "longExit":
                        #     exitType = "longExit"
                        #     stockAlgoLogic.exitOrder(index, exitType, (df.at[lastIndexTimeData, "c"]))

                if (lastIndexTimeData in df.index) & (stockAlgoLogic.openPnl.empty):

                    # if (df.at[lastIndexTimeData, "Strength"] == "BuyerStrong") and (df.at[lastIndexTimeData, "supertrendColour"] == 1) and (df.at[lastIndexTimeData, "rsi"] < 50):
                    #     entry_price = df.at[lastIndexTimeData, "c"]
                    #     stockAlgoLogic.entryOrder(entry_price, stockName,(amountPerTrade//entry_price), "BUY")

                    if (df.at[lastIndexTimeData, "Strength"] == "SellerStrong"):
                        entry_price = df.at[lastIndexTimeData, "c"]
                        stockAlgoLogic.entryOrder(entry_price, stockName,(amountPerTrade//entry_price), "BUY")

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
    strategyName = "SupertrendStrategy"
    version = "v1"

    startDate = datetime(2021, 1, 1, 9, 15)
    endDate = datetime(2025, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/equityResearch/stocksList/nifty50.md", 5)

    algoLogicObj = SupertrendStrategy(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")