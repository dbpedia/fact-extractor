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


def to_labeled(sentences):
    normalizer = DateNormalizer()
    labeled = []
    for sentence_id, rows in sentences.iteritems():
        lu = [x for x in rows if x[-1] == 'LU']
        if len(lu) != 1:
            print 'Could not find LU for sentence %s' % sentence_id
            continue
        else:
            lu = lu[0]
        
        sentence = ' '.join(x[2] for x in rows)
        labels = {
            'id': sentence_id,
            'frame': lu[-2],
            'lu': lu[2],
            'sentence': sentence,
            'FEs': [
                {
                    'chunk': fe[2],
                    'type': 'core',
                    'uri': fe[4],  # classifier returns linked FEs
                    'FE': fe[-1],
                } for fe in rows if fe[-1] not in {'O', 'LU'}
            ]
        }

        print '\n'.join(repr((fe[4], fe[-1])) for fe in rows if fe[-1] not in ['O', 'LU'])

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
@click.argument('output-file', type=click.File('w'))
@click.argument('id-to-title', type=click.File('r'))
@click.option('--format', default='nt')
def main(classified_output, output_file, id_to_title, format):
    sentences = read_sentences(classified_output)
    labeled = to_labeled(sentences)
    mapping = json.load(id_to_title)
    processed, discarded = to_assertions(labeled, mapping, NAMESPACE_MANAGER, {
                                            'ontology': ONTOLOGY_NS,
                                            'resource': RESOURCE_NS,
                                            'fact_extraction': FACT_EXTRACTION_NS,
                                         }, output_file, format)


if __name__ == '__main__':
    main()
