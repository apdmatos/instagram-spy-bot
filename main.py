from spyBot import SpyBot
import logging
from telegramApi import TelegramConfig

def main():
    import argparse
    parser = argparse.ArgumentParser(description='checks the following list of a person and saves it')
    parser.add_argument('username', metavar='username', nargs=1,
                        help='instagram username')
    parser.add_argument('password', metavar='password', nargs=1,
                        help='instagram password')
    parser.add_argument('spy_username', metavar='spy_username', nargs=1,
                        help='instagram username to spy')
    parser.add_argument('--telegram-token', metavar='telegram_token',
                        help='The telegram token to send the message')
    parser.add_argument('--telegram-chat-id', metavar='telegram_chat_id',
                        help='The telegram chat id to send the message to')
    parser.add_argument('--pooling-time', metavar='pooling_time', default=0,
                        help='The pooling interval to get users from instagram')
    parser.add_argument('-debug', '--debug', help="output more detailed information about the bot", action='store_true')
    parser.add_argument('-telChatId', '--tel-chat-id', help="telegram chat id where to send update messages", action='store_true')
    parser.add_argument('-telToken', '--tel-token', help="telegram bot token that will send the message", action='store_true')
    args = parser.parse_args()

    username = args.username[0]
    password = args.password[0]
    spy_username = args.spy_username[0]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    telegram_config = None
    if args.telegram_chat_id and args.telegram_token:
        telegram_config = TelegramConfig(args.telegram_token, args.telegram_chat_id)

    bot = SpyBot(username, password, spy_username, telegram_config, int(args.pooling_time))
    bot.start()


if __name__ == "__main__":
    main()
