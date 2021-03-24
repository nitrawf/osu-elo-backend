import requests
import os
import logging

logger = logging.getLogger(f'eloApp.{__name__}')

class OsuApi():
    def __init__(self, clientId=os.environ.get('OSU_CLIENT_ID'), clientSecret=os.environ.get('OSU_CLIENT_SECRET'), grantType="client_credentials", scope="public"):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.grantType = grantType
        self.scope = scope
        self.baseUrl = "https://osu.ppy.sh/api/v2/"
        self.token = None
        
    
    def connect(self):
        authUrl = 'https://osu.ppy.sh/oauth/token'
        body = {
            "client_id" : self.clientId,
            "client_secret" : self.clientSecret,
            "grant_type" : self.grantType,
            "scope" : self.scope
        }
        headers = {"accept" : "application/json"}

        try:
            r = requests.post(authUrl, data=body, headers=headers)
            data = r.json()
            token = data.get('access_token')
        except Exception as e:
            logger.exception(e)
            return

        self.token = token
        self.headers =  {
                            "accept" : "application/json",
                            "Authorization" : f"Bearer {self.token}"
                        }

    def getMatch(self, matchId):
        r = requests.get(f'{self.baseUrl}matches/{matchId}', headers=self.headers)
        return r.json()
