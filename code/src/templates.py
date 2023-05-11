from os import path
from string import Template

import yaml

templates_dir = path.join(path.dirname(__file__), 'templates')


def load(name: str, variables):
    """
    Load a template file and replace the placeholders with the given.
    """
    file = path.join(templates_dir, name)
    with open(file, 'r') as template:
        contents = template.read()
        replaced = Template(contents).substitute(**variables)
        return list(yaml.safe_load_all(replaced))


# Iluzio
def iluzio_node(*, id: str):
    """
    Load the iluzio node template.
    This includes the deployment, service and network policy.
    """
    return load('iluzio/node.yaml', {'id': id})[0]


def iluzio_link(*, id: str):
    """
    Load the iluzio link template.
    """
    return load('iluzio/link.yaml', {'id': id})[0]


# Native
def native_node(*, id: str, image: str, resources: str) -> tuple[str, str, str]:
    """
    Load the node template.
    This includes the deployment, service and network policy.
    """
    return load('native/node.yaml', {'id': id, 'image': image, 'resources': resources})


# Chaos
def chaos_link(*, name: str, namespace: str, sender: str, receiver: str, direction: str):
    """
    Load the chaos link template.
    This includes the link and the service.
    """
    return load('chaos/link.yaml', {'name': name, 'namespace': namespace, 'sender': sender, 'receiver': receiver, 'direction': direction})[0]
