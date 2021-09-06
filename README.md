Requirements:
Python 3
MySQL 8

Environment Variables:
ELO_DB_URL: 'mysql+mysqldb://{user}:{password}@{mysql_ip}/{db_name}'
SECRET_KEY: Any random string used for encryption
OSU_CLIENT_ID: Create osu! OAuth Application [https://osu.ppy.sh/home/account/edit] 
OSU_CLIENT_SECRET Create osu! OAuth Application [https://osu.ppy.sh/home/account/edit] 

Getting started:
1. Install Pipenv -> pip install pipenv
2. Install Requirements -> pipenv install
3. Run Flask Server -> pipenv run python server.py