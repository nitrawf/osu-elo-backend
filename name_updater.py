from osuApi import OsuApi
from server import app
from models import db, Player

api = OsuApi()
api.connect()

with app.app_context():
    players = Player.query.all()
    for player in players:
        try:
            online_name = api.getUser(player.id)['username']
        except:
            online_name = player.name + '_restricted'
        if player.name != online_name:
            print(f'Name mismatch for player {player.name}. Setting name to {online_name}')
            player.name = online_name
            db.session.add(player)
    db.session.commit()