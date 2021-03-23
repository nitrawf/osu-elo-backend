from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


db = SQLAlchemy()
ma = Marshmallow()


player_match_xref = db.Table('player_match_xref',
    db.Column('playerId', db.Integer, db.ForeignKey('player.id'), primary_key = True),
    db.Column('matchId', db.Integer, db.ForeignKey('match.id'), primary_key = True)
)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(256))
    startTime = db.Column(db.DateTime())
    endTime = db.Column(db.DateTime())
    players = db.relationship('Player', secondary=player_match_xref, lazy='subquery', backref=db.backref('matches', lazy=True))
    games = db.relationship('Game', backref='match', lazy=True)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(256))
    country = db.Column(db.String(256))
    scores = db.relationship('Score', backref='player', lazy=True)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    scores = db.relationship('Score', backref='game', lazy=True)
    mods = db.Column(db.String(256))
    matchId = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    accuray = db.Column(db.Integer)
    position = db.Column(db.Integer)
    mods = db.Column(db.String(256))
    playerId = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)


class MatchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Match
        load_instance = True

class GameSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Game
        load_instance = True

class PlayerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Player
        load_instance = True

matchSchema = MatchSchema()
playerSchema = PlayerSchema()
gameSchema = GameSchema()