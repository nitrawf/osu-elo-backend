Requirements
1. Python 3
2. MySQL 8

Environment Variables:<br />
ELO_DB_URL: 'mysql+mysqldb://{user}:{password}@{mysql_ip}/{db_name}'<br />
SECRET_KEY: Any random string used for encryption<br />
OSU_CLIENT_ID: Create osu! OAuth Application [https://osu.ppy.sh/home/account/edit]<br />
OSU_CLIENT_SECRET Create osu! OAuth Application [https://osu.ppy.sh/home/account/edit]

Getting started:
1. Install Pipenv -> pip install pipenv
2. Install Requirements -> pipenv install
3. Run Flask Server -> pipenv run python server.py