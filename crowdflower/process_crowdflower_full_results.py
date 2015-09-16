#!/opt/local/bin/python
# -*- coding: utf-8 -*-

import sys
import csv
import json
import HTMLParser
from bs4 import BeautifulSoup

h = HTMLParser.HTMLParser()
processed = {}

if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as f:
      results = csv.DictReader(f)
      print results.fieldnames
      # Skip gold
      regular = [row for row in results if row['_golden'] == 'false']
      for riga in regular:
        sentence = riga['_unit_id']
        soup_sent = BeautifulSoup(h.unescape(riga['sentence'].decode('utf-8')))

        if sentence in processed.keys():
          for n in xrange(0, 4):
            answer = riga.get('fe_name' + str(n))
            if answer:
              processed[sentence]['fe' + str(n)]['judgments'] += 1
              fe_name = riga['orig_fe_name' + str(n)]
              candidates = [item.text for item in soup_sent.find_all(fe_name)]
              print candidates
              if candidates and answer in candidates:
                processed[sentence]['fe' + str(n)]['correct'] += 1
              elif not candidates and answer == 'None':
                processed[sentence]['fe' + str(n)]['correct'] += 1
              else:
                processed[sentence]['fe' + str(n)]['wrong'] += 1
        else:
          processed[sentence] = {}
          for n in xrange(0, 4):
            answer = riga.get('fe_name' + str(n))
            if answer:
              fe_name = riga['orig_fe_name' + str(n)]
              candidates = [item.text for item in soup_sent.find_all(fe_name)]
              if candidates and answer in candidates:
                processed[sentence]['fe' + str(n)] = {'judgments': 1, 'correct': 1, 'wrong': 0}
              elif not candidates and answer == 'None':
                processed[sentence]['fe' + str(n)] = {'judgments': 1, 'correct': 1, 'wrong': 0}
              else:
                processed[sentence]['fe' + str(n)] = {'judgments': 1, 'correct': 0, 'wrong': 1}

    print json.dumps(processed, indent=2)

    judgments = answers = correct = wrong = majority = float(0)

    for ans in processed.values():
      for answer in ans.values():
        judgments += answer['judgments']
        answers += 1
        c = answer['correct']
        w = answer['wrong']
        correct += c
        wrong += w
        if c > w:
          majority += 1

    final = {'total_judgments': judgments, 'wrong_judgments': wrong, 'correct_judgments': correct, 'total_FE_definitions': answers,  'correct_majority': majority, 'absolute_accuracy': correct/judgments, 'majority_accuracy': majority/answers}
    print json.dumps(final, indent=2)
