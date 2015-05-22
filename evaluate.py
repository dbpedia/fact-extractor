#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import csv
import logging
import json
import random
import re
from sys import argv, exit
from crowdflower_results_into_training_data import set_majority_vote_answer


FRAME_DEFINITIONS = json.load(open('resources/soccer-lu2frame-dbptypes.json'), 'utf-8')


def setup_logger(level='info'):
    """Convenience function to setup logging capability"""
    levels = {'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG}
    logger = logging.getLogger()
    logger.setLevel(levels[level])
    # Message format
    logFormatter = logging.Formatter("[%(levelname)-7.7s] %(funcName)s - %(message)s")
    # Log to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    return logger


def load_labeled_data(filein):
    """Load labeled data JSON from a file"""
    return json.load(filein, 'utf-8')


def load_expected_fes(frame_definitions):
    """Build the list of core FEs expected for all the defined frames"""
    all_frames = set()
    expected = {}
    for lu in frame_definitions:
        frames = lu['lu']['frames']
        for frame in frames:
            frame_label = frame['frame']
            if frame_label in all_frames:
                continue
            all_frames.add(frame_label)
            fes = frame['FEs']
            core_fes = []
            for fe in fes:
                fe_label, fe_type = fe.items()[0]
                if fe_type == 'core':
                    core_fes.append(fe_label)
            expected[frame_label] = core_fes
    return expected


def read_crowdflower_full_results(full_results):
    """ Reads and aggregates the CrowdFlower full annotation results from an open stream"""
    processed = {}
    results = csv.DictReader(full_results)
    fields = results.fieldnames
    fe_amount = len([f for f in fields if re.match(r'known_fe[0-9]{2}$', f)])
    
    for row in results:
        # Avoid Unicode encode/decode exceptions (csv lib doesn't seem to handle them)
        for k, v in row.iteritems():
            row[k] = v.decode('utf-8')
        sentence_id = row['id']
        sentence = row['sentence']

        # initialize data structure with sentence, frame, lu and entity list
        if not sentence_id in processed:
            processed[sentence_id] = dict()
            processed[sentence_id]['sentence'] = sentence
            processed[sentence_id]['frame'] = row['frame']
            processed[sentence_id]['lu'] = row['lu']
            for n in xrange(0, fe_amount):
                entity = row['orig_known_fe%02d' % n]
                if entity:
                    processed[sentence_id][entity] = {
                        'judgments': 0,
                        'answers': list()
                    }

        # update judgments for each entity
        for n in xrange(0, fe_amount):
            entity = row['orig_known_fe%02d' % n]
            answer = row.get('known_fe%02d' % n)
            if entity and answer:
                processed[sentence_id][entity]['judgments'] += 1
                processed[sentence_id][entity]['answers'].append(answer)

    return processed


def frame_positives(processed_annotation_results):
    """Compute frame true and false positives"""
    return tp, fp


def fe_positives(processed_annotation_results, logger):
    """Compute FEs true and false positives"""
    tp = fp = 0
    for sentence_id, annotations in processed_annotation_results.iteritems():
        for fe in annotations.keys():
            # Skip JSON keys that are not FEs
            if fe in {'frame', 'lu', 'sentence'}:
                continue
            answer = annotations[fe].get('majority')
            # Randomly break ties by picking one of the answers
            if not answer:
                answer = random.choice(annotations[fe]['answers'])
                logger.debug("Randomly broke a tie, picked [%s]" % answer)
            logger.debug("Sentence [%s], FE [%s], answer [%s]" % (sentence_id, fe, answer))
            if answer == u'Sì':
                tp += 1
            else:
                fp += 1
            
    return tp, fp


# Discarded sentences from produce_labeled_data.py need to be manually checked
def frame_false_negatives(missed_sentences):
    """Compute frame false negatives"""
    return len(missed_sentences)
    

# FIXME we are comparing against the frame definitions, not the gold standard here!!!
def fe_false_negatives(labeled_data, expected_fes, logger):
    """Compute core FEs false negatives"""
    fe_fn = 0
    for sentence in labeled_data:
        frame = sentence['frame']
        seen = set([fe['FE'] for fe in sentence['FEs']])
        logger.debug("Sentence %s: frame = [%s], FEs = %s" % (sentence['id'], frame, seen))
        expected = set(expected_fes[frame])
        logger.debug("Expected FEs = %s" % expected)
        missed = expected.intersection(seen)
        logger.debug("Missed FEs = %s" % missed)
        fe_fn += len(missed)
        logger.debug("Current FE false negatives = %d" % fe_fn)
    logger.info("Total FE false negatives = %d" % fe_fn)
    return fe_fn


def precision(tp, fp):
    """Standard precision measure"""
    return float(tp) / float(tp + fp)


def recall(tp, fn):
    """Standard recall measure"""
    return float(tp) / float(tp + fn)


def f1(p, r):
    """Standard F1 measure"""
    return 2 * ((p * r) / (p + r))


def create_cli_parser():
    parser = argparse.ArgumentParser(description='Evaluate the unsupervised approach via standard measures (p, r, f1)')
    parser.add_argument('labeled_data', type=argparse.FileType('r'), help='JSON file containing labeled data for each sentence')
    parser.add_argument('annotation_results', type=argparse.FileType('r'), help='CrowdFlower CSV file containing the annotation results to evaluate against')
    parser.add_argument('--debug', action='store_const', const='debug', help='Toggle debug mode')
    return parser
    

def main():
    cli = create_cli_parser()
    args = cli.parse_args()
    if args.debug:
        logger = setup_logger(args.debug)
    else:
        logger = setup_logger()
    labeled_data = load_labeled_data(args.labeled_data)
    results = read_crowdflower_full_results(args.annotation_results)
    set_majority_vote_answer(results)
    fe_tp, fe_fp = fe_positives(results, logger)
    print precision(fe_tp, fe_fp)
    # print json.dumps(results, ensure_ascii=False, indent=2)
    # expected = load_expected_fes(FRAME_DEFINITIONS)
    # fe_fn = fe_false_negatives(labeled_data, expected, logger)
    # print fe_fn
    return 0
    
    
if __name__ == '__main__':
    exit(main())