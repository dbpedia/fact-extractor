#!/usr/bin/env python
# coding: utf-8

import argparse
import codecs
import csv
import json
import os
import re
import sys
from collections import defaultdict


LU_FRAME_MAP_LOCATION = 'resources/soccer-lu2frame.json'
LU_FRAME_MAP = json.load(open(LU_FRAME_MAP_LOCATION))
TOKENS = []


def load_all_tokens():
    for lu in LU_FRAME_MAP:
        for token in lu['lu']['tokens']:
            TOKENS.append(token)


def prepare_crowdflower_input(chunk_data, debug):
    input_data = []
    for sentence in chunk_data:
        if debug:
            print 'CHUNK DATA: %s' % sentence
        input_row = {}
        input_row['id'] = sentence['id']
        snt = sentence['sentence']
        input_row['sentence'] = snt
        # Tokenize by splitting on spaces
        sentence_tokens = snt.split()
        if debug:
            print 'ID: %s' % input_row['id']
            print 'SENTENCE: %s' % input_row['sentence']
            print 'TOKENS: %s' % sentence_tokens
        frames = []
        for lu in LU_FRAME_MAP:
            lu_tokens = lu['lu']['tokens']
            # Check if a sentence token matches a LU token and assign frames accordingly
            for sentence_token in sentence_tokens:
                if sentence_token in lu_tokens:
                    if debug:
                        print 'SENTENCE TOKEN "%s" MATCHED IN LU TOKENS' % sentence_token
                    input_row['lu'] = lu['lu']['lemma']
                    frames = lu['lu']['frames']
                    if debug:
                        print 'LU LEMMA: %s' % input_row['lu']
                        print 'FRAMES: %s' % frames
                    for frame in frames:
                        # TODO this will overwrite in case of more frames per LU
                        input_row['frame'] = frame['frame']
                        fe_names = frame['FEs']
                        if debug:
                            print 'ASSIGNED FRAME: %s' % frame
                            print 'FEs: %s' % fe_names
                        # Store FE and chunks with incremental numbers
                        # fe_name{i}, fe{j}
                        for i in xrange(0, len(fe_names)):
                            # Also store FE type (core or extra)
                            input_row['fe_name%02d' % i], input_row['fe_name%02d_type' % i] = fe_names[i].items()[0]
                            if debug:
                                print 'FIELD fe_name%02d: %s' % (i, fe_names[i])
                        for j in xrange(0, len(sentence['chunks'])):
                            input_row['fe%02d' % j] = sentence['chunks'][j]
                            if debug:
                                print 'FIELD fe%02d: %s' % (j, sentence['chunks'][j])
        if debug:
            print 'COMPLETE ROW: %s' % input_row
        # Prepare input for DictWriter, since it won't write UTF-8
        input_data.append({k:v.encode('utf-8') for k,v in input_row.items()})
    return input_data


def write_input_spreadsheet(input_data, outfile, debug):
    # Merge all the keys to prepare the CSV headers
    fields = set([k for d in input_data for k in d.keys()])
    fields.add('_golden')
    fields = list(fields)
    gold_columns = []
    for field in fields:
        # Add gold answer columns for each token
        if re.match('fe[0-9]{2}$', field): gold_columns.append(field + '_gold')
    fields += gold_columns
    fields.sort()
    if debug:
        print 'CSV FIELDS: %s' % fields
    writer = csv.DictWriter(outfile, fields)
    writer.writeheader()
    writer.writerows(input_data)
    return 0


def create_cli_parser():
    parser = argparse.ArgumentParser(description='Build input CSV for a Semantic Role Labeling CrowdFlower job')
    parser.add_argument('chunk_data', help='JSON file containing chunk data for each sentence')
    parser.add_argument('-o', '--output', default='crowdflower_input.csv', type=argparse.FileType('wb'), help='Write output to the given file')
    parser.add_argument('--debug', action='store_true', help='Toggle debug mode')
    return parser


if __name__ == "__main__":
    cli = create_cli_parser()
    args = cli.parse_args()
    chunk_data = json.load(codecs.open(args.chunk_data, 'rb', 'utf-8'))
    input_data = prepare_crowdflower_input(chunk_data, args.debug)
    write_input_spreadsheet(input_data, args.output, args.debug)
    sys.exit(0)
