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

CHUNKER_GRAMMAR = "SN: {<PRO.*|DET.*>?<ADJ>*<NOM>+<PRE:det>?<PRO:[^r]*|DET.*>?<ADJ>*<NOM>?<NOM>?}"

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
    np[k] = [' '.join([token for token, pos in t.leaves()]) for t in result.subtrees(lambda result: result.label() == 'SN')]

input_data = []

for path, subdirs, files in os.walk(sys.argv[1]):
    for name in files:
        f = os.path.join(path, name)
        data = json.load(codecs.open(f, 'rb', 'utf-8'), encoding='utf-8')
        mappa = json.load(open(LU_FRAME_MAP_LOCATION))
        input_row = {}
        row_id = name.split('.')[0]
        input_row['id'] = row_id
        sentence = data.keys()[0]
        input_row['sentence'] = sentence
        lu = re.search(r'<strong>([^<]+)</strong>', sentence).group(1)
        input_row['lu'] = lu
        linked_entities = data[sentence]
        frames = mappa[lu].keys()
        for frame in frames:
            fe_names = mappa[lu][frame]
            for k in xrange(0, len(fe_names)):
                input_row['fe_name' + str(k)] = fe_names[k]
            for l in xrange(0, len(np[row_id])):
                input_row['fe' + str(l)] = np[row_id][l]
            for i in xrange(0, len(linked_entities)):
                input_row['entity' + str(i)] = sentence[linked_entities[i]['start']:linked_entities[i]['end']]
                for j in xrange(0, len(linked_entities[i]['types'])):
                    input_row['type' + str(i) + '_' + str(j)] = linked_entities[i]['types'][j][28:]
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
