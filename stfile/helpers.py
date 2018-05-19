# -*- coding: utf-8 -*
import os
import fleep


def get_current_dir():
    return os.path.join(os.path.dirname(__file__))


def prefix_suffix(lst):
    return [word.split(':') for word in lst]


def get_meta_info(filename):
    with open(filename, 'rb') as f:
        info = fleep.get(f.read(128))

    return info.type[0], info.extension[0]
