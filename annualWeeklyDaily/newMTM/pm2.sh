cd "/root/akashEquityBacktestAlgos/annualWeeklyDaily/newMTM"
/usr/local/bin/pm2 start "mtm.py" --interpreter="/root/akashEquityBacktestAlgos/myenv/bin/python3" --name="mtm-1" --no-autorestart --time