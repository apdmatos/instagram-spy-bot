import requests
import logging

TELEGRAM_URL = "https://api.telegram.org/bot{}/sendMessage"
INSTAGRAM_URL = "https://instagram.com/{}"
logger = logging.getLogger(__name__)


class TelegramConfig:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id


class TelegramApi:
    def __init__(self, config):
        self._config = config

    def send_run_update(self, start_following, stopped_following):
        url = TELEGRAM_URL.format(self._config.token)
        text = self._create_message(start_following, stopped_following)

        try:
            r = requests.post(url, json={"chat_id": self._config.chat_id, "text": text})
            if r.status_code is not 200:
                logger.error("got error sending message to telegram {}".format(r.content))

        except Exception as e:
            logger.error("error sending new following list to telegram", e)

    def _create_message(self, start_following, stopped_following):
        return "" \
               "\nstarted following: " + str(len(start_following)) + "" \
               "\n" + self.print_users(start_following) + "" \
               "\n" \
               "\nstopped following: " + str(len(stopped_following)) + "" \
               "\n" + self.print_users(stopped_following) + "" \

    def print_users(self, users):
        text = ""
        for user in users:
            text += INSTAGRAM_URL.format(user) + "\n"
        return text
