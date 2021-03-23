from logging import log
from utils import getLogger, parseMatch
from osuApi import osuApi
from flask import Flask, jsonify
import os
from models import db, ma, Match, matchSchema

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}/serverdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
ma.init_app(app)

api = osuApi()
api.connect()



@app.route('/getMatch/<matchId>')
def getMatch(matchId):
    logger.info(f'Processing match {matchId}.')
    match = Match.query.get(matchId)
    if match is None:
        resp = api.getMatch(matchId)
        parseMatch(resp)
        match = Match.query.get(matchId)
    else:
        logger.info(f'Match is already processed.')
    return jsonify(matchSchema.dump(match))
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    logger = getLogger('eloApp') 

    app.run()


#logger.debug(resp)


