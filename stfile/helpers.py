import os
from yaml import load
from rdflib.namespace import Namespace
from importlib import import_module


_current_dir = os.path.join(os.path.dirname(__file__))
DEFAULT_GRAPH = _current_dir + '/.graph'
DEFAULT_ONTOLOGY = _current_dir + '/ontologies/file_system.owl'
MO_ONTOLOGY = '/home/pablo/Documents/movieontology.owl'


def set_up():
    config = {}

    with open(_current_dir + '/config.yml', 'r') as conf:
        config = load(conf)
        config['prefixes'] = {k: Namespace(v).term('') for k,v in config['prefixes'].items()}

    if not config.get('graph_file'):
        config['graph_file'] = DEFAULT_GRAPH

    if not config.get('base_ontology'):
        config['base_ontology'] = DEFAULT_ONTOLOGY

    tags_actions = {}
    for service, tags in config['agents'].items():
        try:
            service_module = import_module('stfile.agents.' + service)
            action = service_module.action
        except ImportError as e:
            continue

        for tag in tags:
            if tag in tags_actions:
                tags_actions[tag].add(action)
            else:
                tags_actions[tag] = set()
                tags_actions[tag].add(action)

    config['tags_actions'] = tags_actions

    return config, os.path.exists(config['graph_file'])
