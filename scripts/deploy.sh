#!/bin/bash

set -e

env=$1
if [ -z "$1" ]
  then
    echo "Param :env is required as $1"
    exit 1
fi

branch=$2
if [ -z "$2" ]
  then
    echo "Param :branch is required as $2"
    exit 1
fi

echo "Deploying $2 branch to $1"
git fetch origin && git checkout $2 && git merge origin/$2

echo "Overwriting .$1.env to .env"
rm -rf .env
cp ".$1.env" .env


echo "Rebuild docker"
docker-compose -p "demo_blog_fastapi_$1" -f docker-compose.yml -f "docker-compose.$1.yml" up -d --build

echo "Deployed branch $1"
if [ "$1" = "local" ]
  then
    echo "Clear docker cache"
    docker system prune -f
fi
exit 0
