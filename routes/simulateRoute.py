from flask import Blueprint, request
from flask.json import jsonify
from utils import getLogger, simulateElo

simulateBlueprint = Blueprint('simulatebp', __name__, url_prefix='/api/simulate/')
logger =  getLogger('eloApp', __name__)

@simulateBlueprint.route('elo')
def simulate():
    p1Elo = int(request.args.get('p1Elo'))
    p2Elo = int(request.args.get('p2Elo'))
    p1Wins = int(request.args.get('p1Wins'))
    p2Wins = int(request.args.get('p2Wins'))
    return jsonify(simulateElo(p1Elo, p2Elo, p1Wins, p2Wins))
