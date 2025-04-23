from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData, getFnoBacktestData
from backtestTools.util import createPortfolio, calculate_mtm
from backtestTools.util import setup_logger
from datetime import datetime, timedelta
from termcolor import colored, cprint
from datetime import datetime, time
import talib
import logging
import numpy as np
import multiprocessing


class Averaging(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "Averaging":
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
            df = getFnoBacktestData("FINNIFTY", startTimeEpoch-7776000, endTimeEpoch, "1Min")
        except Exception as e:
            raise Exception(e)
        print(df)

        # df.dropna(inplace=True)
        # df.index = df.index + 33300
        # df = df[df.index > startTimeEpoch]
        # df.to_csv(f"{self.fileDir['backtestResultsCandleData']}{stockName}_df.csv")

        # amountPerTrade = 100000
        # lastIndexTimeData = None

        # for timeData in df.index:
        #     stockAlgoLogic.timeData = timeData
        #     stockAlgoLogic.humanTime = datetime.fromtimestamp(timeData)

        #     if lastIndexTimeData in df.index:
        #         logger.info(f"Datetime: {stockAlgoLogic.humanTime}\tStock: {stockName}\tClose: {df.at[lastIndexTimeData,'c']}")

        #     if not stockAlgoLogic.openPnl.empty:
        #         for index, row in stockAlgoLogic.openPnl.iterrows():
        #             try:
        #                 stockAlgoLogic.openPnl.at[index, 'CurrentPrice'] = df.at[lastIndexTimeData, "c"]
        #             except Exception as e:
        #                 logging.info(e)

        #     stockAlgoLogic.pnlCalculator()

        #     # for index, row in stockAlgoLogic.openPnl.iterrows():
        #     #     if lastIndexTimeData in df.index:
        #     #         if df.at[lastIndexTimeData, "c"] <= (0.95*row["EntryPrice"]):
        #     #             exitType = "StoplossHit"
        #     #             stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

        #     if (lastIndexTimeData in df.index):
        #         entry_price = df.at[lastIndexTimeData, "c"]
        #         stockAlgoLogic.entryOrder(entry_price, stockName, 2, "BUY")

        #     lastIndexTimeData = timeData
        #     stockAlgoLogic.pnlCalculator()

        # if not stockAlgoLogic.openPnl.empty:
        #     for index, row in stockAlgoLogic.openPnl.iterrows():
        #         exitType = "Time Up"
        #         stockAlgoLogic.exitOrder(index, exitType)
        # stockAlgoLogic.pnlCalculator()


if __name__ == "__main__":
    startNow = datetime.now()

    devName = "NA"
    strategyName = "Averaging"
    version = "v1"

    startDate = datetime(2022, 1, 1, 9, 15)
    endDate = datetime(2024, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/equityResearch/stocksList/test1.md", 1)

    algoLogicObj = Averaging(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    dailyReport = calculate_mtm(closedPnl, fileDir, timeFrame="d", mtm=False, equityMarket=True)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")