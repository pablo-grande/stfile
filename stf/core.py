# -*- coding: utf-8 -*
import os
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery


graph = Graph()
with open(os.path.join(os.path.dirname(__file__)) + '/ontologies/file_system.owl', 'r') as fs:
    graph.parse(fs)


def query(statement):
    q = prepareQuery(statement)
    rows = graph.query(q)
    return '\n'.join([str(r) for r in rows])

