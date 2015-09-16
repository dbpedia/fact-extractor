# -*- encoding: utf-8 -*-

import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rdflib import Graph
from urllib import quote
from rfc3987 import parse  # URI/IRI validation
from os import sys
from resources import FRAME_IT_TO_EN
from resources import FRAME_DBPO_MAP
from rdflib.namespace import Namespace, NamespaceManager
from rdflib import Graph


# Namespace prefixes for RDF serialization
RESOURCE_NS = Namespace('http://it.dbpedia.org/resource/')
FACT_EXTRACTION_NS = Namespace('http://dbpedia.org/fact-extraction/')
ONTOLOGY_NS = Namespace('http://dbpedia.org/ontology/')
NAMESPACE_MANAGER = NamespaceManager(Graph())
NAMESPACE_MANAGER.bind('resource', RESOURCE_NS)
NAMESPACE_MANAGER.bind('fact', FACT_EXTRACTION_NS)
NAMESPACE_MANAGER.bind('ontology', ONTOLOGY_NS)

NAMESPACES = {
    'ontology': ONTOLOGY_NS,
    'resource': RESOURCE_NS,
    'fact_extraction': FACT_EXTRACTION_NS,
}

def to_assertions(labeled_results, id_to_title, outfile='dataset.nt',
                  score_dataset=None, format='nt'):
    """
    Serialize the labeled results into RDF NTriples

    :param list labeled_results: Data for each sentence. Schema:

     ::

        [
          {
            'id': '',
            'frame': '',
            'lu': '',
            'sentence': '',
            'score': float,  # optional
            'FEs': [
               {
                'chunk': '',
                'type': '',
                'uri/literal': '',  # specify either uri or literal
                'FE': '',
                'score': float  # optional
               },
            ]
          },
        ]
    
    :param dict id_to_title: Mapping between wiki id and article title
    :param str outfile: Path to file in which to save the triples
    :param score_dataset: If and where to save triples' scores
    :type score_dataset: str or None
    :param str format: Format of the triples
    """


    processed, discarded = [], []
    assertions, score_triples= Graph(), Graph()
    assertions.namespace_manager = NAMESPACE_MANAGER
    score_triples.namespace_manager = NAMESPACE_MANAGER

    add_triple = triple_adder(assertions, format)
    add_score = triple_adder(score_triples, format)

    for result in labeled_results:
        print >> sys.stderr, '-' * 50, '\n', result.get('sentence'), '\n', result

        frame = result.get('frame')
        if not frame:
            print >> sys.stderr, ("Couldn't disambiguate any known frames in '%s'" %
                                  result['sentence'])
            discarded.append(result['sentence'])
            continue

        fes = result.get('FEs')
        if not fes:
            print >> sys.stderr, 'No FEs found in "%s"' % result['sentence']
            discarded.append(result['sentence'])
            continue

        processed.append(result['sentence'])

        parts = result['id'].split('.')
        if len(parts) > 1:
            wiki_id, sentence_id = parts[0], parts[1]
        else:
            wiki_id, sentence_id = parts[0], 0

        if wiki_id in id_to_title:
            wiki_title = quote(id_to_title[wiki_id].replace(' ', '_').encode('utf8'))
        else:
            wiki_title = str(wiki_id)
            print '**WARNING** No title for sentence %s, using id as title' % result['id']

        # Mint a URI unicode string
        subject = NAMESPACES['resource'] + wiki_title
        # URI sanity check
        try:
            parsed = parse(subject, rule='URI_reference')
            print >> sys.stderr, 'Valid URI: ', parsed
        except Exception as e:
            print "Couldn't parse '%s' (%s). Skipping ..." % (subject, e)
            continue

        predicate = _uri_for('frame', 'predicate', frame)
        object = _uri_for('frame', 'object', frame) + '_%s_%s' % (wiki_id, sentence_id)
        if not add_triple(subject, predicate, object):
            continue

        if 'sentence' in result:
            add_triple(object, _uri_for(None, 'predicate', 'extractedFrom'),
                       result['sentence'])

        # Always mint an instance type triple for reified nodes
        if predicate.startswith(NAMESPACES['ontology']):
            # Classes start with un upper case, properties with a lower case
            class_start = len(NAMESPACES['ontology'])
            ontology_class = NAMESPACES['ontology'] + \
                             predicate[class_start].upper() + \
                             predicate[class_start + 1:]
            add_triple(object, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                       ontology_class)
        elif predicate.startswith(NAMESPACES['fact_extraction']):
            class_start = len(NAMESPACES['fact_extraction'])
            ontology_class = NAMESPACES['fact_extraction'] + \
                             predicate[class_start].upper() + \
                             predicate[class_start + 1:]
            add_triple(object, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                       ontology_class)

        if result.get('score') is not None:
            predicate = NAMESPACES['fact_extraction'] + 'confidence'
            score = '"%f"^^<http://www.w3.org/2001/XMLSchema#float>' % result['score']
            add_score(object, predicate, score)

        for fe in fes:
            try:
                serialize_fe(fe, object, wiki_title, add_triple, format)
            except Exception as ex:
                print "Exception while serializing", fe, ex
                continue

    try:
        assertions.serialize(outfile, format)
        if score_dataset:
            score_triples.serialize(score_dataset, format)
    except Exception as e:
        # If something goes wrong, probably it's due to exotic URIs
        # so encode the exception to UTF-8!
        print "Couldn't serialize the dataset (%s)" % e.message.encode('utf8')
    return processed, discarded


def serialize_fe(fe, reified, wiki_title, add_triple, format):
    """ Serializes a frame element into triples

    :param dict fe: The data about the FE
    :param str reified: The subject term describing the reified object
    :param str wiki_title: Title of the wikipedia page
    :param triple_adder add_triple: Function called to add the triple,
     see :func:triple_adder
    :param str format: Format in which to save the triple
    :return: Whether the triple could be successfully serialized
    :rtype: bool
    :raises Exception: If it was not possible to serialize the triple
    """
    # The FE predicate takes the FE label
    p1 = _uri_for('FE', 'predicate', fe['FE'])

    # The FE object takes the linked entity URI and/or the literal
    le_uri = fe.get('uri')
    literal = fe.get('literal')
    
    if le_uri:  # It's a URI
        wiki_title = quote(le_uri.split('/')[-1].encode('utf8'))
        o1 = NAMESPACES['resource'] + wiki_title
        parsed = parse(o1, rule='URI_reference')  # URI sanity check
        assert add_triple(reified, p1, o1)

    if literal:  # It's a literal
        if type(literal) in {str, unicode}:
            assert add_triple(reified, p1, literal)

        elif type(literal) == dict:

            if 'duration' in literal:
                assert add_triple(reified, p1, literal['duration'])

            if 'start' in literal:
                assert add_triple(reified, '%sstartYear' % NAMESPACES['ontology'],
                                  literal['start'])

            if 'end' in literal:
                assert add_triple(reified, '%sendYear' % NAMESPACES['ontology'],
                                  literal['end'])

        else:
            raise Exception("Don't know how to serialize: " + repr(literal))


def triple_adder(graph, format):
    """
    returns a function which adds triples to the given graph in the
    given format. call this function with parameters subject,
    predicate and object

    :param graph: The graph in which to add the triple
    :type graph: See :py:class:`rdflib.Graph`
    :param str format: The format in which to serialize the triple
    """
    def add_triple(subject, predicate, object):
        try:
            s = _to_nt_term(subject)
            p = _to_nt_term(predicate)
            o = _to_nt_term(object)
            triple = '%s %s %s .' % (s, p, o)
            graph.parse(data=triple, format=format)
            print >> sys.stderr, 'Frame triple added: %s' % triple
            return True
        except Exception as e:
            s = u"Invalid triple: %s %s %s (%s). Skipping ..." % (subject, predicate,
                                                                  object, e.message)
            return False
    return add_triple


def _to_nt_term(x):
    """
    converts a string into a format suitable to be serialized as triple element
    urls are sorrounded by <>, and literals have the italian language tag added
    unicode strings are encoded into plain strs

    :param str x: The term to serialize
    :return: The formatted term
    """
    if type(x) == unicode:
        x = x.encode('utf8')
    if x.startswith('http://'):
        return '<%s>' % x
    elif not x.startswith('"'):
        return '"%s"@it' % x
    else:
        return x


def _uri_for(_type, _triple_term, term):
    """
    gets the uri to use for encoding the given term.

    :param str _type: What does the term refer to, either frame or FE
    :param str _triple_term: What is the role of the term in the triple; either
    predicate or object
    :param str term: The actual triple term
    :return: The uri
    :rtype: str
    :raises ValueError: if `_triple_term` is not predicate or object
    """
    dbpo = FRAME_DBPO_MAP.get(_type, {}).get(term)
    if dbpo:
        if _triple_term == 'predicate':
            return NAMESPACES['ontology'] + quote(dbpo.encode('utf8'))
        elif _triple_term == 'object':
            # Uppercase first letter
            dbpo = dbpo[0].upper() + dbpo[1:]
            return NAMESPACES['resource'] + quote(dbpo.encode('utf8'))
        else:
            raise ValueError("The triple term must be either 'predicate' or 'object', got " \
                             + _triple_term)
    else:
        label = FRAME_IT_TO_EN.get(_type, {}).get(term) or term
        if _triple_term == 'predicate':
            return NAMESPACES['fact_extraction'] + quote(label.encode('utf8'))
        elif _triple_term == 'object':
            # Uppercase first letter
            label = label[0].upper() + label[1:]
            return NAMESPACES['resource'] + quote(label.encode('utf8'))
        else:
            raise ValueError("The triple term must be either 'predicate' or 'object', got " \
                             + _triple_term)
