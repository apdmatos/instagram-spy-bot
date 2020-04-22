from spyBot import SpyBot
import logging


def main():
    import argparse
    parser = argparse.ArgumentParser(description='checks the following list of a person and saves it')
    parser.add_argument('username', metavar='username', nargs=1,
                        help='instagram username')
    parser.add_argument('password', metavar='password', nargs=1,
                        help='instagram password')
    parser.add_argument('spy_username', metavar='spy_username', nargs=1,
                        help='instagram username to spy')
    parser.add_argument('-debug', '--debug', help="output more detailed information about the bot", action='store_true')
    args = parser.parse_args()

    username = args.username[0]
    password = args.password[0]
    spy_username = args.spy_username[0]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s')
    logger = logging.getLogger('instagram_private_api')
    logger.setLevel(logging.WARNING)
    if args.debug:
        logger.setLevel(logging.DEBUG)

    bot = SpyBot(username, password, spy_username)
    bot.start()


if __name__ == "__main__":
    main()
