from instagram_private_api import Client
from instagram_private_api_extensions import pagination
from persistance import Persistence, Following
import logging
import uuid

DAY_MILLIS = 24 * 60 * 60
logger = logging.getLogger(__name__)


class SpyBot:
    def __init__(self, username, password, spy_username):
        self._username = username
        self._password = password
        self._spy_username = spy_username
        self._login()
        self.persistence = Persistence(spy_username)

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
                                     args={'user_id': user_id, 'rank_token': rank_token}, wait=10)
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

    def start(self):

        iteration = self.persistence.get_current_iteration()
        new_iteration = iteration + 1
        user_id = self._find_user_id_to_spy()

        if user_id is None:
            logger.error("user {} not found".format(self._spy_username))
        else:
            self._download_all_following(user_id, new_iteration)

        started = self.persistence.get_started_following(new_iteration, iteration)
        logger.info("--------------------------------------")
        logger.info("started following {} users".format(len(started)))
        self.printUsers(started)

        stopped = self.persistence.get_stopped_following(new_iteration, iteration)
        logger.info("--------------------------------------")
        logger.info("stopped following {} users".format(len(stopped)))
        self.printUsers(stopped)

        logger.info("--------------------------------------")

        if len(started) == 0 and len(stopped):
            logger.info("Nothing has happened. deleting downloaded users")
            self.persistence.delete_all_iteration(new_iteration)

        logger.info('Bye!')
