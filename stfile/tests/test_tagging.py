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

    def test_1_tag(self):
        stfile.tag(self.folder, [':AlbumFolder'])
        elements = stfile.get_subjects_with([':AlbumFolder'])

        # :AlbumFolder has a label of just 'AlbumFolder'
        values = elements['AlbumFolder']

        self.assertTrue(set(self.contents) <= set(values))
