from collections import defaultdict
from queue import Queue
from cacher import Cacher
from error_handling import ErrorHandler
import twitter

# print('Imported naive_bfs.py')


class NaiveBFS:
    def __init__(self, api):
        self.api = api
        self.cache = Cacher('cache2.txt')

    def bfs(self, start_user, target_user):
        """
        Find shortest path from start_user to target_user, where a path is defined as:
        X --> Y when user X follows user Y.
        This is a horrible algorithm - don't use it unless you're willing to wait for around a week or longer
        if you know the degree of separation is >= 2
        :param start_user: The starting (origin) user
        :param target_user: The user you're trying to find a path to
        :return: A path from start_user to target_user
        """
        api = self.api
        error_handler = ErrorHandler(api=api)
        queue = Queue()
        queue.put(start_user)
        visited = {start_user}
        path_to = defaultdict(lambda: [start_user])

        while queue.not_empty:
            current_user = queue.get()
            if self.cache.read_from_cache(user_id=current_user) is None:  # current_user does not yet exist in cache
                current_user_followings = api.GetFriendIDs(user_id=current_user)
                current_user_screen_name = api.GetUser(user_id=current_user).name
                self.cache.append_to_cache(user_id=current_user, screen_name=current_user_screen_name,
                                           following_ids=current_user_followings)
                print(f"Naive BFS: requested {current_user_screen_name}'s screen name and followings from API. "
                      f"Commencing search.")
            else:
                cached_data = self.cache.read_from_cache(user_id=current_user)
                current_user_screen_name = cached_data['screen_name']  # if user_id exists as a key in cache,
                # screen_name will always exist as well
                if not cached_data['following']:  # i.e. following list does not yet exist in cache
                    current_user_followings = api.GetFriendIDs(user_id=current_user)
                    self.cache.append_to_cache(user_id=current_user, screen_name=current_user_screen_name,
                                               following_ids=current_user_followings)
                    print(f"Naive BFS: retrieved {current_user_screen_name}'s screen name from cache. "
                          f"Requested followings from API. Commencing search.")
                else:
                    current_user_followings = cached_data['following']
                    print(f"Naive BFS: retrieved {current_user_screen_name}'s screen name AND followings from cache. "
                          f"Today is a good day. Commencing search.")

            num_followings = len(current_user_followings)
            for num, following in enumerate(current_user_followings):
                if following not in visited:
                    try:
                        if self.cache.read_from_cache(
                                user_id=following) is None:  # this user does not yet exist in cache
                            following_screen_name = api.GetUser(user_id=following).name
                            self.cache.append_to_cache(user_id=following, screen_name=following_screen_name)
                            print(f"Naive BFS: {current_user_screen_name} follows {following_screen_name}. "
                                  f"Requested {following_screen_name}'s screen name from API and cached.")
                        else:
                            following_screen_name = self.cache.read_from_cache(user_id=following)['screen_name']
                            print(f"Naive BFS: {current_user_screen_name} follows {following_screen_name}. "
                                  f"Retrieved {following_screen_name}'s screen name from cache.")

                        visited.add(following)
                        queue.put(following)
                        current_path = list(path_to[current_user])
                        current_path.extend([following])
                        path_to[following] = current_path
                        if following == target_user:
                            print(f"Naive BFS: {following_screen_name} (target user) found! Stopping search.")
                            break
                    except twitter.error.TwitterError as ex:
                        error_handler.handle(ex, user_id=following)
                else:
                    print('User already visited. Skipping...')
                print(num + 1, '/', num_followings)
            else:
                continue
            break
        if path_to[target_user] != [start_user] or target_user == start_user:
            return path_to[target_user]
        else:
            return None

    def display_paths(self, path):
        """
        Prints out path in English
        :param path: List of users in path
        """
        for idx, user in enumerate(path):
            screen_name = self.cache.read_from_cache(user_id=user)['screen_name']
            if idx == 0:
                print(f'{screen_name} follows ', end='')
            elif idx == len(path) - 1:
                print(screen_name)
            else:
                print(f'{screen_name}, who follows ', end='')

    def run_search(self, origin_user, target_user):
        """
        Driver code to run search
        :param origin_user: User to start search from
        :param target_user: User to find path to
        :return: List of users in possible path from origin_user to target_user
        """
        found_path = self.bfs(start_user=origin_user, target_user=target_user)
        self.display_paths(path=found_path)
        return found_path
