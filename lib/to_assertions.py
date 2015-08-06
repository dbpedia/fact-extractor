# -*- encoding: utf-8 -*-

from rdflib import Graph
from urllib import quote
from rfc3987 import parse  # URI/IRI validation
from os import sys


def to_assertions(labeled_results, id_to_title, namespace_manager, namespaces,
                  outfile='dataset.nt', score_dataset=None, format='nt'):
    """
    Serialize the labeled results into RDF NTriples

    Schema of labeled results:

    [
      {
        'id': '',
        'frame': '',
        'lu': '',
        'sentence': '',
        'score': float  # optional
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

    """


    processed, discarded = [], []
    assertions, score_triples= Graph(), Graph()
    assertions.namespace_manager = namespace_manager
    score_triples.namespace_manager = namespace_manager
    for result in labeled_results:
        print >> sys.stderr, '---', result.get('sentence')

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
        wiki_id, sentence_id = parts[0], parts[1]  # there might be the extension
        if wiki_id in id_to_title:
            wiki_title = quote(id_to_title[wiki_id].replace(' ', '_').encode('utf8'))
        else:
            wiki_title = str(wiki_id)
            print '**WARNING** No title for sentence %s, using id as title' % result['id']

        # Mint a URI unicode string
        subject = namespaces['resource'] + wiki_title
        # URI sanity check
        try:
            parsed = parse(subject, rule='URI_reference')
            print >> sys.stderr, 'Valid URI: ', parsed
        except Exception as e:
            print "Couldn't parse '%s' (%s). Skipping ..." % (subject, e)
            continue

        frame_label = quote(frame.encode('utf8'))
        predicate = namespaces['fact_extraction'] + frame_label
        object = (namespaces['fact_extraction'] + frame_label + '_' +
                  wiki_id + '_' + sentence_id)
        try:
            # Craft an NTriple string
            frame_triple = '<%s> <%s> <%s> .' % (subject, predicate, object)
            # Sanity check + addition
            assertions.parse(data=frame_triple, format=format)
            print >> sys.stderr, 'Frame triple added: %s' % frame_triple
        except Exception as e:
            print "Invalid triple: %s (%s). Skipping ..." % (frame_triple, e)
            continue

        if result.get('score') is not None:
            predicate = namespaces['fact_extraction'] + 'confidence'
            score = '"%f"^^<http://www.w3.org/2001/XMLSchema#float>' % result['score']
            score_triple = '<%s> <%s> %s .' % (object, predicate, score)
            score_triples.parse(data=score_triple, format=format)

        for fe in fes:
            try:
                serialize_fe(fe, object, namespaces, wiki_title, assertions, format)
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


def serialize_fe(fe, reified, namespaces, wiki_title, assertions, format):
    # The FE predicate takes the FE label
    fe_label = quote(fe['FE'].encode('utf8'))
    p1 = '%shas%s' % (namespaces['fact_extraction'], fe_label)

    # The FE object takes the linked entity URI or the literal
    le_uri = fe.get('uri')
    literal = fe.get('literal')
    
    if le_uri:  # It's a URI
        wiki_title = quote(le_uri.split('/')[-1].encode('utf8'))
        o1 = namespaces['resource'] + wiki_title
        parsed = parse(o1, rule='URI_reference')  # URI sanity check
        fe_triple = '<%s> <%s> <%s> .' % (reified, p1, o1)  # Craft an NTriple string
        assertions.parse(data=fe_triple, format=format)  # NTriple sanity check
        print >> sys.stderr, 'FE triple added: %s' % fe_triple

    elif literal:  # It's a literal
        o1 = literal
        if type(literal) in {str, unicode}:
            fe_triple = '<%s> <%s> %s .' % (reified, p1, o1)  # Craft an NTriple string
            assertions.parse(data=fe_triple, format=format)  # NTriple sanity check
            print >> sys.stderr, 'FE triple added: %s' % fe_triple
        elif type(literal) == dict and 'duration' in literal:
            assertions.parse(data='<%s> <%s> %s .' % (reified, p1, o1['duration']),
                             format=format)
            ps = '%sstartYear' % namespaces['ontology']
            assertions.parse(data='<%s> <%s> %s .' % (reified, ps, o1['start']),
                             format=format)
            pe = '%sendYear' % namespaces['ontology']
            assertions.parse(data='<%s> <%s> %s .' % (reified, pe, o1['end']),
                             format=format)
        else:
            raise Exception("Don't know how to serialize: " + repr(literal))
    else:
        raise Exception("FE not tagged as either literal or uri, skipped " + repr(fe))
