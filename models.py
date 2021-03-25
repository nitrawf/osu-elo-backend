from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from OsuApi import OsuApi

db = SQLAlchemy()
ma = Marshmallow()

api = OsuApi()
api.connect()

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
    beatmapId = db.Column(db.Integer, db.ForeignKey('beatmap.id'), nullable=False)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    accuracy = db.Column(db.Float)
    position = db.Column(db.Integer)
    mods = db.Column(db.String(256))
    playerId = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    gameId = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
   
    
class Beatmap(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sr = db.Column(db.Float)
    artist = db.Column(db.String(256))
    creator = db.Column(db.String(256))
    title = db.Column(db.String(256))
    version = db.Column(db.String(256))
    bg = db.Column(db.String(1024))


class MatchSummary(db.Model):
    __tablename__ = 'matchSummary'
    playerId = db.Column(db.Integer, primary_key = True)
    matchId = db.Column(db.Integer, primary_key = True)
    playerName =  db.Column(db.String(256))
    totalScore = db.Column(db.Integer)
    averageScore = db.Column(db.Float)
    averageAccuracy = db.Column(db.Float)
    averagePosition = db.Column(db.Float)


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

class BeatmapSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beatmap
        load_instance = True

class ScoreSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Score
        load_instance = True

class MatchSummarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MatchSummary
        load_instance = True

matchSchema = MatchSchema()
playerSchema = PlayerSchema()
gameSchema = GameSchema()
beatmapSchema = BeatmapSchema()
scoreSchema = ScoreSchema()
matchSummarySchema = MatchSummarySchema()