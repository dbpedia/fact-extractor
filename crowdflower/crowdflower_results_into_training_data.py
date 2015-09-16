#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
this script transforms the output of the crowdflower job, in csv form, into our standard
training format, a tsv with <sentence id> <token id> <token> <POS> <lemma> <frame> <tag>
"""


import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import codecs
import re
import sys
import json
import argparse
import random
from collections import Counter
from lib.orderedset import OrderedSet
from date_normalizer import normalize_numerical_fes
from utils import read_full_results


def set_majority_vote_answer(results_json):
    """ Determine the correct entity which corresponds to a given FE

    :param dict results_json: a dictionary with the FEs of each sentence
    :return: None, but sets a new key 'majority' in each FE
    """

    for k, v in results_json.iteritems():
        for fe in v.keys():
            if fe in {'frame', 'lu', 'sentence'}:
                continue

            answers = [x['answer'] for x in v[fe]['answers']]
            answers_count = Counter(answers)
            majority = v[fe]['judgments'] / 2.0
            for answer, freq in answers_count.iteritems():
                if freq > majority:
                    v[fe]['majority'] = answer

            # Randomly break ties by picking one of the answers
            if not v[fe].get('majority'):
                chosen = random.choice(answers)
                v[fe]['majority'] = chosen
                print "HEADS UP! No majority answer for sentence [%s], FE [%s]. Randomly broken tie, picked [%s]" % (k, fe, answer)


def tag_entities(results):
    """ Creates the IOB tag for each entity found.

    :param dict results: a dictionary with the FEs of each sentence
    :return: None, but sets a new 'entities' key for each sentence
    """
    for annotations in results.values():
        frame = annotations['frame']

        annotations['entities'] = dict()
        for entity in annotations.keys():
            if entity in {'frame', 'lu', 'sentence'}:
                continue

            # skip uncertain answers
            annotation = annotations[entity].get('majority')
            if not annotation or annotation == 'Nessuno':
                continue

            # the entity is an n-gram, regardless of tokenization, so no I- tags
            annotations['entities'][entity] = annotation


def merge_tokens(sentence_id, annotations, lines):
    """ Merge tagged words, LU and FEs

    :param str sentence_id: The ID of the sentence
    :param dict annotations: The data about this sentence
    :param list lines: The POS tagging of the sentence
    :return: The merged tokens enhanced with the frame and the tag
    :rtype: list
    """

    processed = list()
    
    for i, (token, pos, lemma) in enumerate(lines):
        # TODO check if LUs can be more than one token
        tag = 'LU' if lemma == annotations['lu'] else 'O'
        processed.append([
            sentence_id, '-', token, pos, lemma, annotations['frame'], tag
        ])

    # find the entities in the sentence and set group them into a single token
    # checking for single tokens is not enough, entities have to be matched as a
    # whole (i.e. all its tokens must appear in sequence)
    for entity, tag in annotations['entities'].iteritems():
        tokens = entity.split()
        found = False
        i = j = 0

        # try to match all tokens of the entity
        while i < len(processed):
            word = processed[i][2]

            if tokens[j] == word:
                j += 1
                if j == len(tokens):
                    found = True
                    break
            else:
                j = 0
            i += 1

        if found:
            match_start = i - len(tokens) + 1
            to_replace = processed[i]
            # use the 'ENT' tag only if the n-gram has more than 1 token,
            # otherwise keep the original POS tag
            if len(tokens) > 1:
                replacement = [sentence_id, '-', entity, 'ENT', entity,
                               annotations['frame'], tag]
            else:
                replacement = [sentence_id, '-', entity, to_replace[3], entity,
                               annotations['frame'], tag]

            processed = processed[:match_start] + [replacement] + processed[i + 1:]

    return processed


def process_sentence(sentence_id, annotations, lines):
    """ process a single sentence by merging the tokens and normalizing numerical expressions

    :param str sentence_id: The ID of this sentence
    :param dict annotations: The data about this sentence's FEs
    :param list lines: The POS tagging of this sentence
    :return: The processed sentence
    :rtype: list
    """
    merged = merge_tokens(sentence_id, annotations, lines)
    normalized = normalize_numerical_fes(sentence_id, merged)

    # insert correct token ids
    for i, p in enumerate(normalized):
        p[1] = str(i)

    clean = OrderedSet()
    for line in normalized:
        clean.add('\t'.join(line))

    return clean


def produce_training_data(annotations, pos_tagged_sentences_dir, debug):
    """ Adds to the treetagger output information about frames

    :param dict annotations: Annotation data for each sentence
    :param str pos_tagged_sentences_dir: path of directory containing POS tagging results
    :param bool debug: Print debugging information?
    :return: The training data with POS tagging, frame and IOB tag info
    :rtype: list
    """
    output = []
    for sentence_id, annotations in annotations.iteritems():
        # pos-tagged filenames are not formatted with 4 digits, so strip leading zeros
        sentence_id = sentence_id.lstrip('0')
        if not sentence_id: sentence_id = '0'
        # open treetagger output with tagged words
        with(codecs.open(os.path.join(pos_tagged_sentences_dir, sentence_id),
                         'rb', 'utf-8')) as i:
            lines = []
            for line in i:
                items = line.strip().split('\t')
                # there must be 3 items (token, pos, lemma)
                if len(items) != 3:
                    print 'HEADS UP! Sentence [%s], malformed pos-tagged line %s. Skipping...' % (sentence_id, items)
                    continue
                lines.append(items)
            processed = process_sentence(sentence_id, annotations, lines)
            output.extend(processed)

            if debug:
                print 'Annotations'
                print json.dumps(annotations, indent=2)
                print 'Result'
                print '\n'.join(repr(x) for x in processed)

    return output


def main(crowdflower_csv, pos_data_dir, output_file, debug):
    """ Transform the crowdflower results into training data

    :param file crowdflower_csv: The CSV containing crowdflower data
    :param str pos_data_dir: The directory containing POS tagging for each sentence
    :param file output_file: The file in which to write the training data
    :return: 0
    :rtype: int
    """
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
    for l in output:
        output_file.write(l.encode('utf-8') + '\n')

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
