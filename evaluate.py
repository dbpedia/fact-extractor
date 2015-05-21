#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
import json


FRAME_DEFINITIONS = json.load(open('resources/soccer-lu2frame-dbptypes.json'), 'utf-8')


def setup_logger(level='info'):
    """Convenience function to setup logging capability"""
    levels = {'info': logging.INFO, 'warning': logging.WARNING, 'debug': logging.DEBUG}
    logger = logging.getLogger()
    logger.setLevel(levels[level])
    # Message format
    logFormatter = logging.Formatter("[%(levelname)-7.7s] %(funcName)s - %(message)s")
    # Log to console
    # logger.handlers.pop()
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    return logger


def load_labeled_data(filein):
    """Load labeled data JSON from a file"""
    with open(filein) as i:
        data = json.load(i)
    return data


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


def true_positives(annotation_results):
    """Compute frame and FEs true positives"""
    return frame_tp, fe_tp


def frame_false_negatives(labeled_data, sentences):
    """Compute frame false negatives"""
    return frame_fn
    
    
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


if __name__ == '__main__':
    logger = setup_logger('debug')
    labeled_data = load_labeled_data('../hamoltosenso/labeled_data.json')
    expected = load_expected_fes(FRAME_DEFINITIONS)
    fe_fn = fe_false_negatives(labeled_data, expected, logger)
    print fe_fn