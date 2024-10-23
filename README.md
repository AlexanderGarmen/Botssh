Installing a bot on a VDS server

# 1. Update the system
sudo apt update

# 2. Install Python 3 and pip
sudo apt install python3 python3-pip -y

# 3. Install the required libraries for your bot
pip3 install python-telegram-bot psutil nest_asyncio

# 4. Navigate to the directory where your bot is located (if needed)
# cd /path/to/your/bot/directory

# 5. Run the bot
python3 bot.py
