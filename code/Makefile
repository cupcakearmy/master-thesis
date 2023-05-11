# Cluster
cluster-up::
	minikube start --cni calico

cluster-down::
	minikube delete

cluster-dash::
	minikube dashboard

cluster-env::
	# minikube docker-env | source
	eval $(minikube docker-env --shell bash)

# Namespace
ns-up::
	kubectl create namespace simulator
	kubens simulator

ns-down::
	kubectl delete namespaces simulator

ns-reset:: ns-down ns-up

# Chaos Mesh
chaos-up::
	curl -sSL https://mirrors.chaos-mesh.org/v2.5.1/install.sh | bash

chaos-dash::
	minikube service chaos-dashboard -n chaos-mesh

# CRD
crd-up::
	kubectl apply -f ./crd/iluzio.yaml

# Docker
docker::
	./images/build.sh

# General
dash:
	$(MAKE) -j 2 cluster-dash chaos-dash

start:: cluster-up ns-up chaos-up crd-up docker dash

reset:: cluster-down start

operator-up::
	poetry install
	poetry run kopf run -n simulator src/main.py
