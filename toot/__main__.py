import requests
import json

from datetime import datetime
from pprint import pprint
# from toot.asynch.entities import Account, from_dict
from toot.asynch.lazy_entities import Account
from toot.asynch.speed_test import run

if __name__ == '__main__':
    run()

    # with open('acc.json') as f:
    #     data = json.load(f)
    #     account = Account(data)
    #     pprint(account)
    #     print(account.acct)

    # def timeline():
    #     response = requests.get("https://mastodon.social/api/v1/timelines/public?limit=40")
    #     response.raise_for_status()
    #     return response.json()

    # data = timeline()
    # start = datetime.now()
    # parsed = [from_dict(Status, status) for status in data]
    # pprint(parsed)
    # print(len(parsed))
    # print(datetime.now() - start)
