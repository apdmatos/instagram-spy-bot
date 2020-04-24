from instagram_private_api import Client
from instagram_private_api_extensions import pagination
from persistance import Persistence, Following
import logging
import uuid
from telegramApi import TelegramApi
import time

logger = logging.getLogger(__name__)


class SpyBot:
    def __init__(self, username, password, spy_username, telegram_config=None, pooling_interval_hours=0):
        self._username = username
        self._password = password
        self._spy_username = spy_username
        self._login()
        self.persistence = Persistence(spy_username)
        self._pooling_interval_hours = pooling_interval_hours
        if telegram_config is not None:
            self.telegramApi = TelegramApi(telegram_config)

    def _login(self):
        logger.info('authenticating {}... it may take a while'.format(self._username))
        self.api = Client(
            auto_patch=True, authenticate=True,
            username=self._username, password=self._password)

        logger.info('successfully authenticated {}'.format(self._username))

    def _download_all_following(self, user_id, iteration):
        logger.info('downloading users {} is following'.format(self._spy_username))

        rank_token = self.api.generate_uuid()
        following = pagination.page(self.api.user_following,
                                     args={'user_id': user_id, 'rank_token': rank_token}, wait=20)
        count = 0
        it = iter(following)
        while True:
            try:
                results = next(it, None)

                if results is None:
                    break

                count += len(results['users'])
            except Exception as e:
                logger.error('error getting followers from instagram... cleaning up', e)
                self.persistence.delete_all_iteration(iteration)
                return False

            for user in results['users']:
                entity = Following(id=str(uuid.uuid4()), user_id=user['id'], username=user['username'], iteration=iteration)
                self.persistence.save_following(entity)

        logger.info('all following have been downloaded. Downloaded {} profiles'.format(count))
        return True

    def _find_user_id_to_spy(self):
        users = self.api.search_users(self._spy_username)
        user = users['users'][0]

        if user['username'] != self._spy_username:
            logger.error("username {} not found", self._spy_username)
            return None

        return user['pk']

    def printUsers(self, usernames):
        for username in usernames:
            logger.info(username)

    def _sendMessage(self, started_following, stopped_following):
        if self.telegramApi:
            logger.info("sending telegram notification")
            self.telegramApi.send_run_update(started_following, stopped_following)
        else:
            logger.info("skipping telegram notificaiton. bot is not configured")

    def start(self):
        while True:
            iteration = self.persistence.get_current_iteration()
            new_iteration = iteration + 1
            user_id = self._find_user_id_to_spy()

            if user_id is None:
                logger.error("user {} not found".format(self._spy_username))
                break
            else:
                downloaded = self._download_all_following(user_id, new_iteration)
                if downloaded:
                    started = self.persistence.get_started_following(new_iteration, iteration)
                    logger.info("--------------------------------------")
                    logger.info("started following {} users".format(len(started)))
                    self.printUsers(started)

                    stopped = self.persistence.get_stopped_following(new_iteration, iteration)
                    logger.info("--------------------------------------")
                    logger.info("stopped following {} users".format(len(stopped)))
                    self.printUsers(stopped)

                    logger.info("--------------------------------------")

                    self._sendMessage(started, stopped)

                    if len(started) == 0 and len(stopped) == 0:
                        logger.info("Nothing has happened. deleting downloaded users")
                        self.persistence.delete_all_iteration(new_iteration)

                    if self._pooling_interval_hours == 0:
                        break

            logger.info("sleeping for {} hours".format(self._pooling_interval_hours))
            time.sleep(self._pooling_interval_hours * 3600)

        logger.info('Bye!')
