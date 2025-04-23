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


class Vertical100_400(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "Vertical100_400":
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
        
        stocks = ['OFSS', 'USHAMART', 'ELGIEQUIP', 'CENTURYTEX', 'DCMSHRIRAM', 'TRIVENI', 'PRAJIND', 'JMFINANCIL', 'CHOLAFIN', 'SIEMENS', 'SOBHA', 'DIXON', 'KEC', 'KEI', 'BALRAMCHIN', 'GODREJIND', 'BLUEDART', 'IEX', 'GODREJPROP', 'TIINDIA', 'HDFCLIFE', 'BOSCHLTD', 'KNRCON', 'DIVISLAB', 'GRSE', 'APARINDS', 'JKPAPER', 'ESCORTS', 'GUJGASLTD', 'KPRMILL', 'JUSTDIAL', 'BSOFT', 'TIMKEN', 'EIDPARRY', 'MFSL', 'VOLTAS', 'FSL', 'BALAMINES', 'TITAN', 'PFC', 'PRESTIGE', 'BHEL', 'DEEPAKNTR', 'COCHINSHIP', 'ICICIPRULI', 'LINDEINDIA', 'RCF', 'MINDACORP', 'ABCAPITAL', 'SCHAEFFLER', 'SOLARINDS', 'M&M', 'SUNDRMFAST', 'OIL', 'ZENSARTECH', 'ASTRAZEN', 'LT', 'ABB', 'IPCALAB', 'HAL', 'MCX', 'ENDURANCE', 'MPHASIS', 'PEL', 'GMRINFRA', 'CARBORUNIV', 'NIACL', 'CHOLAHLDNG', 'AARTIIND', 'GPIL', 'GLENMARK', 'CHAMBLFERT', 'QUESS', 'INTELLECT','BLS', 'UPL', '3MINDIA', 'DLF', 'LALPATHLAB', 'TATAELXSI', 'JINDALSTEL', 'VGUARD', 'CERA', 'MRPL', 'NETWORK18', 'KSB', 'JSWENERGY', 'BSE', 'BRIGADE', 'BIRLACORPN', 'GLAXO', 'SRF', 'IGL', 'COROMANDEL', 'M&MFIN', 'ACE', 'VBL', 'TECHM', 'CREDITACC', 'CCL', 'BEL', 'WHIRLPOOL', 'NAUKRI', 'BAJFINANCE', 'INDUSINDBK', 'VAIBHAVGBL', 'WIPRO', 'ULTRACEMCO', 'GRINDWELL', 'HINDALCO', 'MANAPPURAM', 'MGL', 'CUMMINSIND', 'RECLTD', 'RKFORGE', 'HFCL', 'JINDALSAW', 'BAYERCROP', 'TEJASNET', 'CANFINHOME', 'IBULHSGFIN', 'GPPL', 'LAURUSLABS', 'NMDC', 'CYIENT', 'GSFC', 'WELCORP', 'GILLETTE', 'NESTLEIND', 'TCS', 'RAMCOCEM', 'MAHLIFE', 'TVSMOTOR', 'ALKYLAMINE', 'PERSISTENT', 'PETRONET', 'GRAPHITE', 'MUTHOOTFIN', 'EXIDEIND', 'BPCL', 'HUDCO', 'HDFCBANK', 'CRISIL', 'GICRE', 'TATAINVEST', 'BAJAJFINSV', 'FACT', 'RAJESHEXPO', 'ECLERX', 'AUROPHARMA', 'GESHIP', 'APOLLOHOSP', 'ASTRAL', 'ACC', 'FORTIS', 'KOTAKBANK', 'SPARC', 'INDHOTEL', 'GSPL', 'LICHSGFIN', 'NATIONALUM', 'PHOENIXLTD', 'HAVELLS', 'CHENNPETRO', 'BHARATFORG', 'ADANIPORTS', 'JKLAKSHMI', 'AJANTPHARM', 'CDSL', 'INFY', 'PAGEIND', 'ICICIGI', 'GNFC', 'OBEROIRLTY', 'LTTS', 'SWANENERGY', 'CROMPTON', 'ASTERDM', 'PNBHOUSING', 'ITI', 'DMART', 'MAHSEAMLES', 'INDIANB', 'SYNGENE', 'RELIANCE', 'TATAPOWER', 'HEROMOTOCO', 'AUBANK', 'BEML', 'NATCOPHARM', 'JKCEMENT', 'GAEL', 'ATUL', 'ABBOTINDIA', 'REDINGTON', 'BERGEPAINT', 'RADICO', 'SBIN', 'IOC', 'BANKINDIA', 'BDL', 'HINDCOPPER', 'KRBL', 'MASTEK', 'HBLPOWER', 'HONAUT', 'CGPOWER', 'DRREDDY', 'PIIND', 'HCLTECH', 'JBCHEPHARM', 'ASIANPAINT', 'SUNPHARMA', 'GODFRYPHLP', 'CESC', 'LUPIN', 'APOLLOTYRE', 'INDIACEM', 'BAJAJ-AUTO', 'HINDPETRO', 'ITC', 'ERIS', 'PGHH', 'PNCINFRA', 'AMBER', 'ASAHIINDIA', 'ADANIENT', 'JSWSTEEL', 'VEDL', 'KANSAINER', 'GAIL', 'CGCL', 'BLUESTARCO', 'JSL', 'MRF', 'RATNAMANI', 'KARURVYSYA', 'BATAINDIA', 'MHRIL', 'GMMPFAUDLR', 'GRASIM', 'AMBUJACEM', 'POLYMED', 'BALKRISIND', 'TRITURBINE', 'CEATLTD', 'SUZLON', 'DEEPAKFERT', 'ISEC', 'CIPLA', 'TRENT', 'PIDILITIND', 'AIAENG', 'FDC', 'TATASTEEL', 'CUB', 'HSCL', 'CONCOR', 'ALLCARGO', 'BIOCON', 'ALKEM', 'TATAMOTORS', 'COLPAL', 'IDFCFIRSTB', 'MARUTI', 'VTL', 'RITES', 'BAJAJHLDNG', 'ONGC', 'FINCABLES', 'BHARTIARTL', 'AXISBANK', 'PRSMJOHNSN', 'RBLBANK', 'IDEA', 'J&KBANK', 'CENTURYPLY', 'ASHOKLEY', 'SHREECEM', 'JUBLFOOD','HDFCAMC', 'INDIGO', 'BANKBARODA', 'UBL', 'NTPC', 'VIPIND', 'GODREJCP', 'SAIL', 'POWERGRID', 'SJVN', 'IDFC', 'APLLTD', 'MMTC', 'HEG', 'TATACHEM', 'TV18BRDCST', 'TATAMTRDVR', 'SAREGAMA', 'YESBANK', 'CASTROLIND', 'GMDCLTD', 'SKFINDIA', 'UCOBANK', 'EIHOTEL', 'COALINDIA', 'ABFRL', 'MOTILALOFS', 'SONATSOFTW', 'ICICIBANK', 'IOB', 'LEMONTREE', 'CANBK', 'TATACONSUM', 'AVANTIFEED', 'SUNDARMFIN', 'FINPIPE', 'BANDHANBNK','BRITANNIA', 'MAHABANK', 'TORNTPHARM', 'IRCON', 'PNB', 'JBMA', 'UNIONBANK', 'THERMAX', 'GRANULES', 'NHPC', 'RAYMOND', 'FINEORG', 'JYOTHYLAB', 'SUNTECK', 'ENGINERSIN', 'FEDERALBNK', 'NCC', 'SUPREMEIND', 'IDBI', 'ADANIGREEN', 'IRB', 'EICHERMOT', 'ADANIPOWER', 'SBILIFE', 'INOXWIND', 'TTML', 'TATACOMM', 'ZEEL', 'NBCC', 'TRIDENT', 'VARROC', 'TORNTPOWER', 'KAJARIACER', 'HINDUNILVR', 'NLCINDIA', 'SCHNEIDER', 'DABUR', 'BBTC', 'ELECON', 'OLECTRA', 'NH', 'HINDZINC', 'EMAMILTD', 'TANLA', 'APLAPOLLO', 'SUNTV', 'AAVAS', 'MARICO', 'CAPLIPOINT']

        df = {}
        directory = "/root/akashEquityBacktestAlgos/annualWeeklyDaily/BacktestResults/NA_Vertical50_v1/2/CandleData"

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
        # directory = "path_to_your_input_directory"

        for filename in os.listdir(directory):
            if filename.endswith('.csv'):
                stock_ticker = filename.split('_')[0]
                try:
                    file_path = os.path.join(directory, filename)
                    stock_df = pd.read_csv(file_path)

                    if 'datetime' not in stock_df.columns:
                        print(f"datetime column not found in {filename}")
                        continue

                    stock_df['datetime'] = pd.to_datetime(stock_df['datetime'], errors='coerce')
                    if stock_df['datetime'].isnull().any():
                        print(f"Invalid datetime entries in {filename}. Rows with invalid dates will be NaN.")
                        stock_df = stock_df.dropna(subset=['datetime'])

                    stock_df['year'] = stock_df['datetime'].dt.year
                    stock_df['month'] = stock_df['datetime'].dt.month

                    stock_df['Last'] = None

                    for year in stock_df['year'].unique():
                        for month in range(1, 13):
                            if month == 12:
                                dec_rows = stock_df[(stock_df['year'] == year) & (stock_df['month'] == month)]
                                if len(dec_rows) > 1:
                                    second_last_row = dec_rows.iloc[-4]
                                    stock_df.loc[second_last_row.name, 'Last'] = 'Last'

                    output_path = os.path.join(directory, f"{stock_ticker}_modified.csv")
                    stock_df.to_csv(output_path, index=False)
                    
                    df[stock_ticker] = stock_df
                    
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    continue

        amountPerTrade = 100000
        lastIndexTimeData = None
        breakeven = {}
        TotalTradeCanCome = 100

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

                            elif df[stock].at[lastIndexTimeData, "Last"] == "Last":
                                exitType = "LastDate"
                                stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "prev_c"])

                                PnL = (((df[stock].at[lastIndexTimeData, "prev_c"] - row['EntryPrice']) * row['Quantity']))//100
                                amountPerTrade = (amountPerTrade + PnL)
                                nowTotalTrades = len(stockAlgoLogic.openPnl)
                                output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, lastDay: {stock}, PnL:{PnL}, amountPerTrade:{amountPerTrade}\n"
                                with open('reposrrrt.txt', 'a') as file:
                                    file.write(output_string)

                            elif df[stock].at[lastIndexTimeData, "yes"] == "no":
                                exitType = "weeklyExit"
                                stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "prev_c"])

                                PnL = ((df[stock].at[lastIndexTimeData, "prev_c"] - row['EntryPrice']) * row['Quantity'])/100
                                amountPerTrade = (amountPerTrade + PnL)
                                nowTotalTrades = len(stockAlgoLogic.openPnl)
                                output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, WeeklyExitHit: {stock}, PnL:{PnL} amountPerTrade:- {amountPerTrade}\n"
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

                                PnL = (((df[stock].at[lastIndexTimeData, "c"] - row['EntryPrice']) * row['Quantity']) // 100)
                                amountPerTrade = (amountPerTrade + PnL)

                                output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, TargetRsi: {stock}, PnL:{PnL} amountPerTrade:- {amountPerTrade}\n"
                                with open('reposrrrt.txt', 'a') as file:
                                    file.write(output_string)

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

if __name__ == "__main__":
    startNow = datetime.now()

    devName = "NA"
    strategyName = "Vertical100_400"
    version = "v1"

    startDate = datetime(2019, 1, 1, 9, 15)
    endDate = datetime(2024, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/akashEquityBacktestAlgos/stocksList/nifty500 copy 2.md",1)

    algoLogicObj = Vertical100_400(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")