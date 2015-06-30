#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import codecs
import re
import sys
import csv
import json
import HTMLParser
import argparse
import os
from collections import Counter
from lib.orderedset import OrderedSet
from date_normalizer import DateNormalizer


def read_full_results(results_file):
    """ Reads and aggregates the results from an open stream"""
    h = HTMLParser.HTMLParser()
    processed = {}

    # TODO csv lib doesn't handle unicode
    results = csv.DictReader(results_file)
    fields = results.fieldnames
    fe_amount = len([f for f in fields if re.match(r'fe[0-9]{2}$', f)])

    # Skip gold
    regular = [row for row in results if row['_golden'] != 'true']
    for row in regular:
        # Avoid Unicode encode/decode exceptions
        for k, v in row.iteritems():
            row[k] = v.decode('utf-8')
        sentence_id = row['id']
        sentence = h.unescape(row['sentence'])

        # initialize data structure with sentence, frame, lu and entity list
        if sentence_id not in processed:
            processed[sentence_id] = dict()
            processed[sentence_id]['sentence'] = sentence
            processed[sentence_id]['frame'] = row['frame']
            processed[sentence_id]['lu'] = row['lu']
            for n in xrange(0, fe_amount):
                entity = row['orig_fe%02d' % n]
                if entity:
                    processed[sentence_id][entity] = {
                        'judgments': 0,
                        'answers': list()
                    }

        # update judgments for each entity
        for n in xrange(0, fe_amount):
            entity = row['orig_fe%02d' % n]
            answer = row.get('fe%02d' % n)
            if entity and answer:
                processed[sentence_id][entity]['judgments'] += 1
                processed[sentence_id][entity]['answers'].append(answer)

    return processed


def set_majority_vote_answer(results_json):
    """ Determine the correct entity which corresponds to a given FE """

    for k, v in results_json.iteritems():
        for fe in v.keys():
            if fe in {'frame', 'lu', 'sentence'}:
                continue

            answers_count = Counter(v[fe]['answers'])
            majority = v[fe]['judgments'] / 2.0
            for answer, freq in answers_count.iteritems():
                if freq > majority:
                    v[fe]['majority'] = answer

            if not v[fe].get('majority'):
                print "HEADS UP! No majority answer for sentence [%s], FE [%s]" % (k, fe)


def tag_entities(results):
    """ Creates the IOB tag for each entity found. """
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

            # build the entity FE label, using FE name and frame
            fe_label = 'B-%s_%s' % (annotation, frame)
            # the entity is an n-gram, regardless of tokenization, so no I- tags
            annotations['entities'][entity] = fe_label


def merge_tokens(sentence_id, annotations, lines):
    """ Merge tagged words, LU and FEs """

    processed = list()
    for i, (token, pos, lemma) in enumerate(lines):
        # TODO check if LUs can be more than one token
        tag = 'B-LU' if lemma == annotations['lu'] else 'O'
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


def normalize_numerical_fes(sentence_id, tokens):
    """ normalize numerical FEs such as dates, durations, etc """
    normalizer = DateNormalizer()
    sentence = ' '.join(x[2] for x in tokens)

    for (start, end), norm in normalizer.normalize_many(sentence):
        original = sentence[start:end]

        # find the first token of the match
        cursor = i = 0
        while cursor < start:
            cursor += len(tokens[i][2]) + 1  # remember the space between tokens
            i += 1

        # find the last token of the match
        j = i + 1
        while ' '.join(x[2] for x in tokens[i:j]) != original:
            j += 1

        # find an appropriate tag (i.e. anything different from 'O'
        # if exists among the matching tokens)
        tags = set(x[-1] for x in tokens[i:j] if x[-1] != 'O')
        assert len(tags) in {0, 1}, 'Cannot decide which tag to use for %s: %r' % (
                                    original, tags)
        tag = tags.pop() if tags else 'O'

        # replace the old tokens with a new one
        tokens = (tokens[:i] +
                  [[sentence_id, '-', original, 'ENT', original, tokens[0][-2], tag]] +
                  tokens[j:])
        assert ' '.join(x[2] for x in tokens) == sentence, 'Failed to rebuild sentence'

    return tokens


def process_sentence(sentence_id, annotations, lines):
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
