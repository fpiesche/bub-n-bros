#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Run this as docker-build.sh [amd64|arm32v7]!"
    exit 1
fi

echo "Building Docker image florianpiesche/bubnbros:$1-latest."
docker build --build-arg BASE_ARCH=$1 -t florianpiesche/bubnbros:$1-latest .
echo "Pushing Docker image florianpiesche/bubnbros:$1-latest."
docker push florianpiesche/bubnbros
