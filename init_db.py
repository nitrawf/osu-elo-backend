from server import app, db, guard
import os
from utils import initEloDiff
from models import User

if app.config['SQLALCHEMY_DATABASE_URI'].startswith('mysql'):
    import queries_mysql as queries
else:
    import queries

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