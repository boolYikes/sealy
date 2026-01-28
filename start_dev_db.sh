#!/bin/bash

docker run -d --name sealy-dev \
    -p 5432:5432 \
    -e POSTGRES_USER=sealy-dev \
    -e POSTGRES_PASSWORD=sealy-dev \
    -e POSTGRES_DB=sealy-dev \
    -v sealy-dev:/var/lib/postgresql/data \
    postgres:16