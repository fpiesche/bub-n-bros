#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No architecture given (options: amd64, arm32v7); defaulting to amd64."
    ARCH=amd64
fi

docker pull florianpiesche/bubnbros:$ARCH-latest
docker stop bubnbros
docker-compose up -d
