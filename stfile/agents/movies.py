"""
Movies integration agent

Connects with OMDb to get info about a movie.
Populate into graph using movie ontology.

Refs:
    * OMDb: http://www.omdbapi.com/
    * OMDb example http://www.omdbapi.com/?t=<title>
"""
def get_movie_info(title):
    from os import getenv
    from requests import get

    OMDb_key = getenv('OMDb_key')
    OMDb_url = 'http://www.omdbapi.com/'
    OMDb_params = {'apikey': OMDb_key, 't': title}

    data = get(OMDb_url, params=OMDb_params).json()

    if data['Response'] == "False":
        return False, data['Error']
    return True, data


def get_title_from_path(path):
    """Build title of movie from its path

    Given a full path it splits in several ways to get only the name of the
    current file: <path>filename<.format>

    HACK PENDING:
    This is a HUGE restriction, movie's titles should be guessed by other means
    than its filename.
    """
    title = path.split('/')[-1].split('.')[:-1]
    if type(title) is list:
        # special case if filename has '.' characters
        title = ' '.join(title)
    return title


def action(graph, NS, node_path):
    from rdflib import Namespace, Literal, BNode
    MO = Namespace('http://www.movieontology.org/2009/10/01/movieontology.owl#')
    DBO = Namespace('http://dbpedia.org/ontology/')
    DBP = Namespace('http://dbpedia.org/page/')

    for movie, path in node_path.items():
        title = get_title_from_path(path)
        ok, info = get_movie_info(title)
        if ok:
            graph.add((movie, NS['a'], MO['Movie']))

            _title = Literal(title)
            if info.get('Title'):
                _title = Literal(info['Title'])
            graph.set((movie, DBO['title'], _title))

            if info.get('Genre'):
                for info_genre in info['Genre'].split(', '):
                    genre = BNode()
                    graph.add((genre, NS['a'], MO['Genre']))
                    graph.set((genre, NS['rdfs']+'label', Literal(info_genre)))
                    graph.add((movie, MO['belongsToGenre'], genre))

            if info.get('Language'):
                for info_language in info['Language'].split(', '):
                    lang = BNode()
                    graph.add((lang, NS['a'], DBO['Language']))
                    graph.set((lang, NS['rdfs']+'label', Literal(info_language)))
                    graph.add((movie, MO['isTranslatedTo'], lang))

            if info.get('Awards'):
                awards = BNode()
                graph.add((awards, NS['a'], MO['Award']))
                graph.set((awards, NS['rdfs']+'label', Literal(info['Awards'])))
                graph.set((movie, MO['isAwardedWith'], awards))

            if info.get('Director'):
                director = BNode()
                graph.add((director, NS['a'], DBP['Film_Director']))
                graph.set((director, NS['rdfs']+'label', Literal(info['Director'])))
                graph.set((movie, MO['hasDirector'], director))

            if info.get('Actors'):
                for info_actor in info['Actors'].split(', '):
                    actor = BNode()
                    graph.add((actor, NS['a'], DBO['Actor']))
                    graph.set((actor, NS['rdfs']+'label', Literal(info_actor)))
                    graph.add((movie, MO['hasActor'], actor))

            if info.get('Country'):
                country = BNode()
                graph.add((country, NS['a'], DBO['Place']))
                graph.set((country, NS['rdfs']+'label', Literal(info['Country'])))
                graph.set((movie, MO['Place'], country))

            if info.get('Plot'):
                graph.set((movie, NS['rdfs']+'comment', Literal(info['Plot'])))


        else:
            print("{name} WARNING: {error}".format(name=__name__, error=info))
