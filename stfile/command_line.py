# -*- coding: utf-8 -*
import argparse
from pprint import pprint
from . import *


def main():
    parser = argparse.ArgumentParser(prog='stf', description='Work with ontologies')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    subparsers = parser.add_subparsers(dest="subparser")

    parser_query = subparsers.add_parser('query', description='Execute raw SPARQL query')
    group = parser_query.add_mutually_exclusive_group(required=True)
    group.add_argument('-q','--query', help='raw SPARQL query', nargs='+')
    group.add_argument('-i','--input', help='input file', type=argparse.FileType('r'))
    parser_query.add_argument('-o','--output', help='output file', type=argparse.FileType('w', encoding='UTF-8'))

    parser_tag = subparsers.add_parser('tag', description='Apply tags to the given path')
    parser_tag.add_argument('path', help='path to run the command', type=str)
    parser_tag.add_argument('tags', help='tags to apply in a <prefix>:<suffix> format', nargs='+')

    parser_list = subparsers.add_parser('list', description='List all instances of a given tag')
    parser_list.add_argument('tags', help='tags to search in a <prefix>:<suffix> format', nargs='+')

    parser_show = subparsers.add_parser('show', description='Shows whole graph')
    parser_show.add_argument('-f', '--format', help='Format of serialization of graph', default='n3', choices=['n3','xml','pretty-xml','nt'])

    args = parser.parse_args()
    subparser = args.subparser


    if subparser == 'query':
        query_results = ""
        if args.query:
            query_results = query(' '.join(args.query))
        if args.input:
            with args.input as f:
                query_results = query(f.read())

        if args.output:
            with args.output as o:
                o.write('\n'.join(query_results))
        else:
            print('\n'.join(query_results))

    elif subparser == 'tag':
        tag(args.path, args.tags)

    elif subparser == 'list':
        results = get_subjects_with(args.tags)
        if all(len(value) == 0 for value in results.values()):
            print("No match was found")
        else:
            pprint(results)

    elif subparser == 'show':
        print(serialize(args.format))
