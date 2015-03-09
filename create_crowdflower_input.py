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
from get_meaningful_sentences import CHUNKER_GRAMMAR, load_pos_data

LU_FRAME_MAP_LOCATION = 'resources/lu-frame-map.json'
LU_FRAME_MAP = json.load(open(LU_FRAME_MAP_LOCATION))
TOKENS = []


def load_all_tokens():
    for lu in LU_FRAME_MAP.keys():
        if LU_FRAME_MAP[lu].get('tokens'):
            for token in LU_FRAME_MAP[lu].get('tokens'):
                TOKENS.append(token)


def add_chunk_data(pos_data):
    chunker = RegexpParser(CHUNKER_GRAMMAR)
    chunks = {} 
    for sentence_id, data in pos_data.iteritems():
        result = chunker.parse(data)
        chunks[sentence_id] = {}
        chunks[sentence_id]['chunks'] = [' '.join([token for token, pos in t.leaves()]) for t in result.subtrees(lambda result: result.label() == 'SN')]
    return chunks

# Assumes entity linked sentences have the <strong> tag
def prepare_crowdflower_input(entity_linked_dir, chunk_data):
    input_data = []
    # Walk into entity linked dir
    for path, subdirs, files in os.walk(entity_linked_dir):
        for name in files:
            # Get sentence ID based on file naming convention {number}.json
            row_id = name.split('.')[0]
            if row_id in chunk_data.keys():
                f = os.path.join(path, name)
                # Load entity linked JSON file
                entity_linked_data = json.load(codecs.open(f, 'rb', 'utf-8'), encoding='utf-8')
                input_row = {}
                input_row['id'] = row_id
                sentence = entity_linked_data.keys()[0]
                input_row['sentence'] = sentence
                # Extract LU token based on the <strong> tag
                match = re.search(r'<strong>([^<]+)</strong>', sentence)
                if match: token = match.group(1)
                else: print "No match in sentence -> %s" % sentence
                frames = []
                for lu in LU_FRAME_MAP.keys():
                    tokens = LU_FRAME_MAP[lu].get('tokens')
                    # Check if the LU token exists in the preloaded LU_FRAME_MAP
                    if tokens and token in tokens:
                        input_row['lu'] = lu
                        frames = [frame for frame in LU_FRAME_MAP[lu].keys() if frame != 'tokens']
                linked_entities = entity_linked_data[sentence]
                for frame in frames:
                    input_row['frame'] = frame
                    fe_names = LU_FRAME_MAP[input_row['lu']][frame]
                    # Store FE, chunks and linked entities with incremental numbers
                    # fe_name{i}, fe{j}, entity{j}, type{j_k} 
                    for i in xrange(0, len(fe_names)):
                        input_row['fe_name' + str(i)] = fe_names[i]
                    for j in xrange(0, len(chunk_data[row_id]['chunks'])):
                        current_np = chunk_data[row_id]['chunks'][j]
                        input_row['fe' + str(j)] = current_np
                        for linked in linked_entities:
                            # Retrieve entity in the sentence based on indices
                            entity_string = sentence[linked['start']:linked['end']]
                            if current_np.find(entity_string) != -1:
                                input_row['entity' + str(j)] = entity_string 
                                for k in xrange(0, len(linked['types'])):
                                    input_row['type' + str(j) + '_' + str(k)] = linked['types'][k][28:]
                # Prepare input for DictWriter, since it won't write UTF-8
                input_data.append({k:v.encode('utf-8') for k,v in input_row.items()})
    return input_data


def write_input_spreadsheet(input_data, outfile='input-data.csv'):
    # Merge all the keys to prepare the CSV headers
    fields = set([k for d in input_data for k in d.keys()])
    fields.add('_golden')
    fields = list(fields)
    fields.sort()
    writer = csv.DictWriter(open(outfile, 'wb'), fields)
    writer.writeheader()
    writer.writerows(input_data)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4:
        pos_data = load_pos_data(sys.argv[1])
        chunk_data = add_chunk_data(pos_data)
        input_data = prepare_crowdflower_input(sys.argv[2], chunk_data)
        outfile = sys.argv[3]
        write_input_spreadsheet(input_data, outfile)
    elif len(sys.argv) == 3:
        pos_data = load_pos_data(sys.argv[1])
        chunk_data = add_chunk_data(pos_data)
        input_data = prepare_crowdflower_input(sys.argv[2], chunk_data)
        write_input_spreadsheet(input_data)
    else:
        print "Usage: python %s <POS_DATA_DIR> <ENTITY_LINKED_DATA_DIR> [OUTPUT_FILE]" % __file__
        sys.exit(1)
