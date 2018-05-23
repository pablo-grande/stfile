# -*- coding: utf-8 -*
import os
import fleep
from yaml import load
from rdflib.namespace import Namespace


_current_dir = os.path.join(os.path.dirname(__file__))
DEFAULT_GRAPH = _current_dir + '/.graph'
DEFAULT_ONTOLOGY = _current_dir + '/ontologies/file_system.owl'


def set_up():
    config = {}

    with open(_current_dir + '/config.yml', 'r') as conf:
        config = load(conf)
        config['namespaces'] = {k: Namespace(v).term('') for k,v in config['namespaces'].items()}

    if not config.get('graph_file'):
        config['graph_file'] = DEFAULT_GRAPH

    if not config.get('base_ontology'):
        config['base_ontology'] = DEFAULT_ONTOLOGY

    return config, os.path.exists(config['graph_file'])


def get_meta_info(filename):
    try:
        type, extension = None, None
        with open(filename, 'rb') as f:
            info = fleep.get(f.read(128))
        type, extension = info.type[0], info.extension[0]
    finally:
        return type, extension
