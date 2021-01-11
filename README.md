# twitter-separation

twitter-separation is a package that finds the path between two users on Twitter through following lists.

## About the project

The package currently includes two algorithms to find a path between two users. They are:

* NaiveBFS
* BidirectionalBFS

These are BFS algorithms on a graph, such that:

* every user is a node;
* when user *X* follows user *Y*, a directed edge is defined such that X ---> Y.

Let's say a user *X* follows users *A* and user *A* follows user *Y*. The bidirectional algorithm also runs a search from the follower list of user *Y*, and calculates an intersect between the following list of user *X* and the follower list of user *Y* at each iteration of the BFS. Hence, the bidirectional algorithm runs better in the general case, except for when the number of followers of the target user is large.

Both take relatively long to run - 40k followers take roughly 8 hours to index and cache - due entirely to Twitter API rate limits. In the future, I might rent a VPS to run this, 'just for the sake of it'.

This was built on top of the [python-twitter](https://github.com/bear/python-twitter) library

## Installation

1. In order to use this package, make sure you have a Twitter Developer Account. You can apply for one [here](https://developer.twitter.com/en/apply-for-access)

2.  Put the credential in a file called `.env` in the same directory as `main.py` with this template. You can find each key by following [this](https://python-twitter.readthedocs.io/en/latest/getting_started.html) guide.
```
#.env
API_KEY=xxxxxx
API_KEY_SECRET=xxxxxx
ACCESS_TOKEN=xxxxxx
ACCESS_TOKEN_SECRET=xxxxxx
```
3. Install dependencies using [pip](https://pip.pypa.io/en/stable/)
```bash
pip install -r requirements.txt
```

## Usage

For easy use, simply run `main.py`. 

To use modules in a package, make sure you've still added the credentials into a `.env` file.

Also, make sure you set up a python-twitter Api object as shown:

```python
def api_setup():
    _api = twitter.Api(consumer_key=API_KEY, consumer_secret=API_KEY_SECRET,
                       access_token_key=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET, sleep_on_rate_limit=True)

    if _api.VerifyCredentials():
        print('Authentication passed.')

    return _api
```

**Usage**:

```python
from twitter-separation.algorithms.naive_bfs import NaiveBFS
from twitter-separation.algorithms.bidirectional_bfs import BidirectionalBFS

naive_obj = NaiveBFS(api)
bidirectional_obj = BidirectionalBFS(api, search_radius=1000, auto_next=True)  # default args

# start_user and target_user are the Twitter IDs of the start user and the target user, respectively.
# IDs can be converted from handles at http://twitterid.com/
_path = naive_obj.run_search(origin_user=start_user, target_user=target_user)
_path = bidirectional_obj.run_search(origin_user=start_user, target_user=target_user)
```

## Contributing
Pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)
