import kopf
import logging

import templates
import k8s
import utils

RESOURCE = 'links.' + utils.GROUP


def get_link_metadata(body):
    try:
        name = body['metadata']['name']
        sender = body['spec']['from']
        receiver = body['spec']['to']
        direction = body['spec']['direction']
        if direction not in ['uni', 'bi']:
            raise kopf.PermanentError(f'Invalid direction "{direction}" for link "{name}"')
        unidirectional = direction == 'uni'
        namespace = body['metadata']['namespace']
        return namespace, name, sender, receiver, unidirectional
    except KeyError as e:
        raise kopf.PermanentError(f'Invalid link "{name}"') from e


def build_labels(node, value):
    return {"metadata": {"labels": {
        f"send-node-{node}": value,
        f"receive-node-{node}": value,
    }}}


@kopf.on.create(RESOURCE)
def create(body, **kwargs) -> None:
    namespace, name, sender, receiver, unidirectional = get_link_metadata(body)

    logging.info(f'Link "{name}" ({sender} -> {receiver})  is created on namespace "{namespace}"')
    logging.debug(body)

    # Chaos experiment
    logging.info(
        f'Creating link "{name}" ({sender} -> {receiver})  on namespace "{namespace}" with parameters "{body.spec}"')
    direction = 'to' if unidirectional else 'both'
    crd = templates.chaos_link(name=name, namespace=namespace, sender=sender, receiver=receiver, direction=direction)
    # Check if there is a fault to apply
    has_fault = False
    if 'bandwidth' in body.spec:
        has_fault = True
        crd['spec']['action'] = 'bandwidth'
        crd['spec']['bandwidth'] = body.spec['bandwidth']
    else:
        crd['spec']['action'] = 'netem'
        for action in ['delay', 'loss', 'duplicate', 'corrupt']:
            if action in body.spec:
                has_fault = True
                crd['spec'][action] = body.spec[action]
    if has_fault:
        # Only create the chaos experiment if there is a fault to apply
        group, version = crd['apiVersion'].split('/')
        kopf.adopt(crd)
        k8s.crd.create_namespaced_custom_object(group, version, namespace, 'networkchaos', crd)

    # Label the pods to enable the service and exception to the network policy
    pod_sender = k8s.core.list_namespaced_pod(namespace=namespace, label_selector=f'node={sender}')
    for pod in pod_sender.items:
        patch = build_labels(receiver, "enabled")
        if unidirectional:
            del patch["metadata"]["labels"][f"receive-node-{receiver}"]
        k8s.core.patch_namespaced_pod(pod.metadata.name, namespace, patch)

    pod_receiver = k8s.core.list_namespaced_pod(namespace=namespace, label_selector=f'node={receiver}')
    for pod in pod_receiver.items:
        patch = build_labels(sender, "enabled")
        if unidirectional:
            del patch["metadata"]["labels"][f"send-node-{sender}"]
        k8s.core.patch_namespaced_pod(pod.metadata.name, namespace, patch)


@ kopf.on.delete(RESOURCE)
def delete(body, **kwargs):
    namespace, name, sender, receiver, unidirectional = get_link_metadata(body)

    logging.info(f'Link "{name}" ({sender} -> {receiver})  is deleted on namespace "{namespace}"')
    logging.debug(body)

    # Reset labels
    pod_sender = k8s.core.list_namespaced_pod(namespace=namespace, label_selector=f'node={sender}')
    for pod in pod_sender.items:
        patch = build_labels(receiver, None)
        if unidirectional:
            del patch["metadata"]["labels"][f"receive-node-{receiver}"]
        k8s.core.patch_namespaced_pod(pod.metadata.name, namespace, patch)

    pod_receiver = k8s.core.list_namespaced_pod(namespace=namespace, label_selector=f'node={receiver}')
    for pod in pod_receiver.items:
        patch = build_labels(sender, None)
        if unidirectional:
            del patch["metadata"]["labels"][f"send-node-{sender}"]
        k8s.core.patch_namespaced_pod(pod.metadata.name, namespace, patch)
