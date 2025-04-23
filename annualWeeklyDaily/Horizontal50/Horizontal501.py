from backtestTools.util import createPortfolio, generateReportFile, calculateDailyReport, limitCapital
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData, getEquityHistData
import talib
import logging
import multiprocessing
import pandas as pd
from termcolor import colored, cprint
from datetime import datetime, timedelta, time
from backtestTools.util import setup_logger

# BLS01_V50
class Vertical50(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "Vertical50":
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

        # stocks = ['OFSS', 'USHAMART', 'ELGIEQUIP', 'CENTURYTEX', 'DCMSHRIRAM', 'TRIVENI', 'PRAJIND', 'JMFINANCIL', 'CHOLAFIN', 'SIEMENS', 'SOBHA', 'DIXON', 'KEC', 'KEI', 'BALRAMCHIN', 'GODREJIND', 'BLUEDART', 'METROPOLIS', 'IEX', 'GODREJPROP', 'TIINDIA', 'HDFCLIFE', 'BOSCHLTD', 'KNRCON', 'DIVISLAB', 'SHRIRAMFIN', 'GRSE', 'APARINDS', 'JKPAPER', 'ESCORTS', 'GUJGASLTD', 'KPRMILL', 'JUSTDIAL', 'BSOFT', 'TIMKEN', 'EIDPARRY', 'MFSL', 'VOLTAS', 'FSL', 'BALAMINES', 'TITAN', 'MAXHEALTH', 'PFC', 'PRESTIGE', 'COFORGE', 'BHEL', 'DEEPAKNTR', 'COCHINSHIP', 'ICICIPRULI', 'LINDEINDIA', 'RCF', 'MINDACORP', 'ABCAPITAL', 'MAZDOCK', 'SCHAEFFLER', 'SOLARINDS', 'M&M', 'SUNDRMFAST', 'OIL', 'ZENSARTECH', 'ASTRAZEN', 'LT', 'ABB', 'IPCALAB', 'HAL', 'MCX', 'ENDURANCE', 'MPHASIS', 'PEL', 'GMRINFRA', 'CARBORUNIV', 'NIACL', 'CHOLAHLDNG', 'AARTIIND', 'GPIL', 'GLENMARK', 'CHAMBLFERT', 'QUESS', 'INTELLECT', 'NAVINFLUOR', 'BLS', 'UPL', '3MINDIA', 'DLF', 'MOTHERSON', 'LALPATHLAB', 'TATAELXSI', 'JINDALSTEL', 'VGUARD', 'CERA', 'MRPL', 'NETWORK18', 'KSB', 'LTIM', 'JSWENERGY', 'BSE', 'BRIGADE', 'KPITTECH', 'BIRLACORPN', 'GLAXO', 'SRF']
        stocks = ['IGL', 'COROMANDEL', 'M&MFIN', 'ACE', 'VBL', 'TECHM', 'CREDITACC', 'CCL', 'BEL', 'WHIRLPOOL', 'NAUKRI', 'BAJFINANCE', 'INDUSINDBK', 'VAIBHAVGBL', 'WIPRO', 'SBICARD', 'FLUOROCHEM', 'ULTRACEMCO', 'GRINDWELL', 'HINDALCO', 'MANAPPURAM', 'MGL', 'CUMMINSIND', 'RECLTD', 'RKFORGE', 'HFCL', 'JINDALSAW', 'BAYERCROP', 'TEJASNET', 'CANFINHOME', 'IBULHSGFIN', 'GPPL', 'LAURUSLABS', 'NMDC', 'CYIENT', 'GSFC', 'WELCORP', 'GILLETTE', 'NESTLEIND', 'TCS', 'RAMCOCEM', 'MAHLIFE', 'TVSMOTOR', 'ALKYLAMINE', 'PERSISTENT', 'PETRONET', 'GRAPHITE', 'MUTHOOTFIN', 'EXIDEIND', 'BPCL', 'HUDCO', 'HDFCBANK', 'CRISIL', 'GICRE', 'TATAINVEST', 'BAJAJFINSV', 'FACT', 'RAJESHEXPO', 'ECLERX', 'AUROPHARMA', 'GESHIP', 'POLYCAB', 'APOLLOHOSP', 'ASTRAL', 'ACC', 'FORTIS', 'KOTAKBANK', 'SPARC', 'INDHOTEL', 'GSPL', 'LICHSGFIN', 'NATIONALUM', 'PHOENIXLTD', 'HAVELLS', 'CHENNPETRO', 'BHARATFORG', 'ADANIPORTS', 'JKLAKSHMI', 'AJANTPHARM', 'CDSL', 'INFY', 'PAGEIND', 'ICICIGI', 'GNFC', 'OBEROIRLTY', 'LTTS', 'SWANENERGY', 'CROMPTON', 'ASTERDM', 'PNBHOUSING', 'ITI', 'DMART', 'MAHSEAMLES', 'INDIANB', 'SYNGENE', 'RELIANCE']
        # stocks = ['TATAPOWER', 'HEROMOTOCO', 'AUBANK', 'BEML', 'NATCOPHARM', 'JKCEMENT', 'GAEL', 'ATUL', 'ABBOTINDIA', 'REDINGTON', 'BERGEPAINT', 'RADICO', 'SBIN', 'IOC', 'BANKINDIA', 'BDL', 'HINDCOPPER', 'KRBL', 'MASTEK', 'HBLPOWER', 'HONAUT', 'CGPOWER', 'DRREDDY', 'PIIND', 'HCLTECH', 'JBCHEPHARM', 'ASIANPAINT', 'SUNPHARMA', 'GODFRYPHLP', 'CESC', 'LUPIN', 'APOLLOTYRE', 'INDIACEM', 'BAJAJ-AUTO', 'HINDPETRO', 'ITC', 'ERIS', 'CHALET', 'PGHH', 'PNCINFRA', 'AMBER', 'ASAHIINDIA', 'ADANIENT', 'JSWSTEEL', 'VEDL', 'KANSAINER', 'GAIL', 'CGCL', 'ADANIENSOL', 'BLUESTARCO', 'JSL', 'MRF', 'RATNAMANI', 'KARURVYSYA', 'BATAINDIA', 'MHRIL', 'GMMPFAUDLR', 'GRASIM', 'AMBUJACEM', 'POLYMED', 'BALKRISIND']
        # stocks = ['TRITURBINE', 'CEATLTD', 'SUZLON', 'DEEPAKFERT', 'ISEC', 'CIPLA', 'TRENT', 'PIDILITIND', 'AIAENG', 'FDC', 'TATASTEEL', 'CUB', 'HSCL', 'CONCOR', 'ALLCARGO', 'BIOCON', 'ALKEM', 'TATAMOTORS', 'COLPAL', 'IDFCFIRSTB', 'MARUTI', 'VTL', 'BAJAJHLDNG', 'ONGC', 'FINCABLES', 'BHARTIARTL', 'AXISBANK', 'PRSMJOHNSN', 'RBLBANK', 'IDEA', 'J&KBANK', 'CENTURYPLY', 'ASHOKLEY', 'SHREECEM', 'JUBLFOOD', 'ATGL', 'DALBHARAT', 'HDFCAMC', 'INDIGO', 'BANKBARODA', 'UBL', 'NTPC', 'VIPIND', 'GODREJCP', 'SAIL', 'POWERGRID', 'SJVN', 'IDFC', 'APLLTD', 'MMTC', 'HEG', 'TATACHEM', 'TV18BRDCST', 'TATAMTRDVR', 'SAREGAMA', 'YESBANK', 'CASTROLIND', 'ZYDUSLIFE', 'RVNL', 'GMDCLTD', 'SKFINDIA', 'UCOBANK']
        # stocks = ['EIHOTEL', 'COALINDIA', 'ABFRL', 'MOTILALOFS', 'SONATSOFTW', 'PATANJALI', 'ICICIBANK', 'IOB', 'IRCTC', 'LEMONTREE', 'CANBK', 'TATACONSUM', 'AVANTIFEED', 'SUNDARMFIN', 'FINPIPE', 'BANDHANBNK','BRITANNIA', 'MAHABANK', 'TORNTPHARM', 'IRCON', 'PNB', 'JBMA', 'UNIONBANK', 'THERMAX', 'GRANULES', 'NHPC', 'RAYMOND', 'POONAWALLA', 'FINEORG', 'JYOTHYLAB', 'SUNTECK', 'ENGINERSIN', 'FEDERALBNK', 'NCC', 'SUPREMEIND', 'IDBI', 'ADANIGREEN', 'IRB', 'EICHERMOT', 'ADANIPOWER', 'SBILIFE', 'INOXWIND', 'TTML', 'TATACOMM', 'ZEEL', 'NBCC', 'TRIDENT', 'VARROC', 'TORNTPOWER', 'KAJARIACER', 'HINDUNILVR', 'NLCINDIA', 'SCHNEIDER', 'DABUR', 'BBTC', 'ELECON', 'OLECTRA', 'NH', 'HINDZINC', 'EMAMILTD', 'TANLA', 'APLAPOLLO', 'SUNTV', 'AAVAS', 'MARICO', 'CAPLIPOINT']

        df = {}

        for stock in stocks:
            df[stock] = getEquityBacktestData(stock, startTimeEpoch - (86400 * 15), endTimeEpoch, "D")
            print(df[stock])
            if df[stock] is not None:
                df[stock]['datetime'] = pd.to_datetime(df[stock]['datetime'])

                df[stock]['time'] = df[stock]['datetime'].dt.strftime('%H:%M')
                df[stock]['date'] = df[stock]['datetime'].dt.date
                df[stock]['month'] = df[stock]['datetime'].dt.month
                df[stock]['year'] = df[stock]['datetime'].dt.year
                df[stock]['day'] = df[stock]['datetime'].dt.day
                df[stock]['yes'] = ''
                df[stock]['stockName'] = stock

                # second_last_indices = df[stock].groupby(df[stock]['datetime'].dt.year).nth(-2).index
                # df[stock].loc[second_last_indices, 'yes'] = 'yes'
                # df[stock].dropna(inplace=True)

                df[stock]["rsi"] = talib.RSI(df[stock]["c"], timeperiod=14)
                df[stock]['prev_rsi'] = df[stock]['rsi'].shift(1)
                df[stock]['prev_c'] = df[stock]['c'].shift(1)

                df[stock].dropna(inplace=True)
                df[stock]['timeUp'] = ""
                df[stock].loc[df[stock].index[-1], 'timeUp'] = 'timeUp'
                df[stock].dropna(inplace=True)

            range_data = pd.read_csv("/root/equityResearch/annualWeeklyDaily/range.csv")

            range_data['startDateRange'] = pd.to_datetime(range_data['startDateRange'], errors='coerce')
            range_data['endDateRange'] = pd.to_datetime(range_data['endDateRange'], errors='coerce')

            for stock, stock_df in df.items():
                stock_df['datetime'] = pd.to_datetime(stock_df['datetime'], errors='coerce')
                stock_df['yes'] = 'no'

                stock_range = range_data[range_data['Symbol'] == stock]
                if stock_range.empty:
                    print(f"No date range found for {stock}. Skipping.")
                    continue

                for idx, row in stock_df.iterrows():
                    stock_date = row['datetime'].date()

                    for _, range_row in stock_range.iterrows():
                        if range_row['startDateRange'].date() <= stock_date <= range_row['endDateRange'].date():
                            stock_df.at[idx, 'yes'] = 'yes'
                            break

                stock_df.dropna(subset=['datetime'], inplace=True)
                print(stock_df.head())

                df[stock].index = df[stock].index + 33300
                file_path = f"{self.fileDir['backtestResultsCandleData']}{stock}_df.csv"
                df[stock].to_csv(file_path)


        # amountPerTrade = 100000
        # lastIndexTimeData = None
        # breakeven = {}
        # TotalTradeCanCome = 50

        # for timeData in df['AARTIIND'].index:
        #     for stock in stocks:
        #         print(stock)

        #         stockAlgoLogic.timeData = timeData
        #         if lastIndexTimeData is not None:
        #             stockAlgoLogic.humanTime = datetime.fromtimestamp(timeData)

        #         if lastIndexTimeData in df[stock].index:
        #             logger.info(f"Datetime: {stockAlgoLogic.humanTime}\tStock: {stockName}\tClose: {df[stock].at[lastIndexTimeData, 'c']}")

        #         stock_openPnl = stockAlgoLogic.openPnl[stockAlgoLogic.openPnl['Symbol'] == stock]

        #         if not stock_openPnl.empty:
        #             for index, row in stock_openPnl.iterrows():
        #                 try:
        #                     stockAlgoLogic.openPnl.at[index, 'CurrentPrice'] = df[stock].at[lastIndexTimeData, "c"]
        #                     if row['EntryPrice'] > row['CurrentPrice']:

        #                         output_string = f"{df[stock].at[lastIndexTimeData, 'datetime']}, inLoss: {stock}\n"
        #                         with open('logs1.txt', 'a') as file:
        #                             file.write(output_string)

        #                 except Exception as e:
        #                     logger.error(f"Error fetching historical data for {row['Symbol']}: {e}")

        #         stockAlgoLogic.pnlCalculator()

        #         for index, row in stock_openPnl.iterrows():
        #             if lastIndexTimeData in df[stock].index:
        #                 if index in stock_openPnl.index:

        #                     if df[stock].at[lastIndexTimeData, "timeUp"] == "timeUp":
        #                         exitType = "TimeUpExit"
        #                         stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "c"])

        #                     elif breakeven.get(stock) != True and row['EntryPrice'] > df[stock].at[lastIndexTimeData, "c"] and df[stock].at[lastIndexTimeData, "rsi"] < 30:
        #                         breakeven[stock] = True
        #                         # output_string = f"{df[stock].at[lastIndexTimeData, 'datetime']}, BreakevenTrigger: {stock},amountPerTrade:{amountPerTrade}\n"
        #                         # with open('saveData.txt', 'a') as file:
        #                         #     file.write(output_string)

        #                     elif breakeven.get(stock) == True and df[stock].at[lastIndexTimeData, "c"] > row['EntryPrice']:
        #                         exitType = "BreakevenExit"
        #                         stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "c"])
        #                         nowTotalTrades = len(stockAlgoLogic.openPnl)
        #                         output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, Breakeen: {stock}\n"
        #                         with open('reposrrrtvertical.txt', 'a') as file:
        #                             file.write(output_string)

        #                         output_string = f"{df[stock].at[lastIndexTimeData, 'datetime']}, BreakevenExit: {stock}\n"
        #                         with open('saveData.txt', 'a') as file:
        #                             file.write(output_string)

        #                         if df[stock].at[lastIndexTimeData, "rsi"] > 70 and stock_openPnl.empty and nowTotalTrades < TotalTradeCanCome:
        #                             entry_price = df[stock].at[lastIndexTimeData, "c"]
        #                             breakeven[stock] = False
        #                             quantity = (amountPerTrade // entry_price)
        #                             # if ((amountPerTrade - (quantity * entry_price)) + BufferAmount) > entry_price:
        #                             #     quantity = quantity + 1
        #                             stockAlgoLogic.entryOrder(entry_price, stock, quantity, "BUY")
        #                             nowTotalTrades = len(stockAlgoLogic.openPnl)
        #                             output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, EntryVERTICAL: {stock},amountPerTrade:{amountPerTrade} quantity:{quantity}\n"
        #                             with open('reposrrrtvertical.txt', 'a') as file:
        #                                 file.write(output_string)
        #                         breakeven[stock] = False

        #                     elif df[stock].at[lastIndexTimeData, "rsi"] < 30 and df[stock].at[lastIndexTimeData, "c"] > row['EntryPrice']:
        #                         exitType = "TargetUsingRsi"
        #                         stockAlgoLogic.exitOrder(index, exitType, df[stock].at[lastIndexTimeData, "c"])

        #                         PnL = (((df[stock].at[lastIndexTimeData, "c"] - row['EntryPrice']) * row['Quantity'])) // 50
        #                         amountPerTrade = amountPerTrade + PnL
        #                         BufferAmount = (amountPerTrade // 2)
        #                         nowTotalTrades = len(stockAlgoLogic.openPnl)
        #                         output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, TargetRsi: {stock}, PnL{PnL} amountPerTrade:- {amountPerTrade}, BufferAmount:- {BufferAmount}\n"
        #                         with open('reposrrrtvertical.txt', 'a') as file:
        #                             file.write(output_string)

        #         if lastIndexTimeData in df[stock].index:

        #             nowTotalTrades = len(stockAlgoLogic.openPnl)
        #             if df[stock].at[lastIndexTimeData, "rsi"] > 60 and stock_openPnl.empty and nowTotalTrades < TotalTradeCanCome:
        #                 entry_price = df[stock].at[lastIndexTimeData, "c"]
        #                 breakeven[stock] = False
        #                 quantity = (amountPerTrade // entry_price)
        #                 # if ((amountPerTrade - (quantity * entry_price)) + BufferAmount) > entry_price:
        #                 #     quantity = quantity + 1
        #                 stockAlgoLogic.entryOrder(entry_price, stock, quantity, "BUY", {"quantity": (amountPerTrade // entry_price)})
 
        #                 nowTotalTrades = len(stockAlgoLogic.openPnl)
        #                 output_string = f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, {df[stock].at[lastIndexTimeData, 'datetime']}, EntryVERTICAL: {stock},amountPerTrade:{amountPerTrade} quantity:{quantity}\n"
        #                 with open('reposrrrtvertical.txt', 'a') as file:
        #                     file.write(output_string)

        #         lastIndexTimeData = timeData
        #         stockAlgoLogic.pnlCalculator()

if __name__ == "__main__":
    startNow = datetime.now()

    devName = "NA"
    strategyName = "Vertical50"
    version = "v1"

    startDate = datetime(2018, 1, 1, 9, 15)
    endDate = datetime(2025, 12, 31, 15, 30)

    portfolio = createPortfolio("/root/akashEquityBacktestAlgos/stocksList/nifty500 copy 2.md",1)

    algoLogicObj = Vertical50(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")