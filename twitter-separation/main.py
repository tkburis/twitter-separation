import twitter
import os
import settings  # run settings for env code
from error_handling import ErrorHandler
from algorithms.bidirectional_bfs import BidirectionalBFS
from algorithms.naive_bfs import NaiveBFS

"""Make sure API keys are in a file called .env in this directory and run this script"""
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")


def api_setup():
    _api = twitter.Api(consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
                       access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True)

    if _api.VerifyCredentials():
        print('Authentication passed.')

    return _api


def main():
    api = api_setup()

    error_handler = ErrorHandler(api=api)
    error_handler.api_test()

    print("Input Twitter IDs. These can be found from twitterid.com")
    start_user = int(input("Find a path from: "))
    target_user = int(input("To: "))
    method = int(input("Choose a search method. NaiveBFS (input 1) is better for low number of followings "
                       "from the start user, whereas BidirectionalBFS (input 2) is better for similar number "
                       "of followings and followers. "))
    if method == 1:
        naive_obj = NaiveBFS(api)
        _path = naive_obj.run_search(origin_user=start_user, target_user=target_user)
    elif method == 2:
        bidirectional_obj = BidirectionalBFS(api, search_radius=1000, auto_next=True)
        _path = bidirectional_obj.run_search(origin_user=start_user, target_user=target_user)


if __name__ == '__main__':
    main()
