#!/opt/local/bin/python
# -*- coding: utf-8 -*-

import codecs
import re
import sys
import csv
import json
import HTMLParser
import argparse
import os
from collections import Counter


def read_full_results(results_file):
    """ Reads and aggregates the results from an open stream"""
    h = HTMLParser.HTMLParser()
    processed = {}

    # TODO csv lib doesn't handle unicode
    results = csv.DictReader(results_file)
    fields = results.fieldnames
    fe_amount = len([f for f in fields if re.match('fe_name[0-9]$', f)])

    # Skip gold
    regular = [row for row in results if row['_golden'] != 'true']
    for row in regular:
        sentence_id = row['id']
        sentence = h.unescape(row['sentence'].decode('utf-8'))

        # initialize data structure with sentence, frame, lu and entity list
        if not sentence_id in processed:
            processed[sentence_id] = dict()
            processed[sentence_id]['sentence'] = sentence
            processed[sentence_id]['frame'] = row['frame']
            processed[sentence_id]['lu'] = row['lu']
            for n in xrange(0, fe_amount):
                entity = row['orig_fe_name' + str(n)]
                processed[sentence_id][entity] = {
                    'judgments': 0,
                    'answers': list()
                }

        # update judgments for each entity
        for n in xrange(0, fe_amount):
            entity = row['orig_fe_name' + str(n)]
            answer = row.get('fe_name' + str(n))
            if answer:
                processed[sentence_id][entity]['judgments'] += 1
                processed[sentence_id][entity]['answers'].append(answer)

    return processed


def set_majority_vote_answer(results_json):
    """ Determine the correct entity which corresponds to a given FE """

    for k,v in results_json.iteritems():
        for fe in v.keys():
            if fe in {'frame', 'lu', 'sentence'}:
                continue

            answers_count = Counter(v[fe]['answers'])
            majority = v[fe]['judgments'] / 2.0
            for answer,freq in answers_count.iteritems():
                if freq > majority:
                    v[fe]['majority'] = answer

            if not v[fe].get('majority'):
                print "HEADS UP! No majority answer for sentence [%s], FE [%s]" % (k, fe)


def tag_entities(results):
    """ Creates the IOB tag for each entity found. """
    for annotations in results.values():
        frame = annotations['frame']

        annotations['entities'] = dict()
        for fe in annotations.keys():
            if fe in {'frame', 'lu', 'sentence'}:
                continue

            # skip uncertain answers
            annotation = annotations[fe].get('majority')
            if not annotation:
                continue

            # build token label using token position, FE and frame
            label = '%s_%s' % (fe, frame)
            iob_tagged = [ (token, '%s-%s' % ('B' if i == 0 else 'I', label))
                for i, token in enumerate(annotation.split())
            ]
            annotations['entities'][fe] = iob_tagged


def produce_training_data(annotations, pos_tagged_sentences_dir):
    """ Adds to the treetagger output information about frames """
    output = []
    for sentence_id, annotations in annotations.iteritems():

        # open treetagger output with tagged words
        with(codecs.open(pos_tagged_sentences_dir + sentence_id, 'rb', 'utf-8')) as i:
            lines = i.readlines()
            lines = [l.strip().split('\t') for l in lines]

            # Each line is a [token, pos, lemma]
            for i in xrange(0, len(lines)):
                # transform line so that it contains the following fields
                # sentence_id     token_id     token   pos     lemma   frame   IOB-tag

                lines[i].insert(0, sentence_id)
                lines[i].insert(1, str(i))
                lines[i].append(annotations['frame'])

                # TODO check if LUs can be more than one token
                if annotations['lu'] in lines[i]:
                    lines[i].append('B-LU') # IOB-tag
                else:
                    lines[i].append('O') # IOB-tag

                # find part of entity associated with the processed line 
                for entity, tokens in annotations['entities'].iteritems():
                    for token, tag in tokens:
                        if token.decode('utf-8') == lines[i][2]:
                            lines[i][-1] = tag

        output.extend(lines)
 
    return output


def main(crowdflower_csv, pos_data_dir, output_file, debug):
    results = read_full_results(crowdflower_csv)
    if debug:
        print 'Results from crowdflower'
        print json.dumps(results, indent=2)

    set_majority_vote_answer(results)
    if debug:
        print 'Computed majority vote'
        print json.dumps(results, indent=2)

    tag_entities(results)
    if debug:
        print 'Entities tagged'
        print json.dumps(results, indent=2)


    output = produce_training_data(results, pos_data_dir)
    if debug:
        print 'Final Output'
        print '\n'.join(repr(l) for l in output)


    output_file.writelines('\t'.join(l).encode('utf-8') + '\n'
                           for l in output
                           if '<strong>' not in l and '</strong>' not in l)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('crowdflower_csv', type=argparse.FileType('r'),
                        help='CSV file with the results coming from crowdflower')
    parser.add_argument('pos_data_dir',
                        help='Directory containing the output of treetagger')
    parser.add_argument('output_file', type=argparse.FileType('w'),
                        help='Where to store the produced training data')
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('-d', dest='debug', action='store_true')
    parser.add_argument('--no-debug', dest='debug', action='store_false')
    args = parser.parse_args()
    assert os.path.exists(args.pos_data_dir)

    main(args.crowdflower_csv, args.pos_data_dir, args.output_file, args.debug)
