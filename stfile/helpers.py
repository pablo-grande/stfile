# -*- coding: utf-8 -*
import os
import fleep
from yaml import load
from rdflib.namespace import Namespace


_current_dir = os.path.join(os.path.dirname(__file__))


def set_up():
    config = {}

    with open(_current_dir + '/config.yml', 'r') as conf:
        config = load(conf)
        config['namespaces'] = {k: Namespace(v).term('') for k,v in config['namespaces'].items()}

    config['graph_file'] = _current_dir + '/.graph'
    config['base_ontology'] = _current_dir + '/ontologies/file_system.owl'

    return config, os.path.exists(config['graph_file'])


def get_meta_info(filename):
    try:
        with open(filename, 'rb') as f:
            info = fleep.get(f.read(128))
        type, extension = info.type[0], info.extension[0]
    except IndexError:
        if len(info.type) == 0:
            type = None
        if len(info.extension) == 0:
            extension = None
    finally:
        return type, extension
