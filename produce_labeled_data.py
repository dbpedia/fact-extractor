#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import os
import stopwords
import sys
from collections import defaultdict
from rdflib import Graph, Namespace, URIRef, BNode, Literal


LU_FRAME_MAP_LOCATION = 'resources/soccer-lu2frame-dbptypes.json'
LU_FRAME_MAP = json.load(open(LU_FRAME_MAP_LOCATION))

# Namespace prefixes for RDF serialization
DBPEDIA_IT = Namespace('http://it.dbpedia.org/resource/')
FACT_EXTRACTION = Namespace('http://dbpedia.org/fact-extraction/')


def label_sentence(entity_linking_results, debug):
    """Produce a labeled sentence by comparing the linked entities to the frame definition"""
    labeled = {}
    links = json.load(codecs.open(entity_linking_results, 'rb', 'utf-8'))
    sentence, val = links.items()[0]
    labeled['sentence'] = sentence
    # Tokenize by splitting on spaces
    sentence_tokens = sentence.split()
    if debug:
        print 'SENTENCE: %s' % sentence
        print 'TOKENS: %s' % sentence_tokens
    frames = []
    for lu in LU_FRAME_MAP:
        lu_tokens = lu['lu']['tokens']
        # Check if a sentence token matches a LU token and assign frames accordingly
        for sentence_token in sentence_tokens:
            if sentence_token in lu_tokens:
                if debug:
                    print 'SENTENCE TOKEN "%s" MATCHED IN LU TOKENS' % sentence_token
                labeled['lu'] = lu['lu']['lemma']
                frames = lu['lu']['frames']
                if debug:
                    print 'LU LEMMA: %s' % labeled['lu']
                    print 'FRAMES: %s' % [frame['frame'] for frame in frames]
                for frame in frames:
                    # TODO this will overwrite in case of more frames per LU
                    labeled['frame'] = frame['frame']
                    FEs = frame['FEs']
                    types_to_FEs = frame['DBpedia']
                    if debug:
                        print 'ASSIGNED FRAME: %s' % frame['frame']
                        print 'FEs: %s' % FEs
                    for diz in val:
                        chunk = diz['chunk']
                        # Filter out linked stopwords
                        if chunk.lower() in stopwords.StopWords.words('italian'):
                            continue
                        types = diz['types']
                        for t in types:
                            for mapping in types_to_FEs:
                                # Strip DBpedia ontology namespace
                                looked_up = mapping.get(t[28:])
                                if looked_up:
                                    if type(looked_up) == list:
                                        labeled['FEs'] = [{'chunk': chunk, 'uri': diz['uri'], 'FE': fe} for fe in looked_up]
                                    else:
                                        labeled['FEs'] = [{'chunk': chunk, 'uri': diz['uri'], 'FE': looked_up}]
                    
    return labeled


def process_dir(indir, debug):
    """Walk into the input directory and process all the entity linking results"""
    processed = []
    for path, subdirs, files in os.walk(indir):
        for name in files:
            f = os.path.join(path, name)
            # Filename is a number
            filename, ext = os.path.splitext(name)
            labeled = label_sentence(f, debug)
            labeled['id'] = '%04d' % int(filename)
            processed.append(labeled)
            if debug:
                print 'LABELED: %s' % labeled
    return processed


# TODO implement the data model
def to_assertions(labeled_results, debug):
    """Serialize the labeled results into RDF"""
    assertions = Graph()
    for result in labeled_results:
        frame = result.get('frame')
        if not frame:
            if debug:
                print 'No frame found in "%s"' % result['sentence']
            continue
        fes = result.get('FEs')
        if not fes:
            if debug:
                print 'No FEs found in "%s"' % result['sentence']
            continue
        # FIXME Assume subject is the Wikipedia URI where the sentence comes from
        s = URIRef(DBPEDIA_IT + 'SENTENCE' + result['id'])
        p = URIRef(FACT_EXTRACTION + frame)
        for fe in fes:
            o = URIRef('%s%s%04d' % (FACT_EXTRACTION, frame, int(result['id'])))
            assertions.add((s, p, o))
#            b_node_subject = '%s_%04d' % (result['frame'], i)
            p1 = URIRef('%shas%s' % (FACT_EXTRACTION, fe['FE']))
#            b_node_predicate = 'has%s' % fe['FE']
            o1 = URIRef(fe['uri'])
#            b_node_object = fe['uri']
            assertions.add((o, p1, o1))
    return assertions.serialize(format='turtle', encoding='utf-8')


if __name__ == '__main__':
    debug = True
    labeled = process_dir(sys.argv[1], debug)
    json.dump(labeled, codecs.open('labeled_data.json', 'wb', 'utf-8'), ensure_ascii=False, indent=2)
    dataset = to_assertions(labeled, debug)
    with codecs.open('dataset.ttl', 'wb', 'utf-8') as o:
        o.writelines(dataset)
