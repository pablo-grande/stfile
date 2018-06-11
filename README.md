# stfile

Python wrapper for RDFLib applied to a file system ontology.

## Getting started
stfile lets you use semantics to tag folders and files.

Tag your files:
```
stf tag path tags [tags ...]
```

List files by given tags:
```
stf list tags [tags ...]
```


### Installing
Use pip to install stfile
```
pip install stfile
```

You can now run the `stf` command or import stfile itself to develop your own stuff.

### Enhance Your Files

Use stfile to develop your own services. Add a Python script on the config file "config.yml" and attach tags.
```
services:
  my-service:
    - <my>:<super_useful_tag>
```
Every time stfile finds a tag attached to a service executes the script with the same name inside the `services/` folder.

A service must implement a `action(graph, namespaces, node_path_dictionary)` function.
* __graph__: A RDFLib Graph instance, contains all current information about the semantic file system
* __namespaces__: A dictionary containing all registered namespaces inside graph
* __node_path_dictionary__: Contains information about the nodes in a `node: path` fashion.

All namespaces included in config.yml will be loaded into the graph to offer basic covering for the file system ontology, but more can be added in order to develop services.

## Semantics

If you wish to have a better perspective about the graph
```
stf show [-h] [-f {n3,xml,pretty-xml,nt}]

Shows whole graph

optional arguments:
  -h, --help            show this help message and exit
  -f {n3,xml,pretty-xml,nt}, --format {n3,xml,pretty-xml,nt}
                        Format of serialization of graph
```

### SPARQL
stfile lets you write SPARQL queries directly to your graph
```
stf query [-h] ([-s SELECT [SELECT ...] | -c CONSTRUCT [CONSTRUCT ...]
                 | -d DESCRIBE [DESCRIBE ...] | -a ASK [ASK ...]]
                 [-r RAW [RAW ...] | -i INPUT] [-w WHERE [WHERE ...]]
                 [-o OUTPUT]

Execute raw SPARQL query

optional arguments:
  -h, --help            show this help message and exit
  -s SELECT [SELECT ...], --select SELECT [SELECT ...]
                        Select query
  -c CONSTRUCT [CONSTRUCT ...], --construct CONSTRUCT [CONSTRUCT ...]
                        Construct query
  -d DESCRIBE [DESCRIBE ...], --describe DESCRIBE [DESCRIBE ...]
                        Describe query
  -a ASK [ASK ...], --ask ASK [ASK ...]
                        Ask query
  -r RAW [RAW ...], --raw RAW [RAW ...]
                        Raw SPARQL query
  -i INPUT, --input INPUT
                        input file
  -w WHERE [WHERE ...], --where WHERE [WHERE ...]
                        Where statement
  -o OUTPUT, --output OUTPUT
                        output file
```
