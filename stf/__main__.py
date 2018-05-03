# -*- coding: utf-8 -*
import argparse
import core


parser = argparse.ArgumentParser(prog='stf', description='Work with ontologies', add_help=False)
parser.add_argument('--version', action='version', version='%(prog)s 0.1')

subparsers = parser.add_subparsers()
parser_query = subparsers.add_parser('query', description='Execute raw SPARQL query', aliases=['q','sparql'])
group = parser_query.add_mutually_exclusive_group(required=True)
group.add_argument('-q','--query', help='raw SPARQL query', nargs='+')
group.add_argument('-i','--input', help='input file', type=argparse.FileType('r'))
parser_query.add_argument('-o','--output', help='output file', type=argparse.FileType('w', encoding='UTF-8'))


args = parser.parse_args()
query_results = ""
if args.query:
    query_results = core.query(' '.join(args.query))
if args.input:
    with args.input as f:
        query_results = core.query(f.read())

if args.output:
    with output as o:
        o.write(query_results)
else:
    print(query_results)

