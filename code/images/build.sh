#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"
eval $(minikube docker-env --shell bash)

function build() {
  docker build -t $1 ./$1
}

build "idle" & build "sidecar"

wait
