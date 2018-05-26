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
graph = Graph()

graph.parse(CONFIG['base_ontology'])
if _load:
    graph.load(CONFIG['graph_file'])


NS = {} #short for namespaces
for _prefix, _uri in graph.namespace_manager.namespaces():
    NS[_prefix] = _uri

if CONFIG.get('prefixes'):
    NS.update(CONFIG['prefixes'])


def _ns_tags(concepts):
    _concepts = [word.split(':') for word in concepts]
    try:
        return [NS[p_s[0].lower()] + p_s[1] for p_s in _concepts]
    except KeyError as error:
        exit("ERROR: Not a valid key for registered namespaces -> {0}".format(error))


def query(statement):
    rows = graph.query(prepareQuery(statement))
    return '\n'.join([str(r) for r in rows])


def serialize(format_as='n3'):
    return graph.serialize(format=format_as).decode('utf-8')


def get_subjects_with(tags):
    """List all subjects with matching tags.

    Retrieves subject's labels with the given tags as objects in a triple from
    the graph. Tries to map with the label of the given namespace, if not found
    the key will be the given tag in the list.

    Args:
    tags: A list of concepts to fill the <object> placeholder in a <subject>,
        <predicate>, <object> triple.

    Returns:
        A dictionary mapping the tag with a list of labels of the object(s) found.
    """
    results = {}
    for index, tag in enumerate(_ns_tags(tags)):
        key = str(graph.label(tag))
        if key == '':
            key = tags[index]
        results[key] = []

        for subject in graph.subjects(None, tag):
            label = graph.label(subject)
            if label != '':
                results[key].append(str(label))

    return results


def get_node_by_label(label):
    found, node = False, BNode()
    search_label = Literal(label, datatype=NS['xsd']+'string')
    for s in graph.subjects(NS['rdfs']+'label', search_label):
        found, node = True, s

    return found, node



def tag(path, tags):
    """Applies tags on the given path in graph.

    Given a path it creates a file or folder instance into the graph and then
    applies the tags to the node. In case of folder, it applies the same
    tags to all its files inside.
    Tryies to find nodes by labels to prevent adding same node with same info
    to graph.

    Args:
        path: File or folder path to get all the data needed to create a new
            node.
        tags: A list of concepts to apply to the node.
    """
    def apply_tags(subject, tags):
        for tag in tags:
            graph.add((subject, NS['a'], tag))


    def tag_file(directory, file_name, tags):
        full_path = os.path.join(directory['path'], file_name)
        found, _file = get_node_by_label(file_name)

        if not found:
            graph.add((_file, NS['a'], NS['nfo']+'FileDataObject'))
            literal_file_name = Literal(file_name, datatype=NS['xsd']+'string')
            graph.set((_file, NS['rdfs']+'label', literal_file_name))
            graph.set((_file, NS['nfo']+'fileName', literal_file_name))
            graph.set(
                (_file, NS['nfo']+'fileSize',
                Literal(os.path.getsize(full_path), datatype=NS['xsd']+'bytes')))

            if not directory['node']:
                _, directory['node'] = get_node_by_label(directory['path'])
            graph.set((_file, NS['']+'location', directory['node']))

            _, file_format = get_meta_info(full_path)
            if file_format:
                graph.set((_file, NS['']+'fileFormat', NS['']+file_format.upper()))

        apply_tags(_file, tags)


    ns_tags = _ns_tags(tags)
    if os.path.isfile(path):
        # Set directoy node to None but same method below can pass correct node
        directory = {'node': None, 'path': '/'.join(os.path.abspath(path).split('/')[:-1])}
        tag_file(directory, os.path.basename(path), ns_tags)

    for root, _, files in os.walk(path):
        dir_path = os.path.abspath(root)
        found, _dir = get_node_by_label(dir_path)

        if not found:
            graph.add((_dir, NS['a'], NS['nfo']+'Folder'))
            literal_dir_path = Literal(dir_path, datatype=NS['xsd']+'string')
            graph.set((_dir, NS['rdfs']+'label', literal_dir_path))
            graph.set((_dir, NS['']+'path', literal_dir_path))

        apply_tags(_dir, ns_tags)
        for file_name in files:
            directory = {'node': _dir, 'path': dir_path}
            tag_file(directory, file_name, ns_tags)

    graph.serialize(CONFIG['graph_file'], format='xml')
