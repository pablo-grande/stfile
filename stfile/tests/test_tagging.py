from unittest import TestCase

import os
import stfile


class TestTagging(TestCase):
    def setUp(self):
        self.folder = os.path.expanduser('~')+'/Music'
        contents = []
        for root, _, files in os.walk(self.folder):
            contents.append(root)
            for f in files:
                contents.append(f)

        self.contents = contents


    def test_get_node_by_label(self):
        tag = ['nfo:Folder']
        stfile.tag(self.folder, tag)
        found, node = stfile.get_node_by_label(self.folder)

    def test_tag_1(self):
        tag = [':AlbumFolder']
        stfile.tag(self.folder, tag)
        elements = stfile.get_nodes_with(tag)
        # :AlbumFolder has a label of just 'AlbumFolder'
        self.assertTrue(set(self.contents) <= set(elements['AlbumFolder']))

    def test_tag_2(self):
        tags = [':AlbumFolder', ':MusicAlbum']
        stfile.tag(self.folder, tags)
        elements = stfile.get_nodes_with(tags)
        self.assertTrue(set(self.contents) <= set(elements['AlbumFolder']))
        self.assertTrue(set(self.contents) <= set(elements['MusicAlbum']))

    def test_prevent_duplicate(self):
        tag = [':AlbumFolder']
        stfile.tag(self.folder, tag)
        elements = stfile.get_nodes_with(tag)
        stfile.tag(self.folder, tag)
        elements_2 = stfile.get_nodes_with(tag)
        self.assertEqual(len(elements['AlbumFolder']), len(elements_2['AlbumFolder']))


    def tearDown(self):
        os.remove('stfile/.graph')
