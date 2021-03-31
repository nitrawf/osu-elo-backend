from server import app, db
from models import Match, Player, Score, EloHistory
from utils import getLogger, calculateEloChange
from sqlalchemy.sql import func


logger = getLogger('bulkElo')

with app.app_context():
    matches = Match.query.order_by(Match.start_time).all()
    for match in matches:
        logger.debug(f'Current processing {match.name} | {match.start_time}')
        if EloHistory.query.filter(EloHistory.match_id == match.id).count() > 0:
                logger.debug('Skipped')
                continue
        for game in match.games:
            
            player_ids = [x[0] for x in db.session.query(Score.player_id).filter(Score.game_id == game.id).all()]
            z = Player.query.with_entities(func.avg(Player.elo).label('average')).filter(Player.id.in_(player_ids)).one()
            logger.debug(f'average elo : {z}')
            game.avg_elo = z.average
            db.session.add(game)
        db.session.add(match)
        try:
            calculateEloChange(match)
        except:
            logger.error('SOmething broke lol')
            continue
