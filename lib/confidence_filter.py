#!/usr/bin/env python
# encoding: utf-8

import click
import re
from os.path import abspath
from numpy import average

@click.command()
@click.argument('fact-dataset', type=click.File('r'))
@click.argument('score-dataset', type=click.File('r'))
@click.argument('output', type=click.File('w'), default='confident.nt')
@click.option('--debug/--no-debug', default=False)
def main(fact_dataset, score_dataset, output, debug):
    all_scores = []
    to_filter = []
    filtered = []
    # In-memory load is needed here, we have to access the data twice
    score_dataset = score_dataset.readlines()
    for triple in score_dataset:
        if not triple:
            if debug:
                print 'Skipping empty line ...'
            continue
        score_match = re.search(r'"([^"]+)"', triple)
        if score_match:
            score = float(score_match.group(1))
        else:
            if debug:
                print "Couldn't extract any score from triple [%s]" % triple.rstrip()
            continue
        if debug:
            print 'Extracted score [%f] from triple [%s]' % (score, triple.rstrip())
        all_scores.append(score)
    # Confidence threshold based on average
    threshold = average(all_scores)
    print 'Confidence threshold set to average score [%f]' % threshold
    for triple in score_dataset:
        if not triple:
            if debug:
                print 'Skipping empty line ...'
            continue
        score_match = re.search(r'"([^"]+)"', triple)
        if score_match:
            score = float(score_match.group(1))
        else:
            if debug:
                print "Couldn't extract any score from triple [%s]" % triple.rstrip()
            continue
        if score >= threshold:
            node = triple.split()[0]
            if debug:
                print 'Score [%f] >= threshold [%f]. Got a confident node [%s]' % (score, threshold, node)
            to_filter.append(node)
    # Avoid in-memory load here, but keep track of the dataset size
    fact_dataset_size = 0
    for triple in fact_dataset:
        fact_dataset_size += 1
        for node in to_filter:
            if node in triple:
                if debug:
                    print 'Triple [%s] contains confident node [%s]' % (triple.rstrip(), node)
                filtered.append(triple)
    output.writelines(filtered)
    print 'Written confident dataset to [%s] with [%d] triples, ' % (abspath(output.name), len(filtered))
    print 'Original dataset has [%d] triples. Difference = [%d] triples' % (fact_dataset_size, fact_dataset_size - len(filtered))
    return 0


if __name__ == '__main__':
    main()
