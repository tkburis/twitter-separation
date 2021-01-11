from cacher import Cacher
import twitter
from time import sleep
import sys

# print('Imported error_handling.py')


class ErrorHandler:
    def __init__(self, api):
        self.api = api
        self.cache = Cacher()

    def api_test(self):
        """
        This instructs user to rerun program in a few minutes if rate limit has exceeded.
        If rate limit has exceeded before running program, sleep_on_rate_limit won't work properly.
        """
        try:
            _ = self.api.GetUser(user_id=813286)
        except twitter.error.TwitterError as ex:
            if ex.message[0]['code'] == 88:
                sys.exit('Rate limit for API calls has exceeded. Rerun program in a few minutes.')
            else:
                raise ex

    def handle_50(self, arg_dict):
        """
        Error 50 means that the user is not found.
        :param arg_dict: All the arguments the error handling will need. Here, we only need user_id.
        """
        self.cache.remove_all_occurrences(user_id=arg_dict['user_id'])
        print(f"Requested user not found. Removed all occurrences of {arg_dict['user_id']} in cache")

    def handle_63(self, arg_dict):
        """
        Error 63 means that the requested user has been suspended. We simply skip the user.
        :param arg_dict: All the arguments the error handling will need. Here, we only need user_id.
        """
        self.cache.remove_all_occurrences(user_id=arg_dict['user_id'])
        print(f"Requested user suspended. Removed all occurrences of {arg_dict['user_id']} in cache")

    def handle_88(self):
        """
        Error 88 means that the Twitter API rate limit has been exceeded. We keep attempting a connection until it
        resolves. This bit of code should not be executed, as we specified sleep_on_rate_limit in the API constructor
        and tested the connection before hand with self.api_test().
        """
        while True:
            try:
                _ = self.api.GetUser(user_id=813286)
            except twitter.error.TwitterError as ex:
                if ex.message[0]['code'] == 88:
                    print('Waiting for rate limit to reset')
                    sleep(60)
                    continue
                else:
                    raise ex
            else:
                break

    def handle(self, ex, **kwargs):
        """
        This acts as a switchboard for each handling method. Note how all the error handlers' names follow the style
        self.handle_{code}().
        :param ex: The raised exception. We need it to identify the error code raised.
        :param kwargs: The specific arguments we need in order to fix the error.
        """
        code = ex.message[0]['code']
        try:
            _ = getattr(self, 'handle_' + str(code))(kwargs)
        except AttributeError:
            print('No handler has been written for this error. Whoops.')
            raise ex
