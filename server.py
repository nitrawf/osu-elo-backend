from utils import getLogger
from flask import Flask, jsonify
from flask_cors import CORS
import os
from models import db, ma
from routes.matchRoute import matchBlueprint

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.environ.get('SECRET_KEY')
#app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}/serverdb.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True



CORS(app)

db.init_app(app)
ma.init_app(app)

app.register_blueprint(matchBlueprint)

@app.route('/')
def hello():
    return jsonify("Hello there")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        conn = db.engine.connect()
        try:
            conn.execute('drop table if exists matchSummary')
        except:
            pass
        conn.execute(f'''
        create view if not EXISTS matchSummary
        as 
        select
        player.id as playerId,
        match.id as matchId,
        player.name as playerName,
        sum(score.score) as totalScore, 
        round(avg(score.position), 2) as averagePosition,
        round(avg(score.score), 2) as averageScore,
        round(avg(score.accuracy), 2) as averageAccuracy
        from match INNER join game on match.id = game.matchId 
        inner join score on game.id = score.gameId 
        inner join player on player.id = score.playerId
        group by playerId, matchId;''')
        
    logger = getLogger('eloApp') 
    app.run()