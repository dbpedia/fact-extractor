#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
this script evaluates the unsupervised approach against the gold standard
"""

import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import csv
import logging
import json
import random
import re
from collections import defaultdict
from sys import argv, exit
from crowdflower.crowdflower_results_into_training_data import set_majority_vote_answer
from resources.soccer_lu2frame_dbtypes import LU_FRAME_MAP as FRAME_DEFINITIONS


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
    """Load labeled data JSON from a file

    :param file filein: Open file with the labeled data
    :return: The labeled data
    :rtype: dict
    """
    return json.load(filein, 'utf-8')


def load_full_gold_standard(full_gold_standard, logger):
    """Read a full annotation to evaluate against from a TSV open stream

    :param list full_gold_standard: Rows of the gold standard file
    :param logger: Logger used to write information
    :return: The parsed data
    :rtype: dict
    :raises ValueError: if it is not possible to correctly split a line
    """
    annotations = []
    loaded = defaultdict(list)
    for line in full_gold_standard:
        current = {}
        # Detect malformed lines
        try:
            sentence_id, token_id, chunk, pos, lemma, frame, tag = line.decode('utf-8').strip().split('\t')
        except ValueError as e:
            logger.error("Malformed gold standard line (failed to split on tabs). Check for spaces instead of tabs and viceversa: %s" % line.decode('utf-8').strip().split('\t'))
            exit(1)
        to_fill = {}
        current['%04d' % int(sentence_id)] = to_fill
        
        to_fill['frame'] = frame
        # # Consider LU lemmas and FEs values for evaluation
        if tag != 'O':
            if tag == 'LU':
                to_fill['FE'] = tag
                to_fill['chunk'] = lemma
            else:
                # FE label naming convention: {LABEL}_{FRAME}
                to_fill['FE'] = tag.split('_')[0]
                to_fill['chunk'] = chunk
        else:
            continue
        annotations.append(current)
    # Join dicts on common ID key
    for annotation in annotations:
        for k, v in annotation.iteritems():
            loaded[k].append(v)
    return loaded


def evaluate_against_gold(labeled_data, gold_standard, logger, exact):
    """
    Evaluate the unsupervised approach output against a fully annotated gold standard.
    FE chunks checking:
    exact = exact string matching
    partial = substring matching

    :param dict labeled_data: Labeled data for each sentence coming from the unsupervised
    :param dict gold_standard: Gold standard data for each sentence
    :param logger: Logger used to write information
    :param bol exact: To perform exact substring matching
    :return: Tuple with two tuples: precision, recall and f1 for frames and for roles
    :rtype: tuple
    """
    if exact:
        logger.info("FE chunks EXACT checking enabled")
    else:
        logger.info("FE chunks PARTIAL checking enabled")
    frame_tp = frame_fp = frame_fn = fe_tp = fe_fp = fe_fn = 0
    for sentence in labeled_data:
        sentence_id = sentence['id']
        logger.debug('Labeled sentence [%s]: "%s"' % (sentence_id, sentence['sentence']))
        annotations = gold_standard.get(sentence_id)
        if not annotations:
            logger.warning("No gold standard for sentence [%s]. Skipping..." % sentence_id)
            logger.debug("=================================")
            continue
        # Frame
        logger.debug("----------- Evaluating frame... -----------")
        seen_frame = sentence.get('frame')
        if not seen_frame:
            frame_fn += 1
            logger.debug("No frame assigned to sentence [%s]. +1 frame false negative, current recall = %f" % (sentence_id, recall(frame_tp, frame_fn)))
            continue
        expected_frame = set([annotation['frame'] for annotation in annotations])
        # All annotations inside a sentence must have the same frame, otherwise the gold standard is wrong
        if len(expected_frame) > 1:
            logger.error("More than 1 frame (%s) detected in gold standard sentence [%s]. Please fix it." % (expected_frame, sentence_id))
            exit(1)
        # Pop the only one element
        expected_frame = expected_frame.pop()
        logger.debug("Seen = [%s], expected = [%s]" % (seen_frame, expected_frame))
        if seen_frame == expected_frame:
            frame_tp += 1
            logger.debug("+1 frame TRUE positive, current precision = %f" % precision(frame_tp, frame_fp))
        else:
            frame_fp += 1
            logger.debug("+1 frame FALSE positive, current precision = %f" % precision(frame_tp, frame_fp))
            frame_fn += 1
            logger.debug("+1 frame FALSE negative, current recall = %f" % recall(frame_tp, frame_fn))
        
        # FEs and LU lemmas
        logger.debug("----------- Evaluating FEs (including LU lemmas)... -----------")
        seen = {} # contains all the seen objects
        # FEs
        seen_fes = sentence['FEs']
        for seen_fe_obj in seen_fes:
            seen_fe = seen_fe_obj['FE']
            seen_chunk = seen_fe_obj['chunk']
            seen[seen_chunk] = seen_fe
        # LU lemmas
        seen_lu_lemma = sentence['lu']
        seen[seen_lu_lemma] = 'LU' 
        
        logger.debug("Seen FEs: %s" % seen)
        expected = {}
        for annotation in annotations:
            expected_fe = annotation['FE']
            expected_chunk = annotation['chunk']
            expected[expected_chunk] = expected_fe
        logger.debug("Expected FEs: %s" % expected)
        for chunk, fe in expected.iteritems():
            # Exact checking
            if exact:
                if chunk in seen.keys():
                    logger.debug("Expected chunk [%s] FOUND in seen chunks %s" % (chunk, seen.keys()))
                    if fe == seen[chunk]:
                        logger.debug("Seen FE = [%s], expected = [%s]" % (seen[chunk], fe))
                        fe_tp += 1
                        logger.debug("+1 FE TRUE positive, current precision = %f" % precision(fe_tp, fe_fp))
                    else:
                        logger.debug("Seen FE = [%s], expected = [%s]" % (seen[chunk], fe))
                        fe_fp += 1
                        logger.debug("+1 FE FALSE positive, current precision = %f" % precision(fe_tp, fe_fp))
                        fe_fn += 1
                        logger.debug("+1 FE FALSE negative, current recall = %f" % recall(fe_tp, fe_fn))
                else:
                    logger.debug("Expected chunk [%s] NOT in seen chunks %s" % (chunk, seen.keys()))
                    fe_fn += 1
                    logger.debug("+1 FE false negative, current recall = %f" % recall(fe_tp, fe_fn))
            # Partial checking
            else:
                partial_matches = 0
                for seen_chunk, seen_fe in seen.iteritems():
                    if seen_chunk in chunk:
                        partial_matches += 1
                        logger.debug("Seen chunk = [%s], expected = [%s]. At least a partial match" % (seen_chunk, chunk))
                        if fe == seen_fe:
                            logger.debug("Seen FE = [%s], expected = [%s]" % (seen_fe, fe))
                            fe_tp += 1
                            logger.debug("+1 FE TRUE positive, current precision = %f" % precision(fe_tp, fe_fp))
                        else:
                            logger.debug("Seen FE = [%s], expected = [%s]" % (seen_fe, fe))
                            fe_fp += 1
                            logger.debug("+1 FE FALSE positive, current precision = %f" % precision(fe_tp, fe_fp))
                            fe_fn += 1
                            logger.debug("+1 FE false negative, current recall = %f" % recall(fe_tp, fe_fn))
                if partial_matches == 0:
                    logger.debug("Expected chunk [%s] NOT in seen chunks %s" % (chunk, seen.keys()))
                    fe_fn += 1
                    logger.debug("+1 FE false negative, current recall = %f" % recall(fe_tp, fe_fn))
        # Check for false positives in the seen FEs that are not expected
        # Exact checking
        if exact:
            for seen_chunk in seen.keys():
                if seen_chunk not in expected.keys():
                    logger.debug("Seen chunk [%s] NOT IN expected chunks %s" % (seen_chunk, expected.keys()))
                    fe_fp += 1
                    logger.debug("+1 FE FALSE positive, current precision = %f" % precision(fe_tp, fe_fp))
        # Partial checking
        else:
            for seen_chunk in seen.keys():
                partial_matches = 0
                for expected_chunk in expected.keys():
                    if seen_chunk in expected_chunk:
                        partial_matches += 1
                if partial_matches == 0:
                    logger.debug("Seen chunk [%s] NOT PART of any expected chunks %s" % (seen_chunk, expected.keys()))
                    fe_fp += 1
                    logger.debug("+1 FE FALSE positive, current precision = %f" % precision(fe_tp, fe_fp))
                            
        logger.debug("=================================")

    # Compute all measures
    frame_precision = precision(frame_tp, frame_fp)
    frame_recall = recall(frame_tp, frame_fn)
    fe_precision = precision(fe_tp, fe_fp)
    fe_recall = recall(fe_tp, fe_fn)
    return ( (frame_precision, frame_recall, f1(frame_precision, frame_recall)), (fe_precision, fe_recall, f1(fe_precision, fe_recall)) )


def precision(tp, fp):
    """Standard precision measure

    :param int tp: True Positives
    :param int fp: False Positives
    :return: The Precision
    :rtype: float
    """
    return float(tp) / float(tp + fp)


def recall(tp, fn):
    """Standard recall measure

    :param int tp: True Poitives
    :param int fn: False Negatives
    :return: The Recall
    :rtype: float
    """
    return float(tp) / float(tp + fn)


def f1(p, r):
    """Standard F1 measure

    :param float p: Precision
    :param float r: Recall
    :return: The F1 score
    :rtype: float
    """
    return 2 * ((p * r) / (p + r))


def create_cli_parser():
    parser = argparse.ArgumentParser(description='Evaluate the unsupervised approach via standard measures (p, r, f1)')
    parser.add_argument('labeled_data', type=argparse.FileType('r'), help='JSON file with labeled data for each sentence')
    parser.add_argument('gold_standard', type=argparse.FileType('r'), help='TSV file with full frame annotation to evaluate against')
    parser.add_argument('--partial', action='store_false', default='True', help='Enable partial matching of FE chunks. Default is exact matching')
    parser.add_argument('--debug', action='store_const', const='debug', help='Toggle debug mode')
    return parser
    

def main(args):
    if args.debug:
        logger = setup_logger(args.debug)
    else:
        logger = setup_logger()
    labeled_data = load_labeled_data(args.labeled_data)
    gold = load_full_gold_standard(args.gold_standard, logger)
    # print json.dumps(gold, ensure_ascii=False, indent=2)
    performance = evaluate_against_gold(labeled_data, gold, logger, args.partial)
    print performance
    return 0
    
    
if __name__ == '__main__':
    cli = create_cli_parser()
    args = cli.parse_args()
    exit(main(args))
