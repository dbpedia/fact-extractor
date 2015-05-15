#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import json
import os
import random
import stopwords
import sys
from rdflib import Graph, URIRef
from rdflib.namespace import Namespace, NamespaceManager


LU_FRAME_MAP_LOCATION = 'resources/soccer-lu2frame-dbptypes.json'
LU_FRAME_MAP = json.load(open(LU_FRAME_MAP_LOCATION))

# Namespace prefixes for RDF serialization
RESOURCE = Namespace('http://it.dbpedia.org/resource/')
FACT_EXTRACTION = Namespace('http://dbpedia.org/fact-extraction/')
NAMESPACE_MANAGER = NamespaceManager(Graph())
NAMESPACE_MANAGER.bind('resource', RESOURCE)
NAMESPACE_MANAGER.bind('fact', FACT_EXTRACTION)


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
                    print 'TOKEN "%s" MATCHED IN LU TOKENS' % sentence_token
                labeled['lu'] = lu['lu']['lemma']
                frames = lu['lu']['frames']
                if debug:
                    print 'LU LEMMA: %s' % labeled['lu']
                    print 'FRAMES: %s' % [frame['frame'] for frame in frames]
                # Frame processing
                for frame in frames:
                    FEs = frame['FEs']
                    types_to_FEs = frame['DBpedia']
                    if debug:
                        print 'CURRENT FRAME: %s' % frame['frame']
                        print 'FEs: %s' % FEs
                    core = False
                    assigned_fes = []
                    for diz in val:
                        chunk = {'chunk': diz['chunk'], 'uri': diz['uri']}
                        # Filter out linked stopwords
                        if chunk['chunk'].lower() in stopwords.StopWords.words('italian'):
                            continue
                        types = diz['types']
                        #### FE assignment ###
                        for t in types:
                            for mapping in types_to_FEs:
                                # Strip DBpedia ontology namespace
                                looked_up = mapping.get(t[28:])
                                if looked_up:
                                    if debug:
                                        print 'Chunk "%s" has an ontology type "%s" that maps to FE "%s"' % (chunk['chunk'], t[28:], looked_up)
                                    ### Frame disambiguation strategy ###
                                    # If there is at least one core FE, then assign that frame
                                    # Will not work if the FEs across competing frames have the same ontology type
                                    # e.g., Attività > Squadra and Partita > [Squadra_1, Squadra_2]

                                    # Check if looked up FE is core
                                    for fe in FEs:
                                        if type(looked_up) == list:
                                            for shared_type_fe in looked_up:
                                                shared_fe_type = fe.get(shared_type_fe)
                                                # TODO overwritten value
                                                if shared_fe_type:
                                                    chunk['type'] = shared_fe_type
                                                if shared_fe_type == 'core':
                                                    if debug:
                                                        print 'Looked up FE "%s" is core' % shared_type_fe
                                                    core = True
                                        else:
                                            fe_type = fe.get(looked_up)
                                            if fe_type:
                                                chunk['type'] = fe_type
                                            if fe_type == 'core':
                                                if debug:
                                                    print 'Looked up FE "%s" is core for frame "%s"' % (looked_up, frame['frame'])
                                                core = True
                                    # No FE disambiguation when multiple FEs have the same ontology type, e.g., [Vincitore, Perdente] -> Club
                                    # Baseline strategy = random assignment
                                    # Needs to be adjusted by humans
                                    if type(looked_up) == list:
                                        chosen = random.choice(looked_up)
                                        chunk['FE'] = chosen
                                        assigned_fes.append(chunk)
                                    else:
                                        chunk['FE'] = looked_up
                                        assigned_fes.append(chunk)
                    # Continue to next frame if no core FE was found
                    if not core:
                        if debug:
                            print 'No core FE for frame "%s": skipping' % frame['frame']
                        continue
                    # Otherwise assign frame and previously stored FEs
                    else:
                        labeled['frame'] = frame['frame']
                        labeled['FEs'] = assigned_fes
                        if debug:
                            print 'ASSIGNED FRAME: %s' % frame['frame']
                            print 'ASSIGNED FEs: %s' % assigned_fes
                    
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
def to_assertions(labeled_results, debug, outfile='dataset.ttl', format='turtle'):
    """Serialize the labeled results into RDF"""
    discarded = []
    assertions = Graph()
    assertions.namespace_manager = NAMESPACE_MANAGER
    for result in labeled_results:
        frame = result.get('frame')
        if not frame:
            if debug:
                print "Couldn't disambiguate any known frames in '%s'" % result['sentence']
            discarded.append(result['sentence'])
            continue
        fes = result.get('FEs')
        if not fes:
            if debug:
                print 'No FEs found in "%s"' % result['sentence']
            continue
        # FIXME Assume subject is the Wikipedia URI where the sentence comes from
        s = URIRef(RESOURCE['SENTENCE%s' % result['id']])
        p = URIRef(FACT_EXTRACTION[frame])
        for fe in fes:
            o = URIRef('%s%s%04d' % (FACT_EXTRACTION, frame, int(result['id'])))
            assertions.add((s, p, o))
            p1 = URIRef('%shas%s' % (FACT_EXTRACTION, fe['FE']))
            o1 = URIRef(fe['uri'])
            assertions.add((o, p1, o1))
    assertions.serialize(outfile, format, encoding='utf-8')
    return discarded


if __name__ == '__main__':
    debug = True
    labeled = process_dir(sys.argv[1], debug)
    json.dump(labeled, codecs.open('labeled_data.json', 'wb', 'utf-8'), ensure_ascii=False, indent=2)
    discarded = to_assertions(labeled, debug)
    with codecs.open('discarded', 'wb', 'utf-8') as o:
        o.writelines([sentence + '\n' for sentence in discarded])
    if debug:
        print '%d out of %d NOT DISAMBIGUATED' % (len(discarded), len(labeled))
