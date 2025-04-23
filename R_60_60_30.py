from backtestTools.util import createPortfolio, calculateDailyReport, limitCapital, generateReportFile, calculate_mtm
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData
from datetime import datetime, timedelta
import talib
import logging
import numpy as np
import multiprocessing
from termcolor import colored, cprint
from datetime import datetime, time
from backtestTools.util import setup_logger

class R_60_60_30(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "R_60_60_30":
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
            df = getEquityBacktestData(stockName, startTimeEpoch-(84400*1000), endTimeEpoch, "1H")
        except Exception as e:
            raise Exception(e)

        df.dropna(inplace=True)
        # df.index = df.index + 33300
        df["ema9"] = talib.EMA(df["c"], timeperiod=9)
        df['prev_ema'] = df['ema9'].shift(1)
        df["rsi"] = talib.RSI(df["c"], timeperiod=14)
        df["prev_rsi"] = df['rsi'].shift(1)

        df['stochasticRsi'] = talib.STOCHRSI(df["c"], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)[0]

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

                    if (df.at[lastIndexTimeData, "rsi"] < 60) and (row['EntryPrice'] < df.at[lastIndexTimeData, "c"]) and (df.at[lastIndexTimeData, "ema9"] < df.at[lastIndexTimeData, "prev_ema"]):
                        exitType = "RSIExitSignal"
                        stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

                    elif (df.at[lastIndexTimeData, "rsi"] < 30):
                        exitType = "TargetStoploss"
                        stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

            if (lastIndexTimeData in df.index) & (stockAlgoLogic.openPnl.empty):

                if (df.at[lastIndexTimeData, "rsi"] > 60) and (df.at[lastIndexTimeData, "prev_rsi"] < 60) and (df.at[lastIndexTimeData, "ema9"] > df.at[lastIndexTimeData, "prev_ema"]):
                    entry_price = df.at[lastIndexTimeData, "c"]
                    stockAlgoLogic.entryOrder(entry_price, stockName, (amountPerTrade//entry_price), "BUY")

            lastIndexTimeData = timeData
            stockAlgoLogic.pnlCalculator()

        if not stockAlgoLogic.openPnl.empty:
            for index, row in stockAlgoLogic.openPnl.iterrows():
                exitType = "Time Up"
                stockAlgoLogic.exitOrder(index, exitType, (df.at[lastIndexTimeData, "c"]))
        stockAlgoLogic.pnlCalculator()


if __name__ == "__main__":
    startNow = datetime.now()

    devName = "NA"
    strategyName = "R_60_60_30"
    version = "v1"

    startDate = datetime(2019, 1, 1, 9, 15)
    endDate = datetime(2024, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/akashEquityBacktestAlgos/stocksList/nifty500 copy.md",1)

    algoLogicObj = R_60_60_30(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    dailyReport = calculate_mtm(closedPnl, fileDir, timeFrame="15T", mtm=True, equityMarket=True)

    limitCapital(closedPnl, fileDir, maxCapitalAmount=100000)

    generateReportFile(dailyReport, fileDir)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")