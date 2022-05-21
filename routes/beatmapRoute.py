from operator import and_

from flask import Blueprint, jsonify
from models import Beatmap, Game, beatmapSchema, db, gameSchema
from sqlalchemy.sql import func
from utils import getLogger

beatmapBlueprint = Blueprint('beatmapbp', __name__, url_prefix='/api/beatmap/')
logger = getLogger('eloApp', __name__)


@beatmapBlueprint.route('mostplayedmaps')
def getMostPlayedMaps():
    logger.info('Getting most played beatmaps')
    data = db.session.query(Beatmap, Game, func.count(Game.id)) \
        .join(Game, Beatmap.id == Game.beatmap_id) \
        .group_by(Beatmap.id, Game.mods) \
        .order_by(func.count(Game.id).desc()) \
        .limit(5) \
        .all()
    logger.info(data)
    dataJson = [{**beatmapSchema.dump(x), **gameSchema.dump(y), 'playcount' : z} for (x, y, z) in data]
    logger.info(dataJson)
    return jsonify(dataJson)

@beatmapBlueprint.route('mostplayedmapper')
def getMostPlayedArtist():
    logger.info('Getting most played mapper')
    data = db.session.query(Beatmap.creator, func.count(Beatmap.id)) \
        .filter(and_(Beatmap.id != -1, Beatmap.creator != None)) \
        .group_by(Beatmap.creator) \
        .order_by(func.count(Beatmap.id).desc()) \
        .limit(5) \
        .all()
    logger.info(data)
    return jsonify(data)
