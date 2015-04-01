#!/usr/bin/env python
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
    # fe_amount = len([f for f in fields if re.match(r'fe[0-9]{2}$', f)])
    token_amount = len([f for f in fields if re.match(r'token[0-9]{2}$', f)])

    # Skip gold
    regular = [row for row in results if row['_golden'] != 'true']
    for row in regular:
        sentence_id = row['id']
        sentence = h.unescape(row['sentence'].decode('utf-8'))

        # initialize data structure with sentence, frame, lu and token list
        if not sentence_id in processed:
            processed[sentence_id] = dict()
            processed[sentence_id]['sentence'] = sentence
            processed[sentence_id]['frame'] = row['frame']
            processed[sentence_id]['lu'] = row['lu']
            for n in xrange(0, token_amount):
                entity = row['orig_token%02d' % n]
                processed[sentence_id][entity] = {
                    'judgments': 0,
                    'answers': list()
                }

        # update judgments for each token
        for n in xrange(0, token_amount):
            entity = row['orig_token%02d' % n]
            answer = row.get('token%02d' % n)
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
            iob_tagged = [ (token, '%s-%s' % ('B' if i == 0 else 'I', label.decode('utf-8')))
                for i, token in enumerate(annotation.split())
            ]
            annotations['entities'][fe] = iob_tagged

        annotations['entities']['lu'] = [ (token, '%s-LU' % ('B' if i == 0 else 'I'))
            for i, token in enumerate(annotations['lu'].split())
        ]


def process_sentence(sentence_id, annotations, lines):
    """ Processes a sentence by merging tagged words, LU and FEs """

    processed = list()
    for i, (token, pos, lemma) in enumerate(lines):
        # TODO check if LUs can be more than one token
        processed.append([
            sentence_id, str(i), token, pos, lemma, annotations['frame'].decode('utf-8'), 'O'
        ])

    # find the entities in the sentence and set iob tags accordingly
    # checking for single tokens is not enough, entities have to be matched as a
    # whole (i.e. all its tokens must appear in sequence)
    for entity, tokens in annotations['entities'].iteritems():
        found = False
        i = j = 0
        while i < len(processed):
            # if we are tagging the LU then grab the infinitive of the verb instead
            # of the actual declined verb
            word = processed[i][2] if entity != 'lu' else processed[i][4]
            if tokens[j][0] == word:
                j += 1
                if j == len(tokens):
                    found = True
                    break
            else:
                j = 0
            i += 1

        if found:
            for line, (token, tag) in zip(processed[i-len(tokens) + 1:i + 1], tokens):
                line[-1] = tag

    return processed


def produce_training_data(annotations, pos_tagged_sentences_dir, debug):
    """ Adds to the treetagger output information about frames """
    output = []
    for sentence_id, annotations in annotations.iteritems():

        # open treetagger output with tagged words
        with(codecs.open(pos_tagged_sentences_dir + sentence_id, 'rb', 'utf-8')) as i:
            lines = [l.strip().split('\t') for l in i.readlines()]
            processed = process_sentence(sentence_id, annotations, lines)
            output.extend(processed)

            if debug:
                print 'Annotations'
                print json.dumps(annotations, indent=2)
                print 'Result'
                print '\n'.join(repr(x) for x in processed)
 
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

    output = produce_training_data(results, pos_data_dir, debug)

    output_file.writelines('\t'.join(l).encode('utf-8') + '\n'
                           for l in output
                           if '<strong>' not in l and '</strong>' not in l)

    return 0


def create_cli_parser():
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

    return parser


if __name__ == "__main__":
    parser = create_cli_parser()
    args = parser.parse_args()
    assert os.path.exists(args.pos_data_dir)

    sys.exit(main(args.crowdflower_csv, args.pos_data_dir, args.output_file, args.debug))
