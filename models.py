from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from osuApi import OsuApi

db = SQLAlchemy()
ma = Marshmallow()
api = OsuApi()
api.connect()

player_match_xref = db.Table('player_match_xref',
    db.Column('playerid', db.Integer, db.ForeignKey('player.id'), primary_key = True),
    db.Column('matchid', db.Integer, db.ForeignKey('match.id'), primary_key = True)
)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(256))
    start_time = db.Column(db.DateTime())
    end_time = db.Column(db.DateTime())
    players = db.relationship('Player', secondary=player_match_xref, lazy='subquery', backref=db.backref('matches', lazy=True), cascade="all, delete")
    games = db.relationship('Game', backref='match', lazy=True, cascade="all, delete-orphan")


class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(256))
    country = db.Column(db.String(256))
    elo = db.Column(db.Integer)
    scores = db.relationship('Score', backref='player', lazy=True)
    #matches = db.relationship('Match', secondary=player_match_xref, lazy='subquery', backref=db.backref('players', lazy=True), cascade="all, delete")

class Game(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    scores = db.relationship('Score', backref='game', lazy=True, cascade="all, delete-orphan")
    mods = db.Column(db.String(256))
    avg_elo = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    beatmap_id = db.Column(db.Integer, db.ForeignKey('beatmap.id'), nullable=False)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    score = db.Column(db.Integer)
    accuracy = db.Column(db.Float)
    position = db.Column(db.Integer)
    mods = db.Column(db.String(256))
    points = db.Column(db.Float)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
   
    
class Beatmap(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sr = db.Column(db.Float)
    artist = db.Column(db.String(256))
    creator = db.Column(db.String(256))
    title = db.Column(db.String(256))
    version = db.Column(db.String(256))
    bg = db.Column(db.String(1024))


class MatchSummary(db.Model):
    __tablename__ = 'match_summary'
    player_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, primary_key=True)
    elo_id = db.Column(db.Integer)
    player_name =  db.Column(db.String(256))
    total_score = db.Column(db.Integer)
    total_points = db.Column(db.Float)
    average_score = db.Column(db.Float)
    average_accuracy = db.Column(db.Float)
    average_position = db.Column(db.Float)
    old_elo = db.Column(db.Integer)
    new_elo = db.Column(db.Integer)
    elo_change = db.Column(db.Integer)


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    roles = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def rolenames(self):
        try:
            return self.roles.split(',')
        except Exception:
            return []

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()
    
    @classmethod
    def identify(cls, id):
        return cls.query.get(id)
    
    @property
    def identity(self):
        return self.id

    def is_valid(self):
        return self.is_active

class EloDiff(db.Model):
    __tablename__ = 'elo_diff'
    id = db.Column(db.Integer, primary_key=True)
    ll = db.Column(db.Integer)
    ul = db.Column(db.Integer)
    low = db.Column(db.Float)
    high =  db.Column(db.Float)

class EloHistory(db.Model):
    __tablename__ = 'elo_history'
    id = db.Column(db.Integer, primary_key=True)
    old_elo = db.Column(db.Integer)
    new_elo = db.Column(db.Integer)
    elo_change = db.Column(db.Integer)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)

class PlayerSummary(db.Model):
    __tablename__ = 'player_summary'
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(256))
    elo = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    total_points = db.Column(db.Float)
    maps_played = db.Column(db.Integer)
    matches_played = db.Column(db.Integer)
    average_score = db.Column(db.Float)
    average_accuracy = db.Column(db.Float)
    average_position = db.Column(db.Float)
    player_rank = db.Column(db.Integer)
    last_played_days = db.Column(db.Integer)

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

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class PlayerSummarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PlayerSummary
        load_instance = True

class EloHistorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EloHistory
        include_fk = True
        load_instance = True

matchSchema = MatchSchema()
playerSchema = PlayerSchema()
gameSchema = GameSchema()
beatmapSchema = BeatmapSchema()
scoreSchema = ScoreSchema()
matchSummarySchema = MatchSummarySchema()
playerSummarySchema = PlayerSummarySchema()
eloHistorySchema = EloHistorySchema()