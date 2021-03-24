from utils import getLogger
from flask import Flask
import os
from models import db, ma
from routes.newMatchRoute import newMatchBlueprint

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.getcwd()}/serverdb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
ma.init_app(app)

app.register_blueprint(newMatchBlueprint)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    logger = getLogger('eloApp') 
    app.run()