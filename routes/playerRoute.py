from flask import Blueprint
from flask.json import jsonify
from models import (EloHistory, Player, PlayerSummary, eloHistorySchema,
                    matchSchema, playerSummarySchema, db, Match)
from utils import getLogger

playerBlueprint = Blueprint('playerbp', __name__, url_prefix='/api/player/')
logger =  getLogger('eloApp', __name__)

@playerBlueprint.route('get-all')
def getAllPlayers():
    players = PlayerSummary.query.all()
    return jsonify([playerSummarySchema.dump(x) for x in players])

@playerBlueprint.route('<playerId>/summary')
def getPlayer(playerId):
    logger.debug(playerId)
    logger.debug(type(playerId))
    try:
        playerId = int(playerId)
        player = PlayerSummary.query.get(playerId)
    except:   
        player = PlayerSummary.query.filter(PlayerSummary.name == playerId).one()
    out = playerSummarySchema.dump(player)
    out.pop('average_position') # Fix later
    out.pop('total_points')
    return jsonify(out)

@playerBlueprint.route('<playerId>/matches')
def getPlayerMatches(playerId):
    matches = Player.query.get(playerId).matches
    return jsonify([matchSchema.dump(x) for x in matches])

@playerBlueprint.route('<playerId>/elo-history')
def getPlayerEloHistory(playerId):
    data = db.session.query(Match, EloHistory) \
        .join(EloHistory, EloHistory.match_id == Match.id) \
        .filter(EloHistory.player_id == playerId).all()
    return jsonify([{**eloHistorySchema.dump(y), **matchSchema.dump(x)} for (x, y) in data])
