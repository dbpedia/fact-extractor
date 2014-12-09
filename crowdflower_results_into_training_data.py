#!/opt/local/bin/python
# -*- coding: utf-8 -*-

import codecs
import re
import sys
import csv
import json
import HTMLParser
from collections import Counter


def read_full_results(results_file):
    h = HTMLParser.HTMLParser()
    processed = {}
    with codecs.open(results_file, 'rb', 'utf-8') as f:
        results = csv.DictReader(f)
        fe_amount = 0
        fields = results.fieldnames
        for f in fields:
            if re.match('fe_name[0-9]$', f):
                fe_amount += 1
        # Skip gold
        regular = [row for row in results if row['_golden'] == 'false']
        for row in regular:
            sentence_id = row['id']
            sentence = h.unescape(row['sentence'].decode('utf-8'))
            if processed.get(sentence_id):
                processed[sentence_id]['sentence'] = sentence
                processed[sentence_id]['frame'] = row['frame']
                processed[sentence_id]['lu'] = row['lu']
                for n in xrange(0, fe_amount):
                    answer = row.get('fe_name' + str(n))
                    answers = processed[sentence_id][row['orig_fe_name' + str(n)]].get('answers', [])
                    if answer:
                        processed[sentence_id][row['orig_fe_name' + str(n)]]['judgments'] += 1
                        answers.append(answer)
            else:
                processed[sentence_id] = {}
                processed[sentence_id]['sentence'] = sentence
                processed[sentence_id]['frame'] = row['frame']
                processed[sentence_id]['lu'] = row['lu']
                for n in xrange(0, fe_amount):
                    answer = row.get('fe_name' + str(n))
                    processed[sentence_id][row['orig_fe_name' + str(n)]] = {}
                    answers = processed[sentence_id][row['orig_fe_name' + str(n)]]['answers'] = []
                    if answer:
                        processed[sentence_id][row['orig_fe_name' + str(n)]]['judgments'] = 1
                        answers.append(answer)
    return processed


def set_majority_vote_answer(results_json):
    for k,v in results_json.iteritems():
        for fe in v.keys():
            if fe:
                answers_count = Counter(v[fe]['answers'])
                majority = float(v[fe]['judgments'])/2.0
                for answer,freq in answers_count.iteritems():
                    if freq > majority: v[fe]['majority'] = answer
                if not v[fe].get('majority'): print "HEADS UP! No majority answer for sentence [%s], FE [%s]" % (k, fe)
    return results_json


def produce_training_data(annotations, pos_tagged_sentences_dir, output_file):
    output = []
    for sentence_id, annotations in annotations.iteritems():
        with(codecs.open(pos_tagged_sentences_dir + sentence_id, 'rb', 'utf-8')) as i:
            lines = i.readlines()
            lines = [l.strip().split('\t') for l in lines]
            # Each line is a [token, pos, lemma]
            for i in xrange(0, len(lines)):
                # sentence_id     token_id     token   pos     lemma   frame   IOB-tag
                lines[i].insert(0, sentence_id)
                lines[i].insert(1, str(i))
                lines[i].append(annotations['frame'])
# TODO check if LUs can be more than one token
                if annotations['lu'] in lines[i]:
                    lines[i].append('B-LU')
                else: lines[i].append('O')
                for fe in annotations.keys():
                    if fe != 'frame' and fe != 'lu':
                        annotation = annotations[fe]
                        annotation = annotation.get('majority')
                        if annotation:
                            tokens = annotation.split()
                            iob_tagged = [(tokens[0], 'B-' + fe)]
                            for token in tokens[1:]:
                                iob_tagged.append((token, 'I-' + fe))
                            for iob_tag in iob_tagged:
                                if iob_tag[0] in lines[i]:
                                    lines[i].pop()
                                    lines[i].append(iob_tag[1])
        for l in lines:
            output.append(' '.join(l) + '\n')
    with codecs.open(output_file, 'wb', 'utf-8') as o:
        o.writelines(output)
    return 0

if __name__ == "__main__":
    annotazione_test = json.loads("""
    { "40": {
        "": {
        "answers": []
        },
        "frame": "Porco_Dio",
        "lu" : "pubblicare",
        "Pubblicatore": {
        "majority": "Fedele anglicano",
        "judgments": 3,
        "answers": [
            "suca",
            "coglione",
            "puppa"
        ]
        },
        "Opera": {
        "majority": "opere a difesa dell' anglicanesimo",
        "judgments": 3,
        "answers": [
        "suca",
        "coglione",
        "puppa"
        ]
        }
        }
    }
    """
    )
    produce_training_data(set_majority_vote_answer(read_full_results(sys.argv[1])), sys.argv[2], sys.argv[3])
