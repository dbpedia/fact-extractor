#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import codecs
import json
import random
from lib import stopwords
import sys
from collections import defaultdict
from urllib import quote
from rfc3987 import parse  # URI/IRI validation
from date_normalizer import DateNormalizer
from resources.soccer_lu2frame_dbtypes import LU_FRAME_MAP
from lib.scoring import compute_score, AVAILABLE_SCORES
import click


NORMALIZER = DateNormalizer()


def label_sentence(entity_linking_results, debug, numerical):
    """Produce a labeled sentence by comparing the linked entities to the frame definition

    :param str entity_linking_results: path to JSON file containing the results of the
                                       entity linking
    :param bool debug: Print debugging information
    :param bool numerical: Normalize numerical FEs
    :return: labeled data for each sentence
    :rtype: dict
    """
    labeled = {}
    links = json.load(codecs.open(entity_linking_results, 'rb', 'utf-8'))
    sentence, val = links.items()[0]
    labeled['sentence'] = sentence
    labeled['FEs'] = defaultdict(list)
    # Tokenize by splitting on spaces
    sentence_tokens = sentence.split()
    if debug:
        print 'SENTENCE: %s' % sentence
        print 'TOKENS: %s' % sentence_tokens
    frames = []
    for lu in LU_FRAME_MAP:
        lu_tokens = lu['lu']['tokens']
        # Check if a sentence token matches a LU token and assign frames accordingly
        for sentence_token in sentence_tokens:
            if sentence_token in lu_tokens:
                if debug:
                    print 'TOKEN "%s" MATCHED IN LU TOKENS' % sentence_token
                labeled['lu'] = lu['lu']['lemma']
                frames = lu['lu']['frames']
                if debug:
                    print 'LU LEMMA: %s' % labeled['lu']
                    print 'FRAMES: %s' % [frame['frame'] for frame in frames]
                # Frame processing
                for frame in frames:
                    FEs = frame['FEs']
                    types_to_FEs = frame['DBpedia']
                    if debug:
                        print 'CURRENT FRAME: %s' % frame['frame']
                        print 'FEs: %s' % FEs
                    core = False
                    assigned_fes = []
                    for diz in val:
                        # Filter out linked stopwords
                        if diz['chunk'].lower() in stopwords.StopWords.words('italian'):
                            continue

                        chunk = {
                            'chunk': diz['chunk'],
                            'uri': diz['uri'],
                            'score': diz['score']
                        }

                        types = diz['types']
                        #### FE assignment ###
                        for t in types:
                            for mapping in types_to_FEs:
                                # Strip DBpedia ontology namespace
                                looked_up = mapping.get(t[28:])
                                if looked_up:
                                    if debug:
                                        print 'Chunk "%s" has an ontology type "%s" that maps to FE "%s"' % (chunk['chunk'], t[28:], looked_up)
                                    ### Frame disambiguation strategy, part 1 ###
                                    # LAPSE ASSIGNMENT
                                    # If there is AT LEAST ONE core FE, then assign that frame
                                    # TODO strict assignment: ALL core FEs must be found
                                    # Will not work if the FEs across competing frames have the same ontology type
                                    # e.g., Attività > Squadra and Partita > [Squadra_1, Squadra_2]

                                    # Check if looked up FE is core
                                    for fe in FEs:
                                        if type(looked_up) == list:
                                            for shared_type_fe in looked_up:
                                                shared_fe_type = fe.get(shared_type_fe)
                                                # TODO overwritten value
                                                if shared_fe_type:
                                                    chunk['type'] = shared_fe_type
                                                if shared_fe_type == 'core':
                                                    if debug:
                                                        print 'Mapped FE "%s" is core for frame "%s"' % (shared_type_fe, frame['frame'])
                                                    core = True
                                        else:
                                            fe_type = fe.get(looked_up)
                                            if fe_type:
                                                chunk['type'] = fe_type
                                            if fe_type == 'core':
                                                if debug:
                                                    print 'Mapped FE "%s" is core for frame "%s"' % (looked_up, frame['frame'])
                                                core = True
                                    ### FE disambiguation strategy ###
                                    # If multiple FEs have the same ontology type, e.g., [Vincitore, Perdente] -> Club
                                    # BASELINE = random assignment
                                    # Needs to be adjusted by humans
                                    if type(looked_up) == list:
                                        chosen = random.choice(looked_up)
                                        chunk['FE'] = chosen
                                        # Avoid duplicates
                                        if chunk not in assigned_fes:
                                            assigned_fes.append(chunk)
                                    else:
                                        chunk['FE'] = looked_up
                                        # Avoid duplicates
                                        if chunk not in assigned_fes:
                                            assigned_fes.append(chunk)
                    # Continue to next frame if NO core FE was found
                    if not core:
                        if debug:
                            print 'No core FE for frame "%s": skipping' % frame['frame']
                        continue
                    # Otherwise assign frame and previously stored FEs
                    else:
                        if debug:
                            print 'ASSIGNING FRAME: %s' % frame['frame']
                            print 'ASSIGNING FEs: %s' % assigned_fes
                        ### Frame disambiguation strategy, part 2 ###
                        # If at least 1 core FE is detected in multiple frames:
                        # BASELINE = random assignment
                        # Needs to be adjusted by humans
                        current_frame = frame['frame']
                        previous_frame = labeled.get('frame')
                        if previous_frame:
                            previous_FEs = labeled['FEs']
                            choice = random.choice([previous_frame, current_frame])
                            if debug:
                                print 'CORE FES FOR MULTIPLE FRAMES WERE DETECTED. MAKING A RANDOM ASSIGNMENT: %s' % choice
                            if choice == current_frame:
                                labeled['frame'] = current_frame
                                labeled['FEs'] = assigned_fes
                        else:
                            labeled['frame'] = current_frame
                            labeled['FEs'] = assigned_fes

    # Normalize + annotate numerical FEs (only if we could disambiguate the sentence)
    if labeled.get('frame') and numerical:
        if debug:
            print 'LABELING AND NORMALIZING NUMERICAL FEs ...'
        for (start, end), tag, norm in NORMALIZER.normalize_many(sentence):
            chunk = sentence[start:end]
            if debug:
                print 'Chunk [%s] normalized into [%s], tagged as [%s]' % (chunk, norm, tag)
            fe = {  # All numerical FEs are extra ones and their values are literals
                'chunk': chunk,
                'FE': tag,
                'type': 'extra',
                'literal': norm,
                'score': 1.0
            }
            labeled['FEs'].append(fe)
    return labeled


def process_dir(indir, debug, numerical):
    """Walk into the input directory and process all the entity linking results,
    creating the labeled data

    :param str indir: Path to the directory with the entity linking results
    :param bool debug: Print debugging information
    :param bool numerical: Normalize numerical FEs
    :return: The labeled data
    :rtype: dict
    """
    processed = []
    for path, subdirs, files in os.walk(indir):
        for name in files:
            f = os.path.join(path, name)
            labeled = label_sentence(f, debug, numerical)
            # Filename is {WIKI_ID}.{SENTENCE_ID}(.{extension})?
            labeled['id'] = '.'.join(name.split('.')[:2])

            processed.append(labeled)
            if debug:
                print 'LABELED: %s' % labeled
    return processed


@click.command()
@click.argument('linked-dir', type=click.Path(exists=True, file_okay=False))
@click.argument('labeled_out', default='labeled.json')
@click.option('--score', type=click.Choice(['arithmetic-mean', 'weighted-mean',
                                            'f-score', '']))
@click.option('--core-weight', default=2)
@click.option('--score-fes/--no-score-fes', help='Score individual FEs')
@click.option('--debug/--no-debug', default=False)
@click.option('--numerical/--no-numerical', default=True)
def main(linked_dir, labeled_out, score, core_weight, score_fes, debug, numerical):
    """
    this script is the actual unsupervised approach which produces labeled data
    out of entity linked sentences
    """
    labeled = process_dir(linked_dir, score_fes, debug, numerical)

    if score:
        for sentence in labeled:
            sentence['score'] = compute_score(sentence, score, core_weight)
            if not score_fes:
                [fe.pop('score') for fe in sentence['FEs']]

    with codecs.open(labeled_out, 'wb', 'utf8') as f:
        json.dump(labeled, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
