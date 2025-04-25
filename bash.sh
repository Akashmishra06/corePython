cd "/root/equityResearch/vwap"
/usr/local/bin/pm2 start "main.py" --interpreter="/root/equityResearch/myenv/bin/python3" --name="main-200-1" --no-autorestart --time