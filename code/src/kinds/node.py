import kopf
import logging
import json

import templates
import k8s
import utils

RESOURCE = 'nodes.' + utils.GROUP


@kopf.on.create(RESOURCE)
def create(body, **kwargs):
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']
    logging.info(f'Node "{name}" is created on namespace "{namespace}"')
    logging.debug(body)

    try:
        resources = json.dumps(body['spec']['resources'])
    except KeyError:
        resources = '{}'
    try:
        airGapped = body['spec']['airGapped'] == True
    except KeyError:
        airGapped = True

    deployment, service, policy = templates.native_node(id=name, image=body['spec']['image'], resources=resources)

    if not airGapped:
        obj = {"ipBlock": {
            "cidr": "0.0.0.0/0",
            "except": ["10.0.0.0/8"]
        }}
        policy['spec']['ingress'].append({'from': [obj]})
        policy['spec']['egress'].append({'to': [obj]})

    logging.debug(deployment)
    logging.debug(service)
    logging.debug(policy)

    kopf.adopt(deployment)
    kopf.adopt(service)
    kopf.adopt(policy)

    k8s.apps.create_namespaced_deployment(namespace, deployment)
    k8s.core.create_namespaced_service(namespace, service)
    k8s.networking.create_namespaced_network_policy(namespace, policy)


@kopf.on.delete(RESOURCE)
def delete(body, **kwargs):
    name = body['metadata']['name']
    logging.info(f'Node "{name}" is deleted')
    logging.debug(body)
