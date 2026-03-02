#!/bin/bash

# Use from local not CI

set -a
source .env
set +a

while [[ $# -gt 0 ]]; do
    case $1 in
        # is it a reset?
        --reset)
            echo "Resetting dev db to init state..."
            if docker ps -aq -f "name=^${DEV_ENV_NAME}$" | grep -q .; then
                docker stop $DEV_ENV_NAME || echo "Container is already stopped. Deleting..."
                docker rm $DEV_ENV_NAME || echo "Container is already deleted."
            fi
            echo "Removing revisions..."
            rm -r alembic/versions/* || echo "Already empty."
            echo "Removing deb db docker volumes..."
            # OR, drop alembic_version and all orm tables
            docker volume rm $DEV_ENV_NAME || true
            # path is re-associated on start, pg will re-init
            docker volume create $DEV_ENV_NAME
            ;;
        *)
            printf '%s\n' \
                "Usage: $(basename "$0") [--reset]" \
                "" \
                "Options:" \
                "    --reset Reset db before starting. Use on ORM change."
            exit 1
            ;;
    esac
    shift
done

# otherwise, do normal procedure
if docker ps -q -f "name=^${DEV_ENV_NAME}$" | grep -q .; then
    echo "Already running"
elif docker ps -aq -f "name=^${DEV_ENV_NAME}$" | grep -q .; then
    docker start $DEV_ENV_NAME >/dev/null
else
    docker run -d --name $DEV_ENV_NAME \
        -p 5432:5432 \
        -e POSTGRES_USER=$DEV_ENV_NAME \
        -e POSTGRES_PASSWORD=$DEV_ENV_NAME \
        -e POSTGRES_DB=$DEV_ENV_NAME \
        -v $DEV_ENV_NAME:/var/lib/postgresql/data \
        postgres:16
fi

until docker exec -it $DEV_ENV_NAME pg_isready 2>&1; do
    sleep 5
done