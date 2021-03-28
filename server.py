from flask.globals import session
from utils import getLogger
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from models import db, ma, User, Score, Player
from utils import initEloDiff
from flask_praetorian import Praetorian
from routes.matchRoute import matchBlueprint
from routes.playerRoute import playerBlueprint
import queries
from sqlalchemy.sql import func

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["JWT_ACCESS_LIFESPAN"] = {'hours' : 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days' : 30}
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

guard = Praetorian()
guard.init_app(app, User)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL_POSTGRES')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

CORS(app)

db.init_app(app)
ma.init_app(app)

app.register_blueprint(matchBlueprint)
app.register_blueprint(playerBlueprint)
logger = getLogger('eloApp') 

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
            conn.execute(queries.drop_match_summary_table)
        except:
            pass
        try:
            conn.execute(queries.drop_player_summary_table)
        except:
            pass
        conn.execute(queries.create_player_summary_view)
        conn.execute(queries.create_match_summary_view)
        if User.query.filter_by(username='admin').count() < 1:
            db.session.add(User(
                username='admin',
                password=guard.hash_password(os.environ.get('ADMIN_PW')),
                roles='admin'
            ))
        initEloDiff()
        db.session.commit()
       
    app.run()