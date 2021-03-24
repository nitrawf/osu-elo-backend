from flask import Blueprint, jsonify, g
from utils import getMatchDetails, parseMatch, getLogger
from models import Match, matchSchema, api

newMatchBlueprint = Blueprint('addMatch', __name__, url_prefix='/api/match/new/')
logger = getLogger('eloApp', __name__) 


@newMatchBlueprint.route('get-details/<matchId>')
def getMatch(matchId):
    logger.info(f'Processing match {matchId}.')
    resp = api.getMatch(matchId)
    return getMatchDetails(resp) 

@newMatchBlueprint.route('process-match', methods = ['POST'])
def processMatch(matchId):
    logger.info(f'Processing match {matchId}.')
    match = Match.query.get(matchId)
    if match is None:
        resp = api.getMatch(matchId)
        parseMatch(resp)
        match = Match.query.get(matchId)
    else:
        logger.info(f'Match is already processed.')
    return jsonify(matchSchema.dump(match))

