#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import csv
import json
import os
import re
import regex
import sys
from collections import OrderedDict


LU_FRAME_MAP_LOCATION = 'resources/soccer-lu2frame.json'
LU_FRAME_MAP = json.load(open(LU_FRAME_MAP_LOCATION))


def tokenize(sentence):
    # Split on anything but letters, numbers and dash punctuation
    return [token for token in regex.split(ur'[^\pL\pN\p{Pd}]+', sentence) if token]


def prepare_crowdflower_input(sentences):
    input_data = []
    for num, sentence in enumerate(sentences):
        input_row = {'id': str(num), 'sentence': sentence}
        tokens = tokenize(sentence)
        # Lookup the LU based on the token
        for i, token in enumerate(tokens):
            for lu_data in LU_FRAME_MAP:
                lu = lu_data['lu']
                if token in lu['tokens']:
                    input_row['lu'] = lu['lemma']
                    # Take the first frame only
                    frame = lu['frames'][0]
                    input_row['frame'] = frame['frame']
                    for j, fe in enumerate(frame['FEs']):
                        # Each FE has only 1 key, i.e., the FE label
                        fe_label = fe.keys()[0]
                        input_row['fe%02d' % j] = fe_label 
                        input_row['fe%02d_type' % j] = fe.get(fe_label)
            input_row['token%02d' % i] = token
        # Prepare input for DictWriter, since it won't write UTF-8
        input_data.append({k:v.encode('utf-8') for k,v in input_row.items()})
    return input_data


def write_input_spreadsheet(input_data, outfile='crowdflower-input-data.csv'):
    # Merge all the keys to prepare the CSV headers
    fields = list(set([k for d in input_data for k in d.keys()]))
    # Gold units need a column flag
    fields.append('_golden')
    gold_columns = []
    for field in fields:
        # Add gold answer columns for each token
        if field.startswith('token'): gold_columns.append(field + '_gold')
    fields += gold_columns
    fields.sort()
    writer = csv.DictWriter(open(outfile, 'wb'), fields)
    writer.writeheader()
    writer.writerows(input_data)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 3:
        with codecs.open(sys.argv[1], 'rb', 'utf-8') as i:
            sentences = [l.strip() for l in i.readlines()] 
        input_data = prepare_crowdflower_input(sentences)
        write_input_spreadsheet(input_data, sys.argv[2])
    elif len(sys.argv) == 2:
        with codecs.open(sys.argv[1], 'rb', 'utf-8') as i:
            sentences = [l.strip() for l in i.readlines()] 
        input_data = prepare_crowdflower_input(sentences)
        write_input_spreadsheet(input_data)
    else:
        print "Usage: python %s <SENTENCES_FILE> [OUTPUT_FILE]" % __file__
        sys.exit(1)
