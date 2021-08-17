import requests
import os
import logging

logger = logging.getLogger(f'eloApp.{__name__}')

class OsuApi():
    # Python wrapper for osu api v2 
    # Refer https://osu.ppy.sh/docs/index.html for official documentation

    def __init__(self, clientId=os.environ.get('OSU_CLIENT_ID'), clientSecret=os.environ.get('OSU_CLIENT_SECRET'), grantType="client_credentials", scope="public"):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.grantType = grantType
        self.scope = scope
        self.baseUrl = "https://osu.ppy.sh/api/v2"
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

    def getMatch(self, matchId, retry=0):
        if retry > 3:
            return({'error': 'authentication failure'})
        r = requests.get(f'{self.baseUrl}/matches/{matchId}', headers=self.headers)
        if r.status_code == 401:
            self.connect()
            return self.getMatch(matchId, retry + 1)
        return r.json()
    
    def getUser(self, userId, retry=0):
        if retry > 3:
            return({'error': 'authentication failure'})
        r = requests.get(f'{self.baseUrl}/users/{userId}/osu?key=id', headers=self.headers)
        if r.status_code == 401:
            self.connect()
            return self.getUser(userId, retry + 1)
        return r.json()
