from utils import getLogger
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from models import db, ma, User
from routes.matchRoute import matchBlueprint
from flask_praetorian import Praetorian
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["JWT_ACCESS_LIFESPAN"] = {'hours' : 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

guard = Praetorian()
guard.init_app(app, User)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_POSTGRES')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CORS(app)

db.init_app(app)
ma.init_app(app)

app.register_blueprint(matchBlueprint)

@app.route('/')
def hello():
    return jsonify("Hello there")

@app.route('/api/login', methods=['POST'])
def login():
    """
    Logs a user in by parsing a POST request containing user credentials and
    issuing a JWT token.
    .. example::
       $ curl http://localhost:5000/api/login -X POST \
         -d '{"username":"Yasoob","password":"strongpassword"}'
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    logger.info(f'Logging in with user: {username}')
    user = guard.authenticate(username, password)
    return {'access_token' : guard.encode_jwt_token(user)}

@app.route('/api/refresh', methods=['POST'])
def refresh():
    """
    Refreshes an existing JWT by creating a new one that is a copy of the old
    except that it has a refrehsed access expiration.
    .. example::
       $ curl http://localhost:5000/api/refresh -X GET \
         -H "Authorization: Bearer <your_token>"
    """
    logger.info("refresh request")
    old_token = request.get_data()
    new_token = guard.refresh_jwt_token(old_token)
    return {'access_token': new_token}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        conn = db.engine.connect()
        try:
            conn.execute('drop table if exists match_summary')
        except:
            pass
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
        if User.query.filter_by(username='admin').count() < 1:
            db.session.add(User(
                username='admin',
                password=guard.hash_password('akelakela'),
                roles='admin'
            ))
        db.session.commit()

        
    logger = getLogger('eloApp') 
    app.run()