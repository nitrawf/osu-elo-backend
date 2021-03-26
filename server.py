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

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_POSTGRES')
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
            conn.execute('drop table if exists match_summary')
        except:
            pass
        # conn.execute(f'''
        # create or replace view match_summary
        # as 
        # select
        # player.id as playerid,
        # match.id as matchid,
        # player.name as player_name,
        # sum(score.score) as total_score, 
        # round(avg(score.position), 2) as average_position,
        # round(avg(score.score), 2) as average_score,
        # round(avg(score.accuracy), 2) as average_accuracy
        # from match INNER join game on match.id = game.matchid
        # inner join score on game.id = score.gameid 
        # inner join player on player.id = score.playerid
        # group by playerid, matchid;''')
        conn.execute(f'''
        create or replace view match_summary
        as 
        select
        player.id as player_id,
        match.id as match_id,
        player.name as player_name,
        sum(score.score) as total_score, 
        round(cast(avg(score.position) as numeric), 2) as average_position,
        round(cast(avg(score.score) as numeric), 2) as average_score,
        round(cast(avg(score.accuracy) as numeric), 2) as average_accuracy
        from match INNER join game on match.id = game.match_id
        inner join score on game.id = score.game_id 
        inner join player on player.id = score.player_id
        group by player.id, match.id;
        ''')

        
    logger = getLogger('eloApp') 
    app.run()