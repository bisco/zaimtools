#!/usr/bin/env python3
# coding: utf-8

import os
import json
import requests
from requests_oauthlib import OAuth1Session
from requests_oauthlib import OAuth1

request_token_url = u"https://api.zaim.net/v2/auth/request"
authorize_url = u"https://auth.zaim.net/users/auth"
access_token_url = u"https://api.zaim.net/v2/auth/access"
callback_uri = u"http://localhost/zaim"
get_money_url = u"https://api.zaim.net/v2/home/money"


def get_key():
    credential_dir = os.path.join(os.path.abspath(os.path.curdir), ".credentials")
    credential_path = os.path.join(credential_dir, "zaim_secret.json")
    with open(credential_path, "r") as f:
        key_data = json.load(f)
        consumer_key = key_data["CONSUMER_KEY"]
        consumer_secret = key_data["CONSUMER_SECRET"]
        return consumer_key, consumer_secret 

def oauth_requests(consumer_key, consumer_secret):
    auth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=callback_uri)
    r = auth.fetch_request_token(request_token_url)
    resource_owner_key = r.get('oauth_token')
    resource_owner_secret = r.get('oauth_token_secret')

    authorization_url = auth.authorization_url(authorize_url)
    print('Please go here and authorize,', authorization_url)
    verifier = input('Paste oauth verifier: ')

    auth = OAuth1Session(client_key=consumer_key,
                         client_secret=consumer_secret,
                         resource_owner_key=resource_owner_key,
                         resource_owner_secret=resource_owner_secret,
                         verifier=verifier)
    oauth_token = auth.fetch_access_token(access_token_url)

    resource_owner_key = oauth_token.get('oauth_token')
    resource_owner_secret = oauth_token.get('oauth_token_secret')
    print("access_key", resource_owner_key)
    print("access_key_secret", resource_owner_secret)

if __name__ == "__main__":
    ckey, csec = get_key()
    oauth_requests(ckey, csec)
