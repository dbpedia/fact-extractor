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
