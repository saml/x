# Quickstart

Start database:
```py
docker-compose up -d
```

Run script:
```bash
python3 -mvenv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Kill databse:
```py
docker-compose stop db1
```

Script should work.

# About

Goal is to figure out how to create reconnecting postgres connection pool.
