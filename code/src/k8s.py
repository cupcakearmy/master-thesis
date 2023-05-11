from kubernetes import client, config

config.load_kube_config()

core = client.CoreV1Api()
apps = client.AppsV1Api()
crd = client.CustomObjectsApi()
networking = client.NetworkingV1Api()
