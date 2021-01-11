from collections import defaultdict
from queue import Queue
from cacher import Cacher
from error_handling import ErrorHandler
import twitter

# print('Imported bidirectional_bfs.py')


class BidirectionalBFS:
    def __init__(self, api, search_radius=1000, auto_next=False):
        self.api = api
        self.search_radius = search_radius
        self.auto_next = auto_next
        self.cache = Cacher('cache2.txt')

    def origin_following_bfs(self, start_user):
        """
        If the origin follows user A and B, and user B follows C, a graph can be drown as such:
        Origin ---> A
               ---> B ----> C
        Every yield expands the radius of the search by 1, until it hits search_radius
        :param start_user: The user from which to start the search
        :yield: All paths possible up to the current radius, in format set({user_id: path_to_that_user_id}, etc.)
        """
        api = self.api
        error_handler = ErrorHandler(api=api)
        queue = Queue()
        queue.put(start_user)
        visited = {start_user}
        path_to = defaultdict(lambda: [start_user])
        _ = path_to[start_user]

        for current_radius in range(self.search_radius):
            if queue.qsize() == 0:
                print('Queue empty. Ending origin BFS.')
                return
            current_user = queue.get()

            if self.cache.read_from_cache(user_id=current_user) is None:  # current_user does not yet exist in cache
                current_user_followings = api.GetFriendIDs(user_id=current_user)
                current_user_screen_name = api.GetUser(user_id=current_user).name
                self.cache.append_to_cache(user_id=current_user, screen_name=current_user_screen_name,
                                           following_ids=current_user_followings)
                print(f"Origin BFS: requested {current_user_screen_name}'s screen name and followings from API. "
                      f"Commencing search.")
            else:
                cached_data = self.cache.read_from_cache(user_id=current_user)
                current_user_screen_name = cached_data['screen_name']  # if user_id exists as a key in cache,
                # screen_name will always exist as well
                if not cached_data['following']:  # i.e. following list does not yet exist in cache
                    current_user_followings = api.GetFriendIDs(user_id=current_user)
                    self.cache.append_to_cache(user_id=current_user, screen_name=current_user_screen_name,
                                               following_ids=current_user_followings)
                    print(f"Origin BFS: retrieved {current_user_screen_name}'s screen name from cache. "
                          f"Requested followings from API. Commencing search.")
                else:
                    current_user_followings = cached_data['following']
                    print(f"Origin BFS: retrieved {current_user_screen_name}'s screen name AND followings from cache. "
                          f"Today is a good day. Commencing search.")

            num_followings = len(current_user_followings)
            for num, following in enumerate(current_user_followings):
                if following not in visited:
                    try:
                        if self.cache.read_from_cache(
                                user_id=following) is None:  # this user does not yet exist in cache
                            following_screen_name = api.GetUser(user_id=following).name
                            self.cache.append_to_cache(user_id=following, screen_name=following_screen_name)
                            print(f"Origin BFS: {current_user_screen_name} follows {following_screen_name}. "
                                  f"Requested {following_screen_name}'s screen name from API and cached.")
                        else:
                            following_screen_name = self.cache.read_from_cache(user_id=following)['screen_name']
                            print(f"Origin BFS: {current_user_screen_name} follows {following_screen_name}. "
                                  f"Retrieved {following_screen_name}'s screen name from cache.")

                        visited.add(following)
                        queue.put(following)
                        current_path = list(path_to[current_user])
                        current_path.extend([following])
                        path_to[following] = current_path
                    except twitter.error.TwitterError as ex:
                        error_handler.handle(ex, user_id=following)
                else:
                    print('User already visited. Skipping...')
                print(num + 1, '/', num_followings)
            yield path_to

    def target_follower_bfs(self, start_user):
        """
        Same as origin_follower_bfs, but the other way round.
        If user A and user B follows target, and user C follows user B:
        C ---> B ---> target
               A --->
        :param start_user: This refers to the target user. The user from which to start the search.
        :yield: All paths possible up to the current radius, in format set({user_id: path_to_that_user_id}, etc.)
        """
        api = self.api
        error_handler = ErrorHandler(api=api)
        queue = Queue()
        queue.put(start_user)
        visited = {start_user}
        path_to = defaultdict(lambda: [start_user])
        _ = path_to[start_user]

        for current_radius in range(self.search_radius):
            if queue.qsize() == 0:
                print('Queue empty. Ending target BFS.')
                return
            current_user = queue.get()

            if self.cache.read_from_cache(user_id=current_user) is None:  # current_user does not yet exist in cache
                current_user_followers = api.GetFollowerIDs(user_id=current_user)
                current_user_screen_name = api.GetUser(user_id=current_user).name
                self.cache.append_to_cache(user_id=current_user, screen_name=current_user_screen_name,
                                           follower_ids=current_user_followers)
                print(f"Target BFS: requested {current_user_screen_name}'s screen name and followers from API. "
                      f"Commencing search.")
            else:
                cached_data = self.cache.read_from_cache(user_id=current_user)
                current_user_screen_name = cached_data['screen_name']  # if user_id exists as a key in cache,
                # screen_name will always exist as well
                if not cached_data['followers']:  # i.e. follower list does not yet exist in cache
                    current_user_followers = api.GetFollowerIDs(user_id=current_user)
                    self.cache.append_to_cache(user_id=current_user, screen_name=current_user_screen_name,
                                               follower_ids=current_user_followers)
                    print(f"Target BFS: retrieved {current_user_screen_name}'s screen name from cache. "
                          f"Requested followers from API. Commencing search.")
                else:
                    current_user_followers = cached_data['followers']
                    print(f"Target BFS: retrieved {current_user_screen_name}'s screen name AND followers from cache. "
                          f"Today is a good day. Commencing search.")

            num_followers = len(current_user_followers)
            for num, follower in enumerate(current_user_followers):
                if follower not in visited:
                    try:
                        if self.cache.read_from_cache(
                                user_id=follower) is None:  # this user does not yet exist in cache
                            follower_screen_name = api.GetUser(user_id=follower).name
                            self.cache.append_to_cache(user_id=follower, screen_name=follower_screen_name)
                            print(f"Target BFS: {current_user_screen_name} is followed by {follower_screen_name}. "
                                  f"Requested {follower_screen_name}'s screen name from API and cached.")
                        else:
                            follower_screen_name = self.cache.read_from_cache(user_id=follower)['screen_name']
                            print(f"Target BFS: {current_user_screen_name} is followed by {follower_screen_name}. "
                                  f"Retrieved {follower_screen_name}'s screen name from cache.")

                        visited.add(follower)
                        queue.put(follower)
                        current_path = list(path_to[current_user])
                        current_path.extend([follower])
                        path_to[follower] = current_path
                    except twitter.error.TwitterError as ex:
                        error_handler.handle(ex, user_id=follower)
                else:
                    print('User already visited. Skipping...')
                print(num + 1, '/', num_followers)
            yield path_to

    def find_middle_users(self, paths_left, paths_right):
        """
        Find intersection between two paths, i.e. the 'middle users'
        :param paths_left:
        :param paths_right:
        :return: List of middle users
        """
        middle_users = paths_left.keys() & paths_right.keys()
        return middle_users

    def reduce_path(self, paths_left, paths_right, middle_user):
        """
        Reduce path from path from the left to path to the right, given the middle element
        :param paths_left:
        :param paths_right:
        :param middle_user:
        :return: Reduced paths
        """
        possible_paths = []

        for middle_user in middle_user:
            new_path = paths_left[middle_user]
            new_path.extend(list(reversed(paths_right[middle_user]))[1:])
            possible_paths.append(new_path)
        return possible_paths

    def display_paths(self, paths):
        """
        Simple UI method that prints the path out in English
        :param paths: list of list of paths. will print them all.
        """
        for path in paths:
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
        Driver code for the whole class.
        :param origin_user: The user to find a connection from
        :param target_user: The user to find a connection to
        :return: Possible paths in a list of lists of Twitter IDs, in X following Y order
        """
        for idx, (paths_left, paths_right) in enumerate(zip(self.origin_following_bfs(start_user=origin_user),
                                                            self.target_follower_bfs(start_user=target_user))):
            print(f"{len(paths_left)} total path(s) from origin. {len(paths_right)} total path(s) from target.")
            middle_users = self.find_middle_users(paths_left, paths_right)
            if len(middle_users) != 0:
                possible_paths = self.reduce_path(paths_left, paths_right, middle_users)
                print(f"{len(possible_paths)} possible path(s) found:")
                self.display_paths(possible_paths)
            else:
                print("No possible paths found.")
            if idx == self.search_radius - 1:
                input("Search concluded with set search_radius. Press enter to close.")
                return possible_paths
            if not self.auto_next:
                input("Press enter to go to next radius")
