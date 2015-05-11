#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import codecs
import csv
import json
import os
import re
import stopwords
import sys
from collections import defaultdict


LU_FRAME_MAP_LOCATION = 'resources/soccer-lu2frame-dbptypes.json'
LU_FRAME_MAP = json.load(open(LU_FRAME_MAP_LOCATION))


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
                                    labeled[chunk] = {'uri': diz['uri'], 'FEs': looked_up}
                    
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
def to_assertions(labeled_results):
    """Serialize the labeled results into RDF"""
    assertions = []
    return assertions


if __name__ == '__main__':
    json.dump(process_dir(sys.argv[1], True), codecs.open('labeled_data.json', 'wb', 'utf-8'), ensure_ascii=False, indent=2)
