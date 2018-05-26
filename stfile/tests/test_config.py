from unittest import TestCase

import stfile
import stfile.helpers as helpers


class TestConfig(TestCase):
    def test_set_up(self):
        config, _ = helpers.set_up()
        self.assertIsInstance(config, dict)
        self.assertIsNotNone(config.get('graph_file'))
        self.assertIsNotNone(config.get('base_ontology'))
        self.assertIsNotNone(config.get('prefixes'))
        self.assertEqual(config.get('language'), 'en')
