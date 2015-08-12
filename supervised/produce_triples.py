# -*- encoding: utf-8 -*-

import os
if __name__ == '__main__' and __package__ is None:
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import click
import json
from lib.to_assertions import to_assertions
from collections import defaultdict
from rdflib.namespace import Namespace, NamespaceManager
from date_normalizer import DateNormalizer
from lib.scoring import compute_score, AVAILABLE_SCORES
from rdflib import Graph


# Namespace prefixes for RDF serialization
RESOURCE_NS = Namespace('http://it.dbpedia.org/resource/')
FACT_EXTRACTION_NS = Namespace('http://dbpedia.org/fact-extraction/')
ONTOLOGY_NS = Namespace('http://dbpedia.org/ontology/')
NAMESPACE_MANAGER = NamespaceManager(Graph())
NAMESPACE_MANAGER.bind('resource', RESOURCE_NS)
NAMESPACE_MANAGER.bind('fact', FACT_EXTRACTION_NS)
NAMESPACE_MANAGER.bind('ontology', ONTOLOGY_NS)


def read_sentences(rows):
    sentences = defaultdict(list)
    for row in rows:
        cols = row[:-1].decode('utf8').split('\t')
        sentences[cols[0]].append(cols)
    return sentences


def read_classifier_confidence(file_in):
    confidence = {}
    for row in file_in:
        sentence_id, token_id, frame_conf, role_conf, link_conf = row.split('\t')
        if not sentence_id in confidence:
            confidence[sentence_id] = {}
        confidence[sentence_id][token_id] = (float(frame_conf), 
                                             float(role_conf),
                                             float(link_conf))
    return confidence



def score_fe(fe, fe_format, confidence, fe_score_type):
    if fe_score_type == 'nothing':
        return 

    frame_conf, role_conf, link_conf = confidence[fe[1]]
    if fe_format == 'uri':
        if fe_score_type == 'svm':
            return role_conf
        elif fe_score_type == 'link':
            return link_conf
        elif fe_score_type == 'both':
            return 2 * (role_conf * link_conf) / (role_conf + link_conf)
    else:
        return role_conf


def to_labeled(sentences, confidence, fe_score_type):
    normalizer = DateNormalizer()
    labeled = []
    for sentence_id, rows in sentences.iteritems():
        lu = [x for x in rows if x[-1] == 'LU']
        if len(lu) != 1:
            print 'Could not find LU for sentence %s' % sentence_id
            continue
        else:
            lu = lu[0]
        
        fe_list = []
        for fe in rows:
            if fe[-1] not in {'O', 'LU'}:
                fe_format = 'uri' if fe[4].startswith('http://') else 'literal'
                score = score_fe(fe, fe_format, confidence.get(sentence_id),
                                 fe_score_type)

                fe_list.append({
                    'chunk': fe[2],
                    'type': 'core',
                    fe_format: fe[4],
                    'FE': fe[-1],
                    'score': float(score) if score is not None else None
                })

        sentence = ' '.join(x[2] for x in rows)
        labels = {
            'id': lu[0],
            'frame': lu[-2],
            'lu': lu[2],
            'sentence': sentence,
            'FEs': fe_list,
        }

        # normalize and annotate numerical expressions
        for (start, end), tag, norm in normalizer.normalize_many(sentence):
            labels['FEs'].append({
                'chunk': sentence[start:end],
                'FE': tag,
                'type': 'extra',
                'literal': norm
            })

        labeled.append(labels)
    return labeled


@click.command()
@click.argument('classified-output', type=click.File('r'))
@click.argument('classified-confidence', type=click.File('r'))
@click.argument('id-to-title', type=click.File('r'))
@click.argument('output-file', type=click.File('w'))
@click.argument('triple-scores', type=click.File('w'))
@click.option('--sentence-score', type=click.Choice(['arithmetic-mean', 'weighted-mean',
                                                     'f-score', 'nothing']))
@click.option('--fe-score', type=click.Choice(['svm', 'link', 'both', 'nothing']))
@click.option('--core-weight', default=2)
@click.option('--format', default='nt')
def main(classified_output, classified_confidence, output_file, id_to_title,
         triple_scores, format, sentence_score, core_weight, fe_score):

    sentences = read_sentences(classified_output)
    confidence = read_classifier_confidence(classified_confidence)
    labeled = to_labeled(sentences, confidence, fe_score)

    if sentence_score != 'nothing':
        for sentence in labeled:
            sentence['score'] = compute_score(sentence, sentence_score, core_weight)

    mapping = json.load(id_to_title)
    processed, discarded = to_assertions(labeled, mapping, NAMESPACE_MANAGER, {
                                            'ontology': ONTOLOGY_NS,
                                            'resource': RESOURCE_NS,
                                            'fact_extraction': FACT_EXTRACTION_NS,
                                         }, output_file, triple_scores, format)


if __name__ == '__main__':
    main()
