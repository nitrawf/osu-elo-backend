from re import match
from flask import Blueprint, jsonify, g
from flask.globals import request
from utils import getMatchDetails, parseMatch, getLogger, fetchMatchSummary
from models import Match, matchSchema, api, db
from flask_praetorian import auth_required

matchBlueprint = Blueprint('addMatch', __name__, url_prefix='/api/match/')
logger = getLogger('eloApp', __name__) 


@matchBlueprint.route('new/get-details/<matchId>')
@auth_required
def getMatch(matchId):
    logger.info(f'Processing match {matchId}.')
    if Match.query.get(matchId) is not None:
        return {'error' : 'Match Already Exists'}, 204
    resp = api.getMatch(matchId)
    return getMatchDetails(resp) 

@matchBlueprint.route('new/process-match', methods = ['POST'])
@auth_required
def processMatch():
    data = request.json
    matchId = data.get('matchId')
    filterdBeatmapList = set([int(x) for x in data.get('filteredBeatmapList')])
    filteredPlayerList = set([int(x) for x in data.get('filteredPlayerList')])
    logger.info(f'Processing match {matchId}.')
    resp = api.getMatch(matchId)
    parseMatch(resp, filterdBeatmapList, filteredPlayerList)
    match = Match.query.get(matchId)
    return jsonify(matchSchema.dump(match))

@matchBlueprint.route('delete/<matchId>')
@auth_required
def deleteMatch(matchId):
    match = Match.query.get(matchId)
    if match is None:
        return {'error' : 'User not found'}, 400
    try:
        db.session.delete(match)
        db.session.commit()
    except Exception as e:
        logger.exception(e)
    return jsonify(f'Deleted {matchId}')

@matchBlueprint.route('delete/', methods=['POST'])
@auth_required
def deleteMatches():
    data = request.json
    matchIds = data.get('matchIds')  
    try:
        matches = Match.query.filter(Match.id.in_(matchIds)).all()
        for match in matches:
            match.players.clear()
            db.session.delete(match)
            db.session.commit()
    except Exception as e:
        logger.exception(e)
    return jsonify(f'Deleted {",".join(matchIds)}')

@matchBlueprint.route('get-summary/<matchId>')
def getMatchSummary(matchId):
    logger.info(f'Fetching match summary for {matchId}')
    return jsonify(fetchMatchSummary(matchId))

@matchBlueprint.route('get-all')
def getMatches():
    matches = Match.query.all()
    return jsonify([matchSchema.dump(x) for x in matches])


