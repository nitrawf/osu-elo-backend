import logging
import os
from datetime import datetime
from models import Match, db, playerSchema, beatmapSchema, Player, Beatmap, Score, Game, scoreSchema, gameSchema, MatchSummary, matchSummarySchema

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
    formatter = logging.Formatter('%(asctime)s - %(name)s.%(lineno)d - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

logger = getLogger('eloApp', __name__)


def parseMatch(data, filteredGameList, filteredPlayerList):   
    match = Match()
    match_ = data['match']
    match.id = match_['id']
    match.name = match_['name']
    match.startTime = datetime.strptime(match_['start_time'], "%Y-%m-%dT%H:%M:%S%z")
    match.endTime = datetime.strptime(match_['end_time'], "%Y-%m-%dT%H:%M:%S%z")

    users = data['users']
    events = data['events']
    
    playerList = parsePlayers(users, filteredPlayerList)
    gameList, beatmapList = parseGames(events, match.id, filteredGameList)

    
    match.players = playerList
    match.games = gameList
    
    db.session.add_all(beatmapList)
    db.session.add(match)
    db.session.commit()



def getMatchDetails(data):
    playerList = parsePlayers(data['users'])
    beatmapList = parseBeatmaps(data['events'])
    return {
        'players' : [playerSchema.dump(x) for x in playerList],
        'beatmaps' : [beatmapSchema.dump(x) for x in beatmapList]
    }


def parsePlayers(users, filter=None):
    playerList = []
    for user in users:
        logger.debug(user['id'])
        if filter is not None and user['id'] not in filter:
            continue
        player = Player.query.get(user['id'])
        if player is None:
            player = Player()
            player.id = user['id']
            player.name = user['username']
            player.country = user['country_code']
        playerList.append(player)
    return playerList


def parseBeatmaps(events):
    beatmapList = []
    for event in events:
        if 'game' in event:
            game_ = event['game']
            beatmap_ = game_['beatmap']
            beatmap = parseBeatmap(beatmap_)
            beatmapList.append(beatmap)
    return beatmapList

def parseBeatmap(beatmap_):
    beatmap = Beatmap()
    beatmap.id = beatmap_['beatmapset']['id']
    beatmap.sr = beatmap_['difficulty_rating']
    beatmap.creator = beatmap_['beatmapset']['creator']
    beatmap.artist = beatmap_['beatmapset']['artist']
    beatmap.title = beatmap_['beatmapset']['title']
    beatmap.bg = beatmap_['beatmapset']['covers']['list@2x']
    beatmap.version = beatmap_['version']
    return beatmap

def parseGames(events, matchId, filter=None):
    gameList = []
    beatmapList = []
    for event in events:
        if 'game' in event:
            game_ = event['game']
            beatmap_ = game_['beatmap']
            if filter is not None and beatmap_['beatmapset']['id'] not in filter:
                continue
            beatmap = parseBeatmap(beatmap_)
            game = Game()
            game.id = game_['id']
            game.mods = ', '.join(game_['mods'])
            game.matchId = matchId
            game.scores = parseScores(game_['scores'], game.id)
            game.beatmapId = beatmap.id
            gameList.append(game)
            beatmapList.append(beatmap) 
    return gameList, beatmapList


def parseScores(scores, gameId):
    scoreList = []
    scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    for i in range(len(scores)):
        score_ = scores[i]
        score = Score()
        score.id = score_['id']
        score.score = score_['score']
        score.accuracy = score_['accuracy']
        score.mods = ', '.join(score_['mods'])
        score.playerId = score_['user_id']
        score.gameId = gameId
        score.position = i + 1
        scoreList.append(score)
    return scoreList

def fetchMatchSummary(id):
    matchSummary = MatchSummary.query.filter_by(matchId = id).all()
    logger.debug(matchSummary)
    return [matchSummarySchema.dump(x) for x in matchSummary]
