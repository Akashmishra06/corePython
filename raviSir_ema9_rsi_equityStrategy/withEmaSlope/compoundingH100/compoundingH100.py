from backtestTools.util import createPortfolio, calculate_mtm
from backtestTools.algoLogic import baseAlgoLogic, equityOverNightAlgoLogic
from backtestTools.histData import getEquityBacktestData
import talib
import concurrent.futures
import threading
import pandas as pd
from termcolor import colored, cprint
from datetime import datetime
from backtestTools.util import setup_logger


class R_60_60_30(baseAlgoLogic):
    def runBacktest(self, portfolio, startDate, endDate):
        if self.strategyName != "R_60_60_30":
            raise Exception("Strategy Name Mismatch")
        cprint(f"Backtesting: {self.strategyName} UID: {self.fileDirUid}", "green")
        first_stock = portfolio if portfolio and portfolio else None
        if first_stock:
            self.backtest(first_stock, startDate, endDate)
            print(colored("Backtesting 100% complete.", "light_yellow"))
        else:
            print(colored("No stocks to backtest.", "red"))
        return self.fileDir["backtestResultsStrategyUid"], self.combinePnlCsv()

    def backtest(self, stockName, startDate, endDate):
        startTimeEpoch = startDate.timestamp()
        endTimeEpoch = endDate.timestamp()
        stockAlgoLogic = equityOverNightAlgoLogic(stockName, self.fileDir)
        logger = setup_logger(stockName, f"{self.fileDir['backtestResultsStrategyLogs']}/{stockName}.log")
        logger.propagate = False

        def process_stock(stock, startTimeEpoch, endTimeEpoch, df_dict):
            df = getEquityBacktestData(stock, startTimeEpoch - (86400 * 500), endTimeEpoch, "D")

            if df is not None:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df["rsi"] = talib.RSI(df["c"], timeperiod=14)
                df['ema9'] = talib.EMA(df['c'], timeperiod=9)
                df['prev_ema'] = df['ema9'].shift(1)
                df.dropna(inplace=True)
                df.index = df.index + 33300
                df = df[df.index > startTimeEpoch]
                df_dict[stock] = df
                df.to_csv(f"{self.fileDir['backtestResultsCandleData']}{stock}_df.csv")
                print(f"Finished processing {stock}")

        def process_stocks_in_parallel(stocks, startTimeEpoch, endTimeEpoch):
            df_dict = {}
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = {executor.submit(process_stock, stock, startTimeEpoch, endTimeEpoch, df_dict): stock for stock in stocks}
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            return df_dict
        stocks = ['OFSS', 'USHAMART', 'ELGIEQUIP', 'CENTURYTEX', 'DCMSHRIRAM', 'TRIVENI', 'PRAJIND', 'JMFINANCIL', 'CHOLAFIN', 'SIEMENS', 'SOBHA', 'DIXON', 'KEC', 'KEI', 'BALRAMCHIN', 'GODREJIND', 'BLUEDART', 'IEX', 'GODREJPROP', 'TIINDIA', 'HDFCLIFE', 'BOSCHLTD', 'KNRCON', 'DIVISLAB', 'GRSE', 'APARINDS', 'JKPAPER', 'ESCORTS', 'GUJGASLTD', 'KPRMILL', 'JUSTDIAL', 'BSOFT', 'TIMKEN', 'EIDPARRY', 'MFSL', 'VOLTAS', 'FSL', 'BALAMINES', 'TITAN', 'PFC', 'PRESTIGE', 'BHEL', 'DEEPAKNTR', 'COCHINSHIP', 'ICICIPRULI', 'LINDEINDIA', 'RCF', 'MINDACORP', 'ABCAPITAL', 'SCHAEFFLER', 'SOLARINDS', 'M&M', 'SUNDRMFAST', 'OIL', 'ZENSARTECH', 'ASTRAZEN', 'LT', 'ABB', 'IPCALAB', 'HAL', 'MCX', 'ENDURANCE', 'MPHASIS', 'PEL', 'GMRINFRA', 'CARBORUNIV', 'NIACL', 'CHOLAHLDNG', 'AARTIIND', 'GPIL', 'GLENMARK', 'CHAMBLFERT', 'QUESS', 'INTELLECT','BLS', 'UPL', '3MINDIA', 'DLF', 'LALPATHLAB', 'TATAELXSI', 'JINDALSTEL', 'VGUARD', 'CERA', 'MRPL', 'NETWORK18', 'KSB', 'JSWENERGY', 'BSE', 'BRIGADE', 'BIRLACORPN', 'GLAXO', 'SRF', 'IGL', 'COROMANDEL', 'M&MFIN', 'ACE', 'VBL', 'TECHM', 'CREDITACC', 'CCL', 'BEL', 'WHIRLPOOL', 'NAUKRI', 'BAJFINANCE', 'INDUSINDBK', 'VAIBHAVGBL', 'WIPRO', 'ULTRACEMCO', 'GRINDWELL', 'HINDALCO', 'MANAPPURAM', 'MGL', 'CUMMINSIND', 'RECLTD', 'RKFORGE', 'HFCL', 'JINDALSAW', 'BAYERCROP', 'TEJASNET', 'CANFINHOME', 'IBULHSGFIN', 'GPPL', 'LAURUSLABS', 'NMDC', 'CYIENT', 'GSFC', 'WELCORP', 'GILLETTE', 'NESTLEIND', 'TCS', 'RAMCOCEM', 'MAHLIFE', 'TVSMOTOR', 'ALKYLAMINE', 'PERSISTENT', 'PETRONET', 'GRAPHITE', 'MUTHOOTFIN', 'EXIDEIND', 'BPCL', 'HUDCO', 'HDFCBANK', 'CRISIL', 'GICRE', 'TATAINVEST', 'BAJAJFINSV', 'FACT', 'RAJESHEXPO', 'ECLERX', 'AUROPHARMA', 'GESHIP', 'APOLLOHOSP', 'ASTRAL', 'ACC', 'FORTIS', 'KOTAKBANK', 'SPARC', 'INDHOTEL', 'GSPL', 'LICHSGFIN', 'NATIONALUM', 'PHOENIXLTD', 'HAVELLS', 'CHENNPETRO', 'BHARATFORG', 'ADANIPORTS', 'JKLAKSHMI', 'AJANTPHARM', 'CDSL', 'INFY', 'PAGEIND', 'ICICIGI', 'GNFC', 'OBEROIRLTY', 'LTTS', 'SWANENERGY', 'CROMPTON', 'ASTERDM', 'PNBHOUSING', 'ITI', 'DMART', 'MAHSEAMLES', 'INDIANB', 'SYNGENE', 'RELIANCE', 'TATAPOWER', 'HEROMOTOCO', 'AUBANK', 'BEML', 'NATCOPHARM', 'JKCEMENT', 'GAEL', 'ATUL', 'ABBOTINDIA', 'REDINGTON', 'BERGEPAINT', 'RADICO', 'SBIN', 'IOC', 'BANKINDIA', 'BDL', 'HINDCOPPER', 'KRBL', 'MASTEK', 'HBLPOWER', 'HONAUT', 'CGPOWER', 'DRREDDY', 'PIIND', 'HCLTECH', 'JBCHEPHARM', 'ASIANPAINT', 'SUNPHARMA', 'GODFRYPHLP', 'CESC', 'LUPIN', 'APOLLOTYRE', 'INDIACEM', 'BAJAJ-AUTO', 'HINDPETRO', 'ITC', 'ERIS', 'PGHH', 'PNCINFRA', 'AMBER', 'ASAHIINDIA', 'ADANIENT', 'JSWSTEEL', 'VEDL', 'KANSAINER', 'GAIL', 'CGCL', 'BLUESTARCO', 'JSL', 'MRF', 'RATNAMANI', 'KARURVYSYA', 'BATAINDIA', 'MHRIL', 'GMMPFAUDLR', 'GRASIM', 'AMBUJACEM', 'POLYMED', 'BALKRISIND', 'TRITURBINE', 'CEATLTD', 'SUZLON', 'DEEPAKFERT', 'ISEC', 'CIPLA', 'TRENT', 'PIDILITIND', 'AIAENG', 'FDC', 'TATASTEEL', 'CUB', 'HSCL', 'CONCOR', 'ALLCARGO', 'BIOCON', 'ALKEM', 'TATAMOTORS', 'COLPAL', 'IDFCFIRSTB', 'MARUTI', 'VTL', 'RITES', 'BAJAJHLDNG', 'ONGC', 'FINCABLES', 'BHARTIARTL', 'AXISBANK', 'PRSMJOHNSN', 'RBLBANK', 'IDEA', 'J&KBANK', 'CENTURYPLY', 'ASHOKLEY', 'SHREECEM', 'JUBLFOOD','HDFCAMC', 'INDIGO', 'BANKBARODA', 'UBL', 'NTPC', 'VIPIND', 'GODREJCP', 'SAIL', 'POWERGRID', 'SJVN', 'IDFC', 'APLLTD', 'MMTC', 'HEG', 'TATACHEM', 'TV18BRDCST', 'TATAMTRDVR', 'SAREGAMA', 'YESBANK', 'CASTROLIND', 'GMDCLTD', 'SKFINDIA', 'UCOBANK', 'EIHOTEL', 'COALINDIA', 'ABFRL', 'MOTILALOFS', 'SONATSOFTW', 'ICICIBANK', 'IOB', 'LEMONTREE', 'CANBK', 'TATACONSUM', 'AVANTIFEED', 'SUNDARMFIN', 'FINPIPE', 'BANDHANBNK','BRITANNIA', 'MAHABANK', 'TORNTPHARM', 'IRCON', 'PNB', 'JBMA', 'UNIONBANK', 'THERMAX', 'GRANULES', 'NHPC', 'RAYMOND', 'FINEORG', 'JYOTHYLAB', 'SUNTECK', 'ENGINERSIN', 'FEDERALBNK', 'NCC', 'SUPREMEIND', 'IDBI', 'ADANIGREEN', 'IRB', 'EICHERMOT', 'ADANIPOWER', 'SBILIFE', 'INOXWIND', 'TTML', 'TATACOMM', 'ZEEL', 'NBCC', 'TRIDENT', 'VARROC', 'TORNTPOWER', 'KAJARIACER', 'HINDUNILVR', 'NLCINDIA', 'SCHNEIDER', 'DABUR', 'BBTC', 'ELECON', 'OLECTRA', 'NH', 'HINDZINC', 'EMAMILTD', 'TANLA', 'APLAPOLLO', 'SUNTV', 'AAVAS', 'MARICO', 'CAPLIPOINT']

        df_dict = process_stocks_in_parallel(stocks, startTimeEpoch, endTimeEpoch)

        amountPerTrade = 100000
        lastIndexTimeData = None
        ProfitAmount = 0
        LossAmount = 0
        TotalTradeCanCome = 100

        for timeData in df_dict['ADANIENT'].index:
            for stock in stocks:
                stockAlgoLogic.timeData = timeData
                stockAlgoLogic.humanTime = datetime.fromtimestamp(timeData)
                print(stock, stockAlgoLogic.humanTime)
                stock_openPnl = stockAlgoLogic.openPnl[stockAlgoLogic.openPnl['Symbol'] == stock]

                if not stock_openPnl.empty:
                    for index, row in stock_openPnl.iterrows():
                        try:
                            stockAlgoLogic.openPnl.at[index, 'CurrentPrice'] = df_dict[stock].at[lastIndexTimeData, "c"]
                        except Exception as e:
                            print(f"Error fetching historical data for {row['Symbol']}")
                stockAlgoLogic.pnlCalculator()

                for index, row in stock_openPnl.iterrows():
                    if lastIndexTimeData in df_dict[stock].index:
                        if index in stock_openPnl.index:

                            if df_dict[stock].at[lastIndexTimeData, "rsi"] < 60 and df_dict[stock].at[lastIndexTimeData, "c"] > row['EntryPrice'] and (df_dict[stock].at[lastIndexTimeData, "prev_ema"] > df_dict[stock].at[lastIndexTimeData, "ema9"]):
                                exitType = "RsiTargetHit"
                                pnll = (df_dict[stock].at[lastIndexTimeData, "c"] - row['EntryPrice']) * row['Quantity']
                                stockAlgoLogic.exitOrder(index, exitType, df_dict[stock].at[lastIndexTimeData, "c"])
                                ProfitAmount = ProfitAmount + pnll
                                nowTotalTrades = len(stockAlgoLogic.openPnl)
                                logger.info(f"{nowTotalTrades}, TotalTradeCanCome:- {TotalTradeCanCome},RsiTargetHit- Datetime: {stockAlgoLogic.humanTime}, Stock: {stock}, pnll:{pnll},ProfitAmount:{ProfitAmount}, exitPrice: {df_dict[stock].at[lastIndexTimeData, 'c']}")

                            elif df_dict[stock].at[lastIndexTimeData, "rsi"] < 30:
                                exitType = "stopLoss"
                                pnll = (row['EntryPrice'] - df_dict[stock].at[lastIndexTimeData, "c"]) * row['Quantity']
                                LossAmount = LossAmount + pnll
                                stockAlgoLogic.exitOrder(index, exitType, df_dict[stock].at[lastIndexTimeData, "c"])
                                nowTotalTrades = len(stockAlgoLogic.openPnl)
                                logger.info(f"{nowTotalTrades}, TotalTradeCanCome:- {TotalTradeCanCome},stopLoss- Datetime: {stockAlgoLogic.humanTime}, Stock: {stock}, pnll: {pnll},LossAmount: {LossAmount}, exitPrice: {df_dict[stock].at[lastIndexTimeData, 'c']}")

                if ProfitAmount > 100000:
                    ProfitAmount = ProfitAmount - 100000
                    TotalTradeCanCome = TotalTradeCanCome + 1
                    logger.info(f"{nowTotalTrades}, TotalTradeCanCome:- {TotalTradeCanCome}, Datetime: {stockAlgoLogic.humanTime},ProfitAmount:-{ProfitAmount}")

                if LossAmount > 100000:
                    LossAmount = LossAmount - 100000
                    TotalTradeCanCome = TotalTradeCanCome - 1
                    logger.info(f"{nowTotalTrades},TotalTradeCanCome:-{TotalTradeCanCome}, Datetime: {stockAlgoLogic.humanTime},lossIncrease:-{LossAmount}")

                if lastIndexTimeData in df_dict[stock].index:
                    nowTotalTrades = len(stockAlgoLogic.openPnl)
                    if (df_dict[stock].at[lastIndexTimeData, "rsi"] > 60) and (df_dict[stock].at[lastIndexTimeData, "prev_ema"] < df_dict[stock].at[lastIndexTimeData, "ema9"]) and (stock_openPnl.empty) and (nowTotalTrades < TotalTradeCanCome):
                        entry_price = df_dict[stock].at[lastIndexTimeData, "c"]
                        nowTotalTrades = nowTotalTrades + 1
                        stockAlgoLogic.entryOrder(entry_price, stock, (amountPerTrade // entry_price), "BUY")
                        logger.info(f"{nowTotalTrades}, TotalTradeCanCome:-{TotalTradeCanCome}, Entry-{stock}- Datetime: {stockAlgoLogic.humanTime}, entryPrice: {df_dict[stock].at[lastIndexTimeData, 'c']}")

                lastIndexTimeData = timeData
                stockAlgoLogic.pnlCalculator()

        for index, row in stockAlgoLogic.openPnl.iterrows():
            if lastIndexTimeData in df_dict[stock].index:
                if index in stockAlgoLogic.openPnl.index:
                    exitType = "TimeUp"
                    stockAlgoLogic.exitOrder(index, exitType, row['CurrentPrice'])

if __name__ == "__main__":
    startNow = datetime.now()

    devName = "AK"
    strategyName = "R_60_60_30"
    version = "v1"

    startDate = datetime(2019, 1, 1, 9, 15)
    endDate = datetime(2024, 12, 31, 15, 30)

    portfolio = 'combinedList'

    algoLogicObj = R_60_60_30(devName, strategyName, version)
    fileDir, closedPnl = algoLogicObj.runBacktest(portfolio, startDate, endDate)

    dailyReport = calculate_mtm(closedPnl, fileDir, timeFrame="15T", mtm=False, equityMarket=True)

    endNow = datetime.now()
    print(f"Done. Ended in {endNow-startNow}")