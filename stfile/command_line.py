# -*- coding: utf-8 -*
import argparse
from pprint import pprint
from os.path import exists
from . import *


def quick_query(args):
    # get (option, full statement) tuple combination by selecting the first element from the args dictionary
    # that has a type list in its value. Build the statement by joining all elements in that list
    selected_option, statement = [(option[0], ' '.join(option[1])) for option in args._get_kwargs() if type(option[1]) is list][0]
    options = {
            'select': 'SELECT ' + statement + ' ',
            'construct': 'CONSTRUCT { ' + statement + ' } ',
            'describe': 'DESCRIBE ' + statement + ' ',
            'ask': 'ASK WHERE { ' + statement + ' } ',
            }

    quick_query = options[selected_option]

    # check for WHERE statement and discard it if ASK was supplied because of redundancy
    if args.where and not args.ask:
        quick_query += 'WHERE { ' + ' '.join(args.where) + ' } '

    return quick_query


def main():
    parser = argparse.ArgumentParser(prog='stf', description='stfile lets you use semantics to tag folders and files')
    subparsers = parser.add_subparsers(dest="subparser")

    parser_query = subparsers.add_parser('query', description='Run a SPARQL query onto graph')
    query_group = parser_query.add_mutually_exclusive_group(required=True)

    quick_group = query_group.add_mutually_exclusive_group()
    quick_group.add_argument('-s','--select', help='Select query', nargs='+')
    quick_group.add_argument('-c','--construct', help='Construct query', nargs='+')
    quick_group.add_argument('-d','--describe', help='Describe query', nargs='+')
    quick_group.add_argument('-a','--ask', help='Ask query', nargs='+')

    raw_group = query_group.add_mutually_exclusive_group()
    raw_group.add_argument('-r','--raw', help='Raw SPARQL query', nargs='+')
    raw_group.add_argument('-i','--input', help='Input file to read SPARQL query from', type=argparse.FileType('r'))

    parser_query.add_argument('-w','--where', help='Where statement', nargs='+')
    parser_query.add_argument('-o','--output', help='Output file to print query results', type=argparse.FileType('w', encoding='UTF-8'))


    parser_tag = subparsers.add_parser('tag', description='Apply tags to the given path')
    parser_tag.add_argument('path', help='Path to run the command', type=str)
    parser_tag.add_argument('tags', help='Tags to apply in a <prefix>:<suffix> format', nargs='+')


    parser_list = subparsers.add_parser('list', description='List all instances of a given tag')
    parser_list.add_argument('tags', help='Tags to search in a <prefix>:<suffix> format', nargs='+')


    parser_show = subparsers.add_parser('show', description='Shows whole graph')
    parser_show.add_argument('-f', '--format', help='Format of serialization of graph', default='n3', choices=['n3','xml','pretty-xml','nt'])


    args = parser.parse_args()
    subparser = args.subparser


    if subparser == 'query':
        query_results = ""
        if args.raw:
            query_results = query(' '.join(args.query))
        elif args.input:
            with args.input as f:
                query_results = query(f.read())
        else:
            query_input = quick_query(args)
            try:
                query_results = query(query_input)
            except Exception as e:
                print("ERROR: Something went wrong with query '{}'. {}".format(query_input, e))

        if len(query_results):
            if args.output:
                with args.output as o:
                    o.write(str(query_results))
            else:
                for r in query_results:
                    print(str(r))

    elif subparser == 'tag':
        if exists(args.path):
            tag(args.path, args.tags)
        else:
            print("ERROR: Path provided \"{}\" does not exists".format(args.path))

    elif subparser == 'list':
        results = get_nodes_with(args.tags)
        if all(len(value) == 0 for value in results.values()):
            print("No match was found")
        else:
            pprint(results, width=100)

    elif subparser == 'show':
        print(serialize(args.format))
