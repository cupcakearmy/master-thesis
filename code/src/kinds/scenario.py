import asyncio
import logging

import kopf

import k8s
import templates
import utils

RESOURCE = 'scenarios.' + utils.GROUP


@kopf.on.create(RESOURCE)
def create(body, patch, **kwargs):
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']
    logging.info(f'scenario "{name}" is created on namespace "{namespace}"')


@kopf.on.delete(RESOURCE)
def delete(body, **kwargs):
    name = body['metadata']['name']
    logging.info(f'scenario "{name}" is deleted')


@kopf.daemon(RESOURCE, cancellation_timeout=1)
async def daemon(meta, status, spec, **kwargs):
    try:
        while True:
            try:
                if status['ended']:
                    return
            except KeyError:
                pass

            name = meta['name']
            namespace = meta['namespace']

            def patch(body):
                k8s.crd.patch_namespaced_custom_object(
                    utils.GROUP, utils.VERSION, namespace, 'scenarios', name, {'status': body})

            def with_prefix(id: str) -> str:
                return f'{name}-{id}'

            now = utils.timestamp_ms()
            try:
                started = status['started']
            except KeyError:
                patch({'started': now})
                logging.info('waiting for scenario to start...')
                await asyncio.sleep(0.1)
                continue

            # Time since the scenario started
            elapsed = now - started
            logging.info(f'elapsed: {elapsed}')
            logging.debug(status)
            # Calculate when the next run should be executed, based on future events
            next_run = None
            for i, event in enumerate(spec['events']):
                offset = (event['offset'] or 0) * 1000
                delta = offset - elapsed
                if delta > 0:
                    if next_run is None or delta < next_run:
                        next_run = delta
                    continue
                try:
                    s = status['events'][str(i)]
                    executed = s['executed']
                except KeyError:
                    executed = False
                if not executed:
                    # Execute event
                    logging.info(f'executing event {i}')
                    patch({'events': {i: {'executed': True, 'timestamp': now}}})
                    action = event['action']

                    if action == 'end':
                        # End scenario
                        logging.info(f'ending scenario {event}')
                        patch({'ended': now})
                        return

                    # NODE
                    elif event['resource'] == 'node':
                        ID = with_prefix(event['id'])
                        if action == 'create':
                            # Create node
                            logging.info(f'creating node {event}')
                            body = templates.iluzio_node(id=ID)
                            body['spec'] = event['spec']
                            kopf.adopt(body)
                            k8s.crd.create_namespaced_custom_object(
                                utils.GROUP, utils.VERSION, namespace, 'nodes', body)

                        elif action == 'delete':
                            # Delete node
                            logging.info(f'deleting node {event}')
                            k8s.crd.delete_namespaced_custom_object(
                                utils.GROUP, utils.VERSION, namespace, 'nodes', ID)

                        else:
                            logging.error(f'unknown action {action}')

                    # LINK
                    elif event['resource'] == 'link':
                        ID = '-'.join(map(lambda x: event[x], ['from', 'to', 'direction']))
                        ID = with_prefix(ID)
                        if action == 'create':
                            # Create links
                            logging.info(f'creating link {event}')
                            body = templates.iluzio_link(id=ID)
                            body['spec'].update(event['spec'])
                            body['spec']['from'] = with_prefix(event['from'])
                            body['spec']['to'] = with_prefix(event['to'])
                            body['spec']['direction'] = event['direction']
                            kopf.adopt(body)
                            k8s.crd.create_namespaced_custom_object(
                                utils.GROUP, utils.VERSION, namespace, 'links', body)

                        elif action == 'delete':
                            # Delete link
                            logging.info(f'deleting link {event}')
                            k8s.crd.delete_namespaced_custom_object(
                                utils.GROUP, utils.VERSION, namespace, 'links', ID)

                        else:
                            logging.error(f'unknown action {action}')

                    else:
                        logging.error(f'unknown resource {event["resource"]}')

            if next_run is None:
                logging.error('no next run could be calculated')
                return
            logging.info(f'waiting for next run in {next_run} ms')
            await asyncio.sleep(next_run / 1000)

    except asyncio.CancelledError:
        logging.info('cancellation requested')
