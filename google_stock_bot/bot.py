import logging
import time

import schedule
import telegram
import yfinance as yf
from telegram.ext import Updater, CommandHandler

from utils import get_secrets, clean_ticker

# set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)


def get_stock_price(ticker):
    ticker_data = yf.Ticker(ticker)
    return ticker_data.get_info()['currentPrice']  # open price


secrets = get_secrets()

BOT_TOKEN = secrets['telegram_api_token']
CHAT_ID = secrets['chat_id']  # Petr Lavrov

TICKER = "GOOG"
# JOB_TIME = "23:28"
JOB_TIME = "18:30"


class StockPriceBot:
    def __init__(self, token, chat_id):
        self.bot = telegram.Bot(token=token)
        self.chat_id = chat_id
        self.updater = telegram.ext.Updater(bot=self.bot)

        # setup telegram bot
        self.configure_commands()

    # 1) Send price
    def send_stock_price(self, chat_id, ticker):
        price = get_stock_price(ticker)
        self.bot.send_message(chat_id=chat_id, text=f'Price of ${ticker} stock: {price}')

    def schedule_job(self, job_time, ticker):  # simplest scheduler possible:
        schedule.every().day.at(job_time).do(
            self.send_stock_price, chat_id=self.chat_id, ticker=ticker)

    # 3) command / price
    def configure_commands(self):
        # start command
        def start(update, context):
            # get the chat id of the user
            chat_id = update.effective_chat.id
            logger.info(f"/start command by user {update.effective_chat.username} chat_id {update.effective_chat.id}")
            # check if the chat id matches the context
            if str(chat_id) == (self.chat_id):
                # respond with a message indicating that the bot is alive
                update.message.reply_text(
                    f"I am alive! And you're my precious petr_lavrov - username: {update.effective_chat.username}, chatid {chat_id}")
            else:
                # respond with a message indicating that the chat id does not match the context
                update.message.reply_text(
                    f"Hi {update.effective_chat.username}! You're an unauthorised user! \n"
                    f"This bot is designed to send daily or scheduled updates about stock prices. \n"
                    f"Currently, I am hardcoded to only work for a specific user and do not save users. "
                    f"You can nudge @petr_lavrov if you want me to implement this :) \n"
                    f"However, you can use the /price command to get the price of a stock")

        # add a command handler for the start command
        self.updater.dispatcher.add_handler(CommandHandler('start', start))

        # get price command
        def get_price(update, context):
            chat_id = update.effective_chat.id
            # get the ticker from the command
            ticker = context.args[0]
            ticker = clean_ticker(ticker)

            # send the stock price for the ticker
            self.send_stock_price(chat_id, ticker)

        # add a command handler for the get_price command
        self.updater.dispatcher.add_handler(CommandHandler('price', get_price))


def main():
    b = StockPriceBot(token=BOT_TOKEN, chat_id=CHAT_ID)
    b.schedule_job(job_time=JOB_TIME, ticker=TICKER)
    b.updater.start_polling()

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
