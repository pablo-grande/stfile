# -*- coding: utf-8 -*
import os
from sys import exit
from rdflib import Graph
from rdflib import BNode
from rdflib import Literal
from rdflib.plugins.sparql import prepareQuery
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
    from rdflib import Namespace

    namespaces = {}
    for k,v in CONFIG['prefixes'].items():
        namespaces[k] = Namespace(v)
    print(statement)
    rows = graph.query(prepareQuery(statement, initNs=namespaces))
    return [r for r in rows]


def serialize(format_as='n3'):
    return graph.serialize(format=format_as).decode('utf-8')


def get_nodes_with(tags):
    """List all nodes with matching tags.

    Retrieves node's labels with the given tags as subject. Maps with the label
    of the given namespace, if not found the key will be the tag in the list.
    Iterates over predicate object triples of given tags in order to fill
    information about the subject, all its predicates and objects.
    Iterates over subject objects triples in case of predicate and returns
    connections between subjects and objects through that edge.

    Args:
        A list of concepts to fill the <object> placeholder in a <subject>,
        <predicate>, <object> triple.

    Returns:
        A dictionary mapping the tag with a list of labels of the object(s) found.
    """
    results = {}
    for index, tag in enumerate(_ns_tags(tags)):
        repr_tag = str(graph.label(tag))
        if repr_tag == '':
            repr_tag = tags[index]

        results[repr_tag] = {}

        for subject in graph.subjects(None, tag):
            repr_subject = str(graph.label(subject))
            if repr_subject != '':
                predicate_objects = {}
                for predicate, object in graph.predicate_objects(subject):
                    # check if there is label for predicate
                    repr_predicate = str(graph.label(predicate))
                    if repr_predicate == '':
                        # by default it would get the word after # from an URI
                        predicate_name = str(predicate).split('#')
                        if len(predicate_name) == 1:
                            # try a regular '/' if no '#' was found
                            predicate_name = str(predicate).split('/')
                        repr_predicate = predicate_name[-1]

                    repr_object = str(graph.label(object))
                    if repr_object == '':
                        repr_object = str(object)

                    if predicate_objects.get(repr_predicate):
                        predicate_objects[repr_predicate].append(repr_object)
                    else:
                        predicate_objects[repr_predicate] = [repr_object]

                    results[repr_tag].update({repr_subject: predicate_objects})


        # get predicate info
        predicate_objects = set()
        for subject, object in graph.subject_objects(tag):
            repr_subject = str(graph.label(subject))
            if repr_subject == '':
                repr_subject = subject
            repr_object = str(graph.label(object))
            if repr_object == '':
                repr_object = object
            predicate_objects.update({repr_object})
            results[repr_tag].update({repr_subject: predicate_objects})

    return results


def get_node_by_label(label):
    found, node = False, BNode()
    search_label = Literal(label, datatype=NS['xsd']+'string')
    for s in graph.subjects(NS['rdfs']+'label', search_label):
        found, node = True, s

    return found, node


# create global variable for dictionary structure that will contain
# {node id: (path or filename, nfo tag of node type=}
# useful to subscribed services
node_path = {}

def tag(path, tags):
    """Applies tags on the given path in graph.

    Given a path finds or creates a file or folder instance into the graph and
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
        from stfile.agents.file_format import action
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
            graph.add((directory['node'], NS['']+'isLocationOf', _file))
            action(graph, NS, {_file: full_path})

        apply_tags(_file, tags)
        global node_path
        node_path.update({_file: full_path})


    ns_tags = _ns_tags(tags)
    if os.path.isfile(path):
        # Set directoy node to None but same method below can pass correct node
        directory = {'node': None, 'path': '/'.join(os.path.abspath(path).split('/')[:-1])}
        tag_file(directory, os.path.basename(path), ns_tags)

    global node_path
    for root, _, files in os.walk(path):
        dir_path = os.path.abspath(root)
        found, _dir = get_node_by_label(dir_path)

        if not found:
            graph.add((_dir, NS['a'], NS['nfo']+'Folder'))
            literal_dir_path = Literal(dir_path, datatype=NS['xsd']+'string')
            graph.set((_dir, NS['rdfs']+'label', literal_dir_path))
            graph.set((_dir, NS['']+'path', literal_dir_path))

        apply_tags(_dir, ns_tags)
        node_path.update({_dir: dir_path})

        for file_name in files:
            directory = {'node': _dir, 'path': dir_path}
            tag_file(directory, file_name, ns_tags)

    # apply actions to graph from subscribed agents
    for tag, actions in CONFIG['tags_actions'].items():
        if tag in tags:
            for action in actions:
                action(graph, NS, node_path)

    graph.serialize(CONFIG['graph_file'], format='xml')
