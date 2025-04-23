cd "/root/akashEquityBacktestAlgos/annualWeeklyDaily/Horizontal50"
/usr/local/bin/pm2 start "Vertical50.py" --interpreter="/root/akashEquityBacktestAlgos/myenv/bin/python3" --name="Vertical100-400-1" --no-autorestart --time
# cd "/root/AkashMockAlgo/weekly_500_stocks/Horizontal50"
# /usr/local/bin/pm2 start "Horizontal50.py" --interpreter="/root/akashEquityBacktestAlgos/myenv/bin/python3" --name="Horizontal01-1" --no-autorestart --time