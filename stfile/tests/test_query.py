from unittest import TestCase

import stfile


class TestQuery(TestCase):
    type, owl_class = stfile.NS['rdf']+'type', stfile.NS['owl']+'Class'
    classes = [(s,) for s in stfile.graph.subjects(type, owl_class)]

    def test_query(self):
        statement = """
        SELECT ?s WHERE { ?s rdf:type owl:Class }
        """
        self.assertEqual(stfile.query(statement), self.classes)
