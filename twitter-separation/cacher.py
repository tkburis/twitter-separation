import json
import os

# print('Imported cacher.py')


class Cacher:
    def __init__(self, cache_file_name='cache.txt'):
        """
        Makes cache file if does not exist already.
        :param cache_file_name: Constant of the name of the cache file
        """
        self.CACHE_FILE_NAME = cache_file_name
        if not os.path.exists(self.CACHE_FILE_NAME):
            with open(self.CACHE_FILE_NAME, 'w') as file:
                file.write('{}')
                file.close()

    def read_from_cache(self, user_id):
        """
        Returns screen name, following, followers, in dictionary-like format.
        :param user_id: Specifies which user to search for
        :return: Screen name, following, followers in dictionary-like format
        """
        with open(self.CACHE_FILE_NAME, 'r') as json_file:
            data = json.load(json_file)
            try:
                json_file.close()
                return data[str(user_id)]
            except KeyError:
                json_file.close()
                return None

    def append_to_cache(self, user_id, screen_name, following_ids=None, follower_ids=None):
        """
        Appends additional information to cache.
        :param user_id: Appends information of user with id 'user_id'; primary key
        :param screen_name: Screen name of user
        :param following_ids: IDs of users that are followed by the user
        :param follower_ids: IDs of users that follow the user
        """
        if follower_ids is None:
            follower_ids = []
        if following_ids is None:
            following_ids = []

        old_data = self.read_from_cache(user_id=user_id)
        if old_data is not None:
            following_ids = list(set(following_ids).union(set(old_data['following'])))
            follower_ids = list(set(following_ids).union(set(old_data['followers'])))
        to_append = {
            str(user_id):
                {
                    'screen_name': screen_name,
                    'following': following_ids,
                    'followers': follower_ids
                }
        }
        with open(self.CACHE_FILE_NAME, 'r+') as json_file:
            data = json.load(json_file)
            data.update(to_append)
            json_file.seek(0)
            json.dump(data, json_file)
            json_file.close()

    def remove_all_occurrences(self, user_id):
        """
        Removes all occurrences of a user from cache.
        :param user_id: Target user id
        """
        with open(self.CACHE_FILE_NAME, 'r+') as json_file:
            # print('yo')
            data = json.load(json_file)
            try:
                del data[str(user_id)]
            except KeyError:
                pass
            for k, v in data.items():
                if v['following'] is not None:
                    if user_id in v['following']:
                        v['following'].remove(user_id)
                        # print('yo')
            json_file.truncate(0)
            json_file.seek(0)
            # print(data)
            json.dump(data, json_file)
            json_file.close()
