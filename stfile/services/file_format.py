import fleep


def action(graph, namespaces, node_path):
    for node, path in node_path.items():
        print("tagging ", node, ": ", path)
        try:
            with open(path, 'rb') as f:
                info = fleep.get(f.read(128))
            type, extension = info.type[0], info.extension[0]
            print("Extension was found ", extension)
            print("Type was ",type)
            print("Setting ",node, " with ", namespaces['']+'fileFormat', namespaces['']+extension.upper())
            graph.set((node, namespaces['a'], namespaces['nfo']+type.title()))
            graph.set((node, namespaces['']+'fileFormat', namespaces['']+extension.upper()))
        except e:
            print(e)
            continue
