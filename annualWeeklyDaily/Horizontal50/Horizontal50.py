from backtestTools.util import createPortfolio, generateReportFile, calculateDailyReport, limitCapital
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData, getEquityHistData
import talib
import os
import logging
import multiprocessing
import pandas as pd
from termcolor import colored, cprint
from datetime import datetime, timedelta, time
from backtestTools.util import setup_logger

# BLS01_V50
class Horizontal50(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "Horizontal50":
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
                print(colored(f"Backtesting {percent_done:.2f}% complete.", "light_yellow"), end="\r")
        return self.fileDir["backtestResultsStrategyUid"], self.combinePnlCsv()

    def backtest(self, stockName, startDate, endDate):
        startTimeEpoch = startDate.timestamp()
        endTimeEpoch = endDate.timestamp()
        stockAlgoLogic = equityOverNightAlgoLogic(stockName, self.fileDir)
        logger = setup_logger(stockName, f"{self.fileDir['backtestResultsStrategyLogs']}/{stockName}.log")
        logger.propagate = False

        df = {}
        directory = "/root/equityResearch/annualWeeklyDaily/Horizontal50/candleData"

        # for filename in os.listdir(directory):
        #     if filename.endswith('.csv'):
        #         stock_ticker = filename.split('_')[0]
        #         try:
        #             file_path = os.path.join(directory, filename)
        #             stock_df = pd.read_csv(file_path)
                    
        #             # Ensure datetime column is in the correct format
        #             if 'datetime' not in stock_df.columns:
        #                 print(f"datetime column not found in {filename}")
        #                 continue
                    
        #             stock_df['datetime'] = pd.to_datetime(stock_df['datetime'])
                    
        #             # Set datetime as index to make operations easier
        #             stock_df.set_index('datetime', inplace=True)
                    
        #             # Add a column 'Year_Last' to mark the last trading day of each year
        #             # Mark the last trading day of each year as 'Last' in a new column
        #             stock_df['Year_Last'] = stock_df.groupby(stock_df.index.year).apply(
        #                 lambda group: group.index == group.index[-1]).astype(int)
                    
        #             # Save the modified DataFrame to a new CSV file with the stock ticker name
        #             output_path = os.path.join(directory, f"{stock_ticker}_modified.csv")
        #             stock_df.to_csv(output_path)
                    
        #             # Append the DataFrame to the 'df' dictionary if needed
        #             df[stock_ticker] = stock_df
                    
        #         except Exception as e:
        #             print(f"Error processing {filename}: {e}")
        #             continue

        # import pandas as pd
        # import os

        # df = {}
        # directory = "path_to_your_input_directory"  # Set your input directory path

        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                stock_ticker = filename.split('_')[0]
                try:
                    file_path = os.path.join(directory, filename)
                    stock_df = pd.read_csv(file_path)

                #     if 'datetime' not in stock_df.columns:
                #         print(f"datetime column not found in {filename}")
                #         continue

                #     stock_df['datetime'] = pd.to_datetime(stock_df['datetime'], errors='coerce')
                #     if stock_df['datetime'].isnull().any():
                #         print(f"Invalid datetime entries in {filename}. Rows with invalid dates will be NaN.")
                #         stock_df = stock_df.dropna(subset=['datetime'])

                #     stock_df['year'] = stock_df['datetime'].dt.year
                #     stock_df['month'] = stock_df['datetime'].dt.month

                #     stock_df['timeUp'] = ""
                #     stock_df.loc[stock_df.index[-1], 'timeUp'] = 'timeUp'
                #     stock_df.dropna(inplace=True)

                #     stock_df['Last'] = None

                #     for year in stock_df['year'].unique():
                #         for month in range(1, 13):
                #             if month == 12:
                #                 dec_rows = stock_df[(stock_df['year'] == year) & (stock_df['month'] == month)]
                #                 if len(dec_rows) > 1:
                #                     second_last_row = dec_rows.iloc[-4]
                #                     stock_df.loc[second_last_row.name, 'Last'] = 'Last'

                #     output_path = os.path.join(directory, f"{stock_ticker}_modified.csv")
                #     stock_df.to_csv(output_path, index=False)

                    stock_df['timeUp'] = ""
                    stock_df.loc[stock_df.index[-2], 'timeUp'] = 'timeUp'
                    df[stock_ticker] = stock_df

                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    continue

        amountPerTrade = 100000
        lastIndexTimeData = None
        breakeven = {}
        TotalTradeCanCome = 100
        ProfitAmount = 0
        LossAmount = 0

        for timeData in df.get('AARTIIND', pd.DataFrame()).index:
            for stock in df.keys():
                if df.get('AARTIIND') is None:
                    continue

                print(stock)

                stockAlgoLogic.timeData = timeData
                if lastIndexTimeData is not None:
                    try:
                        stockAlgoLogic.humanTime = df[stock].at[lastIndexTimeData, "datetime"]
                    except KeyError as e:
                        print(f"KeyError: {e} - Index {lastIndexTimeData} not found in DataFrame for stock {stock}.")
                        stockAlgoLogic.humanTime = None
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                        stockAlgoLogic.humanTime = None

                if lastIndexTimeData in df[stock].index:
                    logger.info(f"Datetime: {stockAlgoLogic.humanTime}\tStock: {stock}\tClose: {df[stock].at[lastIndexTimeData, 'c']}")

                stock_openPnl = stockAlgoLogic.openPnl[stockAlgoLogic.openPnl['Symbol'] == stock]
                if not stock_openPnl.empty:
                    for index, row in stock_openPnl.iterrows():
                        try:
                            stockAlgoLogic.openPnl.at[index, 'CurrentPrice'] = df[stock].at[lastIndexTimeData, "c"]
                        except Exception as e:
                            logger.error(f"Error fetching historical data for {row['Symbol']}: {e}")

                stockAlgoLogic.pnlCalculator()

                for index, row in stock_openPnl.iterrows():
                    if lastIndexTimeData in df[stock].index:
                        if index in stock_openPnl.index:
                            if df[stock].at[lastIndexTimeData, "timeUp"] == "timeUp":
                                exitType = "TimeUpExit"
                                stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "c"])

                            elif df[stock].at[lastIndexTimeData, "yes"] == "no":
                                exitType = "weeklyExit"
                                stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "prev_c"])

                                PnL = ((abs(df[stock].at[lastIndexTimeData, "prev_c"] - row['EntryPrice']) * row['Quantity']))
                                LossAmount = LossAmount + PnL
                                nowTotalTrades = len(stockAlgoLogic.openPnl)
                                output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, WeeklyExitHit: {stock}, PnL:{PnL} LossAmount:- {LossAmount}\n"
                                with open('reposrrrt.txt', 'a') as file:
                                    file.write(output_string)

                            elif breakeven.get(stock) != True and row['EntryPrice'] > df[stock].at[lastIndexTimeData, "c"] and df[stock].at[lastIndexTimeData, "rsi"] < 30:
                                breakeven[stock] = True

                            elif breakeven.get(stock) == True and df[stock].at[lastIndexTimeData, "c"] > row['EntryPrice']:
                                exitType = "BreakevenExit"
                                stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "c"])
                                nowTotalTrades = len(stockAlgoLogic.openPnl)
                                output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, Breakeven: {stock}\n"
                                with open('reposrrrt.txt', 'a') as file:
                                    file.write(output_string)

                                if df[stock].at[lastIndexTimeData, "rsi"] > 60 and nowTotalTrades < TotalTradeCanCome:
                                    entry_price = df[stock].at[lastIndexTimeData, "c"]
                                    breakeven[stock] = False
                                    stockAlgoLogic.entryOrder(entry_price, stock, (amountPerTrade // entry_price), "BUY")
                                    nowTotalTrades = len(stockAlgoLogic.openPnl)
                                    output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, Entry: {stock}\n"
                                    with open('reposrrrt.txt', 'a') as file:
                                        file.write(output_string)
                                breakeven[stock] = False

                            elif df[stock].at[lastIndexTimeData, "rsi"] < 30 and df[stock].at[lastIndexTimeData, "c"] > row['EntryPrice']:
                                exitType = "TargetUsingRsi"
                                stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "c"])
                                nowTotalTrades = len(stockAlgoLogic.openPnl)

                                PnL = (((df[stock].at[lastIndexTimeData, "c"] - row['EntryPrice']) * row['Quantity']))
                                ProfitAmount = ProfitAmount + PnL

                                output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, TargetRsi: {stock}, PnL:{PnL} ProfitAmount:- {ProfitAmount}\n"
                                with open('reposrrrt.txt', 'a') as file:
                                    file.write(output_string)

                if lastIndexTimeData is not None:
                    if ProfitAmount > 100000:
                        ProfitAmount = ProfitAmount - 100000
                        TotalTradeCanCome = TotalTradeCanCome + 1

                        nowTotalTrades = len(stockAlgoLogic.openPnl)

                        if lastIndexTimeData in df[stock].index:
                            output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, ProfitIncrease: {stock}, ProfitAmount: {ProfitAmount}\n"

                            with open('reposrrrt.txt', 'a') as file:
                                file.write(output_string)
                        else:
                            print(f"Index {lastIndexTimeData} not found in DataFrame for stock {stock}")

                    elif LossAmount > 100000:
                        LossAmount = LossAmount - 100000
                        TotalTradeCanCome = TotalTradeCanCome - 1
                        nowTotalTrades = len(stockAlgoLogic.openPnl)

                        if lastIndexTimeData in df[stock].index:
                            output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, ProfitIncrease: {stock}, ProfitAmount: {ProfitAmount}\n"

                            with open('reposrrrt.txt', 'a') as file:
                                file.write(output_string)
                        else:
                            print(f"Index {lastIndexTimeData} not found in DataFrame for stock {stock}")

                if lastIndexTimeData in df[stock].index:
                    nowTotalTrades = len(stockAlgoLogic.openPnl)
                    if df[stock].at[lastIndexTimeData, "rsi"] > 60 and stock_openPnl.empty and nowTotalTrades < TotalTradeCanCome:
                        if df[stock].at[lastIndexTimeData, "yes"] == "yes":
                            entry_price = df[stock].at[lastIndexTimeData, "c"]
                            breakeven[stock] = False

                            stockAlgoLogic.entryOrder(entry_price, stock, (amountPerTrade // entry_price), "BUY", {"quantity": (amountPerTrade // entry_price), "EntryDate":df[stock].at[lastIndexTimeData, "datetime"]})

                            nowTotalTrades = len(stockAlgoLogic.openPnl)
                            output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, Entry: {stock}\n"
                            with open('reposrrrt.txt', 'a') as file:
                                file.write(output_string)

                lastIndexTimeData = timeData
                stockAlgoLogic.pnlCalculator()

            if lastIndexTimeData is not None:   
                if df[stock].at[lastIndexTimeData, "timeUp"] == "timeUp":
                    combined_df = stockAlgoLogic.openPnl.copy()
                    expiryValue = (combined_df['CurrentPrice'] * combined_df['Quantity']).sum()
                    output_string = f"{expiryValue}, {df[stock].at[lastIndexTimeData, 'datetime']}\n"
                    with open('reposrrrtExpiry.txt', 'a') as file:
                        file.write(output_string)

if __name__ == "__main__":
    startNow = datetime.now()

    devName = "NA"
    strategyName = "Horizontal50"
    version = "v1"

    startDate = datetime(2019, 1, 1, 9, 15)
    endDate = datetime(2024, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/akashEquityBacktestAlgos/stocksList/nifty500 copy 2.md",1)

    algoLogicObj = Horizontal50(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")