#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Run this as docker-build.sh [amd64|arm32v7]!"
    exit 1
fi

docker build --build-arg BASE_ARCH=$1 -t my_image:$1-latest .
docker push florianpiesche/bubnbros
