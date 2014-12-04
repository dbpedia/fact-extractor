#!/opt/local/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import csv
import json
import HTMLParser
from collections import Counter

def read_full_results(results_file):
    h = HTMLParser.HTMLParser()
    processed = {}
    with open(results_file, 'rb') as f:
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
                for n in xrange(0, fe_amount):
                    answer = row.get('fe_name' + str(n))
                    answers = processed[sentence_id][row['orig_fe_name' + str(n)]].get('answers', [])
                    if answer:
                        processed[sentence_id][row['orig_fe_name' + str(n)]]['judgments'] += 1
                        answers.append(answer)
            else:
                processed[sentence_id] = {}
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


# FIXME need lemma info
def write_training_data(results_json, output_file):
    with open(output_file, 'wb') as o:
        writer = csv.DictWriter(o, results_json.keys(), separator=' ')
        writer.writeheader()
        writer.writerows(results_json)
    return 0


# sid     tid     token   pos     lemma   frame   LU/FE
# FIXME build an easy-to-parse JSON
# {sid: ..., tid: ..., token: ...} etc.
def flatten_json(results_json):
    return 0


if __name__ == "__main__":
    print json.dumps(set_majority_vote_answer(read_full_results(sys.argv[1])), indent=2)
