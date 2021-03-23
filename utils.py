import logging
import os
from datetime import datetime
from models import *

def getLogger(appName, moduleName=None):
    if moduleName != None:
        return logging.getLogger(f'{appName}.{moduleName}')

    if not os.path.exists('./logs'):
        os.mkdir('logs')
    
    logger = logging.getLogger(appName)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(f'logs/logs_{datetime.now().strftime("%d%m%Y%H%M%S")}.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = getLogger('eloApp', __name__)

def parseMatch(data):   
    match = Match()
    match_ = data['match']
    match.id = match_['id']
    match.name = match_['name']
    match.startTime = datetime.strptime(match_['start_time'], "%Y-%m-%dT%H:%M:%S%z")
    match.endTime = datetime.strptime(match_['end_time'], "%Y-%m-%dT%H:%M:%S%z")

    users = data['users']
    events = data['events']
    
    playerList = parsePlayers(users)
    gameList = parseGames(events, match.id)

    match.players = playerList
    match.games = gameList

    db.session.add(match)
    db.session.commit()

def parsePlayers(users):
    playerList = []
    for user in users:
        player = Player.query.get(user['id'])
        if player is None:
            player = Player()
            player.id = user['id']
            player.name = user['username']
            player.country = user['country_code']
        playerList.append(player)
    return playerList

def parseGames(events, matchId):
    gameList = []
    for event in events:
        if 'game' in event:
            game_ = event['game']
            game = Game()
            game.id = game_['id']
            game.mods = ', '.join(game_['mods'])
            game.matchId = matchId
            game.scores = parseScores(game_['scores'], game.id)
            gameList.append(game)
    return gameList

def parseScores(scores, gameId):
    scoreList = []
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    for i in range(len(scores)):
        score_ = scores[i]
        score = Score()
        score.id = score_['id']
        score.score = score_['score']
        score.accuray = score_['accuracy']
        score.mods = ', '.join(score_['mods'])
        score.playerId = score_['user_id']
        score.gameId = gameId
        score.position = i + 1
        scoreList.append(score)
    return scoreList