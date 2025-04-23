from backtestTools.util import createPortfolio, calculateDailyReport, limitCapital, generateReportFile, calculate_mtm
from backtestTools.histData import getEquityBacktestData, getEquityHistData
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.util import setup_logger
from datetime import datetime, timedelta
from termcolor import colored, cprint
from datetime import datetime, time
import talib as ta
import logging
import numpy as np
import multiprocessing


class RiskRewardStrategy(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "RiskRewardStrategy":
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
            df = getEquityBacktestData(stockName, startTimeEpoch-(86400 * 500), endTimeEpoch, "d")
            df.dropna(inplace=True)
            df.index = df.index + 33300
            df = df[df.index > startTimeEpoch]
            df.to_csv(f"{self.fileDir['backtestResultsCandleData']}{stockName}_df.csv")
            df['MA50'] = ta.SMA(df['c'], timeperiod=50)
            df['MA200'] = ta.SMA(df['c'], timeperiod=200)
            df['RSI'] = ta.RSI(df['c'], timeperiod=14)
            df['MACD'], df['MACD_signal'], df['MACD_hist'] = ta.MACD(df['c'], fastperiod=12, slowperiod=26, signalperiod=9)
            df['Entry_Signal'] = np.where((df['MA50'] > df['MA200']) & (df['RSI'] < 70) & (df['MACD'] > df['MACD_signal']), 'Buy', "")
            df['Exit_Signal'] = np.where((df['MA50'] < df['MA200']) & (df['RSI'] > 70) & (df['MACD'] < df['MACD_signal']), 'Sell', "")
        except Exception as e:
            raise Exception(e)

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

                    # if df.at[lastIndexTimeData, "Exit_Signal"] == "Exit_Signal":
                    #     exitType = "stoplossHit"
                    #     stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

                    if (df.at[lastIndexTimeData, "c"] < (0.80*row["EntryPrice"])):
                        exitType = "StoplossExit"
                        stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

            if (lastIndexTimeData in df.index) & (stockAlgoLogic.openPnl.empty):
                # if (df.at[lastIndexTimeData, "Entry_Signal"] == "Entry_Signal"):
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
    strategyName = "RiskRewardStrategy"
    version = "v1"

    startDate = datetime(2019, 1, 1, 9, 15)
    endDate = datetime(2024, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/equityResearch/equityModel/stockList/nifty50.md",5)

    algoLogicObj = RiskRewardStrategy(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")