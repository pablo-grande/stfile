import fleep


def action(graph, namespaces, node_path):
    for node, path in node_path.items():
        try:
            with open(path, 'rb') as f:
                info = fleep.get(f.read(128))
            type, extension = info.type[0], info.extension[0]
            graph.add((node, namespaces['a'], namespaces['nfo']+type.title()))
            graph.set((node, namespaces['']+'fileFormat', namespaces['']+extension.upper()))
        except IndexError as e:
            print("ERROR: Agent file_format could not guess type or extension for", path)
            continue
