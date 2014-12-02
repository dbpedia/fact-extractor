#!/usr/bin/env python
# coding: utf-8

import codecs
import csv
import json
import os
import re
import sys
from collections import defaultdict
from nltk import RegexpParser

LU_FRAME_MAP_LOCATION = '../training/mappa.json'
POS_TAGGED_DATA_LOCATION = '../training/itwiki/pos-tagged-clean-gold'

MAPPA = json.load(open(LU_FRAME_MAP_LOCATION))
TOKENS = []
for lu in MAPPA.keys():
    if MAPPA[lu].get('tokens'):
        for token in MAPPA[lu].get('tokens'):
            TOKENS.append(token)

CHUNKER_GRAMMAR = r"""
    SN: {<PRO.*|DET.*|>?<ADJ>*<NUM>?<NOM|NPR>+<NUM>?<ADJ|VER:pper>*}
    CHUNK: {<SN><VER.*>+<SN>}
    """

chunker = RegexpParser(CHUNKER_GRAMMAR)
pos_data = defaultdict(list)
for path, subdirs, files in os.walk(sys.argv[2]):
    for name in files:
        f = os.path.join(path, name)
        data = codecs.open(f, 'rb', 'utf-8')
        tokens = data.readlines()
        for line in tokens:
            parts = line.split('\t')
            if len(parts) > 1:
                (token, pos) = (parts[0], parts[1])
                pos_data[name].append((token, pos))

np = {}
for k, v in pos_data.iteritems():
    result = chunker.parse(v)
    good_one = False
    if 'CHUNK' in [s.label() for s in result.subtrees()]:
        for t in result.subtrees(lambda result: result.label() == 'CHUNK'):
            for token, pos in t.leaves():
                if pos.find('VER') != -1 and token in TOKENS: good_one = True
            if good_one: np[k] = [' '.join([token for token, pos in t.leaves()]) for t in result.subtrees(lambda result: result.label() == 'SN')]

input_data = []

for path, subdirs, files in os.walk(sys.argv[1]):
    for name in files:
        row_id = name.split('.')[0]
        if row_id in np.keys():
            f = os.path.join(path, name)
            data = json.load(codecs.open(f, 'rb', 'utf-8'), encoding='utf-8')
            input_row = {}
            input_row['id'] = row_id
            sentence = data.keys()[0]
            input_row['sentence'] = sentence
            match = re.search(r'<strong>([^<]+)</strong>', sentence)
            if match:
                token = match.group(1)
            else:
                print "No match in sentence -> %s" % sentence
            frames = []
            for lu in MAPPA.keys():
                tokens = MAPPA[lu].get('tokens')
                if tokens and token in tokens:
                    input_row['lu'] = lu
                    frames = [frame for frame in MAPPA[lu].keys() if frame != 'tokens']
            linked_entities = data[sentence]
            for frame in frames:
                fe_names = MAPPA[input_row['lu']][frame]
                for i in xrange(0, len(fe_names)):
                    input_row['fe_name' + str(i)] = fe_names[i]
                for j in xrange(0, len(np[row_id])):
                    current_np = np[row_id][j]
                    input_row['fe' + str(j)] = current_np
                    for linked in linked_entities:
                        entity_string = sentence[linked['start']:linked['end']]
                        if current_np.find(entity_string) != -1:
                            input_row['entity' + str(j)] = entity_string 
                            for k in xrange(0, len(linked['types'])):
                                input_row['type' + str(j) + '_' + str(k)] = linked['types'][k][28:]
            # Prepare input for DictWriter, since it won't write UTF-8
            input_data.append({k:v.encode('utf-8') for k,v in input_row.items()})

# Merge all the keys to prepare the CSV headers
fields = set([k for d in input_data for k in d.keys()])
fields.add('_golden')
fields = list(fields)
fields.sort()

writer = csv.DictWriter(open('test.csv', 'wb'), fields)
writer.writeheader()
writer.writerows(input_data)
