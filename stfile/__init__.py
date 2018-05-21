# -*- coding: utf-8 -*
import os
from sys import exit
from rdflib import Graph
from rdflib import BNode
from rdflib import Literal
from rdflib.plugins.sparql import prepareQuery
from .helpers import get_meta_info
from .helpers import set_up


CONFIG, _load = set_up()
GRAPH = Graph()

if _load:
    GRAPH.load(CONFIG['graph_file'])
else:
    GRAPH.parse(CONFIG['base_ontology'])

NS = {}
for _prefix, _uri in GRAPH.namespace_manager.namespaces():
    NS[_prefix] = _uri

if CONFIG.get('namespaces'):
    NS.update(CONFIG['namespaces'])


def _ns_tags(concepts):
    _concepts = [word.split(':') for word in concepts]
    try:
        return [NS[p_s[0].lower()] + p_s[1] for p_s in _concepts]
    except KeyError as error:
        exit("ERROR: Not a valid key for registered namespaces -> {0}".format(error))


def query(statement):
    rows = GRAPH.query(prepareQuery(statement))
    return '\n'.join([str(r) for r in rows])


def serialize(format_as='n3'):
    return GRAPH.serialize(format=format_as).decode('utf-8')


def get_subjects_with(tags):
    """List all subjects with matching tags.

    Retrieves subject's labels with the given tags as objects in a triple from
    the GRAPH. Tries to map with the label of the given namespace, if not found
    the key will be the given tag in the list.

    Args:
    tags: A list of concepts to fill the <object> placeholder in a <subject>,
        <predicate>, <object> triple.

    Returns:
        A dictionary mapping the tag with a list of labels of the object(s) found.
    """
    results = {}
    for index, tag in enumerate(_ns_tags(tags)):
        key = str(GRAPH.label(tag))
        if key == '':
            key = tags[index]
        results[key] = []
        
        for subject in GRAPH.subjects(None, tag):
            label = GRAPH.label(subject)
            if label != '':
                results[key].append(str(label))

    return results


def tag(path, tags):
    """Applies tags on the given path in GRAPH.

    Given a path it creates a file or folder instance into the GRAPH and then
    applies the tags to the node. In case of folder node, it applies the same
    tags to all its files inside.

    Args:
        path: File or folder path to get all the data needed to create a new
            node.
        tags: A list of concepts to apply to the node.
    """
    def _apply_tags(subject, tags):
        for tag in tags:
            GRAPH.add((subject, NS['a'], tag))

    def _tag_file(directory, file_name, tags):
        full_path = os.path.join(directory['path'], file_name)
        _, file_format = get_meta_info(full_path)
        _file = BNode()
        _apply_tags(_file, tags)
        GRAPH.add((_file, NS['a'], NS['nfo']+'FileDataObject'))
        GRAPH.set((_file, NS['rdfs']+'label', Literal(file_name, datatype=NS['xsd']+'string')))
        GRAPH.set((_file, NS['nfo']+'fileName', Literal(file_name, datatype=NS['xsd']+'string')))
        GRAPH.set((_file, NS['nfo']+'fileSize', Literal(os.path.getsize(full_path), datatype=NS['xsd']+'bytes')))
        GRAPH.set((_file, NS['']+'location', directory['node']))
        GRAPH.set((_file, NS['']+'fileFormat', NS['']+file_format.upper()))

    ns_tags = _ns_tags(tags)
    if os.path.isfile(path):
        dir_path = '/'.join(os.path.abspath(path).split('/')[:-1])
        _tag_file({'node': BNode(), 'path': dir_path}, os.path.basename(path), ns_tags)

    for root, _, files in os.walk(path):
        dir_path = os.path.abspath(root)
        _dir = BNode()
        _apply_tags(_dir, ns_tags)
        GRAPH.add((_dir, NS['a'], NS['nfo']+'Folder'))
        GRAPH.set((_dir, NS['rdfs']+'label', Literal(dir_path, datatype=NS['xsd']+'string')))
        GRAPH.set((_dir, NS['']+'path', Literal(dir_path, datatype=NS['xsd']+'string')))

        for file_name in files:
            _tag_file({'node': _dir, 'path': dir_path}, file_name, ns_tags)

    GRAPH.serialize(CONFIG['graph_file'], format='xml')
