#!/usr/bin/env python
# coding: utf-8
"""
this script creates the input csv for the semantic role labeling crowdflower
job given a json file with the labeled data and a json file with the chunks
"""

import argparse
import codecs
import csv
import json
import os
import re
import sys
from collections import defaultdict

# Keep the task simple: avoid timex and numeric FEs in frame definitions
LU_FRAME_MAP_LOCATION = os.path.join(os.path.dirname(__file__),
                                     'resources',
                                     'soccer-lu2frame-dbptypes-notimex.json')
LU_FRAME_MAP = json.load(open(LU_FRAME_MAP_LOCATION))


def prepare_crowdflower_input(labeled_data, chunk_data, debug):
    input_data = []
    # Update labeled data with chunks
    for labeled in labeled_data:
        for chunk in chunk_data:
            if chunk['id'] == labeled['id']:
                labeled.update(chunk)
    for sentence in labeled_data:
        if debug:
            print 'LABELED DATA: %s' % sentence
        chunks = sentence['chunks']
        input_row = {}
        input_row['id'] = sentence['id']
        snt = sentence['sentence']
        input_row['sentence'] = snt
        input_row['lu'] = sentence['lu']
        input_row['frame'] = sentence['frame']
        if debug:
            print 'ID: %s' % input_row['id']
            print 'SENTENCE: %s' % input_row['sentence']
            print 'ALL CHUNKS: %s' % chunks
        fe_names = [fe['FE'] for fe in sentence['FEs']]
        for i, fe in enumerate(sentence['FEs']):
            chunk = fe['chunk']
            input_row['known_fe%02d' % i] = chunk
            input_row['known_fe_name%02d' % i] = fe['FE']
            input_row['known_fe_name_type%02d' % i] = fe['type']
            # Remove already labeled chunks
            if chunk in chunks:
                chunks.remove(chunk)
        if debug:
            print 'PRUNED CHUNKS: %s' % chunks
        # Add FEs from the frame definition, even if some are already labeled
        for lu_obj in LU_FRAME_MAP:
            lu = lu_obj['lu']['lemma']
            if not lu == input_row['lu']:
                continue
            for frame in lu_obj['lu']['frames']:
                if not frame['frame'] == input_row['frame']:
                    continue
                for j, fe in enumerate(frame['FEs']):
                    fe_name, fe_type = fe.items()[0] # Always only one dict
                    input_row['fe_name%02d' % j] = fe_name
                    input_row['fe_name%02d_type' % j] = fe_type
                for k, chunk in enumerate(chunks):
                    input_row['fe%02d' % k] = chunk
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
        if re.search('fe[0-9]{2}$', field): gold_columns.append(field + '_gold')
    fields += gold_columns
    fields.sort()
    if debug:
        print 'CSV FIELDS: %s' % fields
    writer = csv.DictWriter(outfile, fields)
    writer.writeheader()
    writer.writerows(input_data)
    return 0


def create_cli_parser():
    parser = argparse.ArgumentParser(
            description='Build input CSV for a Semantic Role Labeling CrowdFlower job')
    parser.add_argument('labeled_data',
                        help='JSON file containing labeled data for each sentence')
    parser.add_argument('chunks',
                        help='JSON file containing chunks for each sentence')
    parser.add_argument('-o', '--output', default='crowdflower_input.csv',
                        type=argparse.FileType('wb'),
                        help='Write output to the given file')
    parser.add_argument('--debug', action='store_true', help='Toggle debug mode')
    return parser


if __name__ == "__main__":
    cli = create_cli_parser()
    args = cli.parse_args()
    labeled_data = json.load(codecs.open(args.labeled_data, 'rb', 'utf-8'))
    chunks = json.load(codecs.open(args.chunks, 'rb', 'utf-8'))
    input_data = prepare_crowdflower_input(labeled_data, chunks, args.debug)
    write_input_spreadsheet(input_data, args.output, args.debug)
    sys.exit(0)
