## Create virtual environment

```
pyenv local python_3.9.0
virtualenv .venv --python=python3.9
```

### Install packages

```
pip install -r requirements.txt
source .venv/bin/activate
```

### Update requirements file:

```
pip freeze > requirements.txt
```

## Run API

```
sh scripts/start-dev.sh
```

## Unitest

```
cp .env-example .test.env
pytest -x
```

### Run docker-compose

```
cp .<ENVIRONMENT>.env .env
sh scripts/deploy.sh <ENVIRONMENT> <BRANCH>
sh scripts/stop-docker.sh <ENVIRONMENT>
```

### Default account

```
email: blog@example.com
password: 12345678
```

### Connect to mongodb running on docker

```
docker exec -it <MONGODB_INSTANCE_ID> mongosh -u "root" -p "pwd"
```

### Backup mongodb on Docker

```
docker exec -i <CONTAINER_ID> /usr/bin/mongodump --username "root" --password "pwd" --authenticationDatabase admin --db todo --archive > todo.dump
```

### Restore mongodb to Docker

```
docker exec -i <CONTAINER_ID> /usr/bin/mongorestore --username "root" --password "pwd" --authenticationDatabase admin --nsInclude="todo.*" --archive < ~/Downloads/todo.dump
```