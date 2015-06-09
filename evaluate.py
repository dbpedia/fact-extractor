#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import csv
import logging
import json
import random
import re
from collections import defaultdict
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


def load_expected_frames(frame_gold):
    """Build the dict with the expected frames for all the sentences"""
    expected = {}
    for line in frame_gold:
        sentence, frames = line.strip().split('\t')
        frames = frames.split('|')
        expected[sentence] = frames
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


def frame_positives(labeled_data, frame_gold, logger):
    """Compute frame true and false positives"""
    tp = fp = 0
    logger.debug(frame_gold)
    for sentence in labeled_data:
        snt = sentence['sentence']
        seen = sentence['frame']
        expected = frame_gold.get(snt)
        if not expected:
            continue
        logger.debug("Sentence [%s]: frame = [%s]" % (snt, seen))
        logger.debug("Expected frames = %s" % expected)
        if seen in expected:
            tp += 1
            logger.debug("+1 true positive!")
        else:
            fp += 1
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
    
    
def get_labeled_data_subset(full_labeled_data, processed_annotation_results, logger):
    """Return the labeled data subset corresponding to the annotation results"""
    subset = []
    sentence_ids = processed_annotation_results.keys()
    for sentence in full_labeled_data:
        if sentence['id'] in sentence_ids:
            subset.append(sentence)
    return subset
    
    
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


def load_full_gold_standard(full_gold_standard, logger):
    """Read a full annotation to evaluate against from a TSV open stream"""
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
        # It's a FE
        if tag != 'B-LU' and tag != 'O':
            to_fill['FE'] = tag.split('_')[0].replace('B-', '')
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
    """
    if exact:
        logger.info("FE chunks EXACT checking enabled")
    else:
        logger.info("FE chunks PARTIAL checking enabled")
    frame_tp = frame_fp = frame_fn = fe_tp = fe_fp = fe_fn = 0
    for sentence in labeled_data:
        sentence_id = sentence['id']
        logger.debug("Labeled sentence [%s]" % sentence_id)
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
            
        # FEs
        logger.debug("----------- Evaluating FEs... -----------")
        seen_fes = sentence['FEs']
        seen = {}
        for seen_fe_obj in seen_fes:
            seen_fe = seen_fe_obj['FE']
            seen_chunk = seen_fe_obj['chunk']
            seen[seen_chunk] = seen_fe
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
                if partial_matches == 0:
                    logger.debug("Expected chunk [%s] NOT in seen chunks %s" % (chunk, seen.keys()))
                    fe_fn += 1
                    logger.debug("+1 FE false negative, current recall = %f" % recall(fe_tp, fe_fn))
                            
        logger.debug("=================================")

    # Compute all measures
    frame_precision = precision(frame_tp, frame_fp)
    frame_recall = recall(frame_tp, frame_fn)
    fe_precision = precision(fe_tp, fe_fp)
    fe_recall = recall(fe_tp, fe_fn)
    return ( (frame_precision, frame_recall, f1(frame_precision, frame_recall)), (fe_precision, fe_recall, f1(fe_precision, fe_recall)) )


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
    parser.add_argument('labeled_data', type=argparse.FileType('r'), help='JSON file with labeled data for each sentence')
    parser.add_argument('gold_standard', type=argparse.FileType('r'), help='TSV file with full frame annotation to evaluate against')
    parser.add_argument('--crowdflower', type=argparse.FileType('r'), help='CrowdFlower CSV file containing the annotation results to evaluate against')
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
    # results = read_crowdflower_full_results(args.crowdflower)
    # set_majority_vote_answer(results)
    # logger.debug(json.dumps(results, ensure_ascii=False, indent=2))
    # fe_tp, fe_fp = fe_positives(results, logger)
    # fe_precision = precision(fe_tp, fe_fp)
    # expected = load_expected_fes(FRAME_DEFINITIONS)
    # labeled_data_subset = get_labeled_data_subset(labeled_data, results, logger)
    # fe_fn = fe_false_negatives(labeled_data_subset, expected, logger)
    # fe_recall = recall(fe_tp, fe_fn)
    # expected_frames = load_expected_frames(args.frame_gold)
    # frame_tp, frame_fp = frame_positives(labeled_data, expected_frames, logger)
    # frame_precision = precision(frame_tp, frame_fp)
    # logger.info("Frame precision = %f" % frame_precision)
    # logger.info("FE precision = %f" % fe_precision)
    # logger.info("FE recall = %f" % fe_recall)
    # logger.info("FE F1 = %f" % f1(fe_precision, fe_recall))
    return 0
    
    
if __name__ == '__main__':
    cli = create_cli_parser()
    args = cli.parse_args()
    exit(main(args))