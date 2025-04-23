# cd "/root/equityResearch/raviSir_ema9_rsi_equityStrategy/withoutEmaSlope/compoundingH50"
# /usr/local/bin/pm2 start "compoundingH50.py" --interpreter="/root/equityResearch/myenv/bin/python3" --name="without_slope_compoundingH50-1" --no-autorestart --time

# cd "/root/equityResearch/raviSir_ema9_rsi_equityStrategy/withoutEmaSlope/compoundingH100"
# /usr/local/bin/pm2 start "compoundingH100.py" --interpreter="/root/equityResearch/myenv/bin/python3" --name="without_slope_compoundingH100-1" --no-autorestart --time


cd "/root/equityResearch/raviSir_ema9_rsi_equityStrategy/withEmaSlope/compoundingH50"
/usr/local/bin/pm2 start "compoundingH50.py" --interpreter="/root/equityResearch/myenv/bin/python3" --name="with_slope_compoundingH50-1" --no-autorestart --time

cd "/root/equityResearch/raviSir_ema9_rsi_equityStrategy/withEmaSlope/compoundingH100"
/usr/local/bin/pm2 start "compoundingH100.py" --interpreter="/root/equityResearch/myenv/bin/python3" --name="with_slope_compoundingH100-1" --no-autorestart --time