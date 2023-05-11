#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
eval $(minikube docker-env --shell bash)

docker build -t base-station ./base
docker build -t satellite ./sat

kubectl apply -f ./scenario.yaml
