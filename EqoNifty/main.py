from backtestTools.util import createPortfolio
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getFnoBacktestData
from backtestTools.util import setup_logger
from datetime import datetime, timedelta
from termcolor import colored, cprint
from datetime import datetime, time
import multiprocessing
import numpy as np
import logging
import talib


class EqoNifty(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "EqoNifty":
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
            df = getFnoBacktestData(stockName, startTimeEpoch, endTimeEpoch, "1Min")

            if df is None:
                return

            if not all(col in df.columns for col in ['h', 'l', 'c']):
                raise ValueError("Required columns 'h', 'l', 'c' not found in DataFrame")

            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
                df['c'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

            typical_price = (df['h'] + df['l'] + df['c']) / 3
            ema_typical = talib.EMA(typical_price, timeperiod=20)
            atr = talib.ATR(df['h'], df['l'], df['c'], timeperiod=20)

            df['kc_middle'] = ema_typical
            df['kc_upper'] = ema_typical + 2 * atr
            df['kc_lower'] = ema_typical - 2 * atr

            df['Ema10'] = talib.EMA(df['c'], timeperiod=10)

            df['EntryConditions'] = np.where((df['kc_upper'] < df['bb_upper']) & (df['bb_lower'] < df['kc_lower']) & (df['c'] > df['Ema10']), "EntryConditions", "")
            df['ExitConditonOne'] = np.where((df['kc_upper'] > df['bb_upper']), "ExitConditonOne", "")
            df['ExitConditonTwo'] = np.where((df['kc_lower'] < df['bb_lower']), "ExitConditonTwo", "")

        except Exception as e:
            self.strategyLogger.info(f"Data not found for Nifty50 in range {startDate} to {endDate}")
            raise Exception(e)

        df = df[df.index > startTimeEpoch]
        df.to_csv(f"{self.fileDir['backtestResultsCandleData']}{stockName}_df.csv")

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

                    if stockAlgoLogic.humanTime.time() >= time(15,20):
                        exitType = "IntradayExit"
                        stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

                    elif (df.at[lastIndexTimeData, "ExitConditonOne"] == "ExitConditonOne"):
                        exitType = "ExitConditonOne"
                        stockAlgoLogic.exitOrder(index, exitType, df.at[lastIndexTimeData, "c"])

                    elif (df.at[lastIndexTimeData, "ExitConditonTwo"] == "ExitConditonTwo"):
                        exitType = "ExitConditonTwo"
                        stockAlgoLogic.exitOrder(index, exitType,df.at[lastIndexTimeData, "c"])

            if (lastIndexTimeData in df.index) & (stockAlgoLogic.openPnl.empty) & (stockAlgoLogic.humanTime.time() < time(15,20)):

                if (df.at[lastIndexTimeData, "EntryConditions"] == "EntryConditions"):
                    entry_price = df.at[lastIndexTimeData, "c"]
                    stockAlgoLogic.entryOrder(entry_price, stockName, 75, "BUY")

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
    strategyName = "EqoNifty"
    version = "v1"

    startDate = datetime(2021, 1, 1, 9, 15)
    endDate = datetime(2025, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/equityResearch/EqoNifty/stocksNames.md", 1)

    algoLogicObj = EqoNifty(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)
    
    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")