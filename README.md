# PROCOS
###### project &amp; contract system - <br> the command line program for managing contracts and projects.

## Based on:
```
🐍 Python3
🐘 PostgreSQL database
📜 SQLAlchemy ORM
📝 Alembic database migration tool
🐳 Docker containers
```


## DOCKER RUN:


##### 1. Clone repository:

```bash
git clone https://github.com/Aliakseeva/MenuApp
```

##### 2. Run docker-compose:

Make sure you are located in project repository!

```bash
 docker-compose run --service-ports procos
```


## MANUAL RUN:


##### 1. Clone repository:

```bash
git clone https://github.com/Aliakseeva/procos
```

##### 2. Set up .evn file, for example:

```text
DB_HOST=localhost
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASS=postgres
```

##### 3. Create virtual environment and activate it:

Make sure you are located in project repository!

```bash
python -m venv venv
source venv/bin/activate
```

##### 4. Install requirements:

```bash
pip install -r requirements.txt
```

##### 5. Apply migrations:

```bash
alembic upgrade head
```

##### 6. Start the project:

```bash
python3 run.py
```

***

###### *If you get `unicodeencodeerror` (usually on Windows), set `TABLE_STYLE = 'grid'` in procos/const.py*
***


###### Type help to get available commands:
```bash
> help
```

