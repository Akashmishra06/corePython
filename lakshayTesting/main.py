from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData
from termcolor import colored, cprint
from datetime import datetime
import multiprocessing
import numpy as np
import logging
import talib
from backtestTools.util import createPortfolio

# EmaStoch
# Trading Notes
## Example
# ## Entry Condition
# The entry condition for a buy trade is defined as follows:
# ```python
# buy_condition = ((df["ema15"] > df["ema110"]) &
#                  (df['c'] > df["ema15"]) &
#                  (df["c"] > df["o"]) &
#                  (df['StochRSI_K_Smoothed'] > 20) &
#                  (df['StochRSI_K_Smoothed'].rolling(window=10).min() < 20))
# ```
# - **Explanation:**
#   - **EMA15 > EMA110:** The 15-period Exponential Moving Average (EMA) is greater than the 110-period EMA.
#   - **C > EMA15:** The closing price (c) is greater than the 15-period EMA.
#   - **C > O:** The closing price (c) is greater than the opening price (o).
#   - **StochRSI_K_Smoothed > 20:** The smoothed Stochastic RSI (K) is greater than 20.
#   - **StochRSI_K_Smoothed Rolling Min < 20:** The minimum value of the smoothed Stochastic RSI (K) over the last 10 periods is less than 20.
# and rentry  come from above 80
# ### Exit Condition
# The exit condition for a buy trade is defined as follows:
# ```python
# df['buyExitCondition'] = np.where((df['c'] < df['ema110']) & (df['c'] < df['o']), "buyExitCondition", 0)
# ```
# - **Explanation:**
#   - **C < EMA110:** The closing price (c) is less than the 110-period EMA.
#   - **C < O:** The closing price (c) is less than the opening price (o).

class EmaStochasticCrossover(baseAlgoLogic):

    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "EmaStochasticCrossover":
            raise Exception("Strategy Name Mismatch")
        total_backtests = sum(len(batch) for batch in portfolio)
        completed_backtests = 0
        cprint(f"Backtesting: {self.strategyName}_{self.version} UID: {self.fileDirUid}","green",)
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
                print(colored(f"Backtesting {percent_done:.2f}% complete.", "light_yellow"),end=("\r" if percent_done != 100 else "\n"),)
        return self.fileDir["backtestResultsStrategyUid"], self.combinePnlCsv()

    def backtest(self, stockName, startDate, endDate):

        startTimeEpoch = startDate.timestamp()
        endTimeEpoch = endDate.timestamp()

        stockAlgoLogic = equityOverNightAlgoLogic(stockName, self.fileDir)
        stockAlgoLogic.humanTime = startDate

        try:
            df = getEquityBacktestData(stockName, startTimeEpoch, endTimeEpoch, "1H")
        except Exception as e:
            raise Exception(e)

        df.dropna(inplace=True)
        df["ema15"] = talib.EMA(df["c"], timeperiod=15)
        df["ema110"] = talib.EMA(df["c"], timeperiod=110)
        df.dropna(inplace=True)

        df['RSI'] = talib.RSI(df['c'], timeperiod=14)
        df['StochRSI_K'] = ((df['RSI'] - df['RSI'].rolling(window=14).min()) / (df['RSI'].rolling(window=14).max() - df['RSI'].rolling(window=14).min())) * 100
        df['StochRSI_K_Smoothed'] = df['StochRSI_K'].rolling(window=3).mean()
        df['StochRSI_D'] = df['StochRSI_K_Smoothed'].rolling(window=3).mean()
        df.dropna(inplace=True)

        buy_condition = (
            (df["ema15"] > df["ema110"]) &
            (df['c'] > df["ema15"]) &
            (df["c"] > df["o"]) &
            (df['StochRSI_K_Smoothed'] > 20) & 
            (df['StochRSI_K_Smoothed'].rolling(window=10).min() < 20))

        buy_indices = df.index[buy_condition].tolist()
        df['buy_crossover'] = ''

        for i in range(len(buy_indices) - 1):
            start_idx = buy_indices[i]
            end_idx = buy_indices[i + 1]
            df_slice = df.loc[start_idx:end_idx]

            if len(df_slice) > 5:
                if df.loc[start_idx:end_idx, 'StochRSI_K_Smoothed'].max() > 80:
                    df.loc[end_idx, 'buy_crossover'] = 'buy_crossover'

        df['buyEntryCondition'] = np.where(buy_condition, "Buy", 0)
        df['buyExitCondition'] = np.where((df['c'] < df['ema110']) & (df['c'] < df['o']), "buyExitCondition", 0)
        df = df[df.index >= startTimeEpoch]
        df.to_csv(f"{self.fileDir['backtestResultsCandleData']}{stockName}_df.csv")

        amountPerTrade = 100000
        lastIndexTimeData = None

        for timeData in df.index:

            stockAlgoLogic.timeData = timeData
            stockAlgoLogic.humanTime = datetime.fromtimestamp(timeData)

            if not stockAlgoLogic.openPnl.empty:
                for index, row in stockAlgoLogic.openPnl.iterrows():
                    try:
                        stockAlgoLogic.openPnl.at[index,'CurrentPrice'] = df.at[lastIndexTimeData,'c']
                    except Exception as e:
                        logging.info(e)

            stockAlgoLogic.pnlCalculator()

            for index, row in stockAlgoLogic.openPnl.iterrows():

                if (df.at[lastIndexTimeData, "buyExitCondition"] == "buyExitCondition"):
                        exitType = "buyExitCondition"
                        stockAlgoLogic.exitOrder(index, exitType)

            if ((lastIndexTimeData in df.index) & (stockAlgoLogic.openPnl.empty)):
                if (df.at[lastIndexTimeData, "buyEntryCondition"] == "Buy"):
                    entry_price = df.at[lastIndexTimeData, "c"]
                    stockAlgoLogic.entryOrder(entry_price, stockName, (amountPerTrade//entry_price), "BUY")

            if (lastIndexTimeData in df.index):
                if (df.at[lastIndexTimeData, "buy_crossover"] == "buy_crossover"):
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
    strategyName = "EmaStochasticCrossover"
    version = "v1"

    startDate = datetime(2024, 1, 1, 9, 15)
    endDate = datetime(2024, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/Akash_Mishra/*Nifty50stocks/nifty50.md",4)
    # portfolio = createPortfolio("/root/Akash_Mishra/stocksList/Fno_173.md",4)

    algoLogicObj = EmaStochasticCrossover(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)
    
    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")