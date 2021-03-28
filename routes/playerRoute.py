from flask.json import jsonify
from models import PlayerSummary
from flask import Blueprint
from utils import getLogger
from models import PlayerSummary,playerSummarySchema

playerBlueprint = Blueprint('playerbp', __name__, url_prefix='/api/player/')
logger =  getLogger('eloApp', __name__)

@playerBlueprint.route('get-all')
def getAllPlayers():
    players = PlayerSummary.query.all()
    return jsonify([playerSummarySchema.dump(x) for x in players])


