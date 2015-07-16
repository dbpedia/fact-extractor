#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import codecs
import json
import random
from resources import stopwords
import sys
from collections import defaultdict
from urllib import quote
from rfc3987 import parse  # URI/IRI validation
from rdflib import Graph, URIRef
from rdflib.namespace import Namespace, NamespaceManager
from date_normalizer import DateNormalizer
from resources.soccer_lu2frame_dbtypes import LU_FRAME_MAP
from lib.to_assertions import to_assertions

# Namespace prefixes for RDF serialization
RESOURCE_NS = Namespace('http://it.dbpedia.org/resource/')
FACT_EXTRACTION_NS = Namespace('http://dbpedia.org/fact-extraction/')
ONTOLOGY_NS = Namespace('http://dbpedia.org/ontology/')
NAMESPACE_MANAGER = NamespaceManager(Graph())
NAMESPACE_MANAGER.bind('resource', RESOURCE_NS)
NAMESPACE_MANAGER.bind('fact', FACT_EXTRACTION_NS)
NAMESPACE_MANAGER.bind('ontology', ONTOLOGY_NS)


def label_sentence(entity_linking_results, debug):
    """Produce a labeled sentence by comparing the linked entities to the frame definition"""
    labeled = {}
    links = json.load(codecs.open(entity_linking_results, 'rb', 'utf-8'))
    sentence, val = links.items()[0]
    labeled['sentence'] = sentence
    labeled['FEs'] = defaultdict(list)
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
                                    ### Frame disambiguation strategy, part 1 ###
                                    # LAPSE ASSIGNMENT
                                    # If there is AT LEAST ONE core FE, then assign that frame
                                    # TODO strict assignment: ALL core FEs must be found
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
                                                        print 'Mapped FE "%s" is core for frame "%s"' % (shared_type_fe, frame['frame'])
                                                    core = True
                                        else:
                                            fe_type = fe.get(looked_up)
                                            if fe_type:
                                                chunk['type'] = fe_type
                                            if fe_type == 'core':
                                                if debug:
                                                    print 'Mapped FE "%s" is core for frame "%s"' % (looked_up, frame['frame'])
                                                core = True
                                    ### FE disambiguation strategy ###
                                    # If multiple FEs have the same ontology type, e.g., [Vincitore, Perdente] -> Club
                                    # BASELINE = random assignment
                                    # Needs to be adjusted by humans
                                    if type(looked_up) == list:
                                        chosen = random.choice(looked_up)
                                        chunk['FE'] = chosen
                                        # Avoid duplicates
                                        if chunk not in assigned_fes:
                                            assigned_fes.append(chunk)
                                    else:
                                        chunk['FE'] = looked_up
                                        # Avoid duplicates
                                        if chunk not in assigned_fes:
                                            assigned_fes.append(chunk)
                    # Continue to next frame if NO core FE was found
                    if not core:
                        if debug:
                            print 'No core FE for frame "%s": skipping' % frame['frame']
                        continue
                    # Otherwise assign frame and previously stored FEs
                    else:
                        if debug:
                            print 'ASSIGNING FRAME: %s' % frame['frame']
                            print 'ASSIGNING FEs: %s' % assigned_fes
                        ### Frame disambiguation strategy, part 2 ###
                        # If at least 1 core FE is detected in multiple frames:
                        # BASELINE = random assignment
                        # Needs to be adjusted by humans
                        current_frame = frame['frame']
                        previous_frame = labeled.get('frame')
                        if previous_frame:
                            previous_FEs = labeled['FEs']
                            choice = random.choice([previous_frame, current_frame])
                            if debug:
                                print 'CORE FES FOR MULTIPLE FRAMES WERE DETECTED. MAKING A RANDOM ASSIGNMENT: %s' % choice
                            if choice == current_frame:
                                labeled['frame'] = current_frame
                                labeled['FEs'] = assigned_fes
                        else:
                            labeled['frame'] = current_frame
                            labeled['FEs'] = assigned_fes
    # Normalize + annotate numerical FEs (only if we could disambiguate the sentence)
    if labeled.get('frame'):
        if debug:
            print 'LABELING AND NORMALIZING NUMERICAL FEs...'
        normalizer = DateNormalizer()
        for (start, end), tag, norm in normalizer.normalize_many(sentence):
            chunk = sentence[start:end]
            if debug:
                print 'Chunk [%s] normalized into [%s], tagged as [%s]' % (chunk, norm, tag)
            # All numerical FEs are extra ones and their values are literals
            fe = {
                'chunk': chunk,
                'FE': tag,
                'type': 'extra',
                'literal': norm
            }
            labeled['FEs'].append(fe)
    return labeled


def process_dir(indir, debug):
    """Walk into the input directory and process all the entity linking results"""
    processed = []
    for path, subdirs, files in os.walk(indir):
        for name in files:
            f = os.path.join(path, name)
            labeled = label_sentence(f, debug)
            # Filename is {WIKI_ID}.{SENTENCE_ID}
            labeled['id'] = name
            processed.append(labeled)
            if debug:
                print 'LABELED: %s' % labeled
    return processed


if __name__ == '__main__':
    debug = True
    labeled = process_dir(sys.argv[1], debug)
    # labeled = json.load(codecs.open(sys.argv[1], 'rb', encoding='utf8'))
    mapping = json.load(open(sys.argv[2]))
    json.dump(labeled, codecs.open('labeled_data.json', 'wb', 'utf-8'), ensure_ascii=False, indent=2)
    processed, discarded = to_assertions(labeled, mapping, NAMESPACE_MANAGER, {
                                            'ontology': ONTOLOGY_NS,
                                            'resource': RESOURCE_NS,
                                            'fact_extraction': FACT_EXTRACTION_NS,
                                         }, debug)
    with codecs.open('processed', 'wb', 'utf-8') as p:
        p.writelines([sentence + '\n' for sentence in processed])    
    with codecs.open('discarded', 'wb', 'utf-8') as d:
        d.writelines([sentence + '\n' for sentence in discarded])
    if debug:
        print '%d out of %d NOT DISAMBIGUATED' % (len(discarded), len(labeled))
