import logging
import os
from datetime import datetime, timedelta
import csv
from models import EloHistory, Match, db, playerSchema, beatmapSchema, Player, Beatmap, Score, Game, scoreSchema, gameSchema, MatchSummary, matchSummarySchema, EloDiff
from sqlalchemy.sql import func
from collections import defaultdict

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


def parseMatch(data, filteredGameList, filteredPlayerList, defaultElo):
    match = Match()
    match_ = data['match']
    match.id = match_['id']
    match.name = match_['name']
    try:
        match.start_time = datetime.strptime(match_['start_time'], "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=5, minutes=30) # To convert utc to ist
    except:
        match.start_time = datetime.strptime("1900-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
    try:
        match.end_time = datetime.strptime(match_['end_time'], "%Y-%m-%dT%H:%M:%S%z") + timedelta(hours=5, minutes=30) # To convert utc to ist
    except:
        match.end_time = datetime.strptime("2100-12-12T23:59:59", "%Y-%m-%dT%H:%M:%S")
    users = data['users']
    events = data['events']
    
    playerList = parsePlayers(users, filteredPlayerList, defaultElo)
    gameList, beatmapList = parseGames(events, match.id, filteredGameList, filteredPlayerList)

    
    match.players = playerList
    match.games = gameList
    
    if len(beatmapList) > 0:
        db.session.add_all(beatmapList)
    db.session.add(match)
    for game in match.games:
        ''' calculate average player rating for each game, maybe optimization is needed here? '''
        player_ids = [x[0] for x in db.session.query(Score.player_id).filter(Score.game_id == game.id).all()]
        z = Player.query.with_entities(func.avg(Player.elo).label('average')).filter(Player.id.in_(player_ids)).one()
        #logger.debug(f'average elo : {z}')
        game.avg_elo = z.average
        db.session.add(game)
    db.session.commit()



def getMatchDetails(data):
    try:
        playerList = parsePlayers(data['users'])
    except:
        raise Exception('Unable to parse the match. Please check the match id.')
    beatmapList = parseBeatmaps(data['events'])
    return {
        'players' : [playerSchema.dump(x) for x in playerList],
        'beatmaps' : [beatmapSchema.dump(x) for x in beatmapList]
    }


def parsePlayers(users, filter=None, elo=0):
    playerList = []
    for user in users:
        if filter is not None and user['id'] not in filter:
            continue
        player = Player.query.get(user['id'])
        if player is None:
            player = Player()
            player.id = user['id']
            player.name = user['username']
            player.country = user['country_code']
            player.elo = elo
        playerList.append(player)
    return playerList


def parseBeatmaps(events):
    beatmapList = []
    for event in events:
        if 'game' in event:
            game_ = event['game']
            beatmap_ = game_['beatmap']
            beatmap = parseBeatmap(beatmap_)
            beatmap.id = game_['id'] # Use game id instead of beatmap id for handling duplicates
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

def parseGames(events, matchid, filterBeatmap=None, filterPlayer=None):
    gameList = []
    beatmapList = []
    for event in events:
        if 'game' in event:
            game_ = event['game']
            beatmap_ = game_['beatmap']
            if filterBeatmap is not None and game_['id'] not in filterBeatmap:
                continue
            beatmap = parseBeatmap(beatmap_)
            game = Game()
            game.id = game_['id']
            game.mods = ', '.join(game_['mods'])
            game.match_id = matchid            
            scores = parseScores(game_['scores'], game.id, filterPlayer)
            if scores is None:
                logger.warning(f'Skipping game {game.id} due to less players')
                continue
            game.scores = scores
            game.beatmap_id = beatmap.id
            gameList.append(game)
            if Beatmap.query.get(beatmap.id) is None:
                beatmapList.append(beatmap) 
    return gameList, beatmapList


def parseScores(scoresUnfiltered, gameid , filter):
    scoreList = []
    scores = [x for x in scoresUnfiltered if x['user_id'] in filter]
    if len(scores) < 2:# Not counted if only 1 player played the map.
        return None
    scores =  sorted(scores, key=lambda x: x['score'], reverse=True)
    for i in range(len(scores)):
        score_ = scores[i]
        score = Score()
        score.id = score_['id']
        score.score = score_['score']
        score.accuracy = score_['accuracy']
        score.mods = ', '.join(score_['mods'])
        score.player_id = score_['user_id']
        score.game_id = gameid
        score.position = i + 1
        score.points = 1 - ((score.position - 1) / (len(scores) - 1)) ** 1.2 #More lenient 
        scoreList.append(score)
    return scoreList

def fetchMatchSummary(id):
    matchSummary = MatchSummary.query.filter_by(match_id = id).all()
    logger.debug(matchSummary)
    return [matchSummarySchema.dump(x) for x in matchSummary]


def processDelR(delR: dict, matchId: int):
    for key, value in delR.items():
        player = Player.query.get(key)
        if Score.query.filter(Score.player_id == player.id).count() > 300:
            k = 20
        else:
            k = 40
        change = value * k #Fixed as 40 for now
        eloHistory = EloHistory(
            old_elo = player.elo,
            new_elo = player.elo + change,
            elo_change = change,
            match_id = matchId,
            player_id = key
        )
        db.session.add(eloHistory)
        player.elo = player.elo + change
        db.session.add(player)
    db.session.commit()

def calculateEloChange(match : Match):
    ''' Refer: https://handbook.fide.com/chapter/B022017 for details '''
    games = match.games
    delR = defaultdict(lambda : 0)
    for game in games:
        numPlayers = len(game.scores)
        for score in game.scores:
            player = Player.query.get(score.player_id)
            try:
                playerElo = player.elo
            except:
                logger.error(f'Player Missing: {score.player_id}')
                raise Exception
            opponentElo = round(((game.avg_elo * numPlayers) - playerElo) / (numPlayers - 1))
            eloDiff = min(abs(playerElo - opponentElo), 400)
            row = EloDiff.query.filter(EloDiff.ll <= eloDiff, EloDiff.ul >= eloDiff).one()
            if playerElo >= opponentElo:
                pd = row.high
            else:
                pd = row.low
            #logger.debug(f'score.points : {score.points}, pd : {pd}, change : {score.points - pd}')
            delR[player.id] += (score.points - pd)
            #logger.debug(f'player elo = {playerElo}, opponent elo = {opponentElo}')
        #logger.debug(delR)
    processDelR(delR, match.id)



def initEloDiff():
    if EloDiff.query.count() == 0:
        with open("elo_diff.csv") as f:
            z = list(csv.reader(f))
            for i in range(1, len(z)):
                eloDiff = EloDiff(
                    ll=z[i][0],
                    ul=z[i][1],
                    high=z[i][2],
                    low=z[i][3]
                )
                db.session.add(eloDiff)

def addAbandonedMatch(p1Id: int, p2Id: int, n_maps: int, match_name: str) -> Match:
    minMatchId = min(db.session.query(func.min(Match.id).label('min_id')).one().min_id, 0) - 1

    p1 = Player.query.get(p1Id)
    p2 = Player.query.get(p2Id)

    match = Match(
        id=minMatchId,
        name=match_name,
        start_time=datetime.now(),
        end_time=datetime.now(),
        players=[p1, p2],
        games=[]   
    )

    db.session.add(match)
    
    eloDiff = min(abs(p1.elo - p2.elo), 400)
    delR = defaultdict(lambda : 0)
    
    for _ in range(n_maps):
        for player in [p1, p2]:

            if player == p1:
                points = 1
                opponentElo = p2.elo
            else:
                points = 0
                opponentElo = p1.elo
            
            row = EloDiff.query.filter(EloDiff.ll <= eloDiff, EloDiff.ul >= eloDiff).one()
            if player.elo >= opponentElo:
                pd = row.high
            else:
                pd = row.low
            
            logger.debug(f'score.points : {points}, pd : {pd}, change : {points - pd}')
            delR[player.id] += (points - pd)
            logger.debug(f'player elo = {player.elo}, opponent elo = {opponentElo}')
        
        logger.debug(delR)
    
    processDelR(delR, match.id)

    return match