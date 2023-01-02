import os


def get_secrets():
    # Load the secrets from a file
    secrets = {}
    file_path = os.path.join(os.path.dirname(__file__), 'secrets.txt')
    with open(file_path, "r") as f:
        for line in f:
            key, value = line.strip().split(":", 1)
            secrets[key] = value
    return secrets


def get_user_chat_id(bot_token):
    """
    Retrieve chat_id of a most recent user of a bot
    :return: chat_id
    """

    import telegram

    # create a Telegram bot using your API token
    bot = telegram.Bot(token=bot_token)

    # get the list of updates
    updates = bot.getUpdates()

    # print the chat id of the first update
    chat_id = updates[-1].message.chat.id
    return chat_id


def clean_ticker(ticker):
    ticker = ticker.strip('$')
    return ticker
